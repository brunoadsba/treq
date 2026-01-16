# Guia Quick Start: Sprint 1.1 - LangGraph Core

Este guia fornece os passos exatos para você sair do MVP RAG e iniciar a implementação do **Treq Enterprise** hoje mesmo.

---

## 🚀 Passo 1: Instalação e Ambiente

Atualize seu ambiente com as novas dependências necessárias para orquestração de agentes.

```bash
# Instalar dependências core
pip install langgraph langchain-openai langsmith tiktoken

# Configurar variáveis de ambiente (se ainda não tiver)
export LANGCHAIN_TRACING_V2=true
export LANGCHAIN_API_KEY=sua_chave_aqui
export OPENAI_API_KEY=sua_chave_aqui
```

---

## 🏗️ Passo 2: Estrutura de Arquivos

Organize os novos arquivos no seu diretório `src/`:

- `src/agent_state.py`: Define o que o agente "lembra".
- `src/agent_graph.py`: Define o fluxo de raciocínio (nodes e edges).
- `src/tools_mock.py`: Ferramentas simuladas para teste imediato.

---

## 🧠 Passo 3: Implementação do Primeiro Node

Aproveite o `RAGService` que já criamos. No seu arquivo `src/agent_graph.py`, adicione o node de recuperação:

```python
from src.rag_service import RAGService
from src.agent_state import AgentState

rag_service = RAGService()

async def retriever_node(state: AgentState):
    # O user_id vem do estado do agente, garantindo o RLS
    query = state['messages'][-1].content
    results = await rag_service.search_similar(query, user_id=state['user_id'])
    
    return {
        "context": [r.content for r in results],
        "messages": [AIMessage(content="Busquei informações na base de conhecimento.")]
    }
```

---

## 🚦 Passo 4: Rota Paralela no FastAPI

Não quebre o que já funciona. Crie uma nova rota no seu servidor:

```python
@app.post("/agent/chat")
async def agent_chat(request: ChatRequest):
    # 1. Inicializar estado
    initial_state = {
        "messages": [HumanMessage(content=request.query)],
        "user_id": request.user_id,
        "context": []
    }
    
    # 2. Executar o Grafo
    app_graph = graph.compile()
    final_state = await app_graph.ainvoke(initial_state)
    
    return {"response": final_state["messages"][-1].content}
```

---

## ✅ Checklist de Início (Sprint 1.1)

- [ ] **Requirements**: `langgraph` instalado?
- [ ] **Arquitetura**: Rota `/agent/` criada?
- [ ] **Segurança**: `user_id` sendo passado para o grafo?
- [ ] **Mocks**: `JiraCreateTicketTool` (mock) pronto para a Sprint 1.3?

---

**Dica de Ouro**: Comece com um grafo simples de 2 nodes (`planner` -> `retriever`). Assim que ele funcionar na nova rota, adicione o `executor_node` para as ferramentas.

**Você está pronto para começar! 🚀**
