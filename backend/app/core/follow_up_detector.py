"""
Detector de follow-up questions (perguntas de continuação da conversa).
"""
from typing import Optional
from loguru import logger
from app.core.context_manager import ContextManager


def detect_follow_up(query: str, context_manager: ContextManager) -> bool:
    """
    Detecta se é uma pergunta de follow-up (continuação da conversa).
    Usa análise contextual mais inteligente baseada no histórico da conversa.
    
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
    
    # Padrões explícitos de follow-up
    explicit_follow_up_patterns = [
        "detalhe", "mais detalhes", "mais informações", "explique",
        "o que significa", "o que é", "como funciona", "me diga mais",
        "detalhe isso", "explique isso", "o que quer dizer",
        "forneça mais", "mostre mais", "apresente mais",
        "conte mais", "fale mais sobre", "e sobre", "e quanto a",
        "e o que", "e como", "e qual", "e quais"
    ]
    
    # Verificar padrões explícitos primeiro
    is_explicit_follow_up = any(pattern in query_lower for pattern in explicit_follow_up_patterns)
    
    if is_explicit_follow_up:
        logger.info(f"Follow-up explícito detectado: '{query}'")
        return True
    
    # Análise contextual: verificar se a query referencia tópicos da conversa anterior
    if len(context_manager.message_history) > 0:
        # Extrair tópicos principais das últimas mensagens
        recent_topics = []
        for msg in context_manager.message_history[-3:]:  # Últimas 3 mensagens
            if isinstance(msg, dict):
                content = msg.get("content", "").lower()
                # Extrair palavras-chave importantes (nomes próprios, termos técnicos)
                important_keywords = [
                    "salvador", "recife", "bahia", "pernambuco",
                    "alerta", "procedimento", "métrica", "status",
                    "pdf", "documento", "arquivo", "excel",
                    "entrega", "pedido", "cancelamento", "frota"
                ]
                for keyword in important_keywords:
                    if keyword in content and keyword not in recent_topics:
                        recent_topics.append(keyword)
        
        # Verificar se a query atual menciona tópicos da conversa anterior
        if recent_topics:
            mentions_previous_topic = any(topic in query_lower for topic in recent_topics)
            if mentions_previous_topic:
                # Verificar se é uma continuação (não uma nova pergunta completamente diferente)
                continuation_indicators = [
                    "e", "também", "além", "outro", "outra", "outros", "outras",
                    "qual", "quais", "como", "quando", "onde", "por que", "porque"
                ]
                has_continuation = any(indicator in query_lower.split()[:3] for indicator in continuation_indicators)
                
                if has_continuation:
                    logger.info(f"Follow-up contextual detectado (tópico: {recent_topics}): '{query}'")
                    return True
    
    # Verificar se a query é muito curta e há contexto anterior (provavelmente follow-up)
    if len(query_lower.split()) <= 4 and len(context_manager.message_history) > 0:
        # Queries curtas após conversa são geralmente follow-ups
        short_query_indicators = ["isso", "isso aí", "aquilo", "ele", "ela", "eles", "elas"]
        if any(indicator in query_lower for indicator in short_query_indicators):
            logger.info(f"Follow-up curto detectado: '{query}'")
            return True
    
    return False


def expand_query_with_context(
    query: str,
    context_manager: ContextManager,
    max_context_length: int = 300
) -> str:
    """
    Expande query com contexto da conversa anterior E entidades específicas.
    Usa análise mais inteligente do histórico para melhorar a busca RAG.
    
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
    
    # Adicionar contexto da conversa anterior (análise mais inteligente)
    if len(context_manager.message_history) > 0:
        # Extrair tópicos principais das últimas mensagens (usuário e assistente)
        recent_topics = []
        last_user_query = None
        last_assistant_msg = None
        
        for msg in reversed(context_manager.message_history[-4:]):  # Últimas 4 mensagens
            if isinstance(msg, dict):
                role = msg.get("role")
                content = msg.get("content", "").lower()
                
                if role == "user" and not last_user_query:
                    last_user_query = content
                elif role == "assistant" and not last_assistant_msg:
                    last_assistant_msg = content
                
                # Extrair palavras-chave importantes
                important_keywords = [
                    "salvador", "recife", "bahia", "pernambuco",
                    "alerta", "procedimento", "métrica", "status",
                    "pdf", "documento", "arquivo", "excel",
                    "entrega", "pedido", "cancelamento", "frota",
                    "motorista", "veículo", "rota", "logística"
                ]
                for keyword in important_keywords:
                    if keyword in content and keyword not in recent_topics:
                        recent_topics.append(keyword)
        
        # Se há tópicos recentes, adicionar ao contexto expandido
        if recent_topics:
            expanded_parts.append(f"contexto: {', '.join(recent_topics[:5])}")  # Máximo 5 tópicos
        
        # Se a última mensagem do usuário menciona algo específico, incluir
        if last_user_query:
            # Extrair termos principais da última pergunta do usuário
            query_words = last_user_query.split()
            # Filtrar palavras muito comuns
            stop_words = ["o", "a", "os", "as", "de", "da", "do", "das", "dos", "em", "no", "na", "nos", "nas", "para", "com", "que", "qual", "quais", "como", "quando", "onde", "por", "é", "são", "foi", "ser", "estar"]
            important_words = [w for w in query_words if len(w) > 3 and w not in stop_words][:3]
            if important_words:
                expanded_parts.append(f"pergunta anterior: {' '.join(important_words)}")
        
        # Adicionar snippet da última resposta do assistente (se relevante)
        if last_assistant_msg:
            # Extrair apenas termos-chave, não o texto completo
            context_snippet = last_assistant_msg[:max_context_length]
            # Remover palavras muito comuns para focar no conteúdo
            expanded_parts.append(f"resposta anterior mencionou: {context_snippet}")
    
    expanded_query = " ".join(expanded_parts)
    logger.debug(f"Query expandida com contexto inteligente: {len(expanded_query)} caracteres")
    
    return expanded_query

