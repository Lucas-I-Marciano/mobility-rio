from celery import Celery
import time

app = Celery('task', broker="amqp://localhost")

@app.task
def hello(name):
    time.sleep(5)
    return f"Hello {name}"