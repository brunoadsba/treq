from typing import Dict, Any, TYPE_CHECKING
from loguru import logger
import json
from fastapi import HTTPException

if TYPE_CHECKING:
    from app.core.rag_service import RAGService
    from app.services.llm_service import LLMService
from app.core.social_detector import detect_social_interaction
from app.core.consultoria_detector import detect_initial_consultoria, get_initial_consultoria_response
from app.core.follow_up_detector import detect_follow_up, expand_query_with_context
from app.core.query_router import route_query
from app.core.dissatisfaction_detector import detect_dissatisfaction
from app.core.intent_classifier import classify_intent, generate_clarifying_question
from app.utils.input_sanitizer import sanitize_user_input, sanitize_context_dict
from app.utils.pii_anonymizer import sanitize_for_logs
from app.middleware.request_id import get_request_id
from app.api.routes.chat_helpers import (
    get_or_create_context_manager,
    process_entities_and_context,
    fetch_context_and_tools
)

from .models import ChatRequest
from .dependencies import get_context_cache, get_llm_service
from app.core.cot_planner import generate_cot_plan

async def prepare_chat_context(
    chat_request: ChatRequest,
    rag_service: 'RAGService'
) -> Dict[str, Any]:
    """
    Prepara contexto comum para streaming e não-streaming.
    Inclui etapa de planejamento CoT (Chain of Thought).
    """
    # 0. Sanitizar e validar input do usuário
    sanitized_message, is_valid = sanitize_user_input(chat_request.message)
    if not is_valid:
        raise HTTPException(
            status_code=400,
            detail="Mensagem inválida. Verifique se não está vazia e não excede o tamanho máximo permitido."
        )
    
    # Usar mensagem sanitizada daqui em diante
    user_message = sanitized_message
    
    # 1. Detectar interações sociais
    social_response = detect_social_interaction(user_message)
    if social_response:
        logger.info(f"Interação social detectada - resposta direta sem RAG")
        return {"special_response": social_response, "type": "social"}
    
    # 2. Detectar consultoria inicial ou necessidade de clarificação
    if detect_initial_consultoria(user_message):
        logger.info("Consultoria inicial detectada - retornando pergunta interativa")
        initial_response = get_initial_consultoria_response()
        return {"special_response": initial_response, "type": "consultoria"}
    
    # 2.1. Classificar intenção e verificar se precisa clarificação
    if user_message.lower().startswith("consultoria:"):
        intent_result = classify_intent(user_message)
        if intent_result.get("requires_clarification", False):
            clarifying_question = generate_clarifying_question(user_message)
            logger.info(f"Consulta precisa clarificação - gerando pergunta: {clarifying_question[:100]}...")
            return {"special_response": clarifying_question, "type": "consultoria", "intent": intent_result}
    
    # 3. Obter context manager
    context_manager = get_or_create_context_manager(
        chat_request.user_id,
        chat_request.conversation_id,
        get_context_cache()
    )
    
    # 4. Sanitizar contexto antes de processar
    sanitized_context = sanitize_context_dict(chat_request.context)
    
    # 5. Processar entidades e contexto
    entities = process_entities_and_context(
        user_message,
        sanitized_context,
        context_manager
    )
    
    # 6. Detectar follow-up e insatisfação
    is_follow_up = detect_follow_up(user_message, context_manager)
    is_dissatisfied = detect_dissatisfaction(user_message, context_manager)
    if is_dissatisfied:
        sanitized_msg = sanitize_for_logs(user_message, max_length=100)
        request_id = get_request_id()
        logger.warning(
            f"Insatisfação detectada: '{sanitized_msg}' "
            f"(query_type será determinado pela classificação, request_id: {request_id})"
        )
    
    # 7. Classificar query e determinar estratégia
    query_type = context_manager.classify_query(user_message)
    
    # 7.1. Se for pergunta sobre capacidades, retornar resposta direta sem RAG
    if query_type == "capacidade":
        logger.info(f"Pergunta sobre capacidades detectada - resposta direta sem RAG: '{user_message}'")
        capability_response = (
            "Sim, consigo analisar arquivos PDF, DOCX, PPTX e Excel (.xlsx, .xls). "
            "Meu foco é em informações operacionais como procedimentos, métricas e alertas. "
            "Por favor, envie o arquivo usando o botão de anexo na interface e me diga qual informação específica você gostaria de extrair."
        )
        return {"special_response": capability_response, "type": "capacidade"}
    
    strategy, strategy_params = route_query(user_message, query_type)
    request_id = get_request_id()
    logger.info(
        f"Query classificada como: {query_type} (follow-up: {is_follow_up}, "
        f"request_id: {request_id})"
    )
    logger.info(f"Estratégia de roteamento: {strategy} (params: {json.dumps(strategy_params, ensure_ascii=False)})")
    
    # 8. Preparar query para busca (expandir se follow-up)
    search_query = user_message
    if is_follow_up:
        search_query = expand_query_with_context(user_message, context_manager)
        logger.info(f"Query expandida com contexto da conversa anterior")
    
    # 9. Buscar contexto RAG e executar tools
    combined_context, sources, tool_result = await fetch_context_and_tools(
        request_message=user_message,
        query_type=query_type,
        strategy=strategy,
        strategy_params=strategy_params,
        entities=entities,
        search_query=search_query,
        is_follow_up=is_follow_up,
        rag_service=rag_service
    )
    
    # 10. Executar CoT Planner (Fase 3 Feature)
    cot_plan = None
    # Executar CoT se houver contexto ou se for intenção complexa
    if (combined_context or query_type not in ["greeting", "social"]) and query_type != "capacidade":
        llm_service = get_llm_service()
        # Se show_reasoning for False no request, ainda poderiamos executar o CoT internamente para melhorar a resposta?
        # Sim, o objetivo é IMPROVE reasoning.
        cot_plan = await generate_cot_plan(user_message, combined_context, llm_service, query_type)
        
        if cot_plan.get("context_status") == "INSUFFICIENT" and not tool_result:
             logger.warning("CoT Planner indicou contexto insuficiente.")

    return {
        "context_manager": context_manager,
        "entities": entities,
        "query_type": query_type,
        "combined_context": combined_context,
        "sources": sources,
        "tool_result": tool_result,
        "is_follow_up": is_follow_up,
        "strategy": strategy,
        "sanitized_message": user_message,
        "cot_plan": cot_plan
    }
