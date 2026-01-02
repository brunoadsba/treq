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
    Recebe feedback do usuário sobre uma resposta.
    
    Conforme plano chat-inteligente.md:
    "Implemente um botão de Feedback (Gostei / Não Gostei) em cada mensagem.
    Isso será crucial para a Fase 4 (Otimização e Monitoramento)."
    """
    try:
        # Log estruturado para análise futura
        feedback_data = {
            "message_id": request.message_id,
            "feedback_type": request.feedback_type,
            "timestamp": request.timestamp or datetime.now().isoformat(),
            "comment": request.comment,
        }
        
        if request.feedback_type == "positive":
            logger.info(
                f"[FEEDBACK_POSITIVE] 👍 Resposta aprovada | "
                f"message_id: {request.message_id}"
            )
        else:
            logger.warning(
                f"[FEEDBACK_NEGATIVE] 👎 Resposta reprovada | "
                f"message_id: {request.message_id} | "
                f"comment: {request.comment or 'Sem comentário'}"
            )
        
        # TODO: Futuramente, salvar no banco de dados para análise
        # await save_feedback_to_database(feedback_data)
        
        return FeedbackResponse(
            success=True,
            message="Feedback registrado com sucesso"
        )
        
    except Exception as e:
        logger.error(f"Erro ao registrar feedback: {e}")
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
