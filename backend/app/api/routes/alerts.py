from fastapi import APIRouter, Depends, HTTPException, Body, Query
from typing import Annotated, List, Optional
from sqlmodel import Session, select
import datetime

from app.schemas.user_alerts import UserAlertCreate, UserAlertRead, UserAlertUpdate
from app.db.user_alerts import UserAlert
from app.db import get_session
from app.schemas.endpoint_tags import EndpointTags

import logging
from sqlmodel import Session, select # Importe select

# from app.db import session_dependency # Sua dependência de sessão do db.py
# Importe a função utilitária de conversão de tempo (se a extraiu) ou a lógica necessária
# from app.utils.time_conversion import convert_aware_datetime_to_sao_paulo_time

# --- Lógica de conversão (Exemplo se não estiver em utils) ---
# Precisamos dela para o PATCH. É melhor colocar em um arquivo utils.py
from datetime import datetime, time
from zoneinfo import ZoneInfo
SAO_PAULO_TZ = ZoneInfo("America/Sao_Paulo")

def convert_datetime_to_sao_paulo_time(value: datetime) -> time:
    if value.tzinfo is None:
        raise ValueError("Time conversion requires timezone-aware datetime.")
    try:
        local_dt = value.astimezone(SAO_PAULO_TZ)
        return local_dt.time()
    except Exception as e:
        raise ValueError(f"Erro ao converter data/hora para fuso de São Paulo: {e}")

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/alerts", tags=[EndpointTags.ALERTS])

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

@router.get("/{alert_id}", response_model=UserAlertRead)
def read_user_alert(
    *,
    session: session_dependency,
    alert_id: int
):
    """
    Obtém os detalhes de um alerta específico pelo ID.
    """
    logger.info(f"Buscando alerta ID: {alert_id}")
    db_alert = session.get(UserAlert, alert_id)
    if not db_alert:
        logger.warning(f"Alerta ID {alert_id} não encontrado.")
        raise HTTPException(status_code=404, detail="Alerta não encontrado")
    return db_alert

@router.get("/", response_model=List[UserAlertRead])
def list_user_alerts(
    *,
    session: session_dependency,
    user_email: str = Query(..., description="Email do usuário para filtrar os alertas"),
    offset: int = Query(0, ge=0), # Para paginação
    limit: int = Query(100, ge=1, le=200), # Limite razoável
    active_only: bool = Query(True, description="Retornar apenas alertas ativos?")
):
    """
    Lista os alertas de um usuário específico, com opção de filtro e paginação.
    """
    logger.info(f"Listando alertas para {user_email} (offset={offset}, limit={limit}, active_only={active_only})")
    statement = select(UserAlert).where(UserAlert.user_email == user_email)
    if active_only:
        statement = statement.where(UserAlert.alert_active == True)

    statement = statement.offset(offset).limit(limit) # Aplica paginação

    try:
        alerts = session.exec(statement).all()
        logger.info(f"Retornando {len(alerts)} alertas para {user_email}.")
        return alerts
    except Exception as e:
        logger.exception(f"Erro no banco de dados ao listar alertas para {user_email}: {e}")
        raise HTTPException(status_code=500, detail="Erro interno ao buscar alertas.")


# --- UPDATE (NOVO - usando PATCH) ---
@router.patch("/{alert_id}", response_model=UserAlertRead)
def update_user_alert(
    *,
    session: session_dependency,
    alert_id: int,
    alert_update: UserAlertUpdate # Modelo com campos opcionais
):
    """
    Atualiza parcialmente um alerta existente.
    """
    logger.info(f"Recebida requisição para atualizar alerta ID: {alert_id}")
    db_alert = session.get(UserAlert, alert_id)
    if not db_alert:
        logger.warning(f"Alerta ID {alert_id} não encontrado para atualização.")
        raise HTTPException(status_code=404, detail="Alerta não encontrado")

    # Pega os dados que foram enviados na requisição (excluindo os não definidos)
    update_data = alert_update.model_dump(exclude_unset=True)
    logger.info(f"Dados para atualização: {update_data}")

    extra_data = {} # Para campos que precisam de conversão (como tempo)
    for key, value in update_data.items():
        # --- Tratamento especial para campos de tempo ---
        if key in ["time_window_start", "time_window_end"] and isinstance(value, datetime):
             try:
                 # Converte o datetime (aware) para time (aware no fuso SP)
                 time_value = convert_datetime_to_sao_paulo_time(value)
                 setattr(db_alert, key, time_value) # Define o valor convertido
             except ValueError as e:
                 raise HTTPException(status_code=422, detail=f"Erro no campo '{key}': {e}")
        # --- Fim tratamento de tempo ---
        # --- Tratamento bus_line (se aceita lista na entrada mas salva str) ---
        elif key == "bus_line" and isinstance(value, list):
             # Regra de exemplo: salvar apenas a primeira linha da lista
             if value:
                  setattr(db_alert, key, str(value[0]))
             else:
                  raise HTTPException(status_code=422, detail="Campo 'bus_line' não pode ser uma lista vazia.")
        # --- Fim tratamento bus_line ---
        else:
            # Atualiza outros campos diretamente
            setattr(db_alert, key, value)

    try:
        session.add(db_alert)
        session.commit()
        session.refresh(db_alert)
        logger.info(f"Alerta ID {db_alert.id} atualizado com sucesso.")
        return db_alert
    except Exception as e:
        session.rollback()
        logger.exception(f"Erro no banco de dados ao atualizar alerta ID {alert_id}: {e}")
        raise HTTPException(status_code=500, detail="Erro interno ao atualizar o alerta.")


# --- DELETE (NOVO) ---
@router.delete("/{alert_id}", status_code=200) # Retorna 200 OK com mensagem ou 204 No Content
def delete_user_alert(
    *,
    session: session_dependency,
    alert_id: int
):
    """
    Deleta um alerta existente.
    """
    logger.info(f"Recebida requisição para deletar alerta ID: {alert_id}")
    db_alert = session.get(UserAlert, alert_id)
    if not db_alert:
        logger.warning(f"Alerta ID {alert_id} não encontrado para deleção.")
        raise HTTPException(status_code=404, detail="Alerta não encontrado")

    # Aqui também deveria ter uma verificação de permissão/proprietário em um app real

    try:
        session.delete(db_alert)
        session.commit()
        logger.info(f"Alerta ID {alert_id} deletado com sucesso.")
        # Pode retornar 204 No Content ou uma mensagem
        return {"message": "Alerta deletado com sucesso"}
        # Para retornar 204, use status_code=204 e não retorne nada (ou None)
        # from fastapi import Response
        # return Response(status_code=204)
    except Exception as e:
        session.rollback()
        logger.exception(f"Erro no banco de dados ao deletar alerta ID {alert_id}: {e}")
        raise HTTPException(status_code=500, detail="Erro interno ao deletar o alerta.")
