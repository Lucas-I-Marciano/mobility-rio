from celery import Celery

app = Celery('task', broker="amqp://localhost")

@app.task
def hello(name):
    return f"Hello {name}"