# Em backend/app/celery_config.py

from celery import Celery
from celery.schedules import crontab # Import crontab aqui
import os

redis_url = os.getenv('REDIS_URL', "redis://redis:6379/0")

celery_app = Celery(
    "app",
    broker=redis_url,
    backend=redis_url,
    # Adicione a linha include para apontar onde estão suas tarefas
    include=['app.tasks.bus']
)

celery_app.conf.update(
    task_serializer='json',
    accept_content=['json'],
    result_serializer='json',
    timezone='America/Sao_Paulo',
    enable_utc=False,
)

# ---> MOVA O BEAT SCHEDULE PARA CÁ <---
celery_app.conf.beat_schedule = {
    'fetch-bus-data-every-minute': {
        # Use o nome EXATO da tarefa definido no @celery_app.task(name=...)
        'task': 'tasks.fetch_bus_data',
        'schedule': crontab(), # A cada minuto
        # args: () # Se sua task precisasse de argumentos
    },
    # Você pode adicionar outras tarefas agendadas aqui
}