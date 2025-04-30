from pydantic import BaseModel, EmailStr, Field
from datetime import time # Importe time

class ConfirmationEmailRequest(BaseModel):
    recipient_email: EmailStr # Valida o formato do email
    bus_line: str
    stop_lat: float # Latitude do ponto
    stop_lng: float # Longitude do ponto
    start_time: time # Hora de início da janela (já convertida)
    end_time: time   # Hora de fim da janela (já convertida)