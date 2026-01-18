"""
AgentState - Estado do Agente Treq Enterprise

Define o que o agente "lembra" durante a execução do grafo.
O user_id é essencial para propagação do RLS.
"""

from typing import TypedDict, Annotated, List, Dict, Any, Optional, Literal
from langchain_core.messages import BaseMessage
import operator


from .schemas import PlannerDecision


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
        current_decision: Decisão detalhada do Planner (Cognitivo)
        execution_trace: Rastro de raciocínio e execução (Audit)
    """
    messages: Annotated[List[BaseMessage], operator.add]
    user_id: str
    context: List[str]
    next_action: str
    tool_outputs: List[Dict[str, Any]]
    metadata: Optional[Dict[str, Any]]
    
    # Novos campos cognitivos
    current_decision: Optional[PlannerDecision]
    execution_trace: List[Dict[str, Any]]
    retry_count: int
    max_retries: int
    
    # Controle de loop e RAG
    steps_taken: int
    documents_retrieved: List[str]
    
    # Modo de exibição na interface
    response_mode: Literal["text", "tool", "hybrid"]
