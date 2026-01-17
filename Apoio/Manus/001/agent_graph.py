"""
Arquitetura do Grafo de Agente - Treq Enterprise
Implementação inicial do StateGraph usando LangGraph.
"""

from typing import TypedDict, Annotated, List, Dict, Any
from langchain_core.messages import BaseMessage, HumanMessage, AIMessage
import operator

# 1. Definição do Estado do Agente
class AgentState(TypedDict):
    # Annotated com operator.add permite que as mensagens sejam acumuladas (append)
    messages: Annotated[List[BaseMessage], operator.add]
    user_id: str
    context: List[str]
    next_action: str
    tool_outputs: List[Dict[str, Any]]

# 2. Definição dos Nodes (Nódulos)

async def planner_node(state: AgentState):
    """
    Decide se a query precisa de RAG, de uma Ferramenta ou Resposta Direta.
    """
    print("--- PLANNER NODE ---")
    # Lógica de decisão (LLM Call aqui no futuro)
    # Por enquanto, simulamos decisão baseada em palavras-chave
    last_message = state['messages'][-1].content.lower()
    
    if "ticket" in last_message or "jira" in last_message:
        return {"next_action": "call_tool"}
    else:
        return {"next_action": "call_rag"}

async def retriever_node(state: AgentState):
    """
    Executa a busca RAG usando o RAGService existente.
    """
    print("--- RETRIEVER NODE ---")
    # Aqui integraríamos com o RAGService.search_similar
    # O user_id do state garante o RLS
    return {"context": ["Informação recuperada da base de conhecimento..."]}

async def tool_executor_node(state: AgentState):
    """
    Executa ferramentas externas (Jira, Slack, etc).
    """
    print("--- TOOL EXECUTOR NODE ---")
    return {"tool_outputs": [{"tool": "Jira", "result": "Ticket TREQ-123 criado"}]}

async def responder_node(state: AgentState):
    """
    Gera a resposta final para o usuário.
    """
    print("--- RESPONDER NODE ---")
    return {"messages": [AIMessage(content="Aqui está a resposta baseada no contexto ou ação realizada.")]}

# 3. Lógica de Roteamento (Edges Condicionais)

def route_after_planner(state: AgentState):
    if state["next_action"] == "call_tool":
        return "tool_executor"
    return "retriever"

# Nota: A compilação do grafo (StateGraph) requer a biblioteca langgraph instalada.
# Este arquivo serve como blueprint arquitetural para a Sprint 1.1.
