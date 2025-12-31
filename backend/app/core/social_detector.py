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
    
    # Cumprimentos
    greetings = [
        "oi", "olá", "olá", "e aí", "hey", "hello",
        "bom dia", "boa tarde", "boa noite",
        "bom dia!", "boa tarde!", "boa noite!"
    ]
    if any(greeting in query_lower for greeting in greetings):
        logger.info(f"Interação social detectada: cumprimento - '{query}'")
        return "Olá! Sou o Assistente Operacional da Treq. Como posso ajudar você hoje?"
    
    # Perguntas sobre capacidades do assistente (análise de documentos, tipos de arquivo)
    capability_keywords = [
        "arquivo", "documento", "pdf", "docx", "pptx", "excel", "xlsx",
        "extrair", "ler", "le", "analisar", "processar", "aceitar",
        "suporta", "trabalha com", "formato", "tipo de arquivo"
    ]
    capability_questions = [
        r"você\s+(é|está|pode|consegue|faz|realiza|analisa|extrai|lê|le)",
        r"(você|vc)\s+(pode|consegue|faz|realiza|analisa|extrai|lê|le)",
        r"que\s+tipo\s+(de\s+)?(arquivo|documento|formato)",
        r"quais\s+(tipos|formatos)\s+(de\s+)?(arquivo|documento)",
        r"você\s+(aceita|suporta|trabalha\s+com)",
        r"(é|está)\s+capaz\s+(de|de\s+extrair|de\s+ler|de\s+analisar)",
        r"capaz\s+(de|de\s+extrair|de\s+ler|de\s+analisar)",
    ]
    
    import re
    has_capability_keyword = any(keyword in query_lower for keyword in capability_keywords)
    matches_capability_pattern = any(re.search(pattern, query_lower) for pattern in capability_questions)
    
    if has_capability_keyword or matches_capability_pattern:
        logger.info(f"Interação detectada: pergunta sobre capacidades - '{query}'")
        return (
            "Sim, consigo analisar arquivos PDF, DOCX, PPTX e Excel (.xlsx, .xls). "
            "Meu foco é em informações operacionais como procedimentos, métricas e alertas. "
            "Por favor, envie o arquivo usando o botão de anexo na interface e me diga qual informação específica você gostaria de extrair."
        )
    
    # Perguntas sobre o assistente (genéricas)
    about_assistant = [
        "qual seu nome", "quem é você", "o que você faz", "você é",
        "qual é seu nome", "como você se chama", "quem é você",
        "o que você pode fazer", "quais suas funções"
    ]
    if any(phrase in query_lower for phrase in about_assistant):
        logger.info(f"Interação social detectada: pergunta sobre assistente - '{query}'")
        return (
            "Sou o Assistente Operacional da Treq. "
            "Posso ajudar com alertas operacionais, procedimentos, métricas e análise de causas. "
            "Também consigo analisar documentos (PDF, DOCX, PPTX, Excel) para extrair informações operacionais. "
            "O que você gostaria de saber?"
        )
    
    # Agradecimentos
    thanks = [
        "obrigado", "obrigada", "valeu", "agradeço",
        "muito obrigado", "muito obrigada", "obrigado!", "obrigada!",
        "agradeço muito", "valeu mesmo"
    ]
    if any(thanks_word in query_lower for thanks_word in thanks):
        logger.info(f"Interação social detectada: agradecimento - '{query}'")
        return "De nada! Estou aqui para ajudar. Precisa de mais alguma coisa?"
    
    # Despedidas
    farewells = [
        "tchau", "até logo", "até mais", "até breve",
        "falou", "flw", "bye", "até"
    ]
    if any(farewell in query_lower for farewell in farewells):
        logger.info(f"Interação social detectada: despedida - '{query}'")
        return "Até logo! Se precisar de mais alguma coisa, estarei aqui."
    
    # Perguntas genéricas de saúde/estado
    how_are_you = [
        "como vai", "tudo bem", "tudo bom", "como está",
        "e aí", "beleza", "tranquilo"
    ]
    # Mas só se não mencionar operação/unidade (para não confundir com "como está a operação")
    if any(phrase in query_lower for phrase in how_are_you):
        # Verificar se não menciona contexto operacional
        operational_context = [
            "operação", "operacional", "unidade", "salvador", "recife",
            "bahia", "pernambuco", "métrica", "alerta", "procedimento"
        ]
        if not any(context_word in query_lower for context_word in operational_context):
            logger.info(f"Interação social detectada: pergunta genérica - '{query}'")
            return "Tudo bem, obrigado por perguntar! Como posso ajudar você hoje?"
    
    return None  # Não é interação social, continuar com RAG

