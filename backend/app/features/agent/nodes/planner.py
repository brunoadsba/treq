"""
Planner Node - Decide a próxima ação do agente.

Analisa a query do usuário e decide:
- call_rag: Buscar informações na base de conhecimento
- call_tool: Executar uma ferramenta externa (Jira, Slack)
- respond: Responder diretamente (perguntas simples)
"""

from loguru import logger
from ..state import AgentState


from ..tools.registry import ToolRegistry


async def planner_node(state: AgentState) -> dict:
    """
    Decide se a query precisa de RAG, Tool ou Resposta Direta.
    
    Args:
        state: Estado atual do agente
        
    Returns:
        dict com next_action definido
    """
    logger.info("🧠 PLANNER: Analisando query...")
    
    last_message = state['messages'][-1].content
    
    # Detecção dinâmica de intenção via Registry
    detected_tool = ToolRegistry.detect_tool(last_message)
    
    if detected_tool:
        logger.info(f"🔧 PLANNER: Decisão -> call_tool ({detected_tool})")
        return {"next_action": "call_tool"}
    
    # Detecção de Greeting (Saudação)
    # Detecção de Greeting (Saudação) e Inputs Curtos
    GREETINGS = [
        "oi", "ola", "olá", "bom dia", "boa tarde", "boa noite", 
        "e ai", "e aí", "eae", "opa", "hello", "hi", "test", "teste",
        "quem é você", "quem e voce", "quem é voce", "quem e você"
    ]
    
    last_msg_clean = last_message.strip().lower()
    # Remove pontuação básica para comparação
    last_msg_clean = "".join(c for c in last_msg_clean if c.isalnum() or c.isspace())
    
    should_respond_directly = (
        last_msg_clean in GREETINGS or 
        (len(last_msg_clean) < 5 and "ajud" not in last_msg_clean and "erro" not in last_msg_clean)
    )
    
    if should_respond_directly:
        logger.info("👋 PLANNER: Decisão -> respond (Greeting/Short)")
        return {"next_action": "respond"}

    # Default: buscar no RAG
    # --- Novo Fluxo RAG ---
    # Se o modelo decidir buscar conhecimento (passo de pensamento), 
    # ou se for o padrão para perguntas complexas
    
    # Simple Heuristic Fallback (Pode ser substituido por LLM call aqui)
    # Se não é tool direta e não é greeting -> RAG
    
    logger.info("📚 PLANNER: Decisão -> retrieve_knowledge")
    
    # --- Self-Correction Logic ---
    # Verifica se já buscamos e falhou (Contexto vazio ou mensagem de erro)
    # Se steps_taken > 2, desistimos para evitar loop
    steps = state.get("steps_taken", 0)
    context = state.get("context", [])
    
    if steps > 0:
        # Verifica se o último contexto foi vazio ou erro
        last_context = context[-1] if context else ""
        if "SEARCH_EMPTY" in last_context or not context:
            if steps < 2:
                 # TODO: Aqui poderíamos usar um LLM para reformular a query
                 # Por enquanto, como é heurístico, se falhar 1 vez, vamos para o responder
                 # que dirá "Não encontrei".
                 logger.info("⚠️ PLANNER: Busca falhou anteriormente. Encaminhando para resposta final.")
                 return {"next_action": "responder"}
            else:
                 logger.warning("🛑 PLANNER: Loop de busca detectado. Forçando resposta.")
                 return {"next_action": "responder"}

    return {"next_action": "retriever"}
