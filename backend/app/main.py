from fastapi import FastAPI
from dotenv import load_dotenv
from app.api.routes import bus
import redis 
import json
from fastapi import HTTPException

redis_client = redis.Redis(
    host="redis",
    port=6379,
    db=0,
    decode_responses=True,
    socket_connect_timeout=5 # Timeout para conectar
    )

load_dotenv()  # take environment variables

app = FastAPI()

app.include_router(bus.router)

@app.get("/")
async def root():
    if not redis_client:
        raise HTTPException(status_code=503, detail="Serviço Redis indisponível")
    try:
        stored_data = redis_client.get('latest_bus_data')
        if stored_data:
            # Converte a string JSON de volta para um objeto Python
            return json.loads(stored_data)
        else:
            # Se não houver dados no cache, pode retornar vazio ou um erro 404
            raise HTTPException(status_code=404, detail="Dados de ônibus ainda não disponíveis")
    except redis.exceptions.RedisError as e:
        print(f"Erro ao ler dados do Redis: {e}")
        raise HTTPException(status_code=500, detail="Erro interno ao acessar dados")
    except json.JSONDecodeError:
         raise HTTPException(status_code=500, detail="Erro ao decodificar dados armazenados")

