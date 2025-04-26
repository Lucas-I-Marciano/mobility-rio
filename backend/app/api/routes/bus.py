from fastapi import APIRouter, HTTPException, Query, Path, Body
from typing import Annotated, List
import math
import json
import redis
import logging

from app.core.redis import redis_client
from app.services.redis import get_latest_bus_data
from app.services.bus_filtering import filter_and_paginate_buses, add_distance_to_buses
from app.core.exceptions import (
    RedisServiceUnavailableError,
    DataNotFoundError,
    InvalidDataFormatError,
    RedisOperationError,
    ServiceError 
)
from app.utils.bus_record import process_vehicle_data, analyze_vehicle_movement, analyze_vehicle_movement_distance

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/bus")

@router.post("/filter")
def filter_bus(
    page: Annotated[int, Query(ge=1, description="Número da página desejada")] = 1,
    limit: Annotated[int, Query(ge=1, le=100, description="Número de itens por página (máx 100)")] = 10,
    lines: Annotated[List[str] | None, Body(description="Filtrar pela linha do ônibus (opcional)")] = None
    ):
    logger.info(f"Received request for /filter?page={page}&limit={limit}")
    try:
        # 1. Get all data from Redis service
        full_bus_list = get_latest_bus_data()

        # 2. Apply filtering and pagination using the dedicated service
        result = filter_and_paginate_buses(
            full_bus_list=full_bus_list,
            page=page,
            limit=limit,
            lines=lines
        )

        logger.info(f"Returning {len(result['items'])} items for page {result['current_page']}/{result['total_pages']} (Line: {lines or 'All'})")
        return result

    except RedisServiceUnavailableError as e:
        logger.warning(f"Redis service unavailable: {e}")
        raise HTTPException(status_code=503, detail=str(e))
    except DataNotFoundError as e:
        logger.info(f"Data not found: {e}")
        raise HTTPException(status_code=404, detail=str(e))
    except InvalidDataFormatError as e:
        logger.error(f"Invalid data format error: {e}")
        raise HTTPException(status_code=500, detail=str(e))
    except RedisOperationError as e:
        logger.error(f"Redis operation error: {e.original_exception}")
        raise HTTPException(status_code=500, detail="Erro interno ao acessar o cache de dados.")
    except ServiceError as e: # Catch other potential service errors
         logger.error(f"Generic service error: {e}")
         raise HTTPException(status_code=500, detail="Erro interno no serviço.")
    except Exception as e:
        # Catch any other unexpected errors in the route itself
        logger.exception(f"Unexpected error in /filter route: {e}")
        raise HTTPException(status_code=500, detail="Erro interno inesperado no servidor.")

@router.get("/lines")
def get_distinct_lines():
    if not redis_client:
        raise HTTPException(status_code=503, detail="Serviço Redis indisponível")
    try:
        stored_data = redis_client.get('latest_bus_data')
        if stored_data:
            full_bus_list = json.loads(stored_data)

            if not isinstance(full_bus_list, list):
                 raise HTTPException(status_code=500, detail="Formato de dados armazenados inválido (não é uma lista)")

            lines = map(lambda bus_info: bus_info['linha'] if bus_info['linha'] !="FORA DE OP" else "", full_bus_list)
            unique_lines = set(list(lines))
            return sorted(unique_lines)
        else:
            # Se não houver dados no cache, pode retornar vazio ou um erro 404
            raise HTTPException(status_code=404, detail="Dados de ônibus ainda não disponíveis")
    except redis.exceptions.RedisError as e:
        print(f"Erro ao ler dados do Redis: {e}")
        raise HTTPException(status_code=500, detail="Erro interno ao acessar dados")
    except json.JSONDecodeError:
         raise HTTPException(status_code=500, detail="Erro ao decodificar dados armazenados")

@router.get("/lines/{id}")
def retrieve_line(id: Annotated[str, Path()]):
    if not redis_client:
        raise HTTPException(status_code=503, detail="Serviço Redis indisponível")
    try:
        stored_data = redis_client.get('latest_bus_data')
        if stored_data:
            full_bus_list = json.loads(stored_data)

            if not isinstance(full_bus_list, list):
                 raise HTTPException(status_code=500, detail="Formato de dados armazenados inválido (não é uma lista)")

            lines = map(lambda bus_info: bus_info if bus_info['linha'] == id else "", full_bus_list)
            formated_lines = [line for line in list(lines) if line != ""]
            if len(formated_lines) == 0 :
                raise HTTPException(status_code=404, detail="Dados para linha selecionada não encontrados")
            return formated_lines
        else:
            # Se não houver dados no cache, pode retornar vazio ou um erro 404
            raise HTTPException(status_code=404, detail="Dados de ônibus ainda não disponíveis")
    except redis.exceptions.RedisError as e:
        print(f"Erro ao ler dados do Redis: {e}")
        raise HTTPException(status_code=500, detail="Erro interno ao acessar dados")
    except json.JSONDecodeError:
         raise HTTPException(status_code=500, detail="Erro ao decodificar dados armazenados")
    
@router.post("/distance")
def get_bus_distance(
    target_lines: Annotated[List[str], Body(description="Filtrar pela linha do ônibus")],
    dest_lat_float: Annotated[float, Query(description="Latitude do ponto de ônibus")],
    dest_lng_float: Annotated[float, Query(description="Longitude do ponto de ônibus")]
    ):
    """
    Calculate distance to a destination, and return the results.
    """
    logger.info(f"Initiating distance calculation test for lines {target_lines} to ({dest_lat_float}, {dest_lng_float})")

    try:
        # 1. Get all bus data
        full_bus_list = get_latest_bus_data()
        logger.info(f"Fetched {len(full_bus_list)} total buses from Redis.")

        # 2. Filter for the target line (get all items)
        # Note: Passing the line as a list as expected by the modified function
        # Using a large limit to bypass pagination for the test
        pagination_result = filter_and_paginate_buses(
            full_bus_list=full_bus_list,
            page=1,
            limit=len(full_bus_list) + 1, # Ensure limit > total items
            lines=target_lines
        )
        buses_for_line = pagination_result.get("items", [])
        logger.info(f"Found {len(buses_for_line)} buses for line {target_lines}.")

        if not buses_for_line:
             return {"message": f"No buses found for line {target_lines}", "results": []}

        # 3. Calculate distances for the filtered buses
        # Assuming the distance function is named add_distance_to_buses
        results_with_distance = add_distance_to_buses(
            bus_list=buses_for_line,
            dest_lat=dest_lat_float,
            dest_lng=dest_lng_float
        )

        processed_data = process_vehicle_data({"results" : results_with_distance})
        vehicle_movement = analyze_vehicle_movement(processed_data)
        logger.info(f"Calculated distances for {len(results_with_distance)} buses.")
        # Using logger.debug might be better for potentially large output
        logger.debug(f"Results with distance: {results_with_distance}")

        to_return = analyze_vehicle_movement_distance(results_with_distance)
        return {"results": to_return}

    # --- Handle potential errors from services ---
    except RedisServiceUnavailableError as e:
        raise HTTPException(status_code=503, detail=str(e))
    except DataNotFoundError as e:
         # If the base key isn't found, we can't test
         raise HTTPException(status_code=404, detail=str(e))
    except (InvalidDataFormatError, RedisOperationError, ServiceError) as e:
         logger.error(f"Service error during test: {e}")
         raise HTTPException(status_code=500, detail="Erro interno no serviço durante o teste.")
    except Exception as e:
        logger.exception(f"Unexpected error in /test/distance_calc route: {e}")
        raise HTTPException(status_code=500, detail="Erro interno inesperado no servidor de teste.")