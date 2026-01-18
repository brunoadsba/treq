"""
Agent Routes - Endpoints para o Agente Enterprise.

Rota paralela ao /chat/ existente, usando LangGraph.
"""

from fastapi import APIRouter, HTTPException, Depends, Request
from pydantic import BaseModel
from typing import Optional, List, Dict, Any, Literal
from loguru import logger
from langchain_core.messages import HumanMessage

from app.core.dependencies import get_current_user
from app.middleware.rate_limiter import rate_limit
from app.core.governance import get_trace_config
from .state import AgentState
from .graph import create_agent_graph, LANGGRAPH_AVAILABLE


router = APIRouter(prefix="/agent", tags=["Agent Enterprise"])


class AgentChatRequest(BaseModel):
    """Request para o chat do agente."""
    query: str
    thread_id: Optional[str] = None


class ToolExecutionRequest(BaseModel):
    """Request para execução manual de uma ferramenta."""
    tool_name: str
    arguments: Dict[str, Any]
    thread_id: Optional[str] = None
    

class AgentChatResponse(BaseModel):
    """Response do endpoint de chat do agente."""
    response: str
    context_count: int
    tools_used: List[str]
    tool_outputs: List[Dict[str, Any]]
    flow: List[str]
    thread_id: str
    thought: Optional[str] = None
    response_mode: Literal["text", "tool", "hybrid"] = "text"

@router.post("/chat", response_model=AgentChatResponse)
async def agent_chat(
    request: AgentChatRequest,
    current_user_id: str = Depends(get_current_user),
    _: None = Depends(rate_limit("10/minute"))
):
    """
    Endpoint de chat usando o Agente LangGraph com capacidades cognitivas.
    """
    if not LANGGRAPH_AVAILABLE:
        raise HTTPException(
            status_code=503,
            detail="Agente não disponível. LangGraph não instalado."
        )
    
    logger.info(f"🤖 Agent Chat: {request.query[:50]}...")
    
    try:
        # Criar estado inicial ou carregar se thread_id existir
        user_id = current_user_id
        initial_state: AgentState = {
            "messages": [HumanMessage(content=request.query)],
            "user_id": user_id,
            "context": [],
            "next_action": "",
            "tool_outputs": [],
            "metadata": {},
            "steps_taken": 0,
            "documents_retrieved": [],
            "current_decision": None,
            "execution_trace": [],
            "retry_count": 0,
            "max_retries": 3,
            "response_mode": "text"
        }
        
        # Configuração de Tracing (LangSmith) e Checkpointing (LangGraph)
        thread_id = request.thread_id or f"th_{user_id}"
        trace_config = get_trace_config(user_id=user_id, thread_id=thread_id)
        
        # Compilar e executar grafo com tracing
        graph = create_agent_graph()
        final_state = await graph.ainvoke(initial_state, config=trace_config)
        
        # Extrair resposta e metadados cognitivos
        response_text = final_state["messages"][-1].content
        context_count = len(final_state.get("context", []))
        tool_outputs = final_state.get("tool_outputs", [])
        tools_used = [t["tool"] for t in tool_outputs]
        
        # Determinar fluxo executado
        flow = ["planner"]
        next_action = final_state.get("next_action")
        if next_action in ["retriever", "executor"]:
            flow.append(next_action)
        flow.append("responder")
        
        # Extrair raciocínio consolidado
        thought = final_state.get("current_decision").thought if final_state.get("current_decision") else None
        
        logger.info(f"✅ Agent Chat concluído. Fluxo: {' -> '.join(flow)}")
        
        mode = final_state.get("response_mode", "text")
        
        return AgentChatResponse(
            response=response_text if mode != "tool" else "",
            context_count=context_count,
            tools_used=tools_used,
            tool_outputs=tool_outputs,
            flow=flow,
            thread_id=thread_id,
            thought=thought,
            response_mode=mode
        )
        
    except Exception as e:
        logger.error(f"❌ Erro no Agent Chat: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/tools/execute")
async def agent_tool_execute(
    request: ToolExecutionRequest,
    current_user_id: str = Depends(get_current_user),
    _: None = Depends(rate_limit("20/minute"))
):
    """
    Endpoint para execução manual de ferramentas do agente (via Modais).
    """
    from .tools.registry import ToolRegistry
    from app.core.audit import log_mutation
    
    logger.info(f"🔧 Manual Tool Execution: {request.tool_name}")
    
    tool = ToolRegistry.get_tool_by_name(request.tool_name)
    if not tool:
        raise HTTPException(status_code=404, detail=f"Ferramenta {request.tool_name} não encontrada.")
    
    try:
        # Executar ferramenta com os argumentos revisados
        result = await tool.execute(**request.arguments)
        
        # Log Auditoria da Mutação (RLS)
        log_mutation(
            user_id=current_user_id,
            action=f"MANUAL_EXECUTE_TOOL_{request.tool_name.upper()}",
            resource="AGENT_TOOL_MANUAL",
            resource_id=request.tool_name,
            metadata={"args": request.arguments, "result": result, "thread_id": request.thread_id}
        )
        
        return {
            "success": True,
            "data": result,
            "message": result.get("message", "Ação concluída com sucesso.")
        }
        
    except Exception as e:
        logger.error(f"❌ Erro na execução manual da ferramenta {request.tool_name}: {e}")
        return {
            "success": False,
            "message": f"Erro ao executar ferramenta: {str(e)}"
        }


@router.get("/health")
async def agent_health():
    """Verifica se o agente está disponível."""
    return {
        "status": "ok" if LANGGRAPH_AVAILABLE else "degraded",
        "langgraph_available": LANGGRAPH_AVAILABLE,
        "version": "1.0.0-enterprise"
    }
