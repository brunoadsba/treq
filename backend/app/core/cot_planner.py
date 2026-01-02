"""
Módulo Chain of Thought (CoT) Planner.
Responsável por gerar um plano de raciocínio estruturado antes da resposta final.
"""
import json
import re
from typing import Dict, Any, List, Optional
from loguru import logger
from app.services.llm_service import LLMService
from app.services.prompts import SYSTEM_PROMPTS

def _extract_json(text: str) -> Dict[str, Any]:
    """Extrai JSON de uma string de forma robusta, lidando com blocos markdown e prefixos."""
    try:
        # 1. Remover blocos markdown comuns e suas variantes
        content = re.sub(r'```(?:json|formato de dados|planilha|texto)?', '', text, flags=re.IGNORECASE)
        content = content.replace('```', '').strip()
        
        # 2. Encontrar os limites do objeto JSON {...}
        start_idx = content.find('{')
        end_idx = content.rfind('}')
        
        if start_idx != -1 and end_idx != -1:
            json_str = content[start_idx:end_idx+1]
            return json.loads(json_str)
        
        # 3. Fallback: tentar carregar o conteúdo limpo original
        return json.loads(content)
    except Exception as e:
        logger.warning(f"Falha na extração de JSON do CoT: {e}. Texto original: {text[:100]}...")
        raise e

async def generate_cot_plan(
    user_query: str,
    context: List[str],
    llm_service: LLMService,
    query_type: str = "general"
) -> Dict[str, Any]:
    """
    Gera um plano de raciocínio (Chain of Thought) para a query.
    
    Args:
        user_query: Pergunta do usuário.
        context: Lista de chunks de contexto recuperados.
        llm_service: Instância do serviço LLM.
        query_type: Tipo da query (opcional).

    Returns:
        Dict com o plano estruturado (intent, steps, strategy, etc).
        Retorna um plano default em caso de falha.
    """
    logger.info("🧠 Iniciando planejamento CoT...")
    
    # Preparar prompt
    # Buscar prompt específico do planner ou fallback (embora deva existir se o yaml foi criado)
    system_prompt = SYSTEM_PROMPTS.get("cot_planner", "")
    if not system_prompt:
        logger.warning("Prompt 'cot_planner' não encontrado. Usando fallback básico.")
        system_prompt = "Você é um planejador. Retorne JSON com {intent, reasoning_steps}."

    # Contexto formatado
    context_text = "\n---\n".join(context[:5]) # Limitar a 5 chunks para o planner ser rápido
    
    messages = [
        {"role": "system", "content": system_prompt},
        {"role": "user", "content": f"CONTEXTO:\n{context_text}\n\nQUERY USUÁRIO:\n{user_query}"}
    ]

    try:
        # Usar modelo rápido (Nível 1 - 8B) para o planejamento para baixa latência
        # Forçamos o uso do modelo 8B via parâmetro se possível, ou deixamos o seletor decidir
        # Como o prompt é complexo (JSON), talvez 70B seja mais seguro? 
        # Vamos tentar confiar no router, mas idealmente seria um modelo capaz de JSON mode.
        # O LLMService.generate_response usa configs.
        
        # Override temporário: usar modelo complexo se disponível para garantir JSON válido
        # Ou 8B com temperatura baixa. Vamos usar padrão (router decide based on query).
        # Para garantir JSON, vamos instruir "JSON mode" se a API suportar, mas aqui é via prompt.
        
        response_text = llm_service.generate_response(
            messages=messages,
            temperature=0.2, # Baixa temperatura para determinismo JSON
            max_tokens=300,  # Reduzido de 500 para menor latência
            stream=False,
            query_type="planning" # Isso pode acionar modelo mais inteligente no router se configurado
        )
        
        # Parse JSON
        if isinstance(response_text, str):
            plan = _extract_json(response_text)
            logger.info(f"🧠 Plano CoT gerado: {plan.get('intent')} | Status: {plan.get('context_status')}")
            return plan
        
        return _get_default_plan()
        
    except json.JSONDecodeError as e:
        logger.error(f"❌ Erro ao decodificar JSON do CoT Planner: {e}. Output: {response_text[:100]}...")
        return _get_default_plan(error="json_parse_error")
    except Exception as e:
        logger.error(f"❌ Erro no CoT Planner: {e}")
        return _get_default_plan(error=str(e))

def _get_default_plan(error: str = None) -> Dict[str, Any]:
    """Retorna um plano padrão em caso de erro."""
    return {
        "intent": "Responder ao usuário",
        "context_status": "UNKNOWN",
        "context_analysis": "Planejamento falhou, seguindo fluxo padrão.",
        "missing_info": [],
        "strategy": "DIRECT",
        "needs_visualization": False,
        "reasoning_steps": ["Analisar contexto", "Gerar resposta"],
        "error": error
    }
