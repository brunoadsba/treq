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


def route_after_planner(state: AgentState) -> Literal["retriever", "executor"]:
    """Edge condicional após o planner."""
    if state.get("next_action") == "call_tool":
        return "executor"
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
            "executor": "executor"
        }
    )
    
    graph.add_edge("retriever", "responder")
    graph.add_edge("executor", "responder")
    graph.add_edge("responder", END)
    
    # Compilar
    compiled = graph.compile()
    logger.info("✅ Grafo do agente compilado com sucesso")
    
    return compiled
