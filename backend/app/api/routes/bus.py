from fastapi import APIRouter, HTTPException, Query
from typing import Annotated
import math
import json
import redis

from app.core.redis import redis_client

router = APIRouter(prefix="/bus")

@router.get("/filter")
def filter_bus(
    page: Annotated[int, Query(ge=1, description="Número da página desejada")] = 1,
    limit: Annotated[int, Query(ge=1, le=100, description="Número de itens por página (máx 100)")] = 10
):
    if not redis_client:
        raise HTTPException(status_code=503, detail="Serviço Redis indisponível")
    try:
        stored_data = redis_client.get('latest_bus_data')
        if stored_data:
            full_bus_list = json.loads(stored_data)

            if not isinstance(full_bus_list, list):
                 raise HTTPException(status_code=500, detail="Formato de dados armazenados inválido (não é uma lista)")

            total_items = len(full_bus_list)
            offset = (page - 1) * limit
            total_pages = math.ceil(total_items / limit) if limit > 0 else 0
            paginated_items = full_bus_list[offset : offset + limit]

            return {
                "total_items": total_items,
                "total_pages": total_pages,
                "current_page": page,
                "limit": limit,
                "items": paginated_items # A lista de ônibus para a página atual
            }
        else:
            # Se não houver dados no cache, pode retornar vazio ou um erro 404
            raise HTTPException(status_code=404, detail="Dados de ônibus ainda não disponíveis")
    except redis.exceptions.RedisError as e:
        print(f"Erro ao ler dados do Redis: {e}")
        raise HTTPException(status_code=500, detail="Erro interno ao acessar dados")
    except json.JSONDecodeError:
         raise HTTPException(status_code=500, detail="Erro ao decodificar dados armazenados")

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
            return list(data)
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