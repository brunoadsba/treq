import re
from loguru import logger
from langchain_core.output_parsers import PydanticOutputParser
from ..state import AgentState
from ..schemas import PlannerDecision
from ..prompts import get_planner_system_prompt
from app.services.llm_service import LLMService

# Instâncias globais
llm_service = LLMService()
parser = PydanticOutputParser(pydantic_object=PlannerDecision)

def clean_json_response(text: str) -> str:
    """Extrai o bloco JSON de uma resposta que pode conter markdown ou explicações."""
    # Procura pelo maior bloco que começa com '{' e termina com '}'
    # Isso captura o objeto JSON ignorando qualquer texto antes ou depois, incluindo tags de markdown
    match = re.search(r'(\{.*\})', text, re.DOTALL)
    if match:
        return match.group(1).strip()
    return text.strip()

async def planner_node(state: AgentState) -> dict:
    """
    Gera plano de execução usando raciocínio ReAct via LLM.
    """
    logger.info("🧠 PLANNER: Iniciando raciocínio cognitivo...")
    
    last_message = state['messages'][-1].content
    user_id = state.get('user_id', 'Anônimo')
    
    # 1. Preparar Contexto e Prompt
    system_prompt = get_planner_system_prompt({"user_id": user_id})
    format_instructions = parser.get_format_instructions()
    
    messages = [
        {"role": "system", "content": system_prompt},
        {"role": "user", "content": f"Mensagem do usuário: {last_message}\n\n{format_instructions}"}
    ]
    
    try:
        # 2. Chamada ao LLM
        raw_response = llm_service.generate_response(
            messages,
            query_type="agent_planner",
            temperature=0.1 
        )
        
        # Limpeza agressiva do JSON para evitar falhas de modelos "falantes"
        cleaned_response = clean_json_response(raw_response)
        
        # 3. Parsing da Decisão
        decision = parser.parse(cleaned_response)
        logger.info(f"🧠 PLANNER: Intenção detectada -> {decision.intent} (Confiança: {decision.confidence_score})")
        
        # Registrar rastro de pensamento
        execution_trace = state.get('execution_trace', [])
        execution_trace.append({
            "step": "planner",
            "thought": decision.thought,
            "intent": decision.intent,
            "confidence": decision.confidence_score
        })

        # Mapeamento de intenção para next_action do grafo
        intent_mapping = {
            "create_task": "executor",
            "search_knowledge": "retriever",
            "answer_directly": "responder",
            "clarify": "responder" 
        }
        
        next_action = intent_mapping.get(decision.intent, "retriever")

        # 4. Controle de Loop (Auto-correção)
        steps = state.get("steps_taken", 0)
        if next_action == "retriever" and steps >= 2:
            logger.warning("🛑 PLANNER: Limite de buscas atingido. Forçando encerramento.")
            next_action = "responder"

        return {
            "next_action": next_action,
            "current_decision": decision,
            "execution_trace": execution_trace,
            "steps_taken": steps + 1
        }

    except Exception as e:
        logger.error(f"❌ PLANNER: Falha no planejamento - {e}")
        if 'raw_response' in locals():
            logger.debug(f"📄 Raw Response que falhou: {raw_response[:500]}...")
            
        # Fallback seguro
        return {
            "next_action": "retriever",
            "execution_trace": state.get('execution_trace', []) + [{"error": str(e)}],
            "steps_taken": state.get("steps_taken", 0) + 1,
            "current_decision": None
        }
