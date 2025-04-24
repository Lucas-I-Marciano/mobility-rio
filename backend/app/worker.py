import os
from celery import Celery
from dotenv import load_dotenv
import time

load_dotenv()  # take environment variables

redis_url = os.getenv("REDIS_URL", "redis://localhost:6379/0")
print(f"Redis URL: {redis_url}")  # Verifique se a URL do Redis está correta
if redis_url is None:
    raise ValueError("A variável de ambiente REDIS_URL não foi encontrada.")

# Configurar o Celery com a URL do Redis
celery_app  = Celery("app", broker=redis_url)
celery_app.conf.worker_pool = 'solo'

@celery_app.task
def add(x, y):
    print(x+y)
    return x + y