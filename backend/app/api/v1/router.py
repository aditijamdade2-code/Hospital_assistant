from fastapi import APIRouter
from backend.app.api.v1.encounters import router as encounters_router
from backend.app.api.v1.protocols import router as protocols_router
from backend.app.api.v1.websocket import router as ws_router
from backend.app.api.v1.voice import router as voice_router

api_v1_router = APIRouter(prefix="/api/v1")
api_v1_router.include_router(encounters_router)
api_v1_router.include_router(protocols_router)
api_v1_router.include_router(ws_router)
api_v1_router.include_router(voice_router)
