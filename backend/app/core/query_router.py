"""
Query Router: Decide entre Tool-First vs RAG-First vs Hybrid.

Baseado no documento rag-dicas-claude.md, implementa roteamento inteligente
para determinar a melhor estratégia de execução para cada query.
"""
import re
from typing import Dict, Any, Tuple
from loguru import logger


def route_query(query: str, query_type: str) -> Tuple[str, Dict[str, Any]]:
    """
    Classifica query e decide entre Tool-First ou RAG-First.
    
    Princípio Central: "Se a pergunta pode ser respondida verificando um sistema,
    verifique o sistema. Não consulte documentos."
    
    Args:
        query: Texto da query do usuário
        query_type: Tipo da query já classificada pelo query_classifier
        
    Returns:
        tuple: (strategy, params)
            strategy: "tool_first" | "rag_first" | "hybrid"
            params: parâmetros específicos da estratégia
    """
    query_lower = query.lower().strip()
    
    # Patterns para Tool-First (dados em tempo real)
    TOOL_FIRST_PATTERNS = [
        # Métricas em tempo real
        (r"quantos?\s+\w+\s+(hoje|agora|atualmente)", "metric_query"),
        (r"qual\s+(o\s+)?status\s+(do|da)", "status_query"),
        (r"(há|existe|tem)\s+\w+\s+(ativo|pendente|aberto)", "existence_query"),
        
        # Queries temporais explícitas
        (r"(hoje|essa semana|este mês|agora)", "temporal_query"),
        
        # Identificadores específicos
        (r"(pedido|cliente|filial)\s+#?\d+", "entity_query"),
    ]
    
    # Patterns para RAG-First (conhecimento estático)
    RAG_FIRST_PATTERNS = [
        # Procedimentos
        (r"como\s+(fazer|executar|realizar)", "procedure_query"),
        (r"(passo a passo|procedimento|protocolo)", "procedure_query"),
        
        # Políticas
        (r"qual\s+(o|a)\s+(threshold|sla|política)", "policy_query"),
        (r"quando\s+(devemos|devo)\s+", "policy_query"),
        
        # Explicações
        (r"(o que significa|definição|conceito)", "explanation_query"),
        (r"(por que|porque)\s+", "explanation_query"),
        
        # Análise
        (r"(causas|motivos|razões)\s+(de|para)", "analysis_query"),
    ]
    
    # 1. Verificar tipos temporais do classificador (prioridade máxima)
    if query_type in ["metrica_temporal", "status_temporal"]:
        logger.debug(f"Query router: TOOL_FIRST (tipo temporal detectado: {query_type})")
        return "tool_first", {
            "type": query_type,
            "reason": "temporal_query_type",
            "requires_realtime_data": True
        }
    
    # 2. Verificar padrões Tool-First
    for pattern, query_type_pattern in TOOL_FIRST_PATTERNS:
        if re.search(pattern, query_lower):
            logger.debug(f"Query router: TOOL_FIRST (pattern: {pattern})")
            return "tool_first", {
                "type": query_type_pattern,
                "pattern": pattern,
                "requires_realtime_data": True
            }
    
    # 3. Verificar padrões RAG-First
    for pattern, query_type_pattern in RAG_FIRST_PATTERNS:
        if re.search(pattern, query_lower):
            logger.debug(f"Query router: RAG_FIRST (pattern: {pattern})")
            return "rag_first", {
                "type": query_type_pattern,
                "pattern": pattern,
                "requires_knowledge": True
            }
    
    # 4. Verificar se é query de comparação (threshold vs valor atual)
    comparison_patterns = [
        r"estamos\s+(acima|abaixo|dentro|fora)\s+",
        r"(acima|abaixo|dentro|fora)\s+do\s+threshold",
        r"threshold\s+(de|para)",
        r"comparar\s+",
    ]
    for pattern in comparison_patterns:
        if re.search(pattern, query_lower):
            logger.debug(f"Query router: HYBRID (comparison pattern: {pattern})")
            return "hybrid", {
                "type": "comparison_query",
                "pattern": pattern,
                "requires_knowledge": True,
                "requires_realtime_data": True
            }
    
    # 5. Default: RAG-First (conhecimento estático)
    logger.debug(f"Query router: RAG_FIRST (default)")
    return "rag_first", {
        "type": "general",
        "reason": "default_strategy"
    }


def should_use_tool_first(query_type: str, strategy: str) -> bool:
    """
    Verifica se deve usar Tool-First baseado no tipo e estratégia.
    
    Args:
        query_type: Tipo da query classificada
        strategy: Estratégia retornada pelo router
        
    Returns:
        bool: True se deve usar Tool-First
    """
    # Tipos temporais sempre requerem Tool-First
    if query_type in ["metrica_temporal", "status_temporal"]:
        return True
    
    # Estratégia Tool-First ou Hybrid
    if strategy in ["tool_first", "hybrid"]:
        return True
    
    return False


def should_use_rag_first(query_type: str, strategy: str) -> bool:
    """
    Verifica se deve usar RAG-First baseado no tipo e estratégia.
    
    Args:
        query_type: Tipo da query classificada
        strategy: Estratégia retornada pelo router
        
    Returns:
        bool: True se deve usar RAG-First
    """
    # Tipos que sempre requerem conhecimento
    if query_type in ["procedimento", "alerta", "detalhamento"]:
        return True
    
    # Estratégia RAG-First ou Hybrid
    if strategy in ["rag_first", "hybrid"]:
        return True
    
    return False

