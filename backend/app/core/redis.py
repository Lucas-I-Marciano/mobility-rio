import redis 
import os
from dotenv import load_dotenv
load_dotenv()

REDIS_HOST=os.getenv("REDIS_HOST")
REDIS_PORT=os.getenv("REDIS_PORT")
REDIS_DB=os.getenv("REDIS_DB")


redis_client = redis.Redis(
    host=REDIS_HOST,
    port=int(REDIS_PORT),
    db=int(REDIS_DB),
    decode_responses=True,
    socket_connect_timeout=5 # Timeout para conectar
    )