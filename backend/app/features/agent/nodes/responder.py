"""
Responder Node - Gera a resposta final para o usuário.

Combina contexto do RAG e outputs de ferramentas para gerar resposta.
"""

from loguru import logger
from langchain_core.messages import AIMessage
import re

from ..state import AgentState
from ..prompts import AGENT_SYSTEM_PROMPT
from app.services.llm_service import LLMService

# Instância global do serviço (singleton implícito)
llm_service = LLMService()

def sanitize_response(text: str) -> str:
    """Filtro Pós-Recuperação: Remove artefatos internos e corrige branding."""
    # 1. Remover menções a arquivos (ex: .xlsx, .pdf)
    text = re.sub(r'[\w\-\s]+\.(xlsx|xls|pdf|csv|json|txt)', '', text, flags=re.IGNORECASE)
    
    # 2. Forçar branding Treq (se vazou Sotreq de alguma forma)
    # Evita substituir URLs ou emails se não quiser, mas aqui vamos ser agressivos no branding
    text = re.sub(r'\bSotreq\b', 'Treq', text, flags=re.IGNORECASE)
    
    # 3. Remover caminhos de arquivo (ex: /app/data/...)
    text = re.sub(r'(/[a-zA-Z0-9_\-\.]+)+', '', text)
    
    return text.strip()


class BrandingEnforcer:
    """Garante consistência de marca em todas as respostas."""
    
    # Vocabulário proibido (case-insensitive)
    FORBIDDEN_TERMS = {
        r'\b(cérebro decisório|brain|planner|executor)\b': 'assistente',
        r'\bagente treq\b': 'Treq',
        r'\bSotreq\b': 'Treq',
        r'\bIA\b|\bAI\b': 'assistente inteligente',
        r'\bLLM\b|\bmodelo de linguagem\b': 'sistema',
    }
    
    @classmethod
    def sanitize(cls, text: str, context: str = "response") -> str:
        """Sanitiza resposta removendo terminologia técnica."""
        if not text or context == "thought":
            return text
        
        sanitized = text
        for pattern, replacement in cls.FORBIDDEN_TERMS.items():
            sanitized = re.sub(pattern, replacement, sanitized, flags=re.IGNORECASE)
        
        # Remove eventuais vazamentos de labels técnicos (ex: "Thought: ...")
        sanitized = re.sub(r'(Reasoning|Thought|Intent|Confidence):\s*[\w\s]+', '', sanitized)
        return sanitized.strip()


async def responder_node(state: AgentState) -> dict:
    """
    Gera a resposta final combinando contexto, tool outputs e decisões cognitivas.
    """
    logger.info("💬 RESPONDER: Gerando resposta final...")
    
    decision = state.get('current_decision')
    context = state.get('context', [])
    tool_outputs = state.get('tool_outputs', [])
    user_query = state['messages'][0].content
    
    # 1. Prioridade: Decisão Direta do Planner (Clarify ou Answer Directly)
    if decision:
        if decision.intent == "clarify":
            logger.info("💬 RESPONDER: Respondendo pedido de esclarecimento.")
            response = BrandingEnforcer.sanitize(decision.direct_response or decision.thought)
            return {
                "messages": [AIMessage(content=response)],
                "direct_response": response,
                "response_mode": "text"
            }
            
        if decision.intent == "answer_directly" and not context and not tool_outputs:
            logger.info("💬 RESPONDER: Respondendo diretamente (Chit-chat/Geral).")
            response = BrandingEnforcer.sanitize(decision.direct_response or decision.thought)
            return {
                "messages": [AIMessage(content=response)],
                "direct_response": response,
                "response_mode": "text"
            }

    # 2. Prioridade: Resultado de Ferramentas
    if tool_outputs:
        # Ação foi executada via ferramenta
        tool_result = tool_outputs[-1].get('result', {})
        response = BrandingEnforcer.sanitize(tool_result.get('message', 'Operação concluída com sucesso.'))
        logger.info("💬 RESPONDER: Resposta baseada em ferramentas.")
        # Determinar se deve suprimir o texto (Modo Tool)
        tool_name = tool_outputs[-1].get('tool')
        mode = "tool" if tool_name in ["jira_create_ticket", "slack_notify"] else "hybrid"
        
        return {
            "messages": [AIMessage(content=response)],
            "direct_response": response if mode != "tool" else "",
            "response_mode": mode
        }
        
    # 3. Prioridade: Contexto RAG
    if context:
        logger.info("💬 RESPONDER: Gerando resposta baseada em RAG...")
        try:
            from datetime import datetime
            import pytz
            
            tz = pytz.timezone('America/Sao_Paulo')
            now = datetime.now(tz)
            date_context = f"Hoje é {now.strftime('%d/%m/%Y %H:%M:%S')}. Usuário solicitou busca técnica."
            
            formatted_system_prompt = AGENT_SYSTEM_PROMPT.format(date_context=date_context)

            generated_response = llm_service.generate_with_context(
                user_query=user_query,
                context=context,
                system_prompt=formatted_system_prompt,
                query_type="agent_rag"
            )
            
            response = BrandingEnforcer.sanitize(sanitize_response(generated_response))
            return {
                "messages": [AIMessage(content=response)],
                "direct_response": response,
                "response_mode": "hybrid"
            }
            
        except Exception as e:
            logger.error(f"❌ RESPONDER: Erro ao gerar resposta RAG - {e}")
            return {
                "messages": [AIMessage(content="Tive um problema ao processar as informações técnicas. Pode tentar novamente?")],
                "response_mode": "text"
            }
    
    # 4. Fallback: Mensagem Padrão
    logger.warning("💬 RESPONDER: Nenhum conteúdo encontrado, usando fallback.")
    return {
        "messages": [AIMessage(content="Não consegui processar uma resposta adequada agora. Como posso te ajudar de outra forma?")],
        "response_mode": "text"
    }
