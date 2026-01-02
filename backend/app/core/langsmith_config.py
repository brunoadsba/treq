"""
Configuração do LangSmith para observabilidade do sistema RAG.

Conforme Fase 4 do plano chat-inteligente.md:
"Tracing end-to-end com LangSmith para cada query."
"""
import os
from typing import Optional
from loguru import logger
from functools import lru_cache


# Configurações padrão
DEFAULT_PROJECT = "treq-assistente"


def is_langsmith_enabled() -> bool:
    """
    Verifica se o LangSmith está habilitado.
    
    Requer:
    - LANGCHAIN_TRACING_V2=true
    - LANGSMITH_API_KEY configurada
    """
    from app.config import get_settings
    settings = get_settings()
    
    tracing_enabled = settings.langchain_tracing_v2.lower() == "true"
    api_key = settings.langsmith_api_key
    
    enabled = tracing_enabled and bool(api_key)
    # Log temporário para debug
    logger.info(f"LangSmith status check: enabled={enabled}, tracing={tracing_enabled}, key_present={bool(api_key)}")
    
    return enabled


def get_langsmith_client():
    """
    Retorna o cliente LangSmith se disponível.
    
    Returns:
        Client LangSmith ou None se não configurado
    """
    if not is_langsmith_enabled():
        return None
    
    try:
        from langsmith import Client
        return Client()
    except ImportError:
        logger.warning("LangSmith não instalado. Execute: pip install langsmith")
        return None
    except Exception as e:
        logger.error(f"Erro ao inicializar LangSmith: {e}")
        return None


def setup_langsmith():
    """
    Configura o LangSmith para tracing.
    
    Deve ser chamado na inicialização da aplicação.
    """
    from app.config import get_settings
    settings = get_settings()
    
    if not is_langsmith_enabled():
        logger.info("LangSmith desabilitado (LANGCHAIN_TRACING_V2 != true ou LANGSMITH_API_KEY não configurada)")
        return False
    
    # Configurar projeto e variáveis necessárias para o tracer da langsmith
    os.environ["LANGCHAIN_TRACING_V2"] = settings.langchain_tracing_v2
    os.environ["LANGSMITH_API_KEY"] = settings.langsmith_api_key
    os.environ["LANGCHAIN_PROJECT"] = settings.langchain_project
    
    # Verificar conexão
    client = get_langsmith_client()
    if client:
        logger.info(f"✅ LangSmith configurado com sucesso | Projeto: {settings.langchain_project}")
        return True
    
    return False


def get_run_url(run_id: str) -> Optional[str]:
    """
    Retorna URL do dashboard para um run específico.
    
    Args:
        run_id: ID do run no LangSmith
        
    Returns:
        URL do run ou None
    """
    if not is_langsmith_enabled():
        return None
    
    project = os.getenv("LANGCHAIN_PROJECT", DEFAULT_PROJECT)
    return f"https://smith.langchain.com/o/default/projects/p/{project}/r/{run_id}"
