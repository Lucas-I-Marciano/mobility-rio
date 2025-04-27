from sqlmodel import SQLModel
from datetime import datetime, time
from zoneinfo import ZoneInfo
from pydantic import field_validator

SAO_PAULO_TZ = ZoneInfo("America/Sao_Paulo")

class UserAlertCreate(SQLModel):
    # Campos esperados ao criar um novo alerta via API
    user_email: str
    bus_line: list[str] | str
    stop_latitude: float
    stop_longitude: float
    time_window_start: datetime
    time_window_end: datetime
    alert_active: bool | None = True # Pode ser opcional na criação, default True
    
    @field_validator('time_window_start', 'time_window_end', mode='after')
    @classmethod
    def convert_datetime_to_sao_paulo_time(cls, value: datetime) -> time:
        """
        Converte o datetime recebido (aware) para a hora local de São Paulo
        e retorna apenas o objeto time.
        """
        if value.tzinfo is None:
            # Se o Pydantic não conseguiu determinar o fuso (string sem offset), é um erro
            raise ValueError("Formato de data/hora inválido: Fuso horário (offset) é obrigatório.")

        try:
            # Converte para o fuso horário de São Paulo
            local_dt = value.astimezone(SAO_PAULO_TZ)
            # Retorna APENAS a parte da hora (HH:MM:SS)
            return local_dt.time()
        except Exception as e:
            # Captura outros erros de conversão, se houver
            raise ValueError(f"Erro ao converter data/hora para fuso de São Paulo: {e}")

class UserAlertRead(SQLModel):
    id: int
    user_email: str
    bus_line: str
    stop_latitude: float
    stop_longitude: float
    time_window_start: time
    time_window_end: time
    alert_active: bool
    # created_at: datetime
    # updated_at: datetime

class UserAlertUpdate(SQLModel):
    user_email: str | None = None
    bus_line: str | None = None
    stop_latitude: float | None = None
    stop_longitude: float | None = None
    time_window_start: datetime | None = None
    time_window_end: datetime | None = None
    alert_active: bool | None = None