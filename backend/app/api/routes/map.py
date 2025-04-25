from fastapi import APIRouter

router = APIRouter(prefix="/map")

@router.post("/alert")
def create_alert():
    return {"message": "OK"}