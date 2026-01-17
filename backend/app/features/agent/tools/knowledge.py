from typing import Annotated
from langchain_core.tools import tool
from loguru import logger
from app.core.vector_store import get_vector_store

@tool
def search_knowledge_base(query: str) -> str:
    """
    Busca informações relevantes na base de conhecimento do TREQ sobre documentos, processos ou dados da empresa.
    Use esta ferramenta quando precisar de informações factuais ou contexto que não está no histórico da conversa.
    
    Args:
        query: A pergunta ou termo de busca para encontrar informações.
    """
    logger.info(f"🔎 Buscando na knowledge base: '{query}'")
    
    try:
        vector_store = get_vector_store()
        
        # Busca por similaridade com score
        results = vector_store.similarity_search_with_score(query, k=4)
        
        if not results:
            return "Nenhuma informação relevante encontrada na base de conhecimento."
            
        formatted_results = []
        for doc, score in results:
            source = doc.metadata.get("source", "Desconhecido")
            page = doc.metadata.get("page", "?")
            
            # Filtra resultados muito ruins se o score for de distância (menor é melhor para L2/Cosine em algumas implementações, 
            # mas langchain-postgres geralmente retorna similaridade ou distância dependendo da config.
            # Assumindo padrão do langchain: Cosine Similarity, onde 1.0 é idêntico. 
            # Se for Euclidean Distance, 0.0 é idêntico.
            # Vamos apenas formatar por enquanto.
            
            content = doc.page_content
            formatted_results.append(f"--- Fonte: {source} (Página {page}) ---\n{content}\n")
            
        return "\n".join(formatted_results)
        
    except Exception as e:
        logger.error(f"Erro na busca vetorial: {e}")
        return f"Erro ao acessar base de conhecimento: {str(e)}"
