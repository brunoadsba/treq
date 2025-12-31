"""
Middleware para geração e propagação de Request ID.
Facilita rastreamento de requisições através de logs.
"""
import uuid
from contextvars import ContextVar
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request
from starlette.responses import Response

# Context variable para armazenar request_id
request_id_var: ContextVar[str] = ContextVar("request_id", default="")


def get_request_id() -> str:
    """Retorna o request_id atual do contexto."""
    return request_id_var.get("")


class RequestIDMiddleware(BaseHTTPMiddleware):
    """
    Middleware que gera um request_id único para cada requisição HTTP.
    Propaga o request_id através de contextvars para uso em toda a aplicação.
    """
    
    async def dispatch(self, request: Request, call_next):
        # Gerar request_id único (8 caracteres do UUID)
        request_id = str(uuid.uuid4())[:8]
        
        # Armazenar no contexto
        request_id_var.set(request_id)
        
        # Adicionar ao request state para acesso em rotas
        request.state.request_id = request_id
        
        # Processar requisição
        response = await call_next(request)
        
        # Adicionar request_id no header de resposta
        response.headers["X-Request-ID"] = request_id
        
        return response
