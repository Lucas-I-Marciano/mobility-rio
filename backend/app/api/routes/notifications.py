import logging
from fastapi import APIRouter, HTTPException, Depends, BackgroundTasks
# Importe a função de envio e os modelos/constantes
from app.services.notification import (
    send_notification_email,
    EMAIL_CONFIRMATION_SUBJECT,
    EMAIL_CONFIRMATION_BODY_TEXT,
    EMAIL_CONFIRMATION_BODY_HTML
)
from app.schemas.notification import ConfirmationEmailRequest # Modelo de requisição

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/notifications", tags=["Notifications"])

@router.post("/send-confirmation", status_code=202) # 202 Accepted é bom para tarefas de background
async def send_alert_confirmation_email(
    request_data: ConfirmationEmailRequest,
    background_tasks: BackgroundTasks # Para enviar email em background
):
    """
    Envia um e-mail de confirmação para o usuário após a criação bem-sucedida de um alerta.
    """
    logger.info(f"Recebida solicitação para enviar email de confirmação para: {request_data.recipient_email}")

    try:
        # Formata as mensagens com os dados recebidos
        # Formata a hora para HH:MM
        start_time_str = request_data.start_time.strftime('%H:%M')
        end_time_str = request_data.end_time.strftime('%H:%M')

        body_text = EMAIL_CONFIRMATION_BODY_TEXT.format(
            bus_line=request_data.bus_line,
            stop_lat=f"{request_data.stop_lat:.5f}", # Formata float
            stop_lng=f"{request_data.stop_lng:.5f}",
            start_time=start_time_str,
            end_time=end_time_str
        )
        body_html = EMAIL_CONFIRMATION_BODY_HTML.format(
            bus_line=request_data.bus_line,
            stop_lat=f"{request_data.stop_lat:.5f}",
            stop_lng=f"{request_data.stop_lng:.5f}",
            start_time=start_time_str,
            end_time=end_time_str
        )

        # Adiciona a tarefa de envio de email ao background
        # Isso evita que a resposta da API espere o email ser enviado
        background_tasks.add_task(
            send_notification_email,
            recipient_email=request_data.recipient_email,
            email_subject=EMAIL_CONFIRMATION_SUBJECT,
            body_plain_text=body_text,
            body_html_content=body_html
        )

        logger.info(f"Tarefa de envio de email para {request_data.recipient_email} adicionada ao background.")
        return {"message": "Solicitação de envio de email de confirmação recebida."}

    except Exception as e:
        # Captura erros na formatação ou ao adicionar a task (pouco provável)
        logger.exception(f"Erro ao preparar ou agendar email de confirmação para {request_data.recipient_email}: {e}")
        # Não levanta HTTPException aqui, pois o alerta JÁ foi criado.
        # A falha no email de confirmação não deve falhar a operação principal.
        # Apenas retorna uma mensagem indicando que o email pode não ter sido enviado.
        return {"message": "Alerta criado, mas houve um problema ao solicitar o envio do email de confirmação."}