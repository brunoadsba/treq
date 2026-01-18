from loguru import logger
from langchain_core.messages import AIMessage
from ..state import AgentState
from ..tools.registry import ToolRegistry
from app.core.audit import log_mutation


async def executor_node(state: AgentState) -> dict:
    """
    Executa o plano de ação gerado pelo Planner com argumentos dinâmicos.
    """
    logger.info("🔧 EXECUTOR: Iniciando execução do plano...")
    
    decision = state.get('current_decision')
    if not decision or not decision.plan:
        logger.warning("🔧 EXECUTOR: Nenhum plano encontrado para execução.")
        return {
            "tool_outputs": [],
            "messages": [AIMessage(content="Entendi que precisava agir, mas meu planejamento de ferramentas está vazio.")]
        }

    tool_outputs = state.get('tool_outputs', [])
    execution_trace = state.get('execution_trace', [])
    messages = []

    # 1. Processar cada passo do plano
    for step in decision.plan:
        tool_name = step.tool_name
        logger.info(f"🔧 EXECUTOR: Executando {tool_name}...")
        
        tool = ToolRegistry.get_tool_by_name(tool_name)
        if not tool:
            logger.error(f"❌ EXECUTOR: Ferramenta {tool_name} não registrada.")
            execution_trace.append({"step": f"exec_{tool_name}", "status": "failed", "error": f"Tool {tool_name} not found"})
            continue

        # 2. Extrair argumentos do passo (Slot Filling)
        args_dict = {arg.name: arg.value for arg in step.arguments}
        logger.debug(f"🔧 EXECUTOR: Argumentos para {tool_name}: {args_dict}")

        try:
            # 3. Execução Real
            result = await tool.execute(**args_dict)
            
            tool_outputs.append({
                "tool": tool_name, 
                "result": result,
                "prefill": args_dict
            })
            execution_trace.append({
                "step": f"exec_{tool_name}",
                "status": "success",
                "output": result,
                "reasoning": step.reasoning,
                "prefill": args_dict
            })

            # 4. Log Auditoria da Mutação (RLS Seguro)
            log_mutation(
                user_id=state.get('user_id', 'unknown'),
                action=f"EXECUTE_TOOL_{tool_name.upper()}",
                resource="AGENT_TOOL",
                resource_id=tool_name,
                metadata={"args": args_dict, "result": result}
            )

            # Adicionar mensagem de confirmação para o usuário
            msg_text = result.get("message", f"Ação via {tool_name} concluída.")
            messages.append(AIMessage(content=msg_text))

        except Exception as e:
            logger.error(f"❌ EXECUTOR: Falha ao executar {tool_name} - {e}")
            tool_outputs.append({
                "tool": tool_name,
                "status": "error",
                "error": str(e),
                "prefill": args_dict
            })
            execution_trace.append({
                "step": f"exec_{tool_name}", 
                "status": "failed", 
                "error": str(e),
                "prefill": args_dict
            })
            messages.append(AIMessage(content=f"Tive um problema ao rodar a ferramenta {tool_name}: {str(e)}"))

    return {
        "tool_outputs": tool_outputs,
        "execution_trace": execution_trace,
        "messages": messages
    }
