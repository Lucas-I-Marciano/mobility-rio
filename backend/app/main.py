from dotenv import load_dotenv
load_dotenv()

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api.routes import bus, alerts, notifications, default, users
from app.db import create_all_table_and_db
from app.db.user_alerts import UserAlert
from app.schemas.endpoint_tags import EndpointTags

# --- METADATA ---

description = """
## API Alerta Bus Rio 🚌💨

Esta API permite monitorar ônibus da cidade do Rio de Janeiro em tempo real e criar alertas de proximidade personalizados.

**Funcionalidades Principais:**
* **Criação de Alertas:** Usuários podem cadastrar interesse em uma linha de ônibus específica, um ponto de parada e uma janela de horário diária.
* **Monitoramento:** O sistema verifica periodicamente a posição dos ônibus.
* **Notificação:** Envia um e-mail quando um ônibus da linha cadastrada está a ~10 minutos (via transporte público) de chegar ao ponto do usuário, dentro da janela de horário definida (verificação diária após data de início do alerta).
* **Status em Tempo Real:** Fornece a localização atualizada e o tempo estimado de chegada (ETA) para ônibus de uma linha específica em relação a um ponto de destino.

**Fontes de Dados:**
* Posicionamento dos Ônibus: API [Dados Abertos de Mobilidade Urbana do Rio de Janeiro](https://dados.mobilidade.rio/).
* Cálculo de ETA: Utiliza a API [Travel Time](https://traveltime.com/) (requer credenciais próprias configuradas no backend).

**Observação:** Este é um projeto desenvolvido como parte do processo seletivo da Maravi.
"""

tags_metadata = [
    {
        "name": "Welcome",
        "description" : "Endpoint de boas vindas"
    },
    {
        "name": "Alerts",
        "description": "Endpoints para criar e gerenciar alertas de proximidade de ônibus para usuários.",
    },
    {
        "name": "Bus Status",
        "description": "Endpoints para obter informações em tempo real sobre ônibus, incluindo localização, velocidade e tempo estimado de chegada (ETA) a um ponto específico.",
        "externalDocs": {
            "description": "API de Origem (Posição)",
            "url": "https://dados.mobilidade.rio/",
        },
    },
    {
        "name": "ETA Calculation",
        "description": "Endpoints diretos para cálculo de tempo estimado de viagem (usando Travel Time API).",
         "externalDocs": {
            "description": "API Externa Usada",
            "url": "https://traveltime.com/docs",
        },
    },
    {
        "name": "Notifications",
        "description": "Endpoints relacionados ao envio de notificações (ex: confirmação de alerta).",
    },
     {
        "name": "Testing",
        "description": "Endpoints auxiliares usados para testes durante o desenvolvimento.",
    },
    {
        "name": "Users",
        "description": "Endpoints para criar e gerenciar usuários da aplicação.",
    }
]

app = FastAPI(
    title="API Alerta Bus Rio",
    description=description,
    version="0.1.0",
    contact={
        "name": "Lucas Ioran Marciano", 
        "url": "https://github.com/Lucas-I-Marciano", 
        "email": "lucas.marciano99@outlook.com", 
    },
    license_info={
        "name": "MIT License",
        "url": "https://opensource.org/licenses/MIT",
    },
    openapi_tags=tags_metadata
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=['*'],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(default.router)
app.include_router(bus.router)
app.include_router(alerts.router)
app.include_router(notifications.router)
app.include_router(users.router)

@app.on_event("startup")
async def creating_on_startup():
    create_all_table_and_db()

