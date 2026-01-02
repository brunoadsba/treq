from fastapi import APIRouter
import psutil
import time
import os
from datetime import datetime

router = APIRouter(prefix="/monitoring", tags=["monitoring"])

START_TIME = time.time()

@router.get("/metrics")
async def get_metrics():
    """Retorna métricas básicas do sistema e aplicação."""
    process = psutil.Process(os.getpid())
    # Primeira chamada cpu_percent pode retornar 0.0, mas ok.
    cpu = process.cpu_percent()
    memory_info = process.memory_info()
    
    return {
        "status": "healthy",
        "uptime_seconds": round(time.time() - START_TIME, 2),
        "timestamp": datetime.now().isoformat(),
        "system": {
            "cpu_percent": cpu,
            "memory_usage_mb": round(memory_info.rss / 1024 / 1024, 2),
            "threads": process.num_threads()
        }
    }

@router.get("/health")
async def health_check():
    """Health check endpoint dedicado."""
    return {"status": "ok", "service": "treq-monitoring"}
