from fastapi import APIRouter
import psutil
import time
import os
from datetime import datetime
from typing import Dict, Any
from loguru import logger

router = APIRouter(prefix="/monitoring", tags=["monitoring"])

START_TIME = time.time()

# Métricas globais em memória (para produção, usar Redis)
chat_metrics = {
    "total_requests": 0,
    "successful_requests": 0,
    "failed_requests": 0,
    "avg_response_time_ms": 0,
    "rag_queries": 0,
    "rag_no_results": 0,
    "llm_calls": 0,
    "llm_tokens_used": 0,
}

rag_metrics = {
    "total_searches": 0,
    "avg_similarity_score": 0.0,
    "avg_search_time_ms": 0,
    "cache_hits": 0,
    "cache_misses": 0,
}

llm_metrics = {
    "total_calls": 0,
    "total_tokens": 0,
    "avg_latency_ms": 0,
    "model_8b_calls": 0,
    "model_70b_calls": 0,
    "model_glm4_calls": 0,
}


@router.get("/metrics")
async def get_metrics() -> Dict[str, Any]:
    """
    Retorna métricas completas do sistema.

    Inclui:
    - System metrics (CPU, memory, uptime)
    - Chat metrics (requests, errors, response time)
    - RAG metrics (searches, similarity, cache)
    - LLM metrics (calls, tokens, latency)
    """
    process = psutil.Process(os.getpid())
    cpu = process.cpu_percent()
    memory_info = process.memory_info()

    return {
        "timestamp": datetime.now().isoformat(),
        "uptime_seconds": round(time.time() - START_TIME, 2),

        "system": {
            "cpu_percent": cpu,
            "memory_usage_mb": round(memory_info.rss / 1024 / 1024, 2),
            "memory_available_mb": round(psutil.virtual_memory().available / 1024 / 1024, 2),
            "threads": process.num_threads(),
            "status": "healthy"
        },

        "chat": chat_metrics.copy(),

        "rag": rag_metrics.copy(),

        "llm": llm_metrics.copy(),

        "performance": {
            "error_rate": round(
                (chat_metrics["failed_requests"] / chat_metrics["total_requests"] * 100)
                if chat_metrics["total_requests"] > 0 else 0,
                2
            ),
            "avg_response_time_ms": chat_metrics["avg_response_time_ms"],
            "rag_success_rate": round(
                ((chat_metrics["rag_queries"] - chat_metrics["rag_no_results"]) / chat_metrics["rag_queries"] * 100)
                if chat_metrics["rag_queries"] > 0 else 0,
                2
            ),
        }
    }


@router.get("/health")
async def health_check():
    """Health check endpoint dedicado."""
    return {
        "status": "ok",
        "service": "treq-monitoring",
        "timestamp": datetime.now().isoformat()
    }


@router.post("/chat/metrics")
async def record_chat_metrics(
    success: bool,
    response_time_ms: float,
    rag_used: bool = False,
    rag_found: bool = False,
    llm_tokens: int = 0
):
    """
    Registra métricas de uma requisição de chat.

    Args:
        success: Se a requisição foi bem-sucedida
        response_time_ms: Tempo de resposta em ms
        rag_used: Se RAG foi utilizado
        rag_found: Se RAG encontrou documentos
        llm_tokens: Tokens consumidos pelo LLM
    """
    chat_metrics["total_requests"] += 1

    if success:
        chat_metrics["successful_requests"] += 1
    else:
        chat_metrics["failed_requests"] += 1

    # Atualizar média de tempo de resposta (média móvel simples)
    n = chat_metrics["total_requests"]
    current_avg = chat_metrics["avg_response_time_ms"]
    chat_metrics["avg_response_time_ms"] = round(
        ((current_avg * (n - 1)) + response_time_ms) / n,
        2
    )

    # Métricas RAG
    if rag_used:
        chat_metrics["rag_queries"] += 1
        if not rag_found:
            chat_metrics["rag_no_results"] += 1

    # Métricas LLM
    if llm_tokens > 0:
        chat_metrics["llm_calls"] += 1
        chat_metrics["llm_tokens_used"] += llm_tokens

    logger.debug(f"Métricas registradas: success={success}, time={response_time_ms}ms")

    return {"status": "recorded"}


@router.post("/rag/metrics")
async def record_rag_metrics(
    search_time_ms: float,
    similarity_score: float,
    cache_hit: bool = False,
    num_results: int = 0
):
    """
    Registra métricas de uma busca RAG.

    Args:
        search_time_ms: Tempo de busca em ms
        similarity_score: Similaridade média dos resultados
        cache_hit: Se foi cache hit
        num_results: Número de documentos encontrados
    """
    rag_metrics["total_searches"] += 1

    # Atualizar média de similaridade
    n = rag_metrics["total_searches"]
    current_avg = rag_metrics["avg_similarity_score"]
    rag_metrics["avg_similarity_score"] = round(
        ((current_avg * (n - 1)) + similarity_score) / n,
        3
    )

    # Atualizar média de tempo de busca
    current_time_avg = rag_metrics["avg_search_time_ms"]
    rag_metrics["avg_search_time_ms"] = round(
        ((current_time_avg * (n - 1)) + search_time_ms) / n,
        2
    )

    # Cache
    if cache_hit:
        rag_metrics["cache_hits"] += 1
    else:
        rag_metrics["cache_misses"] += 1

    logger.debug(f"Métricas RAG registradas: time={search_time_ms}ms, similarity={similarity_score:.3f}")

    return {"status": "recorded"}


@router.post("/llm/metrics")
async def record_llm_metrics(
    model: str,
    tokens: int,
    latency_ms: float
):
    """
    Registra métricas de uma chamada LLM.

    Args:
        model: Nome do modelo usado (llama-8b, llama-70b, glm-4)
        tokens: Tokens consumidos
        latency_ms: Latência em ms
    """
    llm_metrics["total_calls"] += 1
    llm_metrics["total_tokens"] += tokens

    # Atualizar média de latência
    n = llm_metrics["total_calls"]
    current_avg = llm_metrics["avg_latency_ms"]
    llm_metrics["avg_latency_ms"] = round(
        ((current_avg * (n - 1)) + latency_ms) / n,
        2
    )

    # Contagem por modelo
    if "8b" in model.lower() or "instant" in model.lower():
        llm_metrics["model_8b_calls"] += 1
    elif "70b" in model.lower():
        llm_metrics["model_70b_calls"] += 1
    elif "glm" in model.lower():
        llm_metrics["model_glm4_calls"] += 1

    logger.debug(f"Métricas LLM registradas: model={model}, tokens={tokens}, latency={latency_ms}ms")

    return {"status": "recorded"}


@router.get("/stats/summary")
async def get_stats_summary():
    """
    Retorna um resumo executivo das métricas.

    Formato otimizado para dashboards.
    """
    uptime_hours = round((time.time() - START_TIME) / 3600, 2)

    return {
        "uptime_hours": uptime_hours,
        "total_requests": chat_metrics["total_requests"],
        "success_rate_percent": round(
            (chat_metrics["successful_requests"] / chat_metrics["total_requests"] * 100)
            if chat_metrics["total_requests"] > 0 else 0,
            1
        ),
        "avg_response_time_ms": chat_metrics["avg_response_time_ms"],
        "rag_avg_similarity": rag_metrics["avg_similarity_score"],
        "llm_total_tokens": llm_metrics["total_tokens"],
        "llm_avg_latency_ms": llm_metrics["avg_latency_ms"],
        "system_status": "healthy",
        "timestamp": datetime.now().isoformat()
    }
