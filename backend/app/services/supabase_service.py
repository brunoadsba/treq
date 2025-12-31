"""
Serviço para interagir com Supabase.
Cliente singleton para conexão com banco de dados.
Circuit breakers implementados para operações críticas.
"""
from supabase import create_client, Client
from loguru import logger
from app.config import get_settings
from app.core.circuit_breaker import (
    get_supabase_breaker,
    call_with_circuit_breaker,
    CircuitBreakerError
)

settings = get_settings()

# Instância singleton do cliente Supabase
_supabase_client: Client | None = None


def get_supabase_client() -> Client:
    """
    Retorna instância singleton do cliente Supabase.
    
    Returns:
        Client: Cliente Supabase configurado
    """
    global _supabase_client
    
    if _supabase_client is None:
        if not settings.supabase_url or not settings.supabase_key:
            raise ValueError(
                "Supabase credentials não configuradas. "
                "Configure SUPABASE_URL e SUPABASE_KEY no .env"
            )
        
        _supabase_client = create_client(
            str(settings.supabase_url),  # Converter HttpUrl para string
            settings.supabase_key  # Service role key para operações administrativas
        )
        logger.info("✅ Cliente Supabase inicializado")
    
    return _supabase_client


def get_supabase_anon_client() -> Client:
    """
    Retorna cliente Supabase com anon key (para operações do frontend).
    
    Returns:
        Client: Cliente Supabase com anon key
    """
    if not settings.supabase_url or not settings.supabase_anon_key:
        raise ValueError(
            "Supabase anon credentials não configuradas. "
            "Configure SUPABASE_URL e SUPABASE_ANON_KEY no .env"
        )
    
    return create_client(
        str(settings.supabase_url),  # Converter HttpUrl para string
        settings.supabase_anon_key
    )


def execute_supabase_query(query_func):
    """
    Executa query Supabase protegida por circuit breaker.
    
    Args:
        query_func: Função que retorna um objeto query do Supabase (com .execute())
        
    Returns:
        Resultado da query (.execute())
        
    Raises:
        CircuitBreakerError: Se circuit breaker estiver aberto
        Exception: Outros erros da query
    """
    breaker = get_supabase_breaker()
    
    def _execute():
        result = query_func().execute()
        return result
    
    try:
        return call_with_circuit_breaker(breaker, _execute)
    except CircuitBreakerError as e:
        logger.error(f"Circuit breaker Supabase aberto: {e}")
        raise
    except Exception as e:
        logger.error(f"Erro ao executar query Supabase: {e}")
        raise
