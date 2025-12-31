"""
Detector de insatisfação do usuário (feedback negativo).
"""
from typing import Optional
from loguru import logger
from app.core.context_manager import ContextManager


def detect_dissatisfaction(
    query: str, 
    context_manager: Optional[ContextManager] = None
) -> bool:
    """
    Detecta sinais de insatisfação do usuário na query atual ou no histórico.
    
    Args:
        query: Texto da consulta do usuário
        context_manager: ContextManager com histórico da conversa (opcional)
        
    Returns:
        bool: True se detectar insatisfação, False caso contrário
    """
    query_lower = query.lower().strip()
    
    # Padrões de insatisfação
    dissatisfaction_patterns = [
        "não gostei", "não gostou", "não foi isso", "não é isso",
        "não satisfeito", "não serve", "não ajuda", "não está certo",
        "está errado", "errado", "incorreto", "não entendi",
        "confuso", "não ficou claro", "mal explicado", "pode melhorar",
        "não é o que eu queria", "não resolve", "não responde",
        "falso positivo", "falso negativo", "não é o problema"
    ]
    
    # Verificar query atual
    is_dissatisfied = any(pattern in query_lower for pattern in dissatisfaction_patterns)
    
    # Se há histórico, verificar última resposta do assistente
    if context_manager and len(context_manager.message_history) > 0:
        # Pegar última resposta do assistente
        for msg in reversed(context_manager.message_history):
            if msg["role"] == "assistant":
                last_assistant = msg["content"].lower()
                # Se usuário responde negativamente após uma resposta, é insatisfação
                if is_dissatisfied:
                    logger.info(f"Insatisfação detectada após resposta do assistente: '{query}'")
                    break
    
    if is_dissatisfied:
        logger.info(f"Insatisfação detectada: '{query}'")
    
    return is_dissatisfied
