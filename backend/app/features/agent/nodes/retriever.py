from loguru import logger
from langchain_core.messages import AIMessage
from ..state import AgentState
from ..tools.knowledge import search_knowledge_base

async def retriever_node(state: AgentState) -> dict:
    """
    Executa busca RAG usando a tool search_knowledge_base.
    """
    logger.info("📚 RETRIEVER: Buscando documentos...")
    
    query = state['messages'][-1].content
    
    try:
        # Invoca a ferramenta passando o user_id do estado
        result = search_knowledge_base.invoke({
            "query": query,
            "user_id": state.get("user_id", "anonymous")
        })
        
        # A ferramenta retorna uma string formatada
        # Podemos separar em lista se quisermos manter a estrutura de 'context' como List[str]
        # Por enquanto, vamos colocar o resultado inteiro como um item de contexto
        context = [result]
        
        logger.info(f"📚 RETRIEVER: Busca concluída.")
        
        return {
            "context": context,
            "documents_retrieved": [query], # Rastreia que buscamos essa query
            "steps_taken": state.get("steps_taken", 0) + 1
        }
        
    except Exception as e:
        logger.error(f"❌ RETRIEVER: Erro na busca - {e}")
        return {
            "context": [],
        }
