# Em backend/app/worker.py

import os
# from celery.schedules import crontab # Não precisa mais importar crontab aqui
from dotenv import load_dotenv

from app.celery_config import celery_app

# Manter a importação pode ajudar a garantir o registro da task,
# embora o 'include' em celery_config também deva fazer isso.
from app.tasks import bus
# Ou: import app.tasks.bus

load_dotenv()

# Configurações específicas do worker (se houver)
celery_app.conf.worker_pool = 'solo'

# ---> REMOVA O BEAT SCHEDULE DESTE ARQUIVO <---
# A configuração do beat_schedule foi movida para celery_config.py