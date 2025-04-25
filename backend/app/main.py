from fastapi import FastAPI

from app.api.routes import bus, map

app = FastAPI()

app.include_router(bus.router)
app.include_router(map.router)

@app.get("/")
async def root():
    return {"message" : "Welcome!"}

