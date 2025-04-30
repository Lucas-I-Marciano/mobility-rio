from fastapi import APIRouter

from app.schemas.endpoint_tags import EndpointTags


router = APIRouter(tags=[EndpointTags.DEFAULT])

@router.get("/")
async def root():
    return {"message" : "Welcome!"}