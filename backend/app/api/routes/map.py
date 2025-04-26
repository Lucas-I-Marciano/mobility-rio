from fastapi import APIRouter, HTTPException
from typing import Annotated, Dict
from pydantic import BaseModel, Field
from datetime import datetime
import logging # Para logar erros

from app.services.travel_time import get_travel_time_estimate
from app.schemas.travel_mode import TravelMode

# Configuração básica de logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

router = APIRouter(prefix="/map")

# 1. Defina um modelo Pydantic para o corpo da requisição --> Botar isso no schemas depois
class ETARequest(BaseModel):
    # Use float para validação automática (FastAPI/Pydantic farão a conversão)
    origin_lat: float = Field(..., description="Latitude de origem")
    origin_lng: float = Field(..., description="Longitude de origem")
    dest_lat: float = Field(..., description="Latitude de destino")
    dest_lng: float = Field(..., description="Longitude de destino")
    modal: TravelMode = Field(..., description="Modo de transporte desejado")
    departure_time: datetime = Field(..., description="Data e hora de partida (formato ISO 8601 com offset, ex: 2025-04-25T22:30:00-03:00)")

class ETAResponse(BaseModel):
    total_travel_time_seconds: int
    modes: Dict[str, int] # Dictionary for mode breakdown


@router.post("/eta", response_model=ETAResponse) # Define o modelo de resposta
async def calculate_eta_route(request_data: ETARequest): # Recebe o corpo como modelo
    """
    Endpoint de teste para calcular o tempo estimado de viagem entre dois pontos.
    """
    logger.info(f"Recebida requisição ETA: Origem=({request_data.origin_lat}, {request_data.origin_lng}), Destino=({request_data.dest_lat}, {request_data.dest_lng})")
    try:
        # 3. Chame a função de serviço com 'await' e passe os argumentos corretos
        result_dict = await get_travel_time_estimate(
            origin_lat=request_data.origin_lat,
            origin_lng=request_data.origin_lng,
            dest_lat=request_data.dest_lat,
            dest_lng=request_data.dest_lng,
            modal=request_data.modal.value,
            departure_time=request_data.departure_time
        )

        # 4. Verifique o resultado e retorne apropriadamente
        if result_dict is not None:
            return ETAResponse(
                total_travel_time_seconds=result_dict.pop("total_travel_time_seconds"),
                modes=result_dict
            )
        else:
            # A função get_travel_time_estimate já logou o erro específico
            logger.warning("Não foi possível calcular o ETA.")
            # Retorna um status indicando que o cálculo falhou (ex: 503 se API externa falhou, 404 se rota não encontrada pela API externa)
            # Ou um 500 genérico se a causa não for clara para o cliente.
            raise HTTPException(status_code=503, detail="Não foi possível calcular o tempo de viagem no momento.")

    # 5. Capture exceções específicas ou genéricas de forma mais controlada
    except HTTPException as http_exc:
        # Re-levanta exceções HTTP já tratadas (como as de dentro do get_travel_time_estimate, se houver)
        raise http_exc
    except Exception as e:
        # Captura outros erros inesperados
        logger.exception(f"Erro inesperado ao processar /map/eta: {e}") # logger.exception inclui traceback
        raise HTTPException(status_code=500, detail="Erro interno no servidor ao calcular ETA.")

