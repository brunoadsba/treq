"""
Detector de interações sociais que não precisam de RAG.
Detecta cumprimentos, perguntas sobre o assistente, agradecimentos, etc.
"""
from typing import Optional
from loguru import logger


def detect_social_interaction(query: str) -> Optional[str]:
    """
    Detecta interações sociais que não precisam de RAG.
    Retorna resposta direta ou None se não for social.
    
    Args:
        query: Texto da consulta do usuário
        
    Returns:
        Optional[str]: Resposta direta se for interação social, None caso contrário
    """
    query_lower = query.lower().strip()
    
    # PRIORIDADE: Se a query começa com "consultoria:", NÃO é interação social
    # Deve ser processada como consultoria normal
    if query_lower.startswith("consultoria:"):
        return None
    
    import re
    
    # Função auxiliar para busca exata de palavra/expressão
    def has_exact(pattern_list, text):
        for p in pattern_list:
            # \b garante que seja uma palavra completa
            if re.search(rf'\b{re.escape(p)}\b', text):
                return True
        return False

    # 1. Cumprimentos
    greetings = [
        "oi", "olá", "e aí", "hey", "hello",
        "bom dia", "boa tarde", "boa noite"
    ]
    if has_exact(greetings, query_lower):
        logger.info(f"Interação social detectada: cumprimento - '{query}'")
        return "Olá! Sou o Assistente Operacional da Treq. Como posso ajudar você hoje?"
    
    # 2. Perguntas sobre capacidades (análise de documentos)
    # REMOVIDO: Agora processado pelo query_classifier e context_handler para suportar contexto de anexo
    
    # 3. Perguntas sobre o assistente
    about_assistant = [
        "qual seu nome", "quem é você", "o que você faz", "você é",
        "como você se chama", "o que você pode fazer", "quais suas funções"
    ]
    if has_exact(about_assistant, query_lower):
        logger.info(f"Interação social detectada: pergunta sobre assistente - '{query}'")
        return (
            "Sou o Assistente Operacional da Treq. "
            "Posso ajudar com alertas operacionais, procedimentos, métricas e análise de causas. "
            "Também consigo analisar documentos (PDF, DOCX, PPTX, Excel) para extrair informações operacionais."
        )
    
    # 4. Agradecimentos
    thanks = ["obrigado", "obrigada", "valeu", "agradeço"]
    if has_exact(thanks, query_lower):
        logger.info(f"Interação social detectada: agradecimento - '{query}'")
        return "De nada! Estou aqui para ajudar. Precisa de mais alguma coisa?"
    
    # 5. Despedidas
    farewells = ["tchau", "até logo", "até mais", "até breve", "falou", "flw", "bye"]
    if has_exact(farewells, query_lower):
        logger.info(f"Interação social detectada: despedida - '{query}'")
        return "Até logo! Se precisar de mais alguma coisa, estarei aqui."
    
    # 6. Estado/Saúde
    how_are_you = ["como vai", "tudo bem", "tudo bom", "como está", "beleza", "tranquilo"]
    if has_exact(how_are_you, query_lower):
        operational_context = ["operação", "unidade", "métrica", "alerta", "procedimento"]
        if not has_exact(operational_context, query_lower):
            return "Tudo bem, obrigado por perguntar! Como posso ajudar você hoje?"
    
    return None

