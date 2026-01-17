"""
Agent Graph - Orquestração do agente com LangGraph.

Define o StateGraph com nodes e edges condicionais.
"""

from typing import Literal
from loguru import logger

try:
    from langgraph.graph import StateGraph, END
    LANGGRAPH_AVAILABLE = True
except ImportError:
    LANGGRAPH_AVAILABLE = False
    logger.warning("⚠️ langgraph não instalado. Instale com: pip install langgraph")

from .state import AgentState
from .nodes import planner_node, retriever_node, executor_node, responder_node


def route_after_planner(state: AgentState) -> Literal["retriever", "executor", "responder"]:
    """Edge condicional após o planner."""
    if state.get("next_action") == "call_tool":
        return "executor"
    if state.get("next_action") == "respond":
        return "responder"
    return "retriever"


def create_agent_graph():
    """
    Cria e compila o grafo do agente.
    
    Fluxo:
    START -> planner -> (retriever | executor) -> responder -> END
    
    Returns:
        Compiled StateGraph pronto para execução
        
    Raises:
        ImportError: Se langgraph não estiver instalado
    """
    if not LANGGRAPH_AVAILABLE:
        raise ImportError(
            "langgraph não está instalado. "
            "Execute: pip install langgraph"
        )
    
    logger.info("🔨 Construindo grafo do agente...")
    
    # Criar grafo
    graph = StateGraph(AgentState)
    
    # Adicionar nodes
    graph.add_node("planner", planner_node)
    graph.add_node("retriever", retriever_node)
    graph.add_node("executor", executor_node)
    graph.add_node("responder", responder_node)
    
    # Definir entry point
    graph.set_entry_point("planner")
    
    # Adicionar edges
    graph.add_conditional_edges(
        "planner",
        route_after_planner,
        {
            "retriever": "retriever",
            "executor": "executor",
            "responder": "responder"
        }
    )
    
    graph.add_edge("retriever", "responder")
    graph.add_edge("executor", "responder")
    graph.add_edge("responder", END)
    
    # Compilar
    # Compilar com Checkpointer
    try:
        from app.core.checkpointer import PostgresSaver
        from app.services.vector_health import get_database_url
        
        db_url = get_database_url()
        if db_url:
            checkpointer = PostgresSaver(conn_string=db_url)
            compiled = graph.compile(checkpointer=checkpointer)
            logger.info("✅ Grafo compilado com Checkpointer (Postgres)")
        else:
            logger.warning("⚠️ DATABASE_URL não encontrada. Compilando SEM persistencia.")
            compiled = graph.compile()
            
    except Exception as e:
        logger.error(f"❌ Erro ao configurar Checkpointer: {e}. Usando MemorySaver.")
        from langgraph.checkpoint.memory import MemorySaver
        compiled = graph.compile(checkpointer=MemorySaver())
    
    logger.info("✅ Grafo do agente compilado com sucesso")
    
    return compiled
