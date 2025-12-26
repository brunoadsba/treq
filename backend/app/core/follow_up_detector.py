"""
Detector de follow-up questions (perguntas de continuação da conversa).
"""
from typing import Optional
from loguru import logger
from app.core.context_manager import ContextManager


def detect_follow_up(query: str, context_manager: ContextManager) -> bool:
    """
    Detecta se é uma pergunta de follow-up (continuação da conversa).
    
    Args:
        query: Texto da consulta do usuário
        context_manager: ContextManager com histórico da conversa
        
    Returns:
        bool: True se for follow-up, False caso contrário
    """
    # Verificar se há histórico de conversa
    if len(context_manager.message_history) == 0:
        return False
    
    query_lower = query.lower().strip()
    
    # Padrões de follow-up
    follow_up_patterns = [
        "detalhe", "mais detalhes", "mais informações", "explique",
        "o que significa", "o que é", "como funciona", "me diga mais",
        "detalhe isso", "explique isso", "o que quer dizer",
        "forneça mais", "mostre mais", "apresente mais",
        "conte mais", "fale mais sobre"
    ]
    
    # Verificar se contém padrões de follow-up
    is_follow_up = any(pattern in query_lower for pattern in follow_up_patterns)
    
    if is_follow_up:
        logger.info(f"Follow-up question detectada: '{query}'")
    
    return is_follow_up


def expand_query_with_context(
    query: str,
    context_manager: ContextManager,
    max_context_length: int = 300
) -> str:
    """
    Expande query com contexto da conversa anterior E entidades específicas.
    
    Args:
        query: Query atual do usuário
        context_manager: ContextManager com histórico
        max_context_length: Tamanho máximo do contexto a incluir
        
    Returns:
        str: Query expandida com contexto e entidades
    """
    # Extrair entidades da query atual PRIMEIRO
    entities = context_manager.extract_entities(query)
    
    # Construir partes da query expandida
    expanded_parts = [query]
    
    # Adicionar período se detectado (importante para busca RAG)
    if entities.get("period"):
        month = entities["period"]["month"]
        year = entities["period"]["year"]
        month_names = {
            1: "janeiro", 2: "fevereiro", 3: "março", 4: "abril",
            5: "maio", 6: "junho", 7: "julho", 8: "agosto",
            9: "setembro", 10: "outubro", 11: "novembro", 12: "dezembro"
        }
        month_name = month_names.get(month, f"mês {month}")
        expanded_parts.append(f"período {month_name} {year}")
        logger.debug(f"Query expandida: adicionado período {month_name} {year}")
    
    # Adicionar unidade se detectada
    if entities.get("unit"):
        expanded_parts.append(f"unidade {entities['unit']}")
        logger.debug(f"Query expandida: adicionada unidade {entities['unit']}")
    
    # Adicionar contexto da conversa anterior (se houver histórico)
    if len(context_manager.message_history) > 0:
        # Pegar última resposta do assistente
        last_assistant_msg = None
        for msg in reversed(context_manager.message_history):
            if msg["role"] == "assistant":
                last_assistant_msg = msg["content"]
                break
        
        if last_assistant_msg:
            # Extrair termos importantes da resposta anterior
            context_snippet = last_assistant_msg[:max_context_length]
            expanded_parts.append(f"contexto anterior: {context_snippet}")
    
    expanded_query = " ".join(expanded_parts)
    logger.debug(f"Query expandida com contexto e entidades: {len(expanded_query)} caracteres")
    
    return expanded_query

