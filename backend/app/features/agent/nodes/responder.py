"""
Responder Node - Gera a resposta final para o usuário.

Combina contexto do RAG e outputs de ferramentas para gerar resposta.
"""

from loguru import logger
from langchain_core.messages import AIMessage
from ..state import AgentState
from app.services.llm_clients import stream_groq


async def responder_node(state: AgentState) -> dict:
    """
    Gera a resposta final combinando contexto e tool outputs.
    
    Args:
        state: Estado atual do agente
        
    Returns:
        dict com mensagem de resposta final
    """
    logger.info("💬 RESPONDER: Gerando resposta final...")
    
    context = state.get('context', [])
    tool_outputs = state.get('tool_outputs', [])
    user_query = state['messages'][0].content
    
    # Construir prompt baseado no que temos
    if tool_outputs:
        # Ação foi executada via ferramenta
        tool_result = tool_outputs[-1].get('result', {})
        response = f"Ação realizada: {tool_result.get('message', 'Operação concluída')}"
        
    elif context:
        # Resposta baseada em RAG
        context_text = "\n".join(context[:3])  # Top 3 documentos
        response = f"Com base na documentação:\n\n{context_text[:500]}..."
        
    else:
        response = "Não encontrei informações relevantes para sua pergunta."
    
    logger.info("💬 RESPONDER: Resposta gerada")
    
    return {
        "messages": [AIMessage(content=response)]
    }
