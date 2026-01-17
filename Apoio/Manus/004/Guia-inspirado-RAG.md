Guia Completo de Implementação: Agentic RAG com LangGraph e PGvector (Inspirado no Manus AI)


# Guia Completo de Implementação: Agentic RAG com LangGraph e PGvector (Inspirado no Manus AI)

Este guia detalhado apresenta a arquitetura e a implementação de um sistema de **Retrieval-Augmented Generation (RAG) Agentic**, seguindo os princípios de orquestração e tomada de decisão autônoma observados em agentes avançados como o Manus AI. O foco está na utilização do **LangGraph** para o fluxo de agente e do **PGvector** para a camada de recuperação de conhecimento.

## 1. Arquitetura e Fluxo de Execução

A arquitetura Agentic RAG é baseada no padrão **ReAct (Reasoning and Acting)**, onde o Agente (LLM) decide iterativamente entre pensar, agir (chamar ferramentas) e observar o resultado.

| Componente | Função Principal | Tecnologia Recomendada |
| :--- | :--- | :--- |
| **Orquestrador** | Gerencia o estado e o fluxo de execução (Loop ReAct). | LangGraph |
| **Agente de Decisão** | LLM que analisa a *query* e decide se precisa de contexto externo (RAG). | OpenAI GPT-4o / gpt-4o-mini |
| **Camada de Recuperação** | Armazena e busca vetores de alta dimensão para RAG. | PostgreSQL + PGvector |
| **Ferramentas (Tools)** | Funções que o Agente pode chamar (ex: `retrieve_context`). | LangChain Tools |
| **API** | Expõe o Agente para o *frontend* ou outros serviços. | FastAPI |
| **Memória** | Persistência do histórico de conversas e estado do grafo. | LangGraph Checkpointer (PostgreSQL) |

### Fluxo de Execução (Loop ReAct)

1.  **Entrada:** O usuário envia uma pergunta via API (`/chat`).
2.  **Nó `agent` (Think):** O LLM recebe a pergunta e o histórico. Ele decide:
    *   **Ação (Act):** Se a pergunta requer conhecimento externo, ele chama a ferramenta `retrieve_context`.
    *   **Resposta Final:** Se a pergunta é de conhecimento geral ou a busca anterior foi suficiente, ele gera a resposta final.
3.  **Roteamento Condicional:**
    *   Se o LLM chamou uma ferramenta, o fluxo vai para o nó `tools`.
    *   Se o LLM gerou a resposta final, o fluxo termina (`END`).
4.  **Nó `tools` (Observe):** A ferramenta `retrieve_context` é executada, consultando o PGvector. O resultado (chunks de texto) é retornado como uma `ToolMessage`.
5.  **Ciclo:** O resultado da ferramenta é enviado de volta para o nó `agent`, que agora tem o contexto para gerar uma resposta informada.

## 2. Configuração do Ambiente e Dependências

### 2.1. Dependências (requirements.txt)

```python
# Core
python-dotenv
fastapi
uvicorn
psycopg2-binary # Para PostgreSQL

# LangChain/LangGraph
langchain
langgraph
langchain-openai
langchain-community
langchain-text-splitters
langchain-postgres # Para integração com PGvector

# Data Ingestion
unstructured # Para carregar diversos tipos de documentos
pypdf # Para PDFs
chromadb # Para testes locais de VectorStore
```

### 2.2. Configuração do Banco de Dados (PGvector)

Recomenda-se o uso de Docker para isolar o ambiente do PostgreSQL com a extensão PGvector instalada.

**`docker-compose.yml`**

```yaml
version: '3.8'

services:
  db:
    image: ankane/postgres-pgvector:latest
    restart: always
    environment:
      POSTGRES_USER: user
      POSTGRES_PASSWORD: password
      POSTGRES_DB: rag_db
    ports:
      - "5432:5432"
    volumes:
      - postgres_data:/var/lib/postgresql/data

volumes:
  postgres_data:
```

**Comando para iniciar:** `docker compose up -d`

## 3. Ingestão de Dados (Criação do VectorStore)

O processo de ingestão transforma seus documentos em vetores e os armazena no PGvector.

### 3.1. Script de Ingestão (`ingest.py`)

Este script demonstra a lógica de *chunking* e a criação do *VectorStore*. Para o PGvector, a classe `PGVector` do LangChain é utilizada.

```python
import os
from langchain_community.document_loaders import TextLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_openai.embeddings import OpenAIEmbeddings
# Importe PGVector para produção
# from langchain_postgres import PGVector 
from dotenv import load_dotenv

load_dotenv()

# Configurações de Conexão PGvector (Produção)
CONNECTION_STRING = "postgresql+psycopg2://user:password@localhost:5432/rag_db"
COLLECTION_NAME = "manus_knowledge"

def ingest_data():
    """Processa o arquivo de conhecimento, divide em chunks e cria o VectorStore."""
    
    # 1. Carregamento e Chunking
    loader = TextLoader("knowledge_base.txt") # Substitua por PDF, DOCX, etc.
    documents = loader.load()

    text_splitter = RecursiveCharacterTextSplitter(
        chunk_size=1000,
        chunk_overlap=200,
        length_function=len,
    )
    chunks = text_splitter.split_documents(documents)
    print(f"Documentos divididos em {len(chunks)} chunks.")

    # 2. Criação dos Embeddings e VectorStore
    embeddings = OpenAIEmbeddings(model="text-embedding-3-small")

    # --- Implementação PGvector ---
    # vectorstore = PGVector.from_documents(
    #     documents=chunks,
    #     embedding=embeddings,
    #     connection_string=CONNECTION_STRING,
    #     collection_name=COLLECTION_NAME,
    # )
    # print("Ingestão de dados concluída no PGvector.")
    
    # --- Implementação Chroma (Apenas para Teste Local) ---
    from langchain_community.vectorstores import Chroma
    vectorstore = Chroma.from_documents(
        documents=chunks,
        embedding=embeddings,
        persist_directory="chroma_db"
    )
    vectorstore.persist()
    print("Ingestão de dados concluída no Chroma (Teste Local).")

if __name__ == "__main__":
    if not os.getenv("OPENAI_API_KEY"):
        print("ERRO: A variável de ambiente OPENAI_API_KEY não está configurada.")
    else:
        ingest_data()
```

## 4. Lógica Central do Agente (LangGraph)

O LangGraph define o ciclo de vida do Agente, permitindo que ele tome decisões complexas.

### 4.1. Definição do Estado e Ferramentas (`agent_core.py`)

```python
import os
from typing import Literal, TypedDict, Annotated
from operator import itemgetter

from langchain_core.messages import HumanMessage, AIMessage, ToolMessage
from langchain_openai.chat_models import ChatOpenAI
from langchain_openai.embeddings import OpenAIEmbeddings
from langchain_core.tools import tool
from langgraph.graph import END, StateGraph
from langgraph.prebuilt import ToolNode
# Importe PGVector para produção
# from langchain_postgres import PGVector 
from dotenv import load_dotenv

load_dotenv()

# --- 1. Configuração e Inicialização ---
llm = ChatOpenAI(model="gpt-4o-mini", temperature=0)
embeddings = OpenAIEmbeddings(model="text-embedding-3-small")

# Configuração do Retriever (Substitua Chroma por PGVector em produção)
# retriever = PGVector(
#     connection_string=CONNECTION_STRING,
#     collection_name=COLLECTION_NAME,
#     embedding_function=embeddings
# ).as_retriever()
from langchain_community.vectorstores import Chroma
vectorstore = Chroma(persist_directory="chroma_db", embedding_function=embeddings)
retriever = vectorstore.as_retriever()

# --- 2. Definição do Estado do Grafo ---
class AgentState(TypedDict):
    """Representa o estado do grafo LangGraph."""
    messages: Annotated[list, itemgetter("messages")]

# --- 3. Definição das Ferramentas (Tools) ---
@tool
def retrieve_context(query: str) -> str:
    """
    Busca documentos relevantes na base de conhecimento (PGvector/Chroma)
    para responder à pergunta do usuário.
    """
    print(f"-> TOOL: Buscando contexto para a query: '{query}'")
    results = retriever.invoke(query)
    context = "\n\n".join([doc.page_content for doc in results])
    return context

tools = [retrieve_context]
tool_node = ToolNode(tools)
llm_with_tools = llm.bind_tools(tools)

# --- 4. Definição dos Nós e Roteamento ---
def call_model(state: AgentState):
    """Chama o LLM com o histórico de mensagens atual."""
    messages = state["messages"]
    response = llm_with_tools.invoke(messages)
    return {"messages": [response]}

def should_continue(state: AgentState) -> Literal["tools", END]:
    """Decide se o LLM chamou uma ferramenta ou se deve encerrar."""
    last_message = state["messages"][-1]
    if last_message.tool_calls:
        return "tools"
    return END

# --- 5. Construção e Compilação do Grafo ---
workflow = StateGraph(AgentState)
workflow.add_node("agent", call_model)
workflow.add_node("tools", tool_node)
workflow.add_edge("tools", "agent")
workflow.add_conditional_edges("agent", should_continue, {"tools": "tools", END: END})
workflow.set_entry_point("agent")
app = workflow.compile()

# --- 6. Função de Chat para a API ---
def run_agent_chat(user_input: str, thread_id: str = "default_thread"):
    """Executa o loop do agente e retorna a resposta final."""
    user_message = HumanMessage(content=user_input)
    
    # Nota: Para persistência de sessão (memória de longo prazo),
    # você deve configurar um checkpointer LangGraph com o PostgreSQL.
    
    final_state = app.invoke({"messages": [user_message]})
    return final_state["messages"][-1].content

if __name__ == "__main__":
    # Exemplo de uso
    print("Rodando teste do Agente...")
    response = run_agent_chat("Quais são os componentes chave de um Agentic RAG?")
    print(f"\nAgente Responde: {response}")
```

## 5. Exposição da API (FastAPI)

Para tornar o Agente acessível, criamos uma API RESTful.

### 5.1. Script da API (`api.py`)

```python
import os
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from agent_core import run_agent_chat
from dotenv import load_dotenv

load_dotenv()

# Verifica se a chave da API está configurada
if not os.getenv("OPENAI_API_KEY"):
    raise EnvironmentError("OPENAI_API_KEY não configurada. Verifique seu arquivo .env.")

app = FastAPI(
    title="Manus AI-Inspired Agentic RAG API",
    description="API para o Agente RAG Orquestrado por LangGraph.",
    version="1.0.0"
)

class ChatRequest(BaseModel):
    """Estrutura da requisição de chat."""
    user_input: str
    thread_id: str = "default_thread" # Para persistência de sessão

class ChatResponse(BaseModel):
    """Estrutura da resposta de chat."""
    response: str

@app.post("/chat", response_model=ChatResponse)
async def chat_endpoint(request: ChatRequest):
    """
    Rota principal para interagir com o Agente RAG.
    """
    try:
        agent_response = run_agent_chat(
            user_input=request.user_input,
            thread_id=request.thread_id
        )
        return ChatResponse(response=agent_response)
    except Exception as e:
        print(f"Erro durante a execução do agente: {e}")
        raise HTTPException(status_code=500, detail=f"Erro interno do servidor: {str(e)}")

@app.get("/health")
async def health_check():
    """Rota de verificação de saúde da API."""
    return {"status": "ok", "agent_status": "ready"}
```

### 5.2. Comando para Rodar a API

```bash
uvicorn api:app --host 0.0.0.0 --port 8000
```

## 6. Próximos Passos e Melhores Práticas

Para evoluir este projeto para um padrão de produção como o Manus AI, considere:

1.  **Memória de Longo Prazo (Checkpointer):** Implemente o `PostgresSaver` do LangGraph para persistir o estado do grafo no PostgreSQL, permitindo que o agente se lembre de conversas anteriores.
2.  **Reranking:** Adicione uma etapa de *reranking* (ex: usando modelos Cohere ou BGE) após a recuperação do PGvector para refinar a relevância dos *chunks* antes de enviá-los ao LLM.
3.  **Multi-Tooling:** Crie ferramentas adicionais (ex: busca na web, calculadora, acesso a APIs internas) e permita que o Agente decida qual usar, elevando o nível de autonomia.
4.  **Monitoramento:** Integre o sistema com ferramentas de observabilidade (ex: LangSmith, Prometheus) para rastrear o fluxo de execução, latência e custo de cada ciclo do Agente.
5.  **Segurança:** Implemente autenticação e autorização na API (FastAPI) e garanta que as chaves de API e a *connection string* do banco de dados sejam gerenciadas com segurança (ex: HashiCorp Vault ou variáveis de ambiente seguras).

---
**Atenção:** Para que o código funcione, você deve substituir `"SUA_CHAVE_AQUI"` pela sua chave real da OpenAI no arquivo `.env` e garantir que o `OPENAI_API_KEY` esteja acessível ao ambiente de execução. O erro `openai.NotFoundError: Error code: 404` indica que a chave não foi reconhecida ou o modelo não foi encontrado.
