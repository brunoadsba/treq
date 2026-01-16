"""
Autenticação simples por API Key.
Middleware para proteção de endpoints sensíveis.

Não substitui autenticação JWT completa, mas provê proteção mínima
para ambientes de demonstração e MVP.
"""
import os
from fastapi import Header, HTTPException
from loguru import logger

# Chave configurada via variável de ambiente
API_KEY = os.getenv("TREQ_API_KEY", "")


async def verify_api_key(x_api_key: str = Header(None, alias="X-API-Key")) -> str:
    """
    Valida a chave API no header X-API-Key.
    
    Comportamento:
    - Em desenvolvimento (API_KEY vazia): permite acesso livre com warning
    - Em produção (API_KEY configurada): requer chave válida
    
    Args:
        x_api_key: Valor do header X-API-Key
        
    Returns:
        str: A chave validada ou "dev-mode"
        
    Raises:
        HTTPException 401: Se chave ausente ou inválida (em produção)
    """
    # Se não configurada, permitir acesso (modo dev)
    if not API_KEY:
        logger.warning("⚠️ TREQ_API_KEY não configurada - autenticação desabilitada")
        return "dev-mode"
    
    if not x_api_key:
        raise HTTPException(
            status_code=401,
            detail="API Key não fornecida. Inclua header X-API-Key."
        )
    
    if x_api_key != API_KEY:
        logger.warning("Tentativa de acesso com API Key inválida")
        raise HTTPException(
            status_code=401,
            detail="API Key inválida."
        )
    
    return x_api_key


# Dependency para uso opcional (rotas públicas podem não usar)
def get_optional_api_key(x_api_key: str = Header(None, alias="X-API-Key")) -> str | None:
    """
    Versão opcional do validador - não bloqueia se chave ausente.
    Útil para rotas semi-públicas onde autenticação é preferida mas não obrigatória.
    """
    if not API_KEY:
        return None
    return x_api_key if x_api_key == API_KEY else None
