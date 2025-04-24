from app.celery_config import celery_app
import requests
import redis
import os
import json
from datetime import datetime, timedelta # Import datetime

redis_url = os.getenv("REDIS_URL", "redis://localhost:6379/0")
try:
    redis_client = redis.Redis(
        host="redis",
        port=6379,
        db=0,
        decode_responses=True,
        socket_connect_timeout=5 # Timeout para conectar
    )
    redis_client.ping()
    print("tasks/bus.py: Conectado ao Redis") # Adiciona nome do arquivo ao log
except redis.exceptions.ConnectionError as e:
    print(f"tasks/bus.py: ERRO ao conectar ao Redis: {e}")

@celery_app.task(name='tasks.fetch_bus_data')
def get_bus():
    API_URL = "https://dados.mobilidade.rio/gps/sppo"
    now = datetime.now()
    # Pega um intervalo de 2 minutos para aumentar a chance de pegar dados
    # A API pode ter um pequeno delay
    some_minutes_ago = now - timedelta(minutes=2)

    data_final_str = now.strftime('%Y-%m-%d %H:%M:%S')
    data_inicial_str = some_minutes_ago.strftime('%Y-%m-%d %H:%M:%S')

    params = {
        'dataInicial': data_inicial_str,
        'dataFinal': data_final_str
    }
    print(f"Task get_bus: Buscando dados entre {data_inicial_str} e {data_final_str}")

    try:
        # Faz a requisição à API com timeout
        response_get = requests.get("https://dados.mobilidade.rio/gps/sppo?dataInicial=2025-04-22+20:13:00&dataFinal=2025-04-22+20:13:00", timeout=45)
        # Levanta uma exceção para respostas HTTP ruins (4xx ou 5xx)
        response_get.raise_for_status()

        # Tenta decodificar a resposta JSON
        try:
            data = response_get.json()
            print("DATA: ", data)
        except json.JSONDecodeError as e:
            print(f"Task get_bus: ERRO ao decodificar JSON da API. Status Code: {response_get.status_code}, Resposta: {response_get.text[:200]}... Erro: {e}")
            return None # Falha ao decodificar, não há o que salvar

        # Verifica se a resposta é uma lista (como esperado agora)
        if not isinstance(data, list):
            print(f"Task get_bus: ERRO - API retornou um tipo inesperado: {type(data)}. Conteúdo: {str(data)[:200]}...")
            # Decide o que fazer: aqui, vamos tratar como se não houvesse dados
            data_to_store = []
            record_count = 0
        else:
            # A resposta é uma lista (pode ser vazia)
            data_to_store = data
            record_count = len(data_to_store)

        # Verifica se o cliente Redis está disponível antes de usar
        if not redis_client:
                print("Task get_bus: ERRO - Cliente Redis não conectado. Não foi possível salvar.")
                # Retorna None ou talvez a contagem, mas sem salvar? Decidi retornar None.
                return None

        # Tenta salvar a lista de dados (como string JSON) no Redis
        try:
            redis_client.set('latest_bus_data', json.dumps(data_to_store), ex=300) # Expira em 5 minutos
            print(f"Task get_bus: Dados de ônibus armazenados no Redis. {record_count} registros.")
            return record_count # Retorna o número de registros processados/salvos
        except redis.exceptions.RedisError as e:
            print(f"Task get_bus: ERRO ao salvar no Redis: {e}")
            return None # Falha ao salvar

    # Tratamento de exceções específicas da requisição
    except requests.exceptions.Timeout:
        print(f"Task get_bus: ERRO - Timeout ao acessar API {API_URL}")
        return None
    except requests.exceptions.RequestException as e:
        # Captura outros erros de requisição (conexão, HTTPError de raise_for_status, etc.)
        print(f"Task get_bus: ERRO na requisição à API: {e}")
        return None
    # Captura qualquer outro erro inesperado durante a execução da tarefa
    except Exception as e:
        print(f"Task get_bus: ERRO inesperado na tarefa: {e}")
        # Considerar usar logger.exception(e) para obter o traceback completo nos logs
        return None