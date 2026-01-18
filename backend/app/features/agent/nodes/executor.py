"""
Executor Node - Executa ferramentas externas.

Invoca ferramentas como Jira, Slack baseado na decisão do Planner.
"""

from loguru import logger
from langchain_core.messages import AIMessage
from ..state import AgentState
from ..tools.registry import ToolRegistry
from app.core.audit import log_mutation


async def executor_node(state: AgentState) -> dict:
    """
    Executa a ferramenta apropriada baseado no contexto.
    
    Args:
        state: Estado atual do agente
        
    Returns:
        dict com tool_outputs preenchido
    """
    logger.info("🔧 EXECUTOR: Executando ferramenta...")
    
    last_message = state['messages'][-1].content
    tool_outputs = []
    
    # 1. Detectar Ferramenta via Registry (SSOT)
    tool_name = ToolRegistry.detect_tool(last_message)
    
    if tool_name:
        tool = ToolRegistry.get_tool_by_name(tool_name)
        if tool:
            logger.info(f"🔧 EXECUTOR: Ferramenta detectada -> {tool.name}")
            
            # TODO: Usar LLM para extração de argumentos na Sprint 2.4
            # Por enquanto, fallback para argumentos padrão/heurísticos
            result = None
            
            if tool.name == "jira_create_ticket":
                result = await tool.execute(
                    summary="Ticket criado via Treq Agent",
                    description=last_message
                )
            elif tool.name == "slack_notify":
                result = await tool.execute(
                    channel="#geral",  # Hardcoded por enquanto
                    message=last_message
                )
                
            if result:
                tool_outputs.append({"tool": tool.name, "result": result})
    else:
        logger.warning(f"🔧 EXECUTOR: Nenhuma ferramenta correspondente encontrada para: {last_message[:20]}...")
    
    # ... Resto da função permanece igual ...

    
    if tool_outputs:
        result_msg = tool_outputs[0]["result"].get("message", "Ação executada")
        logger.info(f"🔧 EXECUTOR: {result_msg}")
        
        # Log Auditoria da Mutaçao
        log_mutation(
            user_id=state.get('user_id', 'unknown'),
            action=f"EXECUTE_TOOL_{tool_outputs[0]['tool'].upper()}",
            resource="AGENT_TOOL",
            resource_id=tool_outputs[0]['tool'],
            metadata={"result": result_msg}
        )
        
        return {
            "tool_outputs": tool_outputs,
            "messages": [AIMessage(content=result_msg)]
        }
    
    return {
        "tool_outputs": [],
        "messages": [AIMessage(content="Nenhuma ferramenta executada.")]
    }
