"""
Executor Node - Executa ferramentas externas.

Invoca ferramentas como Jira, Slack baseado na decisão do Planner.
"""

from loguru import logger
from langchain_core.messages import AIMessage
from ..state import AgentState
from ..tools import JiraCreateTicketTool, SlackSendMessageTool


async def executor_node(state: AgentState) -> dict:
    """
    Executa a ferramenta apropriada baseado no contexto.
    
    Args:
        state: Estado atual do agente
        
    Returns:
        dict com tool_outputs preenchido
    """
    logger.info("🔧 EXECUTOR: Executando ferramenta...")
    
    last_message = state['messages'][-1].content.lower()
    tool_outputs = []
    
    # Detectar qual ferramenta usar
    if "jira" in last_message or "ticket" in last_message:
        tool = JiraCreateTicketTool()
        result = await tool.execute(
            summary=f"Ticket criado via Treq Agent",
            description=state['messages'][-1].content
        )
        tool_outputs.append({"tool": tool.name, "result": result})
        
    elif "slack" in last_message or "notificar" in last_message:
        tool = SlackSendMessageTool()
        result = await tool.execute(
            channel="#geral",
            message=state['messages'][-1].content
        )
        tool_outputs.append({"tool": tool.name, "result": result})
    
    if tool_outputs:
        result_msg = tool_outputs[0]["result"].get("message", "Ação executada")
        logger.info(f"🔧 EXECUTOR: {result_msg}")
        return {
            "tool_outputs": tool_outputs,
            "messages": [AIMessage(content=result_msg)]
        }
    
    return {
        "tool_outputs": [],
        "messages": [AIMessage(content="Nenhuma ferramenta executada.")]
    }
