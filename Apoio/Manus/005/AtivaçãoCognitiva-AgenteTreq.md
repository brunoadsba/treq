# Guia de Implementação Padrão Indústria: Ativação Cognitiva do Agente Treq

## Pré-requisitos Técnicos

```bash
# Dependências obrigatórias
pydantic>=2.0.0
langchain>=0.1.0
openai>=1.0.0
tiktoken>=0.5.0
structlog>=23.0.0
```

## Fase 1: Fundação e Contratos Técnicos

### 1.1 Criação dos Schemas Base

**Arquivo:** `agent/schemas/planner.py`

```python
from pydantic import BaseModel, Field
from typing import List, Literal, Optional
from datetime import datetime

class ToolArgument(BaseModel):
    """Argumento individual para execução de ferramenta"""
    name: str = Field(description="Nome do parâmetro")
    value: str | int | bool | dict = Field(description="Valor extraído")
    confidence: float = Field(ge=0.0, le=1.0, description="Confiança da extração")

class ActionStep(BaseModel):
    """Passo atômico do plano de execução"""
    tool_name: str = Field(description="Identificador único da ferramenta")
    arguments: List[ToolArgument] = Field(default_factory=list)
    reasoning: str = Field(description="Por que executar esta ação")
    fallback_tool: Optional[str] = Field(None, description="Ferramenta alternativa se falhar")

class PlannerDecision(BaseModel):
    """Decisão completa do planejador cognitivo"""
    intent: Literal["create_task", "search_knowledge", "answer_directly", "clarify"] 
    thought: str = Field(min_length=10, description="Raciocínio estruturado do LLM")
    plan: List[ActionStep] = Field(max_length=5, description="Máximo 5 passos por segurança")
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
```

### 1.2 Atualização do Estado do Agente

**Arquivo:** `agent/state.py`

```python
from dataclasses import dataclass, field
from typing import List, Optional
from .schemas.planner import PlannerDecision

@dataclass
class AgentState:
    """Estado enriquecido com capacidades cognitivas"""
    user_id: str
    session_id: str
    conversation_history: List[dict] = field(default_factory=list)
    
    # Novos campos cognitivos
    current_decision: Optional[PlannerDecision] = None
    execution_trace: List[dict] = field(default_factory=list)
    retry_count: int = 0
    max_retries: int = 3
    
    def log_thought(self, thought: str, metadata: dict = None):
        """Registra raciocínio para auditoria"""
        self.execution_trace.append({
            "timestamp": datetime.utcnow().isoformat(),
            "thought": thought,
            "metadata": metadata or {}
        })
    
    def should_retry(self) -> bool:
        return self.retry_count < self.max_retries
```

### 1.3 Sistema de Logs Estruturado

**Arquivo:** `core/logging.py`

```python
import structlog

def configure_logging():
    structlog.configure(
        processors=[
            structlog.contextvars.merge_contextvars,
            structlog.processors.add_log_level,
            structlog.processors.TimeStamper(fmt="iso"),
            structlog.processors.JSONRenderer()
        ],
        wrapper_class=structlog.make_filtering_bound_logger(logging.INFO),
        logger_factory=structlog.PrintLoggerFactory(),
    )

logger = structlog.get_logger()

# Uso no planner
logger.info("planner.decision", 
            intent=decision.intent, 
            confidence=decision.confidence_score,
            thought=decision.thought)
```

---

## Fase 2: Núcleo Cognitivo (Planner)

### 2.1 Prompt Engineering - Sistema ReAct

**Arquivo:** `agent/prompts/planner_system.py`

```python
from datetime import datetime

def get_planner_system_prompt(user_context: dict) -> str:
    current_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    
    return f"""Você é o Cérebro Decisório do Agente Treq. Analise a intenção do usuário usando raciocínio estruturado.

CONTEXTO OPERACIONAL:
- Data/Hora: {current_time}
- Usuário: {user_context.get('name', 'Anônimo')}
- Time: {user_context.get('team', 'Não especificado')}

FERRAMENTAS DISPONÍVEIS:
1. jira_create_issue: Criar tarefas no Jira (requer: summary, description, assignee?)
2. slack_send_message: Enviar mensagens (requer: channel, text)
3. rag_search: Buscar documentação interna (requer: query, filters?)

PROTOCOLO DE DECISÃO (ReAct):
1. **Thought**: Analise a intenção e identifique dados faltantes
2. **Action**: Escolha a ferramenta mais adequada
3. **Argument Extraction**: Extraia parâmetros com confiança >= 0.7
4. **Validation**: Se confiança < 0.7, use intent="clarify"

REGRAS OBRIGATÓRIAS:
- Sempre gere o campo "thought" com no mínimo 20 palavras
- Máximo de 3 ferramentas por plano
- Se ambíguo, SEMPRE peça esclarecimento (intent="clarify")

Responda EXCLUSIVAMENTE em JSON válido seguindo o schema PlannerDecision."""
```

### 2.2 Implementação do Planner Cognitivo

**Arquivo:** `agent/planner.py`

```python
from langchain_openai import ChatOpenAI
from langchain_core.output_parsers import PydanticOutputParser
from .schemas.planner import PlannerDecision
from .prompts.planner_system import get_planner_system_prompt

class CognitivePlanner:
    def __init__(self, llm_service, user_context: dict):
        self.llm = llm_service.get_model("gpt-4o-mini")  # Modelo lite para baixa latência
        self.user_context = user_context
        self.parser = PydanticOutputParser(pydantic_object=PlannerDecision)
        
    async def plan(self, user_message: str, state: AgentState) -> PlannerDecision:
        """Gera plano de execução usando raciocínio ReAct"""
        
        system_prompt = get_planner_system_prompt(self.user_context)
        
        messages = [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": f"Mensagem: {user_message}\n\nInstrução: {self.parser.get_format_instructions()}"}
        ]
        
        try:
            response = await self.llm.ainvoke(messages)
            decision = self.parser.parse(response.content)
            
            # Log estruturado
            state.log_thought(decision.thought, {
                "intent": decision.intent,
                "confidence": decision.confidence_score
            })
            
            return decision
            
        except Exception as e:
            logger.error("planner.failed", error=str(e), message=user_message)
            # Fallback: resposta direta sem ferramentas
            return PlannerDecision(
                intent="answer_directly",
                thought=f"Erro no planejamento: {str(e)}. Respondendo diretamente.",
                plan=[],
                confidence_score=0.0
            )
```

---

## Fase 3: Executor de Ferramentas

### 3.1 Camada de Extração Dinâmica

**Arquivo:** `agent/executor.py`

```python
from typing import Any, Dict
from pydantic import ValidationError

class ToolExecutor:
    def __init__(self, tool_registry: dict):
        self.tools = tool_registry  # {tool_name: ToolClass}
        
    async def execute_plan(self, decision: PlannerDecision, state: AgentState) -> Dict[str, Any]:
        """Executa plano com validação e retry automático"""
        
        results = []
        
        for step in decision.plan:
            try:
                tool = self.tools.get(step.tool_name)
                if not tool:
                    raise ValueError(f"Ferramenta {step.tool_name} não encontrada")
                
                # Converte argumentos para dict
                args_dict = {arg.name: arg.value for arg in step.arguments}
                
                # Validação via schema da ferramenta
                validated_args = tool.argument_schema(**args_dict)
                
                # Execução segura
                result = await tool.execute(validated_args, user_id=state.user_id)
                
                results.append({
                    "tool": step.tool_name,
                    "status": "success",
                    "output": result
                })
                
            except ValidationError as e:
                logger.warning("executor.validation_failed", tool=step.tool_name, errors=e.errors())
                
                if step.fallback_tool and state.should_retry():
                    state.retry_count += 1
                    # Tentar ferramenta alternativa
                    continue
                    
                results.append({
                    "tool": step.tool_name,
                    "status": "failed",
                    "error": "Parâmetros inválidos"
                })
                
        return {"results": results, "trace": state.execution_trace}
```

### 3.2 Exemplo de Ferramenta com Schema

**Arquivo:** `tools/jira_tool.py`

```python
from pydantic import BaseModel, Field

class JiraCreateIssueArgs(BaseModel):
    summary: str = Field(min_length=5, description="Título da issue")
    description: str = Field(default="")
    assignee: str | None = Field(None, description="Email do responsável")
    priority: Literal["High", "Medium", "Low"] = Field(default="Medium")

class JiraTool:
    argument_schema = JiraCreateIssueArgs
    
    async def execute(self, args: JiraCreateIssueArgs, user_id: str):
        # Implementação real com validação RLS
        jira_client = get_jira_client(user_id)
        issue = jira_client.create_issue(
            project="TREQ",
            summary=args.summary,
            description=args.description
        )
        return {"issue_key": issue.key, "url": issue.permalink()}
```

---

## Fase 4: Integração e Testes

### 4.1 Orquestração Completa

**Arquivo:** `agent/orchestrator.py`

```python
class AgentOrchestrator:
    def __init__(self, planner, executor, user_context):
        self.planner = planner
        self.executor = executor
        self.user_context = user_context
        
    async def process_message(self, message: str, session_id: str) -> dict:
        state = AgentState(
            user_id=self.user_context['id'],
            session_id=session_id
        )
        
        # Etapa 1: Planejamento
        decision = await self.planner.plan(message, state)
        state.current_decision = decision
        
        # Etapa 2: Roteamento
        if decision.intent == "clarify":
            return {
                "response": "Preciso de mais informações. " + decision.thought,
                "needs_clarification": True
            }
        
        if decision.intent == "answer_directly":
            # Sem ferramentas, apenas resposta do LLM
            return {"response": decision.thought}
        
        # Etapa 3: Execução
        execution_result = await self.executor.execute_plan(decision, state)
        
        # Etapa 4: Síntese final
        final_response = self._synthesize_response(decision, execution_result)
        
        return {
            "response": final_response,
            "metadata": {
                "intent": decision.intent,
                "confidence": decision.confidence_score,
                "tools_used": [r['tool'] for r in execution_result['results']]
            }
        }
```

### 4.2 Testes de Integração

**Arquivo:** `tests/test_cognitive_agent.py`

```python
import pytest
from agent.orchestrator import AgentOrchestrator

@pytest.mark.asyncio
async def test_task_creation_flow():
    orchestrator = AgentOrchestrator(...)
    
    result = await orchestrator.process_message(
        "Criar task pra implementar login OAuth com prazo até sexta",
        session_id="test-123"
    )
    
    assert result['metadata']['intent'] == 'create_task'
    assert result['metadata']['confidence'] > 0.8
    assert 'jira_create_issue' in result['metadata']['tools_used']
```

---

## Checklist de Implementação

**Fase 1:**
- [ ] Schemas Pydantic criados e validados
- [ ] AgentState atualizado com campos cognitivos
- [ ] Sistema de logs estruturado configurado

**Fase 2:**
- [ ] Prompt ReAct implementado
- [ ] CognitivePlanner testado com casos edge
- [ ] Mecanismo de fallback funcionando

**Fase 3:**
- [ ] ToolExecutor com validação dinâmica
- [ ] Retry logic implementado
- [ ] Segurança RLS em todas as ferramentas

**Fase 4:**
- [ ] Orquestrador completo integrado
- [ ] Testes de latência (< 2s meta)
- [ ] Documentação técnica finalizada

Podemos continuar? A próxima etapa do projeto é: **detalhamento da infraestrutura Docker para deploy do novo cérebro cognitivo**.