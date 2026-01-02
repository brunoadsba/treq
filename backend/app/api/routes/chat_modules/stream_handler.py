from typing import Any, List, Dict, Optional, Generator
from loguru import logger
import json

from app.services.llm_service import LLMService
from app.core.context_manager import ContextManager
from app.core.consultant_validator import validate_consultant_response, assess_response_quality
from app.core.tracing import trace_llm_call
from app.utils.stream_validator import StreamValidator
from app.api.routes.chat_helpers import build_llm_messages
from app.utils.technical_term_filter import (
    filter_technical_terms,
    StreamingTermFilter,
    _detect_remaining_technical_terms
)

from .models import ChatRequest


def fallback_complete_response(
    messages: List[Dict[str, str]],
    llm_service: LLMService,
    query_type: str,
    query_text: str,
    chat_request: ChatRequest,
    context_manager: ContextManager,
    sources: List[Dict[str, Any]],
    strategy: str,
    tool_result: Optional[Any],
    fallback_reason: str = "unknown",
    cot_plan: Optional[Dict[str, Any]] = None
) -> Generator[str, None, None]:
    """
    Fallback: gera resposta completa quando streaming falha.
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
        elif fallback_reason in ["stream_validation_failed", "stream_error_no_chunks", "stop_iteration", "stream_processing_error"]:
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
            "tool_data": tool_result.data if tool_result and tool_result.success else None,
            "reasoning": cot_plan
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


def generate_stream_response(
    chat_request: ChatRequest,
    llm_service: LLMService,
    context_manager: ContextManager,
    query_type: str,
    combined_context: List[str],
    tool_result: Optional[Any],
    is_follow_up: bool,
    sources: List[Dict[str, Any]],
    strategy: str,
    sanitized_message: str,
    cot_plan: Optional[Dict[str, Any]] = None,
    run_id: Optional[str] = None
):
    """
    Generator para streaming de respostas via SSE.
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
        
        # Injetar CoT nas mensagens se disponível para guiar o modelo
        if cot_plan:
             steps = "\n".join([f"- {step}" for step in cot_plan.get("reasoning_steps", [])])
             instruction = f"INSTRUÇÃO DE RACIOCÍNIO:\nSiga estes passos planejados para responder:\n{steps}"
             
             messages.append({
                 "role": "system", 
                 "content": instruction
             })
        
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
                yield from fallback_complete_response(
                    messages, llm_service, query_type, sanitized_message,
                    chat_request, context_manager, sources, strategy, tool_result,
                    fallback_reason="stream_validation_failed",
                    cot_plan=cot_plan
                )
                return
            
            logger.info("✅ Validação bem-sucedida - iniciando loop SSE")
            
            # Enviar evento de reasoning (CoT) inicial se disponível
            if cot_plan:
                yield f"data: {json.dumps({'type': 'reasoning', 'plan': cot_plan, 'run_id': run_id, 'done': False})}\n\n"
            
            # Criar filtro de streaming que acumula chunks parcialmente
            # Buffer aumentado de 15 para 25 para capturar termos compostos e corrompidos (ex: SLazo)
            stream_filter = StreamingTermFilter(buffer_size=25)
            
            # Loop SSE com tratamento de erros melhorado
            try:
                for chunk in validated_gen:
                    chunk_count += 1
                    
                    # Aplicar filtro de termos técnicos em cada chunk
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
                    yield from fallback_complete_response(
                        messages, llm_service, query_type, sanitized_message,
                        chat_request, context_manager, sources, strategy, tool_result,
                        fallback_reason="stream_error_no_chunks",
                        cot_plan=cot_plan
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
            
            # Aplicar filtro de termos técnicos na resposta completa (pós-processamento final)
            full_response = filter_technical_terms(full_response)
            
            # Validação final de termos
            remaining_terms = _detect_remaining_technical_terms(full_response)
            if remaining_terms:
                logger.warning(
                    f"⚠️ Termo técnico detectado após filtragem no streaming! Termos: {remaining_terms}. "
                    f"Reaplicando filtro...",
                    extra={"remaining_terms": remaining_terms, "response_preview": full_response[:200]}
                )
                full_response = filter_technical_terms(full_response)
            
            # Validar tom conversacional para consultorias em modo streaming
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
            
            # Validar Grounding (Anti-alucinação) - Gatekeeper
            # Nota: Em streaming, já enviamos os chunks, então apenas logamos se falhar
            from app.core.grounding_validator import GroundingValidator
            grounding_validator = GroundingValidator()
            
            context_text = "\n\n".join(combined_context) if combined_context else ""
            
            # Validação síncrona simplificada para streaming (sem async)
            is_grounded = True
            confidence = 0.5
            
            if context_text and len(full_response) >= 50:
                try:
                    # Chamada síncrona do método de validação
                    messages_validation = [
                        {"role": "system", "content": "Você é um verificador de fatos técnico e preciso."},
                        {"role": "user", "content": grounding_validator.VALIDATION_PROMPT.format(
                            context=context_text[:4000],
                            response=full_response[:2000]
                        )}
                    ]
                    
                    validation_response = llm_service._generate_response_non_stream(
                        messages=messages_validation,
                        selected_model="llama-3.1-8b-instant",
                        provider="groq",
                        temperature=0.1,
                        max_tokens=200
                    )
                    
                    is_grounded, confidence, reason = grounding_validator._parse_validation_response(validation_response)
                    
                    if not is_grounded:
                        logger.warning(
                            f"[GROUNDING_STREAM_WARNING] Resposta pode conter alucinação - "
                            f"Confiança: {confidence:.2f}, Motivo: {reason}"
                        )
                        # Enviar evento de warning ao cliente
                        yield f"data: {json.dumps({'type': 'grounding_warning', 'confidence': confidence, 'reason': reason})}\n\n"
                    else:
                        logger.debug(f"[GROUNDING_STREAM_OK] Confiança: {confidence:.2f}")
                        
                except Exception as e:
                    logger.warning(f"Erro na validação de grounding em streaming: {e}")
            
            # Adicionar mensagens ao histórico
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
                "tool_data": tool_result.data if tool_result and tool_result.success else None,
                "reasoning": cot_plan,
                "run_id": run_id
            }
            logger.info(f"📤 Enviando evento final (done=True)")
            yield f"data: {json.dumps(final_data)}\n\n"
            
        except StopIteration:
            logger.error("❌ StopIteration no loop - usando fallback")
            yield from fallback_complete_response(
                messages, llm_service, query_type, sanitized_message,
                chat_request, context_manager, sources, strategy, tool_result,
                fallback_reason="stop_iteration",
                cot_plan=cot_plan
            )
        except Exception as stream_error:
            logger.error(f"❌ Erro ao processar stream: {stream_error}")
            import traceback
            logger.error(traceback.format_exc())
            yield from fallback_complete_response(
                messages, llm_service, query_type, sanitized_message,
                chat_request, context_manager, sources, strategy, tool_result,
                fallback_reason="stream_processing_error",
                cot_plan=cot_plan
            )
        
    except Exception as e:
        logger.error(f"Erro no stream: {e}")
        error_data = {
            "error": str(e),
            "done": True
        }
        yield f"data: {json.dumps(error_data)}\n\n"
