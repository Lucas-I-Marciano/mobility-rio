from celery import Celery
from celery.schedules import crontab
import os
from dotenv import load_dotenv
load_dotenv()

redis_url = os.getenv('REDIS_URL', "redis://localhost:6379/0")

celery_app = Celery(
    "app",
    broker=redis_url,
    backend=redis_url,
    include=['app.tasks.bus', 'app.tasks.alerts'] # onde estão as tarefas
)

celery_app.conf.update(
    task_serializer='json',
    accept_content=['json'],
    result_serializer='json',
    timezone='America/Sao_Paulo',
    enable_utc=False,
    worker_pool = "solo"
)


celery_app.conf.beat_schedule = {
    'fetch-bus-data-every-minute': {
        'task': 'tasks.fetch_bus_data',
        'schedule': crontab(minute='*'), # A cada minuto
    },
    'fetch-alert-data-every-minute': {
        'task': 'tasks.check_bus_alerts',
        'schedule': crontab(minute='*'), # A cada minuto
    }
}