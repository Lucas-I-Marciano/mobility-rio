from fastapi import APIRouter

router = APIRouter(prefix="/bus")

@router.post("/")
def test():
    return {"message":"ok"}