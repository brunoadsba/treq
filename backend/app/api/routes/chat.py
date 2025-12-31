"""
Rotas da API para chat.
"""
from fastapi import APIRouter, HTTPException, Depends, Request
from fastapi.responses import StreamingResponse
from pydantic import BaseModel, Field
from typing import List, Optional, Dict, Any, Generator
from loguru import logger
import json

from app.services.llm_service import LLMService
from app.core.rag_service import RAGService
from app.core.context_manager import ContextManager
from app.core.social_detector import detect_social_interaction
from app.core.consultoria_detector import detect_initial_consultoria, get_initial_consultoria_response
from app.core.follow_up_detector import detect_follow_up, expand_query_with_context
from app.core.query_router import route_query
from app.core.dissatisfaction_detector import detect_dissatisfaction
from app.core.intent_classifier import classify_intent, generate_clarifying_question
from app.core.consultant_validator import validate_consultant_response, assess_response_quality
from app.utils.stream_validator import StreamValidator
from app.utils.input_sanitizer import sanitize_user_input, validate_input_length, get_max_input_length, sanitize_context_dict
from app.utils.pii_anonymizer import sanitize_for_logs
from app.middleware.request_id import get_request_id
from app.middleware.rate_limiter import limiter, get_rate_limit, rate_limit
from slowapi.errors import RateLimitExceeded
from app.api.routes.chat_helpers import (
    get_or_create_context_manager,
    process_entities_and_context,
    build_llm_messages,
    fetch_context_and_tools
)

router = APIRouter(prefix="/chat", tags=["chat"])


# Instâncias singleton dos serviços
_llm_service: Optional[LLMService] = None
_rag_service: Optional[RAGService] = None
_visualization_service: Optional[Any] = None

# Cache de ContextManager por conversa
_context_cache: Dict[str, ContextManager] = {}


def get_llm_service() -> LLMService:
    """Retorna instância singleton do LLM Service."""
    global _llm_service
    if _llm_service is None:
        _llm_service = LLMService()
    return _llm_service


def get_rag_service() -> RAGService:
    """Retorna instância singleton do RAG Service."""
    global _rag_service
    if _rag_service is None:
        _rag_service = RAGService()
    return _rag_service


def get_visualization_service():
    """Retorna instância singleton do Visualization Service."""
    global _visualization_service
    if _visualization_service is None:
        from app.services.visualization_service import VisualizationService
        _visualization_service = VisualizationService()
    return _visualization_service


# Schemas Pydantic
class ChatMessage(BaseModel):
    """Mensagem do chat."""
    role: str = Field(..., description="Role da mensagem: 'user' ou 'assistant'")
    content: str = Field(..., description="Conteúdo da mensagem")


class ChatRequest(BaseModel):
    """Request para chat."""
    message: str = Field(..., min_length=1, max_length=get_max_input_length(), description=f"Mensagem do usuário (máximo {get_max_input_length()} caracteres)")
    user_id: str = Field(..., description="ID do usuário")
    conversation_id: Optional[str] = Field(None, description="ID da conversa (opcional)")
    context: Optional[Dict[str, Any]] = Field(None, description="Contexto adicional (unidade, período, etc.)")
    stream: Optional[bool] = Field(False, description="Se True, retorna streaming SSE")
    visualization: Optional[bool] = Field(False, description="Se True, ativa modo visualização gráfica")
    action_id: Optional[str] = Field(None, description="ID da ação rápida (ex: 'alertas', 'status-recife')")


class ChatResponse(BaseModel):
    """Response do chat."""
    response: str = Field(..., description="Resposta do assistente")
    conversation_id: Optional[str] = Field(None, description="ID da conversa")
    context_summary: str = Field(..., description="Resumo do contexto atual")
    sources: List[Dict[str, Any]] = Field(default_factory=list, description="Fontes usadas (do RAG)")
    strategy: Optional[str] = Field(None, description="Estratégia usada (tool_first, rag_first, hybrid)")
    tool_data: Optional[Dict[str, Any]] = Field(None, description="Dados retornados por tools (se aplicável)")
    chart_data: Optional[Dict[str, Any]] = Field(None, description="Dados de gráfico (se visualization=True)")


async def _prepare_chat_context(
    chat_request: ChatRequest,
    rag_service: RAGService
) -> Dict[str, Any]:
    """
    Prepara contexto comum para streaming e não-streaming.
    
    Args:
        chat_request: Request do chat
        rag_service: Serviço RAG
        
    Returns:
        Dict com contexto preparado ou None se for resposta especial (social/consultoria inicial)
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
    
    # 2.1. Classificar intenção e verificar se precisa clarificação (Problema 5)
    # Aplicar apenas para consultorias (queries que começam com "consultoria:")
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
        _context_cache
    )
    
    # 4. Sanitizar contexto antes de processar
    sanitized_context = sanitize_context_dict(chat_request.context)
    
    # 5. Processar entidades e contexto (usar contexto sanitizado)
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
    
    return {
        "context_manager": context_manager,
        "entities": entities,
        "query_type": query_type,
        "combined_context": combined_context,
        "sources": sources,
        "tool_result": tool_result,
        "is_follow_up": is_follow_up,
        "strategy": strategy,
        "sanitized_message": user_message  # Mensagem sanitizada para uso posterior
    }


def _generate_stream_response(
    chat_request: ChatRequest,
    llm_service: LLMService,
    context_manager: ContextManager,
    query_type: str,
    combined_context: List[str],
    tool_result: Optional[Any],
    is_follow_up: bool,
    sources: List[Dict[str, Any]],
    strategy: str,
    sanitized_message: str
):
    """
    Generator para streaming de respostas via SSE.
    
    Yields:
        str: Eventos SSE formatados
    """
    try:
        # Construir mensagens para LLM usando função auxiliar (com mensagem sanitizada)
        messages = build_llm_messages(
            request_message=sanitized_message,
            query_type=query_type,
            combined_context=combined_context,
            is_follow_up=is_follow_up,
            llm_service=llm_service,
            context_manager=context_manager
        )
        
        # Gerar stream com StreamValidator para prevenir iterator exhaustion
        full_response = ""
        chunk_count = 0
        try:
            logger.info(f"🔄 Iniciando geração de stream para query_type: {query_type}")
            raw_generator = llm_service.generate_response(
                messages=messages,
                query_type=query_type,
                query_text=sanitized_message,
                stream=True
            )
            
            # Envolver com StreamValidator para validação sem consumo prematuro
            validated_gen = StreamValidator(raw_generator)
            
            # Validação explícita
            if not validated_gen.validate():
                logger.error(f"❌ Validação falhou - tentando fallback (query_type: {query_type}, strategy: {strategy})")
                yield from _fallback_complete_response(
                    messages, llm_service, query_type, sanitized_message,
                    chat_request, context_manager, sources, strategy, tool_result,
                    fallback_reason="stream_validation_failed"
                )
                return
            
            logger.info("✅ Validação bem-sucedida - iniciando loop SSE")
            
            # Importar filtro de termos técnicos para streaming
            from app.utils.technical_term_filter import StreamingTermFilter
            
            # Criar filtro de streaming que acumula chunks parcialmente
            stream_filter = StreamingTermFilter(buffer_size=15)
            
            # Loop SSE com tratamento de erros melhorado
            try:
                for chunk in validated_gen:
                    chunk_count += 1
                    
                    # Aplicar filtro de termos técnicos em cada chunk (com buffer para padrões divididos)
                    filtered_chunk = stream_filter.filter_chunk(chunk)
                    full_response += filtered_chunk
                    
                    # Enviar chunk filtrado via SSE
                    yield f"data: {json.dumps({'chunk': filtered_chunk, 'done': False})}\n\n"
                
                # Processar qualquer conteúdo restante no buffer
                remaining = stream_filter.flush()
                if remaining:
                    full_response += remaining
                    yield f"data: {json.dumps({'chunk': remaining, 'done': False})}\n\n"
                    
                    if chunk_count == 1:
                        logger.info(f"📤 Primeiro chunk enviado via SSE: '{chunk[:50] if len(chunk) > 50 else chunk}...'")
                    elif chunk_count % 100 == 0:
                        logger.debug(f"📤 {chunk_count} chunks enviados via SSE")
                
                logger.info(f"✅ Stream completo: {chunk_count} chunks processados, {len(full_response)} caracteres")
                
            except Exception as e:
                logger.error(f"❌ Erro durante streaming após {chunk_count} chunks: {e}")
                import traceback
                logger.error(traceback.format_exc())
                # Tentar fallback se ainda não enviou nenhum chunk
                if chunk_count == 0:
                    logger.warning("Nenhum chunk foi enviado, tentando fallback")
                    yield from _fallback_complete_response(
                        messages, llm_service, query_type, sanitized_message,
                        chat_request, context_manager, sources, strategy, tool_result,
                        fallback_reason="stream_error_no_chunks"
                    )
                    return
                else:
                    # Enviar erro ao cliente
                    error_data = {
                        "error": f"Erro durante streaming: {str(e)}",
                        "chunks_sent": chunk_count,
                        "done": True
                    }
                    yield f'data: {json.dumps(error_data)}\n\n'
            
            # Aplicar filtro de termos técnicos na resposta completa (pós-processamento)
            # Nota: Já aplicamos em cada chunk, mas aplicamos novamente no final para garantir
            # que padrões que podem ter sido divididos entre chunks sejam capturados
            full_response = filter_technical_terms(full_response)
            
            # Validação: verificar se ainda há termos técnicos após filtragem
            from app.utils.technical_term_filter import _detect_remaining_technical_terms
            remaining_terms = _detect_remaining_technical_terms(full_response)
            if remaining_terms:
                logger.warning(
                    f"⚠️ Termo técnico detectado após filtragem no streaming! Termos: {remaining_terms}. "
                    f"Reaplicando filtro...",
                    extra={"remaining_terms": remaining_terms, "response_preview": full_response[:200]}
                )
                full_response = filter_technical_terms(full_response)  # Reaplica
            
            # Validar tom conversacional para consultorias em modo streaming (Problema 4)
            if query_type == "consultoria":
                validation_result = validate_consultant_response(full_response)
                if not validation_result.get("valid", True):
                    logger.warning(
                        f"[CONSULTATION_VALIDATION_STREAM] Resposta rejeitada - Issues: {validation_result.get('issues', [])}"
                    )
                # Avaliar qualidade da resposta para logging
                quality_assessment = assess_response_quality(full_response)
                logger.info(
                    f"[CONSULTATION_RESPONSE_STREAM] Query: '{sanitized_message[:100]}...' | "
                    f"Quality: {quality_assessment} | Valid: {validation_result.get('valid', True)}"
                )
            
            # Adicionar mensagens ao histórico (usar mensagem sanitizada)
            context_manager.add_message("user", sanitized_message)
            context_manager.add_message("assistant", full_response)
            
            # Enviar evento final com metadados
            final_data = {
                "chunk": "",
                "done": True,
                "conversation_id": chat_request.conversation_id,
                "context_summary": context_manager.get_context_summary(),
                "sources": sources,
                "strategy": strategy,
                "tool_data": tool_result.data if tool_result and tool_result.success else None
            }
            logger.info(f"📤 Enviando evento final (done=True)")
            yield f"data: {json.dumps(final_data)}\n\n"
            
        except StopIteration:
            logger.error("❌ StopIteration no loop - usando fallback")
            yield from _fallback_complete_response(
                messages, llm_service, query_type, sanitized_message,
                chat_request, context_manager, sources, strategy, tool_result,
                fallback_reason="stop_iteration"
            )
        except Exception as stream_error:
            logger.error(f"❌ Erro ao processar stream: {stream_error}")
            import traceback
            logger.error(traceback.format_exc())
            yield from _fallback_complete_response(
                messages, llm_service, query_type, sanitized_message,
                chat_request, context_manager, sources, strategy, tool_result,
                fallback_reason="stream_processing_error"
            )
        
    except Exception as e:
        logger.error(f"Erro no stream: {e}")
        error_data = {
            "error": str(e),
            "done": True
        }
        yield f"data: {json.dumps(error_data)}\n\n"


def _fallback_complete_response(
    messages: List[Dict[str, str]],
    llm_service: LLMService,
    query_type: str,
    query_text: str,
    chat_request: ChatRequest,
    context_manager: ContextManager,
    sources: List[Dict[str, Any]],
    strategy: str,
    tool_result: Optional[Any],
    fallback_reason: str = "unknown"
) -> Generator[str, None, None]:
    """
    Fallback: gera resposta completa quando streaming falha.
    
    Args:
        messages: Mensagens preparadas
        llm_service: Serviço LLM
        query_type: Tipo da query
        query_text: Texto da query
        chat_request: Request original
        context_manager: Gerenciador de contexto
        sources: Fontes de informação
        strategy: Estratégia usada
        tool_result: Resultado de tools
        fallback_reason: Motivo do fallback (para feedback ao usuário)
        
    Yields:
        Resposta completa em evento SSE único
    """
    logger.warning(f"🔄 Executando fallback: resposta completa (não-streaming). Motivo: {fallback_reason}")
    
    try:
        # Gerar resposta completa
        full_response = llm_service.generate_response(
            messages=messages,
            query_type=query_type,
            query_text=query_text,
            stream=False
        )
        
        logger.info(f"✅ Fallback bem-sucedido: {len(full_response)} caracteres (reason: {fallback_reason})")
        
        # Aplicar filtro de termos técnicos na resposta completa (pós-processamento)
        from app.utils.technical_term_filter import filter_technical_terms, _detect_remaining_technical_terms
        full_response = filter_technical_terms(full_response)
        
        # Validação: verificar se ainda há termos técnicos após filtragem
        remaining_terms = _detect_remaining_technical_terms(full_response)
        if remaining_terms:
            logger.warning(
                f"⚠️ Termo técnico detectado após filtragem no fallback! Termos: {remaining_terms}. "
                f"Reaplicando filtro...",
                extra={"remaining_terms": remaining_terms, "response_preview": full_response[:200], "fallback_reason": fallback_reason}
            )
            full_response = filter_technical_terms(full_response)  # Reaplica
        
        # Adicionar ao histórico (query_text já é sanitizado)
        context_manager.add_message("user", query_text)
        context_manager.add_message("assistant", full_response)
        
        # Determinar mensagem de feedback baseada no motivo
        feedback_message = None
        if fallback_reason == "rpc_function_missing":
            feedback_message = "Base de conhecimento atualizada. Resposta completa devido à otimização do sistema."
        elif fallback_reason == "stream_validation_failed":
            feedback_message = "Resposta completa devido a uma pequena interrupção no streaming."
        elif fallback_reason == "stream_error_no_chunks":
            feedback_message = "Resposta completa devido a uma pequena interrupção no streaming."
        elif fallback_reason == "stop_iteration":
            feedback_message = "Resposta completa devido a uma pequena interrupção no streaming."
        elif fallback_reason == "stream_processing_error":
            feedback_message = "Resposta completa devido a uma pequena interrupção no streaming."
        
        # Enviar como único chunk com metadados
        final_data = {
            "chunk": full_response,
            "done": True,
            "fallback": True,
            "fallback_reason": fallback_reason,
            "fallback_message": feedback_message,
            "conversation_id": chat_request.conversation_id,
            "context_summary": context_manager.get_context_summary(),
            "sources": sources,
            "strategy": strategy,
            "tool_data": tool_result.data if tool_result and tool_result.success else None
        }
        yield f'data: {json.dumps(final_data)}\n\n'
        
    except Exception as e:
        logger.error(f"❌ Fallback também falhou: {e}")
        import traceback
        logger.error(traceback.format_exc())
        error_message = "Erro ao gerar resposta. Tente novamente."
        error_data = {
            "error": error_message,
            "done": True,
            "fallback": True,
            "fallback_reason": "fallback_failed"
        }
        yield f'data: {json.dumps(error_data)}\n\n'


@router.post("/")
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
    1. Prepara contexto comum (detecções, context manager, RAG, tools)
    2. Gera resposta com LLM (streaming ou não-streaming)
    3. Retorna resposta e fontes
    
    Se chat_request.stream=True, retorna Server-Sent Events (SSE) streaming.
    """
    # Log temporário para diagnóstico de rate limiting
    from slowapi.util import get_remote_address
    client_ip = get_remote_address(request)
    logger.debug(f"Rate limit check - IP: {client_ip}, Limit: {get_rate_limit('chat')}")
    
    try:
        # NOVO: Modo visualização - gerar gráfico se visualization=True e action_id fornecido
        if chat_request.visualization and chat_request.action_id:
            logger.info(
                f"[VISUALIZATION] Modo visualização ativado: "
                f"action_id={chat_request.action_id}, "
                f"period={chat_request.context.get('period', 'today') if chat_request.context else 'today'}, "
                f"unit={chat_request.context.get('unit') if chat_request.context else None}"
            )
            
            try:
                chart_data = await visualization_service.generate_chart_data(
                    action_id=chat_request.action_id,
                    period=chat_request.context.get("period", "today") if chat_request.context else "today",
                    unit=chat_request.context.get("unit") if chat_request.context else None
                )
                
                if chart_data:
                    logger.info(
                        f"[VISUALIZATION] Gráfico gerado com sucesso: "
                        f"type={chart_data.get('type')}, "
                        f"title={chart_data.get('title')}, "
                        f"empty={chart_data.get('metadata', {}).get('empty', False)}"
                    )
                    
                    if chat_request.stream:
                        # Streaming: enviar chart_data em um único evento SSE
                        def chart_stream():
                            yield f'data: {json.dumps({"chunk": "", "chart_data": chart_data, "done": True})}\n\n'
                        
                        return StreamingResponse(
                            chart_stream(),
                            media_type="text/event-stream",
                            headers={
                                "Cache-Control": "no-cache",
                                "Connection": "keep-alive",
                                "X-Accel-Buffering": "no"
                            }
                        )
                    else:
                        # Não-streaming: retornar ChatResponse com chart_data
                        return ChatResponse(
                            response=f"Gráfico: {chart_data['title']}",
                            conversation_id=chat_request.conversation_id,
                            context_summary="",
                            sources=[],
                            chart_data=chart_data
                        )
                else:
                    logger.warning(
                        f"[VISUALIZATION] Falha ao gerar gráfico para {chat_request.action_id}. "
                        f"Retornando None - usando fallback texto"
                    )
                    # Continuar com fluxo normal abaixo
            except Exception as e:
                logger.error(
                    f"[VISUALIZATION] Exceção ao gerar gráfico para {chat_request.action_id}: {e}"
                )
                import traceback
                logger.error(traceback.format_exc())
                # Continuar com fluxo normal (fallback para texto)
        
        # Preparar contexto comum (detecções, RAG, tools, etc.)
        # Nota: Validação de tamanho é feita pelo Pydantic (422) e pelo sanitize_user_input (400)
        prepared_context = await _prepare_chat_context(chat_request, rag_service)
        
        # Verificar se é resposta especial (social/consultoria inicial)
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
                # Não-streaming: retornar ChatResponse
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
        
        # Modo streaming
        if chat_request.stream:
            logger.info(f"🚀 Criando StreamingResponse para query_type: {query_type}")
            return StreamingResponse(
                _generate_stream_response(
                    chat_request=chat_request,
                    llm_service=llm_service,
                    context_manager=context_manager,
                    query_type=query_type,
                    combined_context=combined_context,
                    tool_result=tool_result,
                    is_follow_up=is_follow_up,
                    sources=sources,
                    strategy=strategy,
                    sanitized_message=sanitized_message
                ),
                media_type="text/event-stream",
                headers={
                    "Cache-Control": "no-cache",
                    "Connection": "keep-alive",
                    "X-Accel-Buffering": "no"
                }
            )
        
        # Modo não-streaming
        # Construir mensagens para LLM (usar mensagem sanitizada)
        messages = build_llm_messages(
            request_message=sanitized_message,
            query_type=query_type,
            combined_context=combined_context,
            is_follow_up=is_follow_up,
            llm_service=llm_service,
            context_manager=context_manager
        )
        
        # Gerar resposta com LLM
        response_text = llm_service.generate_response(
            messages=messages,
            query_type=query_type,
            query_text=sanitized_message,
            stream=False
        )
        
        # Nota: O filtro de termos técnicos já é aplicado no llm_service.py
        # Não precisa aplicar novamente aqui
        
        # Validar tom conversacional para consultorias (Problema 4)
        if query_type == "consultoria":
            validation_result = validate_consultant_response(response_text)
            if not validation_result.get("valid", True):
                logger.warning(
                    f"[CONSULTATION_VALIDATION] Resposta rejeitada - Issues: {validation_result.get('issues', [])}"
                )
                # Log de avisos (não bloqueantes)
                if validation_result.get("warnings"):
                    logger.info(f"[CONSULTATION_VALIDATION] Avisos: {validation_result.get('warnings', [])}")
            
            # Avaliar qualidade da resposta para logging
            quality_assessment = assess_response_quality(response_text)
            response_quality = {
                "length": len(response_text),
                "quality": quality_assessment,
                "validation": validation_result,
                "document_count": len(combined_context),
                "has_sufficient_context": len(combined_context) >= 2
            }
            logger.info(
                f"[CONSULTATION_RESPONSE] Query: '{sanitized_message[:100]}...' | "
                f"Response quality: {response_quality}"
            )
        else:
            logger.info(f"Resposta gerada - Query Type: {query_type}, Strategy: {strategy}")
        
        # Adicionar mensagens ao histórico (usar mensagem sanitizada)
        context_manager.add_message("user", sanitized_message)
        context_manager.add_message("assistant", response_text)
        
        # Retornar resposta
        return ChatResponse(
            response=response_text,
            conversation_id=chat_request.conversation_id,
            context_summary=context_manager.get_context_summary(),
            sources=sources,
            strategy=strategy,
            tool_data=tool_result.data if tool_result and tool_result.success else None
        )
        
    except HTTPException:
        # Re-raise HTTPException para que seja tratada pelo handler do FastAPI
        raise
    except RateLimitExceeded:
        # Re-raise RateLimitExceeded para que seja tratada pelo handler do FastAPI
        raise
    except Exception as e:
        # Log detalhado internamente
        logger.error(f"Erro no endpoint de chat: {e}")
        import traceback
        logger.error(traceback.format_exc())
        
        # Retornar mensagem genérica ao cliente (não expor detalhes internos)
        raise HTTPException(
            status_code=500,
            detail="Erro interno ao processar sua solicitação. Por favor, tente novamente."
        )


@router.get("/health")
async def health_check():
    """Health check do endpoint de chat."""
    return {"status": "ok", "service": "chat"}
