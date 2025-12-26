"""
FastAPI application principal.
"""
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from loguru import logger
from app.config import get_settings

settings = get_settings()

# Configurar logging
logger.add(
    "logs/app.log",
    rotation="500 MB",
    retention="10 days",
    level=settings.log_level,
    format="{time:YYYY-MM-DD HH:mm:ss} | {level} | {message}",
)

app = FastAPI(
    title=settings.app_name,
    version="1.0.0",
    debug=settings.debug,
)

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Ajustar em produção
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/")
async def root():
    """Endpoint raiz."""
    return {
        "message": "Treq Assistente Operacional API",
        "version": "1.0.0",
        "status": "ok",
    }


@app.get("/health")
async def health_check():
    """Health check endpoint."""
    return {"status": "ok", "service": "treq-assistente-backend"}

