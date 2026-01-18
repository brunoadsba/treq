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
from jose import jwt
import datetime

settings = get_settings()

# Instância singleton do cliente Supabase
_supabase_client: Client | None = None


def get_supabase_client() -> Client:
    """
    Retorna cliente com SERVICE_ROLE (Bypassa RLS).
    USAR APENAS PARA OPERAÇÕES ADMINISTRATIVAS.
    """
    global _supabase_client
    
    if _supabase_client is None:
        if not settings.supabase_url or not settings.supabase_key:
            raise ValueError("Supabase service credentials não configuradas.")
        
        _supabase_client = create_client(
            str(settings.supabase_url),
            settings.supabase_key
        )
        logger.warning("⚠️ Cliente Supabase SERVICE_ROLE inicializado (RLS BYPASS)")
    
    return _supabase_client

def generate_supabase_jwt(user_id: str) -> str:
    """
    Gera um JWT compatível com o Supabase para forçar o RLS no banco de dados.
    Usa o secret do Supabase para assinar o token.
    """
    payload = {
        "aud": "authenticated",
        "exp": datetime.datetime.utcnow() + datetime.timedelta(minutes=60),
        "sub": user_id,
        "role": "authenticated",
        "app_metadata": {"provider": "external"},
        "user_metadata": {}
    }
    return jwt.encode(payload, settings.supabase_key, algorithm="HS256")

def get_user_supabase_client(user_id: str) -> Client:
    """
    Retorna um cliente Supabase autenticado para o usuário específico.
    Este cliente RESPEITA o RLS do Supabase.
    """
    if not user_id or user_id == "anonymous":
        return get_supabase_anon_client()
        
    token = generate_supabase_jwt(user_id)
    
    return create_client(
        str(settings.supabase_url),
        settings.supabase_anon_key,
        options={"headers": {"Authorization": f"Bearer {token}"}}
    )


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
