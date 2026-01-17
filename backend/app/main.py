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

# Adicionar handler para stderr (Console) - Resolvendo Segfault no WSL2
import sys
logger.add(
    sys.stderr,
    level=settings.log_level,
    format="<green>{time:YYYY-MM-DD HH:mm:ss}</green> | <level>{level: <8}</level> | <level>{message}</level>",
    enqueue=False
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
# Se permitir credenciais, Origins não pode conter "*" em muitos navegadores (CORS Policy)
raw_origins = settings.cors_origins.split(",") if settings.cors_origins else []
allowed_origins = [o.strip() for o in raw_origins if o.strip()]

# Lista explícita de origens confiáveis para produção + local
trusted_origins = [
    "https://treq-bay.vercel.app",
    "http://localhost:3000",
    "http://127.0.0.1:3000"
]

for origin in trusted_origins:
    if origin not in allowed_origins:
        allowed_origins.append(origin)

# Se ainda assim o usuário colocou "*" no ENV, o CORSMiddleware do FastAPI 
# vai reclamar se allow_credentials=True. Vamos garantir que funcione.
if "*" in allowed_origins and True: # settings.allow_credentials
    # Se houver wildcard, removemos o wildcard e mantemos apenas as origens explícitas
    # ou deixamos o FastAPI tratar (ele vai dar erro se não filtrarmos).
    allowed_origins = [o for o in allowed_origins if o != "*"]

app.add_middleware(
    CORSMiddleware,
    allow_origins=allowed_origins if allowed_origins else ["*"],
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

@app.get("/routes")
async def list_routes():
    return [{"path": route.path, "name": route.name} for route in app.routes]

# INCLUIR ROTAS (Agora são leves devido ao lazy loading nos routes)
logger.info("📦 Iniciando registro individual de rotas...")

# CHAT
try:
    from app.api.routes import chat
    app.include_router(chat.router)
    logger.info("✅ Router chat incluído")
except Exception as e:
    logger.error(f"❌ Falha ao incluir router CHAT: {e}")

# HEALTH (Serviços LLM)
try:
    from app.api.routes import health as health_route
    app.include_router(health_route.router)
    logger.info("✅ Router health incluído")
except Exception as e:
    logger.error(f"❌ Falha ao incluir router HEALTH: {e}")

# MONITORING
try:
    from app.api.routes import monitoring
    app.include_router(monitoring.router)
    logger.info("✅ Router monitoring incluído")
except Exception as e:
    logger.error(f"❌ Falha ao incluir router MONITORING: {e}")

# FEEDBACK
try:
    from app.api.routes import feedback
    app.include_router(feedback.router)
    logger.info("✅ Router feedback incluído")
except Exception as e:
    logger.error(f"❌ Falha ao incluir router FEEDBACK: {e}")

# AUDIO
try:
    from app.api.routes import audio
    app.include_router(audio.router)
    logger.info("✅ Router audio incluído")
except Exception as e:
    logger.error(f"❌ Falha ao incluir router AUDIO: {e}")

# DOCUMENTS
try:
    from app.api.routes import documents
    app.include_router(documents.router)
    logger.info("✅ Router documents incluído")
except Exception as e:
    logger.error(f"❌ Falha ao incluir router DOCUMENTS: {e}")

# VISION (Feature Modular)
try:
    from src.features.vision.routes import router as vision_router
    app.include_router(vision_router)
    logger.info("✅ Router vision incluído")
except Exception as vision_err:
    logger.warning(f"⚠️ Router vision opcional não incluído: {vision_err}")

# AGENT (Enterprise - LangGraph)
try:
    from app.features.agent.routes import router as agent_router
    app.include_router(agent_router)
    logger.info("✅ Router agent (Enterprise) incluído")
except Exception as agent_err:
    logger.warning(f"⚠️ Router agent opcional não incluído: {agent_err}")

# CONNECTORS (Enterprise - Confluence, Slack)
try:
    from app.features.connectors.routes import router as connectors_router
    app.include_router(connectors_router)
    logger.info("✅ Router connectors incluído")
except Exception as conn_err:
    logger.warning(f"⚠️ Router connectors opcional não incluído: {conn_err}")

logger.info("🚀 Processo de registro de rotas concluído")

# Startup Final
@app.on_event("startup")
async def startup_event():
    logger.info("🚀 Servidor Pronto! (Modo Cloud)")
    logger.info("✨ TREQ BACKEND VIVO E OPERACIONAL")

# 279 lines originally
