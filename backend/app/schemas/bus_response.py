from pydantic import BaseModel, Field
from datetime import datetime
from typing import Optional

class BusStatus(BaseModel):
    ordem: str
    latitude: float
    longitude: float
    velocidade: float
    linha: str | list[str]
    datahora_ultima: datetime 
    eta_seconds: int | None = None # Tempo estimado até o ponto do usuário em segundos

    class Config:
        from_attributes = True # Se usar ORM/SQLModel mais tarde