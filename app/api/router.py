from fastapi import APIRouter
from app.api import document_routes, risk_routes, health_routes

api_router = APIRouter()

api_router.include_router(health_routes.router, prefix="/health", tags=["health"])
api_router.include_router(document_routes.router, prefix="/document", tags=["document"])
api_router.include_router(risk_routes.router, prefix="/risk", tags=["risk"])

