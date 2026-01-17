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
    thread_id: str = "default_thread" # Para persistência de sessão (não implementada neste exemplo)

class ChatResponse(BaseModel):
    """Estrutura da resposta de chat."""
    response: str

@app.post("/chat", response_model=ChatResponse)
async def chat_endpoint(request: ChatRequest):
    """
    Rota principal para interagir com o Agente RAG.
    """
    try:
        # Chama a função principal do agente
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

# Para rodar a API: uvicorn api:app --reload --host 0.0.0.0 --port 8000
