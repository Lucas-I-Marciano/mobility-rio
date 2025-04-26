from fastapi import APIRouter, HTTPException, Query, Path
from typing import Annotated
import math
import json
import redis
import logging

from app.core.redis import redis_client
from app.services.redis import get_latest_bus_data
from app.core.exceptions import (
    RedisServiceUnavailableError,
    DataNotFoundError,
    InvalidDataFormatError,
    RedisOperationError,
    ServiceError 
)

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/bus")

@router.get("/filter")
def filter_bus(
    page: Annotated[int, Query(ge=1, description="Número da página desejada")] = 1,
    limit: Annotated[int, Query(ge=1, le=100, description="Número de itens por página (máx 100)")] = 10
    ):
    logger.info(f"Received request for /filter?page={page}&limit={limit}")
    try:
        full_bus_list = get_latest_bus_data()

        # --- Pagination Logic ---
        total_items = len(full_bus_list)
        offset = (page - 1) * limit
        total_pages = math.ceil(total_items / limit) if limit > 0 else 0
        paginated_items = full_bus_list[offset : offset + limit]
        # --- End Pagination ---

        logger.info(f"Returning {len(paginated_items)} items for page {page}/{total_pages}")
        return {
            "total_items": total_items,
            "total_pages": total_pages,
            "current_page": page,
            "limit": limit,
            "items": paginated_items
        }

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