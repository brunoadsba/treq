from typing import Optional, Any, Dict
# Lazy imports para economizar memória no startup

# Instâncias singleton dos serviços
_llm_service: Optional[LLMService] = None
_rag_service: Optional[RAGService] = None
_visualization_service: Optional[Any] = None

# Cache de ContextManager por conversa
# Nota: Em produção, idealmente usar Redis ou similar
_context_cache: Dict[str, ContextManager] = {}

def get_llm_service():
    """Retorna instância singleton do LLM Service."""
    global _llm_service
    if _llm_service is None:
        from app.services.llm_service import LLMService
        _llm_service = LLMService()
    return _llm_service


def get_rag_service():
    """Retorna instância singleton do RAG Service."""
    global _rag_service
    if _rag_service is None:
        from app.core.rag_service import RAGService
        _rag_service = RAGService()
    return _rag_service


def get_visualization_service():
    """Retorna instância singleton do Visualization Service."""
    global _visualization_service
    if _visualization_service is None:
        from app.services.visualization_service import VisualizationService
        _visualization_service = VisualizationService()
    return _visualization_service

def get_context_cache() -> Dict[str, ContextManager]:
    """Retorna a referência ao cache de contextos."""
    return _context_cache
