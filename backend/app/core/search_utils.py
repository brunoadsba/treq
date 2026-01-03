"""
Utilitários para busca RAG com threshold adaptativo e fallback.
"""
from typing import Dict, Any, Optional, List
from loguru import logger
from app.core.rag_service import RAGService
from app.core.tracing import trace_rag_pipeline


def get_adaptive_threshold(query_type: str, corpus_size: int = 45) -> float:
    """
    Calcula threshold adaptativo baseado no tamanho do corpus.
    
    Rationale:
    - Corpus pequeno (<100): thresholds mais baixos para aumentar recall
    - Corpus médio (100-500): thresholds moderados
    - Corpus grande (>500): thresholds padrão
    
    Args:
        query_type: Tipo da query (procedimento, alerta, etc)
        corpus_size: Tamanho atual do corpus de documentos
    
    Returns:
        float: Threshold recomendado para busca semântica
    """
    if corpus_size < 100:  # Corpus pequeno (nosso caso: 45 chunks)
        base_threshold = 0.30
        procedimento_boost = 0.05
    elif corpus_size < 500:  # Corpus médio
        base_threshold = 0.40
        procedimento_boost = 0.05
    else:  # Corpus grande
        base_threshold = 0.50
        procedimento_boost = 0.05
    
    # Procedimentos são mais específicos, aumenta threshold levemente
    if query_type == "procedimento":
        return base_threshold + procedimento_boost
    
    return base_threshold


def get_adaptive_top_k(query_type: str, initial_results: Optional[List] = None) -> int:
    """
    Calcula top_k adaptativo baseado no tipo de query.
    
    Fase 2: Top-k dinâmico ajustado conforme tipo de query.
    Queries mais complexas precisam de mais contexto.
    
    Args:
        query_type: Tipo da query (procedimento, detalhamento, etc.)
        initial_results: Resultados iniciais (opcional) para ajuste dinâmico
        
    Returns:
        int: Número de documentos a retornar
    """
    # Base top_k por tipo de query
    base_top_k = {
        "procedimento": 8,  # Precisa de mais contexto (passos completos)
        "detalhamento": 6,  # Precisa de contexto detalhado
        "causa": 6,  # Análise precisa de múltiplos documentos
        "status": 5,  # Status precisa de informações atuais
        "alerta": 4,  # Alertas são mais específicos
        "metrica": 3,  # Métricas são pontuais
        "geral": 5   # Padrão para queries genéricas
    }
    
    # Top-k base para o tipo de query
    top_k = base_top_k.get(query_type, 5)
    
    # Ajuste dinâmico: se similaridade inicial é baixa, aumentar top_k
    # para compensar e aumentar chance de encontrar documentos relevantes
    if initial_results and len(initial_results) > 0:
        first_similarity = initial_results[0].get('similarity', 1.0)
        if first_similarity < 0.75:
            # Se primeira similaridade é baixa, aumentar top_k
            top_k = min(top_k + 2, 10)  # Máximo 10 documentos
            logger.debug(
                f"Ajuste dinâmico: similaridade inicial baixa ({first_similarity:.2f}), "
                f"aumentando top_k de {base_top_k.get(query_type, 5)} para {top_k}"
            )
    
    return top_k


def search_with_fallback(
    query: str,
    query_type: str,
    rag_service: RAGService,
    top_k: int = 5,
    min_docs: int = 2,
    filters: Optional[Dict[str, Any]] = None
) -> tuple[list[dict], float]:
    """
    Busca com fallback automático de threshold.
    
    Estratégia:
    1. Tenta threshold inicial (adaptativo)
    2. Se retorna < min_docs, reduz threshold em 0.05
    3. Repete até encontrar min_docs ou atingir threshold mínimo (0.20)
    
    Args:
        query: Query do usuário
        query_type: Tipo da query
        rag_service: Instância do RAGService
        top_k: Número máximo de documentos
        min_docs: Número mínimo de documentos desejados
        filters: Filtros opcionais de metadata para busca
    
    Returns:
        tuple: (lista de documentos, threshold utilizado)
    """
    initial_threshold = get_adaptive_threshold(query_type)
    thresholds = [initial_threshold]
    
    # Gera lista de fallback thresholds (reduz 0.05 a cada tentativa)
    current = initial_threshold
    while current > 0.20:
        current -= 0.05
        thresholds.append(round(current, 2))
    
    logger.info(f"Iniciando busca com fallback. Thresholds: {thresholds} (filtros: {filters})")
    
    for threshold in thresholds:
        results = rag_service.search_similar(
            query=query,
            top_k=top_k,
            similarity_threshold=threshold,
            filters=filters  # Passar filtros para busca
        )
        
        logger.debug(f"Threshold {threshold:.2f}: {len(results)} documentos encontrados")
        
        if len(results) >= min_docs:
            logger.info(f"✅ Fallback bem-sucedido com threshold {threshold:.2f}")
            return results, threshold
    
    # Se nenhum threshold encontrou docs suficientes, retorna o melhor resultado
    final_results = rag_service.search_similar(
        query=query,
        top_k=top_k,
        similarity_threshold=0.20,
        filters=filters  # Passar filtros também no fallback final
    )
    
    logger.warning(
        f"⚠️ Fallback atingiu threshold mínimo (0.20). "
        f"Retornando {len(final_results)} documentos."
    )
    
    return final_results, 0.20


@trace_rag_pipeline(name="hybrid_search_with_fallback")
def search_hybrid_with_fallback(
    query: str,
    query_type: str,
    rag_service: RAGService,
    top_k: int = 5,
    min_docs: int = 2,
    filters: Optional[Dict[str, Any]] = None
) -> tuple[list[dict], float, str]:
    """
    Busca híbrida (vetorial + keyword) com fallback automático.
    
    Melhor para termos exatos como códigos de erro, nomes de peças, etc.
    
    Args:
        query: Query do usuário
        query_type: Tipo da query
        rag_service: Instância do RAGService
        top_k: Número máximo de documentos
        min_docs: Número mínimo de documentos desejados
        filters: Filtros opcionais de metadata
    
    Returns:
        tuple: (lista de documentos, threshold utilizado, tipo de busca)
    """
    initial_threshold = get_adaptive_threshold(query_type)
    
    logger.info(f"Iniciando busca híbrida para query_type: {query_type}")
    
    # Tentar busca híbrida primeiro
    try:
        results = rag_service.search_hybrid(
            query=query,
            top_k=top_k,
            similarity_threshold=initial_threshold,
            filters=filters
        )
        
        if len(results) >= min_docs:
            logger.info(f"✅ Busca híbrida bem-sucedida: {len(results)} docs")
            return results, initial_threshold, "hybrid"
        
        # Se não encontrou docs suficientes, tentar com threshold menor
        if len(results) < min_docs:
            lower_threshold = max(0.20, initial_threshold - 0.10)
            results = rag_service.search_hybrid(
                query=query,
                top_k=top_k,
                similarity_threshold=lower_threshold,
                filters=filters
            )
            
            if len(results) >= min_docs:
                logger.info(f"✅ Busca híbrida com threshold reduzido: {len(results)} docs")
                return results, lower_threshold, "hybrid"
        
        # Se ainda não encontrou, retornar o que temos
        if results:
            logger.info(f"⚠️ Busca híbrida retornou {len(results)} docs (menos que min_docs)")
            return results, initial_threshold, "hybrid"
            
    except Exception as e:
        logger.warning(f"Erro na busca híbrida, usando fallback vetorial: {e}")
    
    # Fallback para busca vetorial padrão
    results, threshold = search_with_fallback(
        query=query,
        query_type=query_type,
        rag_service=rag_service,
        top_k=top_k,
        min_docs=min_docs,
        filters=filters
    )
    
    return results, threshold, "vector"


def should_use_hybrid_search(query: str) -> bool:
    """
    Determina se a query deve usar busca híbrida.
    
    Híbrida é melhor para:
    - Códigos de erro (ex: "ERR-001", "E404")
    - Nomes técnicos (ex: "Parafuso Allen M5")
    - Siglas e abreviações
    - Queries curtas e específicas
    
    Args:
        query: Query do usuário
        
    Returns:
        bool: True se deve usar híbrida
    """
    import re
    
    # Padrões que indicam necessidade de busca exata
    patterns = [
        r'\b[A-Z]{2,5}-?\d{2,5}\b',  # Códigos como ERR-001, E404
        r'\b\d+[A-Za-z]+\b',  # Códigos alfanuméricos como 5W30, M5
        r'\b[A-Z]{2,}\b',  # Siglas em maiúsculo
    ]
    
    for pattern in patterns:
        if re.search(pattern, query):
            logger.debug(f"Query contém padrão para busca híbrida: {pattern}")
            return True
    
    # Queries de até 10 palavras se beneficiam de busca híbrida para garantir recall
    # Especialmente útil quando há mismatch de modelos de embedding
    word_count = len(query.split())
    if word_count <= 10:
        return True
    
    return False
