from fastapi import FastAPI
from fastapi import HTTPException
import redis 
import json


from app.api.routes import bus
from app.core.redis import redis_client


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
            return {"message": "Success! Showing first 30 values", "data": json.loads(stored_data)[:30]}
        else:
            # Se não houver dados no cache, pode retornar vazio ou um erro 404
            raise HTTPException(status_code=404, detail="Dados de ônibus ainda não disponíveis")
    except redis.exceptions.RedisError as e:
        print(f"Erro ao ler dados do Redis: {e}")
        raise HTTPException(status_code=500, detail="Erro interno ao acessar dados")
    except json.JSONDecodeError:
         raise HTTPException(status_code=500, detail="Erro ao decodificar dados armazenados")

