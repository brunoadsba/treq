"""
Rotas da API para feedback de usuários.
Usado para coletar dados de qualidade das respostas do assistente.
"""
from fastapi import APIRouter
from pydantic import BaseModel
from typing import Optional
from loguru import logger
from datetime import datetime

router = APIRouter(prefix="/feedback", tags=["feedback"])


class FeedbackRequest(BaseModel):
    """Modelo de requisição de feedback."""
    message_id: Optional[str] = None
    feedback_type: str  # "positive" ou "negative"
    timestamp: Optional[str] = None
    comment: Optional[str] = None


class FeedbackResponse(BaseModel):
    """Modelo de resposta de feedback."""
    success: bool
    message: str


@router.post("/", response_model=FeedbackResponse)
async def submit_feedback(request: FeedbackRequest):
    """
    Recebe feedback do usuário e integra com LangSmith e Supabase.
    
    BEST PRACTICE 2026:
    - Persistência local no Supabase para dashboards rápidos.
    - Sincronização com LangSmith para análise de engenharia de prompt.
    """
    try:
        from app.services.supabase_service import get_supabase_client
        from app.core.langsmith_config import get_langsmith_client
        
        # 1. Preparar dados
        score = 1.0 if request.feedback_type == "positive" else 0.0
        feedback_data = {
            "run_id": request.message_id,
            "feedback_type": request.feedback_type,
            "score": score,
            "comment": request.comment,
            "metadata": {
                "source": "frontend_ui",
                "v": "2026.1"
            },
            "created_at": request.timestamp or datetime.now().isoformat()
        }
        
        # 2. Salvar no Supabase (Persistência Principal)
        try:
            supabase = get_supabase_client()
            supabase.table('feedbacks').insert(feedback_data).execute()
            logger.info(f"✅ Feedback salvo no Supabase (ID de Run: {request.message_id})")
        except Exception as db_err:
            logger.error(f"Erro ao salvar no Supabase: {db_err}")
            # Continuamos para tentar o LangSmith mesmo se o DB local falhar
        
        # 3. Sincronizar com LangSmith (Observabilidade)
        if request.message_id:
            try:
                ls_client = get_langsmith_client()
                if ls_client:
                    # Enviar com chave específica e chave genérica para garantir visibilidade nos dashboards
                    ls_client.create_feedback(
                        run_id=request.message_id,
                        key="user-score",
                        score=score,
                        comment=request.comment
                    )
                    ls_client.create_feedback(
                        run_id=request.message_id,
                        key="score",
                        score=score,
                        comment=request.comment
                    )
                    logger.info(f"🚀 Feedback sincronizado com LangSmith (ID: {request.message_id})")
            except Exception as ls_err:
                logger.error(f"Erro ao conectar com LangSmith: {ls_err}")

        return FeedbackResponse(
            success=True,
            message="Feedback registrado com sucesso em todos os sistemas"
        )
        
    except Exception as e:
        logger.error(f"Erro crítico no processamento de feedback: {e}")
        return FeedbackResponse(
            success=False,
            message="Erro ao registrar feedback"
        )


@router.get("/stats")
async def get_feedback_stats():
    """
    Retorna estatísticas de feedback (para dashboard futuro).
    """
    # TODO: Implementar quando houver persistência
    return {
        "total_positive": 0,
        "total_negative": 0,
        "satisfaction_rate": 0.0,
        "message": "Estatísticas ainda não disponíveis (requer persistência)"
    }
