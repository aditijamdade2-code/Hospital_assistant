import logging
from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from backend.app.core.config import settings
from backend.app.database.session import init_db
from backend.app.protocols.loader import protocol_loader
from backend.app.api.v1.router import api_v1_router

logging.basicConfig(
    level=getattr(logging, settings.LOG_LEVEL.upper(), logging.INFO),
    format="%(asctime)s [%(levelname)s] %(name)s - %(message)s"
)
logger = logging.getLogger("hospital_assistant")

@asynccontextmanager
async def lifespan(app: FastAPI):
    logger.info("Initializing Hospital OPD Assistant...")
    # Initialize database tables
    await init_db()
    # Load all clinical protocols
    protocol_loader.load_all()
    logger.info("System ready. Serving clinical protocols and encounter endpoints.")
    yield
    logger.info("Shutting down Hospital OPD Assistant.")

app = FastAPI(
    title="Hospital OPD Multilingual Voice Assistant - API",
    description="Assistive clinical intake, red-flag safety, and protocol triage system.",
    version="1.0.0",
    lifespan=lifespan
)

# CORS middleware for Next.js frontend communication
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins + ["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(api_v1_router)

@app.get("/")
async def root():
    return {
        "service": "Hospital OPD Multilingual Assistant",
        "version": "1.0.0",
        "status": "operational",
        "disclaimer": "DEMO / REQUIRES CLINICAL VALIDATION. Assistive workflow only. Not an autonomous clinical decision tool."
    }

@app.get("/health")
async def health_check():
    return {
        "status": "healthy",
        "environment": settings.ENVIRONMENT,
        "llm_provider": settings.LLM_PROVIDER,
        "protocols_loaded": len(protocol_loader.list_all())
    }
