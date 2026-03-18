from fastapi import APIRouter
from app.core.models import HealthCheckResponse

router = APIRouter()

@router.get("/livez", response_model=HealthCheckResponse)
async def livez():
    return {"status": "ok", "message": "Service is live"}

@router.get("/readyz", response_model=HealthCheckResponse)
async def readyz():
    return {"status": "ok", "message": "Service is ready"}

