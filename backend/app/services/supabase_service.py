"""
Serviço para interagir com Supabase.
Cliente singleton para conexão com banco de dados.
"""
from supabase import create_client, Client
from loguru import logger
from app.config import get_settings

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
            settings.supabase_url,
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
        settings.supabase_url,
        settings.supabase_anon_key
    )

