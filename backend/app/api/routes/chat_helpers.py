"""
Funções auxiliares para processamento de chat.
Extraídas de chat.py para melhor organização e manutenibilidade.
"""
from loguru import logger

from app.core.search_utils import get_adaptive_top_k, search_with_fallback
from app.core.query_router import should_use_tool_first, should_use_rag_first
from app.core.tools import MetricsTool
from app.core.param_extractor import extract_tool_params
from app.utils.pii_anonymizer import anonymize_pii
from typing import List, Dict, Any, Optional, Tuple, TYPE_CHECKING

if TYPE_CHECKING:
    from app.services.llm_service import LLMService
    from app.core.rag_service import RAGService
    from app.core.context_manager import ContextManager


def get_or_create_context_manager(
    user_id: str,
    conversation_id: Optional[str],
    context_cache: Dict[str, 'ContextManager']
) -> 'ContextManager':
    """
    Obtém ou cria um ContextManager para a conversa.
    
    Args:
        user_id: ID do usuário
        conversation_id: ID da conversa (opcional)
        context_cache: Cache de context managers
        
    Returns:
        ContextManager: Gerenciador de contexto da conversa
    """
    cache_key = f"{user_id}:{conversation_id or 'default'}"
    if cache_key not in context_cache:
        context_cache[cache_key] = ContextManager(user_id=user_id)
        logger.debug(f"ContextManager criado para: {cache_key}")
    else:
        logger.debug(f"ContextManager recuperado para: {cache_key} (histórico: {len(context_cache[cache_key].message_history)} mensagens)")
    
    return context_cache[cache_key]


def process_entities_and_context(
    request_message: str,
    request_context: Optional[Dict[str, Any]],
    context_manager: 'ContextManager'
) -> Dict[str, Any]:
    """
    Processa entidades e contexto da requisição.
    
    Args:
        request_message: Mensagem do usuário
        request_context: Contexto adicional da requisição
        context_manager: Gerenciador de contexto
        
    Returns:
        Dict com entidades extraídas
    """
    # Extrair entidades automaticamente da query
    entities = context_manager.extract_entities(request_message)
    
    if entities.get("unit"):
        context_manager.update_unit(entities["unit"])
    if entities.get("period"):
        context_manager.update_period(
            entities["period"]["month"],
            entities["period"]["year"]
        )
    
    # Atualizar contexto se fornecido explicitamente (sobrescreve extração automática)
    if request_context:
        if "unit" in request_context:
            context_manager.update_unit(request_context["unit"])
        if "period" in request_context:
            period = request_context["period"]
            context_manager.update_period(
                period.get("month", 12),
                period.get("year", 2024)
            )
    
    return entities


def build_llm_messages(
    request_message: str,
    query_type: str,
    combined_context: List[str],
    is_follow_up: bool,
    llm_service: 'LLMService',
    context_manager: 'ContextManager'
) -> List[Dict[str, str]]:
    """
    Constrói mensagens para o LLM com contexto e histórico.
    
    Args:
        request_message: Mensagem do usuário
        query_type: Tipo da query
        combined_context: Contexto combinado (RAG + tools)
        is_follow_up: Se é follow-up
        llm_service: Serviço LLM
        context_manager: Gerenciador de contexto
        
    Returns:
        Lista de mensagens formatadas para o LLM
    """
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
    
    # Anonimizar PII antes de enviar para LLM
    anonymized_message, pii_stats = anonymize_pii(request_message)
    if pii_stats.get("replaced", 0) > 0:
        logger.info(
            f"PII anonimizado antes de enviar para LLM: "
            f"{pii_stats['replaced']} ocorrência(s) de {', '.join(pii_stats['types'].keys())}"
        )
    
    # Construir conteúdo do usuário com contexto (usando mensagem anonimizada)
    if combined_context:
        # IMPORTANTE: Não adicionar "Documento X:" antes do contexto
        # O LLM está proibido de mencionar documentos, então não devemos incluir essas referências no contexto
        context_text = "\n\n---\n\n".join(combined_context)
        
        # Instruções aprimoradas para consultorias (reforço das regras)
        extraction_instructions = ""
        if query_type == "consultoria":
            extraction_instructions = """

INSTRUÇÕES DE EXECUÇÃO (OBRIGATÓRIO):
1. EXTRAÇÃO OBRIGATÓRIA: O contexto acima contém TODAS as informações disponíveis. Você DEVE extrair números, listas, categorias e percentuais mencionados LITERALMENTE.
2. FORMATO: Use **PROBLEMA IDENTIFICADO:** seguido de **SOLUÇÃO PROPOSTA:**.
3. BUSCA AMPLA: Se o contexto menciona unidades/regiões diferentes da solicitada, APRESENTE essas informações como contexto relacionado. Busque variações de termos (ex: "Recife" = "NE-Recife" = "Recife/PE").
4. ❌ PROIBIDO REFERENCIAR DOCUMENTOS: NUNCA escreva "Documento X", "Documento Y", "Documento 1", "Documento 2" ou qualquer referência a documentos. O contexto NÃO contém cabeçalhos de documentos. Apresente o conteúdo diretamente.
5. ❌ PROIBIDO SUGERIR ARQUIVOS EXTERNOS: Não sugira abrir CSVs, JSONs ou outros arquivos. Use APENAS o texto acima.
6. EXTRAIR DADOS: Copie números, percentuais e categorias EXATAMENTE como aparecem no contexto acima.
7. ❌ PROIBIDO DIZER "NÃO HÁ INFORMAÇÕES": NUNCA diga "não há informações" ou "infelizmente não há informações" sem antes apresentar TODAS as informações relacionadas que encontrar no contexto. Se houver informações sobre unidades similares, apresente-as.
8. APENAS diga "não há informações" se o contexto estiver COMPLETAMENTE vazio e sem nenhuma relação possível ao tópico.
"""
        
        user_content = f"""CONTEXTO DISPONÍVEL (Leia completamente antes de responder):
{context_text}
---{extraction_instructions}
PERGUNTA DO USUÁRIO:
{anonymized_message}

Responda usando APENAS as informações do contexto acima. NUNCA mencione "Documento X" ou qualquer referência a documentos."""
    else:
        user_content = anonymized_message
    
    messages.append({"role": "user", "content": user_content})
    
    return messages


async def fetch_context_and_tools(
    request_message: str,
    query_type: str,
    strategy: str,
    strategy_params: Dict[str, Any],
    entities: Dict[str, Any],
    search_query: str,
    is_follow_up: bool,
    rag_service: 'RAGService'
) -> Tuple[List[str], List[Dict[str, Any]], Optional[Any]]:
    """
    Busca contexto RAG e executa tools conforme estratégia.
    
    Args:
        request_message: Mensagem do usuário
        query_type: Tipo da query
        strategy: Estratégia de roteamento
        strategy_params: Parâmetros da estratégia
        entities: Entidades extraídas
        search_query: Query para busca RAG
        is_follow_up: Se é follow-up
        rag_service: Serviço RAG
        
    Returns:
        Tuple[combined_context, sources, tool_result]
    """
    should_use_rag = should_use_rag_first(query_type, strategy)
    should_use_tool = should_use_tool_first(query_type, strategy)
    
    tool_result = None
    if should_use_tool:
        if query_type in ["metrica_temporal", "status_temporal"] or "metric" in strategy_params.get("type", ""):
            metrics_tool = MetricsTool()
            tool_params = extract_tool_params(
                query=request_message,
                query_type=query_type,
                entities=entities
            )
            tool_result = await metrics_tool.execute(**tool_params)
            if not tool_result.success:
                should_use_rag = True
    
    rag_results = []
    context_texts = []
    sources = []
    
    if should_use_rag:
        from app.core.search_utils import should_use_hybrid_search, search_hybrid_with_fallback
        
        top_k = get_adaptive_top_k(query_type)
        
        # Usar busca híbrida para termos exatos ou queries curtas
        if should_use_hybrid_search(search_query):
            logger.debug(f"Usando busca híbrida para query: {search_query[:50]}...")
            rag_results, used_threshold, search_type = search_hybrid_with_fallback(
                query=search_query,
                query_type=query_type,
                rag_service=rag_service,
                top_k=top_k,
                min_docs=2,
                filters=None
            )
        else:
            # Busca vetorial padrão para queries longas/conversacionais
            rag_results, used_threshold = search_with_fallback(
                query=search_query,
                query_type=query_type,
                rag_service=rag_service,
                top_k=top_k,
                min_docs=2,
                filters=None
            )
            search_type = "vector"
        
        context_texts = [result["content"] for result in rag_results]
        sources = [
            {
                "content": result["content"][:200] + "..." if len(result["content"]) > 200 else result["content"],
                "similarity": round(result.get("similarity", result.get("score", 0.0)), 3),
                "metadata": result.get("metadata", {}),
                "search_type": result.get("search_type", search_type)
            }
            for result in rag_results
        ]
        logger.debug(f"RAG retornou {len(context_texts)} documentos (threshold: {used_threshold})")
        
        # Logging estruturado para consultoria (Problema 5)
        if query_type == "consultoria":
            context_quality = {
                "document_count": len(context_texts),
                "has_sufficient_context": len(context_texts) >= 2,
                "avg_similarity": round(
                    sum(s.get("similarity", 0.0) for s in sources) / len(sources) if sources else 0.0,
                    3
                ),
                "min_similarity": round(
                    min(s.get("similarity", 0.0) for s in sources) if sources else 0.0,
                    3
                )
            }
            logger.info(
                f"[CONSULTATION_LOG] Query: '{request_message[:100]}...' | "
                f"Context quality: {context_quality} | "
                f"Top-K: {top_k} | Threshold: {used_threshold}"
            )
    
    # Combinar contexto RAG + Tool
    combined_context = []
    if context_texts:
        combined_context.extend(context_texts)
    if tool_result and tool_result.success:
        combined_context.append(f"DADOS EM TEMPO REAL:\n{_format_tool_result(tool_result.data)}")
        logger.debug(f"Contexto combinado: RAG ({len(context_texts)} docs) + Tool (1 resultado)")
    
    return combined_context, sources, tool_result


def _format_tool_result(tool_data: Dict[str, Any]) -> str:
    """
    Formata resultado de tool para contexto do LLM.
    
    Args:
        tool_data: Dados retornados pela tool
        
    Returns:
        str: Texto formatado para contexto
    """
    if isinstance(tool_data, dict):
        parts = []
        if "metric_name" in tool_data:
            parts.append(f"Métrica: {tool_data['metric_name']}")
        if "value" in tool_data:
            parts.append(f"Valor: {tool_data['value']}")
        if "count" in tool_data:
            parts.append(f"Total de registros: {tool_data['count']}")
        return "\n".join(parts) if parts else str(tool_data)
    return str(tool_data)
