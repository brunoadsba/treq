from pydantic import BaseModel, Field
from typing import List, Optional, Dict, Any
from app.utils.input_sanitizer import get_max_input_length

class ChatMessage(BaseModel):
    """Mensagem do chat."""
    role: str = Field(..., description="Role da mensagem: 'user' ou 'assistant'")
    content: str = Field(..., description="Conteúdo da mensagem")


class ChatRequest(BaseModel):
    """Request para chat."""
    message: str = Field(..., min_length=1, max_length=get_max_input_length(), description=f"Mensagem do usuário (máximo {get_max_input_length()} caracteres)")
    user_id: str = Field("anonymous", description="ID do usuário")
    conversation_id: Optional[str] = Field(None, description="ID da conversa (opcional)")
    context: Optional[Dict[str, Any]] = Field(None, description="Contexto adicional (unidade, período, etc.)")
    stream: Optional[bool] = Field(False, description="Se True, retorna streaming SSE")
    visualization: Optional[bool] = Field(False, description="Se True, ativa modo visualização gráfica")
    action_id: Optional[str] = Field(None, description="ID da ação rápida (ex: 'alertas', 'status-recife')")
    show_reasoning: Optional[bool] = Field(False, description="Se True, inclui reasoning/CoT na resposta")
    image_url: Optional[str] = Field(None, description="URL da imagem anexada (opcional)")


class ChatResponse(BaseModel):
    """Response do chat."""
    response: str = Field(..., description="Resposta do assistente")
    conversation_id: Optional[str] = Field(None, description="ID da conversa")
    run_id: Optional[str] = Field(None, description="ID do run no LangSmith (para feedback)")
    context_summary: str = Field(..., description="Resumo do contexto atual")
    sources: List[Dict[str, Any]] = Field(default_factory=list, description="Fontes usadas (do RAG)")
    strategy: Optional[str] = Field(None, description="Estratégia usada (tool_first, rag_first, hybrid)")
    tool_data: Optional[Dict[str, Any]] = Field(None, description="Dados retornados por tools (se aplicável)")
    chart_data: Optional[Dict[str, Any]] = Field(None, description="Dados de gráfico (se visualization=True)")
    reasoning: Optional[Dict[str, Any]] = Field(None, description="Plano de raciocínio (CoT) se solicitado")
