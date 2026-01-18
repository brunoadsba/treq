from pydantic import BaseModel, Field
from typing import List, Literal, Optional, Any
from datetime import datetime

class ToolArgument(BaseModel):
    """Argumento individual para execução de ferramenta"""
    name: str = Field(description="Nome do parâmetro")
    value: Any = Field(description="Valor extraído")
    confidence: float = Field(default=1.0, ge=0.0, le=1.0, description="Confiança da extração")

class ActionStep(BaseModel):
    """Passo atômico do plano de execução"""
    tool_name: str = Field(description="Identificador único da ferramenta")
    arguments: List[ToolArgument] = Field(default_factory=list)
    reasoning: str = Field(description="Por que executar esta ação")
    fallback_tool: Optional[str] = Field(None, description="Ferramenta alternativa se falhar")

class PlannerDecision(BaseModel):
    """Decisão completa do planejador cognitivo"""
    intent: Literal["create_task", "search_knowledge", "answer_directly", "clarify"] 
    thought: str = Field(min_length=10, description="Raciocínio estruturado interno do LLM")
    direct_response: Optional[str] = Field(None, description="Resposta amigável ao usuário para intents 'answer_directly' ou 'clarify'")
    plan: List[ActionStep] = Field(default_factory=list, max_length=5, description="Máximo 5 passos por segurança")
    confidence_score: float = Field(ge=0.0, le=1.0)
    timestamp: datetime = Field(default_factory=datetime.utcnow)
    
    class Config:
        json_schema_extra = {
            "example": {
                "intent": "create_task",
                "thought": "Usuário solicitou criação de tarefa com prazo específico. Necessário extrair título, descrição e data limite.",
                "plan": [
                    {
                        "tool_name": "jira_create_issue",
                        "arguments": [
                            {"name": "summary", "value": "Implementar login OAuth", "confidence": 0.95}
                        ],
                        "reasoning": "Criar issue no Jira com dados estruturados"
                    }
                ],
                "confidence_score": 0.92
            }
        }
