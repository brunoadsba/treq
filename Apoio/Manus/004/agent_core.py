import os
from typing import Literal, TypedDict, Annotated
from operator import itemgetter

from langchain_core.messages import HumanMessage, AIMessage, ToolMessage
from langchain_openai.chat_models import ChatOpenAI
from langchain_openai.embeddings import OpenAIEmbeddings
from langchain_community.vectorstores import Chroma
from langchain_core.tools import tool
from langgraph.graph import END, StateGraph
from langgraph.prebuilt import ToolNode
from dotenv import load_dotenv

load_dotenv()

# --- 1. Configuração e Inicialização ---
# A chave da API do OpenAI deve estar no .env ou ambiente
if not os.getenv("OPENAI_API_KEY"):
    raise ValueError("OPENAI_API_KEY não configurada.")

# Inicialização do LLM e Embeddings
llm = ChatOpenAI(model="gpt-4o-mini", temperature=0)
embeddings = OpenAIEmbeddings(model="text-embedding-3-small")

# Inicialização do VectorStore (Chroma para demonstração)
# No ambiente de produção, substitua por PGvector
CHROMA_PATH = "chroma_db"
vectorstore = Chroma(
    persist_directory=CHROMA_PATH,
    embedding_function=embeddings
)
retriever = vectorstore.as_retriever()

# --- 2. Definição do Estado do Grafo (Graph State) ---
class AgentState(TypedDict):
    """
    Representa o estado do grafo LangGraph.
    O histórico de mensagens é a chave principal.
    """
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
    
    # Formata os resultados para o LLM
    context = "\n\n".join([doc.page_content for doc in results])
    return context

tools = [retrieve_context]
tool_node = ToolNode(tools)

# LLM com as ferramentas vinculadas
llm_with_tools = llm.bind_tools(tools)

# --- 4. Definição dos Nós do Grafo (Nodes) ---
def call_model(state: AgentState):
    """
    Chama o LLM com o histórico de mensagens atual.
    """
    messages = state["messages"]
    response = llm_with_tools.invoke(messages)
    
    # Adiciona a resposta do LLM ao histórico
    return {"messages": [response]}

def should_continue(state: AgentState) -> Literal["tools", END]:
    """
    Função de roteamento condicional.
    Decide se o LLM chamou uma ferramenta ou se deve encerrar.
    """
    last_message = state["messages"][-1]
    
    # Se o LLM sugeriu uma chamada de ferramenta, vá para o nó 'tools'
    if last_message.tool_calls:
        print("-> ROUTER: LLM chamou uma ferramenta. Indo para 'tools'.")
        return "tools"
    
    # Caso contrário, encerre o grafo e retorne a resposta final
    print("-> ROUTER: LLM gerou a resposta final. Encerrando.")
    return END

# --- 5. Construção do Grafo (Graph Construction) ---
workflow = StateGraph(AgentState)

# Adiciona os nós
workflow.add_node("agent", call_model)
workflow.add_node("tools", tool_node)

# Define o ponto de entrada
workflow.add_edge("tools", "agent") # O resultado da ferramenta volta para o agente

# Define o roteamento condicional
workflow.add_conditional_edges(
    "agent",
    should_continue,
    {
        "tools": "tools",
        END: END,
    },
)

# Define o ponto de início
workflow.set_entry_point("agent")

# Compila o grafo
app = workflow.compile()

# --- 6. Função de Chat para a API ---
def run_agent_chat(user_input: str, thread_id: str = "default_thread"):
    """
    Executa o loop do agente e retorna a resposta final.
    """
    # Cria a mensagem inicial do usuário
    user_message = HumanMessage(content=user_input)
    
    # O LangGraph usa um checkpointer para gerenciar o histórico de conversas (memória)
    # Para simplificar, usaremos uma execução sem persistência aqui.
    # Em produção, o checkpointer deve ser configurado com o PostgreSQL.
    
    # Executa o grafo
    final_state = app.invoke({"messages": [user_message]})
    
    # Retorna o conteúdo da última mensagem (a resposta do LLM)
    return final_state["messages"][-1].content

if __name__ == "__main__":
    # Exemplo de uso
    print("--- Iniciando Ingestão de Dados (necessário rodar ingest.py primeiro) ---")
    # Nota: Para este exemplo funcionar, você deve rodar 'python3 ingest.py' primeiro.
    
    print("\n--- Teste 1: Pergunta que requer RAG ---")
    response = run_agent_chat("Quais são os componentes chave de um Agentic RAG?")
    print(f"\nAgente Responde: {response}")
    
    print("\n--- Teste 2: Pergunta que não requer RAG (conhecimento geral do LLM) ---")
    response = run_agent_chat("Qual a capital do Brasil?")
    print(f"\nAgente Responde: {response}")
