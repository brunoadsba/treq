from typing import Annotated
from langchain_core.tools import tool
from loguru import logger
from app.core.vector_store import get_vector_store

@tool
def search_knowledge_base(query: str, user_id: str = "anonymous") -> str:
    """
    Busca informações relevantes na base de conhecimento do TREQ sobre documentos, processos ou dados da empresa.
    
    Args:
        query: A pergunta ou termo de busca para encontrar informações.
        user_id: ID do usuário para filtragem de dados (fornecido pelo Agente).
    """
    logger.info(f"🔎 Buscando na knowledge base para user '{user_id}': '{query}'")
    
    try:
        vector_store = get_vector_store()
        
        # Filtro de metadados para garantir RLS no nível de aplicação (além do banco)
        search_filter = {"user_id": user_id} if user_id != "anonymous" else {}
        
        # Busca por similaridade com score e filtro
        results = vector_store.similarity_search_with_score(
            query, 
            k=4,
            filter=search_filter
        )
        
        if not results:
            # Retorno padronizado para o Planner detectar falha e tentar self-correction
            logger.info("⚠️ Busca retornou vazio.")
            return "SEARCH_EMPTY: Nenhuma informação relevante encontrada na base de conhecimento."
            
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
