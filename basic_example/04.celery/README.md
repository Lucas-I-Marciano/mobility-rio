# Celery

### Starting

`pip install celery`  
`celery -A task worker -l info --pool=solo`  
`podman compose up`  
or  
`docker-compose up`

Create a app instance of Celery linked with RabitMQ  
RabbitMQ -> On docker, it will create queue for Celery  
flower -> To see tasks flow
