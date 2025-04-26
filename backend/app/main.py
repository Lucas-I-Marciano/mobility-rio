from dotenv import load_dotenv
load_dotenv()

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api.routes import bus, map, alerts
from app.db import create_all_table_and_db
from app.db.user_alerts import UserAlert

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=['*'],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(bus.router)
app.include_router(map.router)
app.include_router(alerts.router)

@app.on_event("startup")
async def creating_on_startup():
    create_all_table_and_db()

@app.get("/")
async def root():
    return {"message" : "Welcome!"}

