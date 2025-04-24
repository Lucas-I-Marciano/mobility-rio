from fastapi import FastAPI
from dotenv import load_dotenv
from .worker import add

load_dotenv()  # take environment variables

app = FastAPI()

@app.get("/")
async def root():
    add.delay(4,4)
    return {"message": "Hello World"}

