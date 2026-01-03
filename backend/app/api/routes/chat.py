"""
Rotas da API para chat.
"""
from fastapi import APIRouter, HTTPException, Depends, Request
from fastapi.responses import StreamingResponse
from typing import Any
from loguru import logger
import json

from app.middleware.rate_limiter import get_rate_limit, rate_limit
from slowapi.errors import RateLimitExceeded
from app.api.routes.chat_helpers import build_llm_messages
from app.core.tracing import trace_llm_call
from langsmith.run_helpers import get_current_run_tree

# Importar módulos refatorados
from .chat_modules.models import ChatRequest, ChatResponse
from .chat_modules.dependencies import get_llm_service, get_rag_service, get_visualization_service
from .chat_modules.context_handler import prepare_chat_context
from .chat_modules.stream_handler import generate_stream_response
from .chat_modules.visualization_handler import handle_visualization

router = APIRouter(prefix="/chat", tags=["chat"])

@router.post("/")
@trace_llm_call(name="chat_endpoint", run_type="chain")
async def chat(
    request: Request,
    chat_request: ChatRequest,
    _: None = Depends(rate_limit(get_rate_limit("chat"))),  # Rate limiting via dependency injection
    llm_service: LLMService = Depends(get_llm_service),
    rag_service: RAGService = Depends(get_rag_service),
    visualization_service: Any = Depends(get_visualization_service)
):
    """
    Endpoint principal de chat.
    
    Processo:
    1. Verifica visualização (gráficos)
    2. Prepara contexto comum (detecções, context manager, RAG, tools, CoT Planner)
    3. Retorna resposta especial (social/consultoria) se aplicável
    4. Gera resposta com LLM (streaming ou não-streaming)
    """
    # BEST PRACTICE 2026: Capturar IDs de rastreio logo no início para vinculação de feedback
    run_tree = get_current_run_tree()
    run_id = str(run_tree.id) if run_tree else None
    
    # Log temporário para diagnóstico de rate limiting
    # Rate limiting check (internal)
    logger.debug(f"Rate limit check - Limit: {get_rate_limit('chat')}")
    
    try:
        # 1. Modo visualização
        viz_response = await handle_visualization(chat_request, visualization_service)
        if viz_response:
            return viz_response
        
        # 2. Preparar contexto comum
        prepared_context = await prepare_chat_context(chat_request, rag_service)
        
        # 3. Verificar se é resposta especial (social/consultoria inicial)
        if "special_response" in prepared_context:
            response_text = prepared_context["special_response"]
            response_type = prepared_context["type"]
            
            if chat_request.stream:
                # Streaming: enviar resposta especial
                def special_stream():
                    yield f"data: {json.dumps({'chunk': response_text, 'done': False})}\n\n"
                    yield f"data: {json.dumps({'chunk': '', 'done': True, 'conversation_id': chat_request.conversation_id})}\n\n"
                return StreamingResponse(special_stream(), media_type="text/event-stream")
            else:
                context_summary = "Interação social" if response_type == "social" else "Consultoria inicial"
                return ChatResponse(
                    response=response_text,
                    conversation_id=chat_request.conversation_id,
                    context_summary=context_summary,
                    sources=[]
                )
        
        # Extrair contexto preparado
        context_manager = prepared_context["context_manager"]
        query_type = prepared_context["query_type"]
        combined_context = prepared_context["combined_context"]
        sources = prepared_context["sources"]
        tool_result = prepared_context["tool_result"]
        is_follow_up = prepared_context["is_follow_up"]
        strategy = prepared_context["strategy"]
        sanitized_message = prepared_context["sanitized_message"]
        cot_plan = prepared_context.get("cot_plan")
        
        # 4. Modo streaming
        if chat_request.stream:
            logger.info(f"🚀 Criando StreamingResponse para query_type: {query_type}")
            return StreamingResponse(
                generate_stream_response(
                    chat_request=chat_request,
                    llm_service=llm_service,
                    context_manager=context_manager,
                    query_type=query_type,
                    combined_context=combined_context,
                    tool_result=tool_result,
                    is_follow_up=is_follow_up,
                    sources=sources,
                    strategy=strategy,
                    sanitized_message=sanitized_message,
                    cot_plan=cot_plan,
                    run_id=run_id
                ),
                media_type="text/event-stream",
                headers={
                    "Cache-Control": "no-cache",
                    "Connection": "keep-alive",
                    "X-Accel-Buffering": "no"
                }
            )
        
        # 5. Modo não-streaming
        # Construir mensagens para LLM
        messages = build_llm_messages(
            request_message=sanitized_message,
            query_type=query_type,
            combined_context=combined_context,
            is_follow_up=is_follow_up,
            llm_service=llm_service,
            context_manager=context_manager
        )
        
        # Injetar CoT se disponível
        if cot_plan:
             steps = "\n".join([f"- {step}" for step in cot_plan.get("reasoning_steps", [])])
             messages.append({
                 "role": "system", 
                 "content": f"INSTRUÇÃO DE RACIOCÍNIO:\nSiga estes passos planejados para responder:\n{steps}"
             })
        
        # Gerar resposta com LLM
        response_text = llm_service.generate_response(
            messages=messages,
            query_type=query_type,
            query_text=sanitized_message,
            stream=False
        )
        
        # Validar Grounding (Anti-alucinação) - Gatekeeper
        from app.core.grounding_validator import grounding_validator
        
        context_text = "\n\n".join(combined_context) if combined_context else ""
        is_grounded, confidence, reason = await grounding_validator.validate(
            response=response_text,
            context=context_text,
            llm_service=llm_service
        )
        
        if not is_grounded:
            logger.warning(
                f"[GROUNDING_REJECTED] Resposta rejeitada - Confiança: {confidence:.2f}, Motivo: {reason}"
            )
            response_text = grounding_validator.get_fallback_response(
                has_context=bool(combined_context)
            )
        else:
            logger.debug(f"[GROUNDING_OK] Confiança: {confidence:.2f}, Motivo: {reason}")
        
        # Validar tom conversacional para consultorias (Problema 4)
        if query_type == "consultoria":
            validation_result = validate_consultant_response(response_text)
            if not validation_result.get("valid", True):
                logger.warning(
                    f"[CONSULTATION_VALIDATION] Resposta rejeitada - Issues: {validation_result.get('issues', [])}"
                )
                if validation_result.get("warnings"):
                    logger.info(f"[CONSULTATION_VALIDATION] Avisos: {validation_result.get('warnings', [])}")
            
            # Avaliar qualidade da resposta para logging
            quality_assessment = assess_response_quality(response_text)
            response_quality = {
                "length": len(response_text),
                "quality": quality_assessment,
                "validation": validation_result,
                "document_count": len(combined_context),
                "has_sufficient_context": len(combined_context) >= 2,
                "grounding": {"is_grounded": is_grounded, "confidence": confidence}
            }
            logger.info(
                f"[CONSULTATION_RESPONSE] Query: '{sanitized_message[:100]}...' | "
                f"Response quality: {response_quality}"
            )
        else:
            logger.info(f"Resposta gerada - Query Type: {query_type}, Strategy: {strategy}, Grounding: {is_grounded}")
        
        # Adicionar mensagens ao histórico
        context_manager.add_message("user", sanitized_message)
        context_manager.add_message("assistant", response_text)
        
        # Retornar resposta
        return ChatResponse(
            response=response_text,
            conversation_id=chat_request.conversation_id,
            context_summary=context_manager.get_context_summary(),
            sources=sources,
            strategy=strategy,
            tool_data=tool_result.data if tool_result and tool_result.success else None,
            reasoning=cot_plan,
            run_id=run_id
        )
        
    except HTTPException:
        raise
    except RateLimitExceeded:
        raise
    except Exception as e:
        logger.error(f"Erro no endpoint de chat: {e}")
        import traceback
        logger.error(traceback.format_exc())
        raise HTTPException(
            status_code=500,
            detail="Erro interno ao processar sua solicitação. Por favor, tente novamente."
        )


@router.get("/health")
async def health_check():
    """Health check do endpoint de chat."""
    return {"status": "ok", "service": "chat"}
