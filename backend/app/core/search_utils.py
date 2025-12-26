"""
Utilitários para busca RAG com threshold adaptativo e fallback.
"""
from typing import Dict, Any, Optional
from loguru import logger
from app.core.rag_service import RAGService


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

