"""
Rotas da API para chat.
"""
from fastapi import APIRouter, HTTPException, Depends
from fastapi.responses import StreamingResponse
from pydantic import BaseModel, Field
from typing import List, Optional, Dict, Any
from loguru import logger
import json

from app.services.llm_service import LLMService
from app.core.rag_service import RAGService
from app.core.context_manager import ContextManager
from app.core.social_detector import detect_social_interaction
from app.core.follow_up_detector import detect_follow_up, expand_query_with_context
from app.core.search_utils import get_adaptive_threshold, search_with_fallback
from app.core.query_router import route_query, should_use_tool_first, should_use_rag_first
from app.core.tools import MetricsTool
from app.core.param_extractor import extract_tool_params

router = APIRouter(prefix="/chat", tags=["chat"])


def _format_tool_result(tool_data: Dict[str, Any]) -> str:
    """
    Formata resultado de tool para contexto do LLM.
    
    Args:
        tool_data: Dados retornados pela tool
        
    Returns:
        str: Texto formatado para contexto
    """
    if isinstance(tool_data, dict):
        # Formatar dados estruturados
        parts = []
        if "metric_name" in tool_data:
            parts.append(f"Métrica: {tool_data['metric_name']}")
        if "value" in tool_data:
            parts.append(f"Valor: {tool_data['value']}")
        if "count" in tool_data:
            parts.append(f"Total de registros: {tool_data['count']}")
        return "\n".join(parts) if parts else str(tool_data)
    return str(tool_data)


# Instâncias singleton dos serviços
_llm_service: Optional[LLMService] = None
_rag_service: Optional[RAGService] = None

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


# Schemas Pydantic
class ChatMessage(BaseModel):
    """Mensagem do chat."""
    role: str = Field(..., description="Role da mensagem: 'user' ou 'assistant'")
    content: str = Field(..., description="Conteúdo da mensagem")


class ChatRequest(BaseModel):
    """Request para chat."""
    message: str = Field(..., description="Mensagem do usuário")
    user_id: str = Field(..., description="ID do usuário")
    conversation_id: Optional[str] = Field(None, description="ID da conversa (opcional)")
    context: Optional[Dict[str, Any]] = Field(None, description="Contexto adicional (unidade, período, etc.)")
    stream: Optional[bool] = Field(False, description="Se True, retorna streaming SSE")


class ChatResponse(BaseModel):
    """Response do chat."""
    response: str = Field(..., description="Resposta do assistente")
    conversation_id: Optional[str] = Field(None, description="ID da conversa")
    context_summary: str = Field(..., description="Resumo do contexto atual")
    sources: List[Dict[str, Any]] = Field(default_factory=list, description="Fontes usadas (do RAG)")
    strategy: Optional[str] = Field(None, description="Estratégia usada (tool_first, rag_first, hybrid)")
    tool_data: Optional[Dict[str, Any]] = Field(None, description="Dados retornados por tools (se aplicável)")


async def _generate_stream_response(
    request: ChatRequest,
    llm_service: LLMService,
    rag_service: RAGService,
    context_manager: ContextManager,
    query_type: str,
    combined_context: List[str],
    tool_result: Optional[Any],
    is_follow_up: bool,
    sources: List[Dict[str, Any]],
    strategy: str
):
    """
    Generator para streaming de respostas via SSE.
    
    Yields:
        str: Eventos SSE formatados
    """
    try:
        # Construir mensagens para LLM
        messages = []
        
        # Selecionar prompt do sistema
        if query_type in llm_service.SYSTEM_PROMPTS:
            system_content = llm_service.SYSTEM_PROMPTS[query_type]
        else:
            system_content = llm_service.DEFAULT_PROMPT
        
        messages.append({"role": "system", "content": system_content})
        
        # Adicionar histórico se follow-up
        if is_follow_up:
            messages.extend(context_manager.get_recent_messages(n=3))
        
        # Construir conteúdo do usuário com contexto
        if combined_context:
            context_text = "\n\n---\n\n".join([
                f"Documento {i+1}:\n{ctx}"
                for i, ctx in enumerate(combined_context)
            ])
            user_content = f"""CONTEXTO DOS DOCUMENTOS:
{context_text}

---

PERGUNTA DO USUÁRIO:
{request.message}

Responda usando APENAS as informações do contexto acima."""
        else:
            user_content = request.message
        
        messages.append({"role": "user", "content": user_content})
        
        # Gerar stream
        full_response = ""
        for chunk in llm_service.generate_response(
            messages=messages,
            query_type=query_type,
            query_text=request.message,
            stream=True
        ):
            full_response += chunk
            # Enviar chunk via SSE
            yield f"data: {json.dumps({'chunk': chunk, 'done': False})}\n\n"
        
        # Adicionar mensagens ao histórico
        context_manager.add_message("user", request.message)
        context_manager.add_message("assistant", full_response)
        
        # Enviar evento final com metadados
        final_data = {
            "chunk": "",
            "done": True,
            "conversation_id": request.conversation_id,
            "context_summary": context_manager.get_context_summary(),
            "sources": sources,
            "strategy": strategy,
            "tool_data": tool_result.data if tool_result and tool_result.success else None
        }
        yield f"data: {json.dumps(final_data)}\n\n"
        
    except Exception as e:
        logger.error(f"Erro no stream: {e}")
        error_data = {
            "error": str(e),
            "done": True
        }
        yield f"data: {json.dumps(error_data)}\n\n"


@router.post("/")
async def chat(
    request: ChatRequest,
    llm_service: LLMService = Depends(get_llm_service),
    rag_service: RAGService = Depends(get_rag_service)
):
    """
    Endpoint principal de chat.
    
    Processo:
    1. Classifica a query
    2. Busca contexto relevante no RAG
    3. Gera resposta com LLM usando contexto
    4. Retorna resposta e fontes
    
    Se request.stream=True, retorna Server-Sent Events (SSE) streaming.
    """
    try:
        # Verificar se é streaming
        if request.stream:
            # Processar até o ponto de gerar resposta (mesma lógica não-streaming)
            # mas retornar via SSE
            
            # 1. DETECÇÃO DE INTERAÇÕES SOCIAIS
            social_response = detect_social_interaction(request.message)
            if social_response:
                logger.info(f"Interação social detectada - resposta direta sem RAG")
                # Para streaming, enviar resposta completa de uma vez
                async def social_stream():
                    yield f"data: {json.dumps({'chunk': social_response, 'done': False})}\n\n"
                    yield f"data: {json.dumps({'chunk': '', 'done': True, 'conversation_id': request.conversation_id})}\n\n"
                return StreamingResponse(social_stream(), media_type="text/event-stream")
            
            # 2. Obter context manager
            cache_key = f"{request.user_id}:{request.conversation_id or 'default'}"
            if cache_key not in _context_cache:
                _context_cache[cache_key] = ContextManager(user_id=request.user_id)
            context_manager = _context_cache[cache_key]
            
            # 3-12. Mesma lógica de processamento (classificação, RAG, tools, etc.)
            entities = context_manager.extract_entities(request.message)
            if entities.get("unit"):
                context_manager.update_unit(entities["unit"])
            if entities.get("period"):
                context_manager.update_period(
                    entities["period"]["month"],
                    entities["period"]["year"]
                )
            
            if request.context:
                if "unit" in request.context:
                    context_manager.update_unit(request.context["unit"])
                if "period" in request.context:
                    period = request.context["period"]
                    context_manager.update_period(period.get("month", 12), period.get("year", 2024))
            
            is_follow_up = detect_follow_up(request.message, context_manager)
            query_type = context_manager.classify_query(request.message)
            strategy, strategy_params = route_query(request.message, query_type)
            
            search_query = request.message
            if is_follow_up:
                search_query = expand_query_with_context(request.message, context_manager)
            
            should_use_rag = should_use_rag_first(query_type, strategy)
            should_use_tool = should_use_tool_first(query_type, strategy)
            
            tool_result = None
            if should_use_tool:
                if query_type in ["metrica_temporal", "status_temporal"] or "metric" in strategy_params.get("type", ""):
                    metrics_tool = MetricsTool()
                    tool_params = extract_tool_params(
                        query=request.message,
                        query_type=query_type,
                        entities=entities
                    )
                    tool_result = await metrics_tool.execute(**tool_params)
                    if not tool_result.success:
                        should_use_rag = True
            
            rag_results = []
            context_texts = []
            if should_use_rag:
                top_k = 5 if query_type in ["procedimento", "detalhamento"] else 3
                rag_results, used_threshold = search_with_fallback(
                    query=search_query,
                    query_type=query_type,
                    rag_service=rag_service,
                    top_k=top_k,
                    min_docs=2,
                    filters=None
                )
                context_texts = [result["content"] for result in rag_results]
            
            sources = [
                {
                    "content": result["content"][:200] + "..." if len(result["content"]) > 200 else result["content"],
                    "similarity": round(result["similarity"], 3),
                    "metadata": result.get("metadata", {})
                }
                for result in rag_results
            ]
            
            combined_context = context_texts.copy() if context_texts else []
            if tool_result and tool_result.success and tool_result.data:
                tool_context = f"DADOS EM TEMPO REAL:\n{_format_tool_result(tool_result.data)}"
                combined_context.append(tool_context)
            
            # Retornar streaming
            return StreamingResponse(
                _generate_stream_response(
                    request=request,
                    llm_service=llm_service,
                    rag_service=rag_service,
                    context_manager=context_manager,
                    query_type=query_type,
                    combined_context=combined_context,
                    tool_result=tool_result,
                    is_follow_up=is_follow_up,
                    sources=sources,
                    strategy=strategy
                ),
                media_type="text/event-stream",
                headers={
                    "Cache-Control": "no-cache",
                    "Connection": "keep-alive",
                    "X-Accel-Buffering": "no"
                }
            )
        
        # Modo não-streaming (código original)
        # 1. DETECÇÃO DE INTERAÇÕES SOCIAIS (antes de qualquer processamento)
        social_response = detect_social_interaction(request.message)
        if social_response:
            logger.info(f"Interação social detectada - resposta direta sem RAG")
            return ChatResponse(
                response=social_response,
                conversation_id=request.conversation_id,
                context_summary="Interação social",
                sources=[]
            )
        
        # 2. Obter ou criar context manager (persistente por conversa)
        cache_key = f"{request.user_id}:{request.conversation_id or 'default'}"
        if cache_key not in _context_cache:
            _context_cache[cache_key] = ContextManager(user_id=request.user_id)
        context_manager = _context_cache[cache_key]
        
        logger.debug(f"ContextManager recuperado/criado para: {cache_key} (histórico: {len(context_manager.message_history)} mensagens)")
        
        # 3. Extrair entidades automaticamente da query
        entities = context_manager.extract_entities(request.message)
        if entities.get("unit"):
            context_manager.update_unit(entities["unit"])
        if entities.get("period"):
            context_manager.update_period(
                entities["period"]["month"],
                entities["period"]["year"]
            )
        
        # 4. Atualizar contexto se fornecido explicitamente (sobrescreve extração automática)
        if request.context:
            if "unit" in request.context:
                context_manager.update_unit(request.context["unit"])
            if "period" in request.context:
                period = request.context["period"]
                context_manager.update_period(period.get("month", 12), period.get("year", 2024))
        
        # 5. Detectar follow-up questions
        is_follow_up = detect_follow_up(request.message, context_manager)
        
        # 6. Classificar query
        query_type = context_manager.classify_query(request.message)
        logger.info(f"Query classificada como: {query_type} (follow-up: {is_follow_up})")
        
        # 6.1. Roteamento: decidir estratégia (Tool-First vs RAG-First vs Hybrid)
        strategy, strategy_params = route_query(request.message, query_type)
        logger.info(f"Estratégia de roteamento: {strategy} (params: {strategy_params})")
        
        # 7. Preparar query para busca RAG (expandir se follow-up)
        search_query = request.message
        if is_follow_up:
            search_query = expand_query_with_context(request.message, context_manager)
            logger.info(f"Query expandida com contexto da conversa anterior")
        
        # 8. Decidir se deve usar RAG baseado na estratégia
        should_use_rag = should_use_rag_first(query_type, strategy)
        should_use_tool = should_use_tool_first(query_type, strategy)
        
        # Não usar RAG para queries muito genéricas sem contexto operacional
        query_lower = request.message.lower()
        generic_queries = ["oi", "olá", "tudo bem", "como vai"]
        if query_lower.strip() in generic_queries:
            should_use_rag = False
            should_use_tool = False
        
        # 9. Executar Tool-First (se necessário)
        tool_result = None
        if should_use_tool:
            logger.info(f"Executando Tool-First para query tipo: {query_type}")
            try:
                # Por enquanto, apenas MetricsTool implementada
                if query_type in ["metrica_temporal", "status_temporal"] or "metric" in strategy_params.get("type", ""):
                    metrics_tool = MetricsTool()
                    
                    # Extrair parâmetros da query de forma inteligente
                    tool_params = extract_tool_params(
                        query=request.message,
                        query_type=query_type,
                        entities=entities
                    )
                    
                    # Executar tool com parâmetros extraídos
                    tool_result = await metrics_tool.execute(**tool_params)
                    
                    if tool_result.success:
                        logger.info(f"✅ Tool retornou dados: {tool_result.data}")
                    else:
                        logger.warning(f"⚠️ Tool falhou: {tool_result.error or tool_result.message}")
                        # Fallback para RAG se tool falhar
                        should_use_rag = True
            except Exception as e:
                logger.error(f"Erro ao executar tool: {e}")
                import traceback
                logger.error(traceback.format_exc())
                # Fallback para RAG em caso de erro
                should_use_rag = True
        
        # 10. Preparar filtros de metadata para busca RAG (se período/unidade detectados)
        rag_filters = None
        if entities.get("period"):
            # Filtrar documentos que mencionam o período específico
            # Nota: Por enquanto, filtro por metadata não está implementado no RAG,
            # mas a query expandida já inclui o período, melhorando a busca semântica
            month = entities["period"]["month"]
            year = entities["period"]["year"]
            logger.debug(f"Período detectado para filtro RAG: {month}/{year}")
            # TODO: Implementar filtro por metadata quando suportado
        
        # 11. Buscar contexto relevante no RAG (se necessário)
        rag_results = []
        used_threshold = 0.0
        context_texts = []
        
        if should_use_rag:
            # Aumentar top_k para detalhamento (precisa de mais documentos)
            top_k = 5 if query_type in ["procedimento", "detalhamento"] else 3
            # Usar query expandida se for follow-up
            rag_results, used_threshold = search_with_fallback(
                query=search_query,  # Usar query expandida (já inclui período/unidade)
                query_type=query_type,
                rag_service=rag_service,
                top_k=top_k,
                min_docs=2,
                filters=rag_filters  # Passar filtros (por enquanto None, mas preparado para futuro)
            )
            
            logger.info(
                f"Busca RAG retornou {len(rag_results)} documentos "
                f"(threshold: {used_threshold:.2f})"
            )
            
            # Extrair contexto dos resultados RAG
            context_texts = [result["content"] for result in rag_results]
        else:
            logger.info("RAG não utilizado - usando conhecimento geral do LLM")
        
        # 12. Preparar fontes para resposta
        sources = [
            {
                "content": result["content"][:200] + "..." if len(result["content"]) > 200 else result["content"],
                "similarity": round(result["similarity"], 3),
                "metadata": result.get("metadata", {})
            }
            for result in rag_results
        ]
        
        # 13. Gerar resposta com LLM
        # Preparar contexto combinado (RAG + Tool se necessário)
        combined_context = context_texts.copy() if context_texts else []
        
        # Adicionar dados da tool ao contexto se disponível
        if tool_result and tool_result.success and tool_result.data:
            tool_context = f"DADOS EM TEMPO REAL:\n{_format_tool_result(tool_result.data)}"
            combined_context.append(tool_context)
            logger.debug(f"Contexto combinado: RAG ({len(context_texts)} docs) + Tool (1 resultado)")
        
        if combined_context:
            # Usar contexto RAG + Tool + histórico da conversa (se follow-up)
            response_text = llm_service.generate_with_context(
                user_query=request.message,
                context=combined_context,
                query_type=query_type,
                conversation_history=context_manager.get_recent_messages(n=3) if is_follow_up else None
            )
        elif tool_result and tool_result.success:
            # Se apenas tool retornou dados (sem RAG), usar apenas tool
            response_text = llm_service.generate_with_context(
                user_query=request.message,
                context=[f"DADOS EM TEMPO REAL:\n{_format_tool_result(tool_result.data)}"],
                query_type=query_type,
                conversation_history=context_manager.get_recent_messages(n=3) if is_follow_up else None
            )
        else:
            # Usar conhecimento geral do LLM (sem contexto RAG/Tool)
            response_text = llm_service.generate_response(
                [
                    {
                        "role": "system",
                        "content": (
                            "Você é o Assistente Operacional da Treq. "
                            "Responda de forma útil e profissional. "
                            "Se a pergunta for sobre operações da Treq, "
                            "informe que precisa de mais contexto específico."
                        )
                    },
                    {
                        "role": "user",
                        "content": request.message
                    }
                ],
                query_type=query_type,
                query_text=request.message  # Passar query_text para detecção de tarefas pesadas
            )
        
        # 14. Adicionar mensagens ao histórico
        context_manager.add_message("user", request.message)
        context_manager.add_message("assistant", response_text)
        
        # 15. Logging do nível usado (para rastreabilidade no endpoint)
        logger.info(f"Resposta gerada - Query Type: {query_type}, Strategy: {strategy}")
        
        # 16. Retornar resposta
        return ChatResponse(
            response=response_text,
            conversation_id=request.conversation_id,
            context_summary=context_manager.get_context_summary(),
            sources=sources,
            strategy=strategy,
            tool_data=tool_result.data if tool_result and tool_result.success else None
        )
        
    except Exception as e:
        logger.error(f"Erro no endpoint de chat: {e}")
        import traceback
        logger.error(traceback.format_exc())
        raise HTTPException(status_code=500, detail=f"Erro ao processar chat: {str(e)}")


@router.get("/health")
async def health_check():
    """Health check do endpoint de chat."""
    return {"status": "ok", "service": "chat"}

