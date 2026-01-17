"""
Agent Routes - Endpoints para o Agente Enterprise.

Rota paralela ao /chat/ existente, usando LangGraph.
"""

from fastapi import APIRouter, HTTPException, Depends, Request
from pydantic import BaseModel
from typing import Optional, List
from loguru import logger
from langchain_core.messages import HumanMessage

from app.middleware.simple_auth import verify_api_key
from app.middleware.rate_limiter import rate_limit
from app.core.governance import get_trace_config
from .state import AgentState
from .graph import create_agent_graph, LANGGRAPH_AVAILABLE


router = APIRouter(prefix="/agent", tags=["Agent Enterprise"])


class AgentChatRequest(BaseModel):
    """Request para o endpoint de chat do agente."""
    query: str
    user_id: Optional[str] = None
    thread_id: Optional[str] = None
    

class AgentChatResponse(BaseModel):
    """Response do endpoint de chat do agente."""
    response: str
    context_count: int
    tools_used: List[str]
    flow: List[str]

@router.post("/chat", response_model=AgentChatResponse)
async def agent_chat(
    request: AgentChatRequest,
    req: Request,
    api_key: str = Depends(verify_api_key),
    _: None = Depends(rate_limit("10/minute"))
):
    """
    Endpoint de chat usando o Agente LangGraph.
    
    Fluxo: Planner -> (RAG | Tool) -> Responder
    
    Args:
        request: Query e user_id
        api_key: API Key validada
        
    Returns:
        Resposta do agente com metadados do fluxo
    """
    if not LANGGRAPH_AVAILABLE:
        raise HTTPException(
            status_code=503,
            detail="Agente não disponível. LangGraph não instalado."
        )
    
    logger.info(f"🤖 Agent Chat: {request.query[:50]}...")
    
    try:
        # Criar estado inicial
        user_id = request.user_id or "anonymous"
        initial_state: AgentState = {
            "messages": [HumanMessage(content=request.query)],
            "user_id": user_id,
            "context": [],
            "next_action": "",
            "tool_outputs": [],
            "metadata": {},
            "steps_taken": 0,
            "documents_retrieved": []
        }
        
        # Configuração de Tracing (LangSmith) e Checkpointing (LangGraph)
        thread_id = request.thread_id or f"th_{user_id}"
        trace_config = get_trace_config(user_id=user_id, thread_id=thread_id)
        
        # Compilar e executar grafo com tracing
        graph = create_agent_graph()
        final_state = await graph.ainvoke(initial_state, config=trace_config)
        
        # Extrair resposta
        response_text = final_state["messages"][-1].content
        context_count = len(final_state.get("context", []))
        tools_used = [t["tool"] for t in final_state.get("tool_outputs", [])]
        
        # Determinar fluxo executado
        flow = ["planner"]
        if final_state.get("next_action") == "call_tool":
            flow.append("executor")
        elif final_state.get("next_action") == "respond":
            pass # Pula retriever
        else:
            flow.append("retriever")
        flow.append("responder")
        
        logger.info(f"✅ Agent Chat concluído. Fluxo: {' -> '.join(flow)}")
        
        return AgentChatResponse(
            response=response_text,
            context_count=context_count,
            tools_used=tools_used,
            flow=flow
        )
        
    except Exception as e:
        logger.error(f"❌ Erro no Agent Chat: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/health")
async def agent_health():
    """Verifica se o agente está disponível."""
    return {
        "status": "ok" if LANGGRAPH_AVAILABLE else "degraded",
        "langgraph_available": LANGGRAPH_AVAILABLE,
        "version": "1.0.0-enterprise"
    }
