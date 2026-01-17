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


async def responder_node(state: AgentState) -> dict:
    """
    Gera a resposta final combinando contexto e tool outputs.
    
    Args:
        state: Estado atual do agente
        
    Returns:
        dict com mensagem de resposta final
    """
    logger.info("💬 RESPONDER: Gerando resposta final...")
    
    context = state.get('context', [])
    tool_outputs = state.get('tool_outputs', [])
    user_query = state['messages'][0].content
    
    # Construir prompt baseado no que temos
    # Construir prompt baseado no que temos
    if tool_outputs:
        # Ação foi executada via ferramenta
        tool_result = tool_outputs[-1].get('result', {})
        response = f"Ação realizada: {tool_result.get('message', 'Operação concluída')}"
        
    elif state.get("next_action") == "respond":
        # Resposta direta (Greeting/Chit-chat)
        response = "Olá! Sou o Treq, seu Assistente Operacional. Como posso ajudar com os procedimentos e status das unidades hoje?"
        
    elif context:
        # Resposta baseada em RAG via LLM
        try:
            # Injetar contexto temporal
            from datetime import datetime
            import pytz
            
            tz = pytz.timezone('America/Sao_Paulo')
            now = datetime.now(tz)
            date_context = f"Hoje é {now.strftime('%d/%m/%Y')}, dia da semana: {now.strftime('%A')}. Hora atual: {now.strftime('%H:%M')}."
            
            formatted_system_prompt = AGENT_SYSTEM_PROMPT.format(date_context=date_context)

            generated_response = llm_service.generate_with_context(
                user_query=user_query,
                context=context,
                system_prompt=formatted_system_prompt,
                query_type="agent_rag"
            )
            
            # Aplicar filtro pós-recuperação
            response = sanitize_response(generated_response)
            
        except Exception as e:
            logger.error(f"❌ Erro ao gerar resposta LLM: {e}")
            response = "Tive um problema ao processar sua resposta. Por favor, tente novamente."
        
    else:
        response = "Não encontrei informações relevantes para sua pergunta nos meus manuais. Poderia reformular?"
    
    logger.info("💬 RESPONDER: Resposta gerada")
    
    return {
        "messages": [AIMessage(content=response)]
    }
