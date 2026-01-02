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
    capability_keywords = [
        "arquivo", "documento", "pdf", "docx", "pptx", "excel", "xlsx",
        "extrair", "ler", "analisar", "processar", "aceitar",
        "suporta", "trabalha com", "formato", "tipo de arquivo"
    ]
    capability_questions = [
        r"você\s+(é|está|pode|consegue|faz|realiza|analisa|extrai|lê|le)",
        r"(você|vc)\s+(pode|consegue|faz|realiza|analisa|extrai|lê|le)",
        r"que\s+tipo\s+(de\s+)?(arquivo|documento|formato)",
        r"quais\s+(tipos|formatos)\s+(de\s+)?(arquivo|documento)",
        r"você\s+(aceita|suporta|trabalha\s+com)",
        r"(é|está)\s+capaz\s+(de|de\s+extrair|de\s+ler|de\s+analisar)",
    ]
    
    if has_exact(capability_keywords, query_lower) or any(re.search(p, query_lower) for p in capability_questions):
        logger.info(f"Interação detectada: pergunta sobre capacidades - '{query}'")
        return (
            "Sim, consigo analisar arquivos PDF, DOCX, PPTX e Excel (.xlsx, .xls). "
            "Meu foco é em informações operacionais como procedimentos, métricas e alertas. "
            "Por favor, envie o arquivo usando o botão de anexo na interface e me diga qual informação específica você gostaria de extrair."
        )
    
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

