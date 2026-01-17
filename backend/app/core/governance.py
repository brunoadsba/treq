"""
Módulo de Governança e Observabilidade (LangSmith).

Centraliza configurações de tracing, tags e metadados.
"""

import os
from typing import Dict, Any, Optional
from langchain_core.tracers.context import collect_runs
from langsmith import Client
from loguru import logger


# Cliente LangSmith Singleton
_client: Optional[Client] = None


def get_langsmith_client() -> Client:
    """Retorna cliente LangSmith configurado."""
    global _client
    if _client is None:
        api_key = os.getenv("LANGCHAIN_API_KEY")
        if not api_key:
            logger.warning("LANGCHAIN_API_KEY não encontrada. Tracing pode falhar.")
        
        _client = Client()
    return _client


def get_trace_config(user_id: str, thread_id: str = None) -> Dict[str, Any]:
    """
    Gera configuração de tracing para uma execução.
    
    Args:
        user_id: ID do usuário (para filtro/rate limit)
        thread_id: ID da conversa/thread
        
    Returns:
        Dict com tags e metadata para o config do invoke/ainvoke
    """
    project_name = os.getenv("LANGCHAIN_PROJECT", "treq-default")
    
    metadata = {
        "user_id": user_id,
        "environment": os.getenv("ENVIRONMENT", "development"),
        "project": project_name
    }
    
    if thread_id:
        metadata["thread_id"] = thread_id
        
    config = {
        "metadata": metadata,
        "tags": ["agent", "enterprise", f"user:{user_id}"],
        "project_name": project_name
    }
    
    if thread_id:
        config["configurable"] = {"thread_id": thread_id}
        
    return config
