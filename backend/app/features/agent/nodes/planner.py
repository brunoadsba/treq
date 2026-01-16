"""
Planner Node - Decide a próxima ação do agente.

Analisa a query do usuário e decide:
- call_rag: Buscar informações na base de conhecimento
- call_tool: Executar uma ferramenta externa (Jira, Slack)
- respond: Responder diretamente (perguntas simples)
"""

from loguru import logger
from ..state import AgentState


async def planner_node(state: AgentState) -> dict:
    """
    Decide se a query precisa de RAG, Tool ou Resposta Direta.
    
    Args:
        state: Estado atual do agente
        
    Returns:
        dict com next_action definido
    """
    logger.info("🧠 PLANNER: Analisando query...")
    
    last_message = state['messages'][-1].content.lower()
    
    # Lógica de decisão baseada em keywords
    # TODO: Substituir por LLM call na Sprint 1.1.3
    tool_keywords = ["ticket", "jira", "criar ticket", "abrir chamado"]
    slack_keywords = ["notificar", "slack", "avisar equipe", "enviar mensagem"]
    
    if any(kw in last_message for kw in tool_keywords):
        logger.info("🔧 PLANNER: Decisão -> call_tool (Jira)")
        return {"next_action": "call_tool"}
    
    if any(kw in last_message for kw in slack_keywords):
        logger.info("📢 PLANNER: Decisão -> call_tool (Slack)")
        return {"next_action": "call_tool"}
    
    # Default: buscar no RAG
    logger.info("📚 PLANNER: Decisão -> call_rag")
    return {"next_action": "call_rag"}
