"""
Detector de consultoria inicial (sem problema específico).
"""
from typing import Optional
from loguru import logger


def detect_initial_consultoria(query: str) -> bool:
    """
    Detecta se é uma consultoria inicial sem problema específico.
    
    IMPORTANTE: Apenas queries vazias após "consultoria:" são consideradas iniciais.
    Qualquer conteúdo específico deve ser processado como consultoria normal.
    
    Args:
        query: Texto da consulta do usuário
        
    Returns:
        bool: True se for consultoria inicial (apenas "consultoria:" vazio), False caso contrário
    """
    query_lower = query.lower().strip()
    
    # Se não começa com "consultoria:", não é consultoria
    if not query_lower.startswith("consultoria:"):
        return False
    
    # Remover prefixo "consultoria:" e espaços
    query_content = query_lower.replace("consultoria:", "").strip()
    
    # Apenas se o conteúdo estiver completamente vazio, é consultoria inicial
    # Qualquer conteúdo específico (mesmo genérico) deve ser processado pelo LLM
    is_initial = query_content == ""
    
    if is_initial:
        logger.info(f"Consultoria inicial detectada (query vazia): '{query}'")
    else:
        logger.info(f"Consultoria com conteúdo específico (não inicial): '{query}' - será processada pelo LLM")
    
    return is_initial


def get_initial_consultoria_response() -> str:
    """
    Retorna resposta inicial para consultoria.
    
    Returns:
        str: Pergunta inicial interativa
    """
    return (
        "Olá! Sou o Assistente Operacional da Treq. "
        "Em que posso ajudar você hoje?\n\n"
        "Posso ajudar com:\n"
        "• Análise de problemas operacionais\n"
        "• Sugestões estratégicas\n"
        "• Otimização de processos\n"
        "• Identificação de causas raiz\n\n"
        "Descreva sua situação ou dúvida e eu farei uma análise detalhada."
    )
