from fastapi import FastAPI

from app.api.routes import bus

app = FastAPI()

app.include_router(bus.router)

@app.get("/")
async def root():
    return {"message" : "Welcome!"}

