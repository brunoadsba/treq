"""
Planner Node - Decide a próxima ação do agente.

Analisa a query do usuário e decide:
- call_rag: Buscar informações na base de conhecimento
- call_tool: Executar uma ferramenta externa (Jira, Slack)
- respond: Responder diretamente (perguntas simples)
"""

from loguru import logger
from ..state import AgentState


from ..tools.registry import ToolRegistry


async def planner_node(state: AgentState) -> dict:
    """
    Decide se a query precisa de RAG, Tool ou Resposta Direta.
    
    Args:
        state: Estado atual do agente
        
    Returns:
        dict com next_action definido
    """
    logger.info("🧠 PLANNER: Analisando query...")
    
    last_message = state['messages'][-1].content
    
    # Detecção dinâmica de intenção via Registry
    detected_tool = ToolRegistry.detect_tool(last_message)
    
    if detected_tool:
        logger.info(f"🔧 PLANNER: Decisão -> call_tool ({detected_tool})")
        return {"next_action": "call_tool"}
    
    # Default: buscar no RAG
    logger.info("📚 PLANNER: Decisão -> call_rag")
    return {"next_action": "call_rag"}
