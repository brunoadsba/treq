"""
Middleware de Rate Limiting para proteção contra abuso de API.
Usa slowapi para limitar requisições por endpoint.
"""
from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.middleware import SlowAPIMiddleware
from slowapi.util import get_remote_address
from slowapi.errors import RateLimitExceeded
from fastapi import Request
from loguru import logger
from app.config import get_settings

settings = get_settings()

# Criar instância do limiter
limiter = Limiter(
    key_func=get_remote_address,
    default_limits=[f"{settings.rate_limit_per_minute}/minute"],
    storage_uri="memory://",  # Em memória para desenvolvimento (produção: usar Redis)
    strategy="fixed-window"  # Janela fixa de 1 minuto
)

# Configurações de rate limit por tipo de endpoint
RATE_LIMITS = {
    "chat": "30/minute",  # Endpoint de chat (considerando streaming e custo de LLM)
    "audio": "60/minute",  # STT/TTS
    "documents": "10/minute",  # Upload de documentos (mais restritivo)
    "default": f"{settings.rate_limit_per_minute}/minute"  # Limite padrão
}


def get_rate_limit(endpoint_type: str = "default") -> str:
    """
    Retorna o rate limit configurado para um tipo de endpoint.
    
    Args:
        endpoint_type: Tipo do endpoint (chat, audio, documents, default)
    
    Returns:
        String de rate limit no formato "X/minute"
    """
    return RATE_LIMITS.get(endpoint_type, RATE_LIMITS["default"])


def setup_rate_limiting(app):
    """
    Configura rate limiting na aplicação FastAPI.
    
    Args:
        app: Instância do FastAPI
    
    Returns:
        Instância do limiter
    
    Nota: O handler de RateLimitExceeded deve ser registrado no main.py
    para garantir ordem correta dos handlers.
    """
    app.state.limiter = limiter
    
    # Adicionar SlowAPIMiddleware - necessário para que o decorator funcione corretamente
    app.add_middleware(SlowAPIMiddleware)
    
    # Handler será registrado no main.py para garantir ordem correta
    logger.info("✅ Rate limiting configurado (com SlowAPIMiddleware)")
    return limiter


def get_client_ip(request: Request) -> str:
    """
    Obtém o IP do cliente da requisição.
    Útil para rate limiting baseado em IP.
    
    Args:
        request: Requisição FastAPI
    
    Returns:
        String com o IP do cliente
    """
    return get_remote_address(request)


def rate_limit(limit_value: str):
    """
    Cria uma dependência de FastAPI para rate limiting usando slowapi.
    
    Esta função retorna uma dependência que verifica o rate limit antes
    de executar o endpoint. Se o limite for excedido, lança RateLimitExceeded.
    
    Args:
        limit_value: String de rate limit (ex: "30/minute")
    
    Returns:
        Função dependency que pode ser usada com Depends()
    
    Exemplo de uso:
        @router.post("/endpoint")
        async def my_endpoint(
            request: Request,
            _: None = Depends(rate_limit("30/minute")),
            ...
        ):
            ...
    """
    async def limit_dependency(request: Request):
        """
        Dependency que verifica rate limit antes de executar o endpoint.
        
        Usa o limiter do app.state para verificar limites e lança
        RateLimitExceeded se o limite for excedido.
        """
        # Obter limiter do app.state (garantido pela configuração)
        if not hasattr(request.app.state, 'limiter'):
            logger.warning("app.state.limiter não encontrado - rate limiting desabilitado")
            return
        
        app_limiter = request.app.state.limiter
        
        # Obter endpoint name para identificar a rota
        endpoint_name = f"{request.url.path}:{request.method.lower()}"
        
        # Obter chave de identificação (IP ou outro identificador)
        key = get_remote_address(request)
        
        # Criar LimitGroup como o decorator faz internamente
        from slowapi.wrappers import LimitGroup
        
        limit_group = LimitGroup(
            limit_value,
            get_remote_address,
            None,  # scope
            False,  # per_method
            None,  # methods
            None,  # error_message
            None,  # exempt_when
            1,  # cost
            True  # override_defaults
        )
        
        # Obter limites do grupo
        limit_group.request = request
        limits = list(limit_group)
        
        # Avaliar limites usando o método interno do limiter
        app_limiter._Limiter__evaluate_limits(request, endpoint_name, limits)
        
        # Se chegou aqui, rate limit não foi excedido
    
    return limit_dependency
