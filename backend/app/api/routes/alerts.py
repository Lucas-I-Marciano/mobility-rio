from fastapi import APIRouter, Depends, HTTPException, Body
from typing import Annotated
from sqlmodel import Session
import datetime

from app.schemas.user_alerts import UserAlertRead, UserAlertCreate
from app.db.user_alerts import UserAlert
from app.db import get_session

router = APIRouter(prefix="/alerts")

session_dependency = Annotated[Session, Depends(get_session)] # Help on database management

@router.post("/", response_model=UserAlertRead)
def create_user_alert(
    *,
    session: session_dependency,
    alert_in: UserAlertCreate
):
    # Cria uma instância do modelo de banco de dados a partir do modelo de entrada da API
    db_alert = UserAlert.model_validate(alert_in) # SQLModel v0.0.14+

    session.add(db_alert)
    session.commit()
    session.refresh(db_alert) # Recarrega o objeto para obter id, created_at, updated_at
    return db_alert

@router.get("/user-alerts/{alert_id}", response_model=UserAlertRead)
def read_user_alert(
    *,
    session: session_dependency,
    alert_id: int
):
    alert = session.get(UserAlert, alert_id)
    if not alert:
        raise HTTPException(status_code=404, detail="User Alert not found")
    return alert