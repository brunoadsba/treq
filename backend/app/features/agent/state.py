"""
AgentState - Estado do Agente Treq Enterprise

Define o que o agente "lembra" durante a execução do grafo.
O user_id é essencial para propagação do RLS.
"""

from typing import TypedDict, Annotated, List, Dict, Any, Optional
from langchain_core.messages import BaseMessage
import operator


class AgentState(TypedDict):
    """
    Estado compartilhado entre todos os nodes do grafo.
    
    Attributes:
        messages: Histórico de mensagens (acumulativo via operator.add)
        user_id: ID do usuário para filtro RLS
        context: Documentos recuperados pelo RAG
        next_action: Próxima ação decidida pelo planner
        tool_outputs: Resultados das ferramentas executadas
        metadata: Metadados adicionais (opcional)
    """
    messages: Annotated[List[BaseMessage], operator.add]
    user_id: str
    context: List[str]
    next_action: str
    tool_outputs: List[Dict[str, Any]]
    metadata: Optional[Dict[str, Any]]
    
    # Controle de loop e RAG
    steps_taken: int
    documents_retrieved: List[str]
