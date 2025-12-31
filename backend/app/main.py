"""
FastAPI application principal.
"""
from fastapi import FastAPI, HTTPException, Depends
from fastapi.middleware.cors import CORSMiddleware
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request
from loguru import logger
import time
from app.config import get_settings
from app.middleware.request_id import RequestIDMiddleware, get_request_id
from app.middleware.rate_limiter import setup_rate_limiting
from slowapi.errors import RateLimitExceeded

settings = get_settings()


# Configurar logging
logger.remove()  # Remover handler padrão

# Sink customizado para logging em arquivo com rotation
from pathlib import Path
import os

# Criar diretório de logs se não existir
log_dir = Path("logs")
log_dir.mkdir(exist_ok=True)
log_file = log_dir / "app.log"

def log_sink(message):
    """Sink customizado que processa logs diretamente."""
    record = message.record
    
    # Obter request_id do contexto
    request_id = get_request_id()
    request_id_str = f"[{request_id}]" if request_id else "[--------]"
    
    # Formatar timestamp
    time_str = record["time"].strftime("%Y-%m-%d %H:%M:%S")
    
    # Formatar nível
    level_str = record["level"].name.ljust(8)
    
    # Mensagem (já formatada pelo Loguru, não precisa processar novamente)
    log_message = str(message)
    
    # Exception (se houver)
    exception_str = ""
    if record["exception"]:
        exception_str = f"\n{record['exception']}"
    
    # Formatar linha final
    formatted = f"{time_str} | {level_str} | {request_id_str: <10} | {log_message}{exception_str}\n"
    
    # Escrever no arquivo (append mode)
    try:
        with open(log_file, "a", encoding="utf-8") as f:
            f.write(formatted)
    except Exception:
        # Fallback para stderr se não conseguir escrever no arquivo
        import sys
        sys.stderr.write(formatted)

# Adicionar sink customizado (sem formato para evitar processamento duplo)
logger.add(
    log_sink,
    level=settings.log_level,
    format="{message}",  # Formato simples, processamos tudo no sink
)

app = FastAPI(
    title=settings.app_name,
    version="1.0.0",
    debug=False,  # Sempre False para não usar handler padrão do Starlette que expõe tracebacks
)

# Request ID Middleware (deve ser o primeiro para garantir request_id disponível nos logs)
app.add_middleware(RequestIDMiddleware)

# Exception Handling Middleware (captura exceções de todos os middlewares seguintes)
class ExceptionHandlingMiddleware(BaseHTTPMiddleware):
    """Middleware para capturar todas as exceções e retornar mensagens genéricas."""
    
    async def dispatch(self, request: Request, call_next):
        try:
            response = await call_next(request)
            return response
        except (HTTPException, RateLimitExceeded):
            # Re-raise HTTPException e RateLimitExceeded para que FastAPI trate corretamente (não capturar)
            raise
        except Exception as exc:
            import traceback
            logger.error(f"Erro capturado pelo middleware: {exc}")
            logger.error(traceback.format_exc())
            
            return JSONResponse(
                status_code=500,
                content={"detail": "Erro interno ao processar sua solicitação. Por favor, tente novamente."}
            )

# Adicionar exception handling middleware (último adicionado = primeiro na cadeia de execução)
app.add_middleware(ExceptionHandlingMiddleware)

# Rate Limiting (configurar antes dos routers)
app_limiter = setup_rate_limiting(app)

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Ajustar em produção
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# Exception Handlers Globais (DEVE SER ANTES DOS ROUTERS)
@app.exception_handler(RateLimitExceeded)
async def rate_limit_exceeded_handler(request, exc: RateLimitExceeded):
    """
    Handler para RateLimitExceeded - retorna status 429.
    """
    from slowapi import _rate_limit_exceeded_handler
    return await _rate_limit_exceeded_handler(request, exc)


@app.exception_handler(HTTPException)
async def http_exception_handler(request, exc: HTTPException):
    """
    Handler para HTTPException - permite que HTTPExceptions passem normalmente.
    """
    return JSONResponse(
        status_code=exc.status_code,
        content={"detail": exc.detail}
    )


@app.exception_handler(Exception)
async def global_exception_handler(request, exc):
    """
    Handler global para não expor tracebacks mesmo em modo debug.
    Garante que mensagens de erro sejam genéricas para o cliente.
    """
    import traceback
    logger.error(f"Erro não tratado: {exc}")
    logger.error(traceback.format_exc())
    
    return JSONResponse(
        status_code=500,
        content={"detail": "Erro interno ao processar sua solicitação. Por favor, tente novamente."}
    )


@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request, exc):
    """
    Handler para erros de validação do Pydantic.
    Retorna mensagem genérica sem expor detalhes dos campos inválidos.
    """
    logger.warning(f"Erro de validação: {exc}")
    return JSONResponse(
        status_code=422,
        content={"detail": "Erro de validação nos dados fornecidos."}
    )


@app.get("/")
async def root():
    """Endpoint raiz."""
    return {
        "message": "Treq Assistente Operacional API",
        "version": "1.0.0",
        "status": "ok",
    }


@app.get("/health")
async def health_check():
    """Health check endpoint."""
    return {"status": "ok", "service": "treq-assistente-backend"}


# Incluir rotas
from app.api.routes import chat, audio, documents, health
app.include_router(chat.router)
app.include_router(audio.router)
app.include_router(documents.router)
app.include_router(health.router)

# Endpoint de teste para rate limiting (para diagnóstico)
@app.get("/test-rate-limit")
@setup_rate_limiting(app).limit("5/minute")
async def test_rate_limit(request: Request):
    """
    Endpoint de teste para verificar se rate limiting está funcionando.
    Limite: 5 requisições por minuto.
    """
    return {"message": "Rate limit test - OK", "timestamp": time.time()}
