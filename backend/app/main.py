from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api.routes import bus, map

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

@app.get("/")
async def root():
    return {"message" : "Welcome!"}

