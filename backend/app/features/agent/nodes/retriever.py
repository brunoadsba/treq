"""
Retriever Node - Busca informações na base de conhecimento.

Integra com o RAGService existente, preservando o RLS via user_id.
"""

from loguru import logger
from langchain_core.messages import AIMessage
from ..state import AgentState
from app.core.rag_service import RAGService


# Instância singleton do RAGService
_rag_service = None


def get_rag_service() -> RAGService:
    """Lazy initialization do RAGService."""
    global _rag_service
    if _rag_service is None:
        _rag_service = RAGService()
    return _rag_service


async def retriever_node(state: AgentState) -> dict:
    """
    Executa busca RAG usando o RAGService existente.
    
    O user_id do state garante que o RLS seja aplicado.
    
    Args:
        state: Estado atual do agente
        
    Returns:
        dict com context preenchido
    """
    logger.info("📚 RETRIEVER: Buscando documentos...")
    
    query = state['messages'][-1].content
    user_id = state.get('user_id')
    
    rag_service = get_rag_service()
    
    try:
        results = await rag_service.search_similar(
            query=query,
            user_id=user_id,
            top_k=5
        )
        
        context = [doc['content'] for doc in results]
        
        logger.info(f"📚 RETRIEVER: {len(context)} documentos encontrados")
        
        return {
            "context": context,
            "messages": [AIMessage(content=f"Encontrei {len(context)} documentos relevantes.")]
        }
        
    except Exception as e:
        logger.error(f"❌ RETRIEVER: Erro na busca - {e}")
        return {
            "context": [],
            "messages": [AIMessage(content="Não consegui buscar informações no momento.")]
        }
