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

# Adicionar handler para stdout (Console) - ESSENCIAL PARA RENDER/VERCEL
import sys
logger.add(
    sys.stdout,
    level=settings.log_level,
    format="<green>{time:YYYY-MM-DD HH:mm:ss}</green> | <level>{level: <8}</level> | <level>{message}</level>",
    enqueue=True
)

# Sink customizado para logging em arquivo com rotation
from pathlib import Path
import os

# Criar diretório de logs se não existir
log_dir = Path("logs")
log_dir.mkdir(exist_ok=True)
log_file = log_dir / "app.log"

def log_sink(message):
    """Sink customizado que processa logs diretamente para arquivo."""
    record = message.record
    request_id = get_request_id()
    request_id_str = f"[{request_id}]" if request_id else "[--------]"
    time_str = record["time"].strftime("%Y-%m-%d %H:%M:%S")
    level_str = record["level"].name.ljust(8)
    log_message = str(message)
    
    exception_str = ""
    if record["exception"]:
        exception_str = f"\n{record['exception']}"
    
    formatted = f"{time_str} | {level_str} | {request_id_str: <10} | {log_message}{exception_str}\n"
    
    try:
        with open(log_file, "a", encoding="utf-8") as f:
            f.write(formatted)
    except Exception:
        pass

# Adicionar sink de arquivo
logger.add(
    log_sink,
    level=settings.log_level,
    format="{message}",
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
origins = [o.strip() for o in settings.cors_origins.split(",")] if settings.cors_origins else ["*"]
app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# Startup Event - Pré-carregar modelo de embedding
@app.on_event("startup")
async def startup_event():
    """
    Startup event simplificado para deploy rápido.
    Os modelos serão carregados sob demanda (lazy loading).
    """
    logger.info("🚀 Servidor pronto para receber requisições (Modo Cloud)")


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


# Saúde do servidor
@app.get("/health")
async def health_check():
    return {"status": "ok", "service": "treq-backend", "up": True}

@app.get("/")
async def root():
    return {"status": "online", "message": "TREQ API"}

# INCLUIR ROTAS (Agora são leves devido ao lazy loading nos routes)
try:
    logger.info("📦 Iniciando importação de rotas...")
    from app.api.routes import chat, health as health_route, monitoring, feedback, audio, documents
    logger.info("✅ Imports de app.api.routes concluídos")
    
    try:
        from src.features.vision.routes import router as vision_router
        logger.info("✅ Import de vision_router concluído")
    except Exception as vision_err:
        logger.warning(f"⚠️ Erro ao importar vision_router: {vision_err}")
        vision_router = None

    app.include_router(chat.router)
    logger.info("✅ Router chat incluído")
    app.include_router(health_route.router)
    logger.info("✅ Router health incluído")
    app.include_router(monitoring.router)
    logger.info("✅ Router monitoring incluído")
    app.include_router(feedback.router)
    logger.info("✅ Router feedback incluído")
    app.include_router(audio.router)
    logger.info("✅ Router audio incluído")
    app.include_router(documents.router)
    logger.info("✅ Router documents incluído")
    
    if vision_router:
        app.include_router(vision_router)
        logger.info("✅ Router vision incluído")
        
    logger.info("🚀 Todas as rotas registradas com sucesso")
except Exception as e:
    logger.error(f"❌ Erro crítico ao registrar rotas: {e}")
    import traceback
    logger.error(traceback.format_exc())

# Startup Final
@app.on_event("startup")
async def startup_event():
    logger.info("🚀 Servidor Pronto! (Modo Cloud)")
    logger.info("✨ TREQ BACKEND VIVO E OPERACIONAL")
