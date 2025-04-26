from sqlmodel import SQLModel
from decimal import Decimal
import datetime

class UserAlertCreate(SQLModel):
    # Campos esperados ao criar um novo alerta via API
    user_email: str
    bus_line: list[str]
    stop_latitude: Decimal
    stop_longitude: Decimal
    time_window_start: datetime.time
    time_window_end: datetime.time
    alert_active: bool | None = True # Pode ser opcional na criação, default True

class UserAlertRead(SQLModel):
    # Campos retornados ao ler um alerta da API
    id: int
    user_email: str
    bus_line: str
    stop_latitude: Decimal
    stop_longitude: Decimal
    time_window_start: datetime.time
    time_window_end: datetime.time
    alert_active: bool
    created_at: datetime.datetime
    updated_at: datetime.datetime

class UserAlertUpdate(SQLModel):
     # Campos que podem ser atualizados via API (exemplo)
    user_email: str | None = None
    bus_line: str | None = None
    stop_latitude: Decimal | None = None
    stop_longitude: Decimal | None = None
    time_window_start: datetime.time | None = None
    time_window_end: datetime.time | None = None
    alert_active: bool | None = None