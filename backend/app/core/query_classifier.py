"""
Classificador de queries para determinar o tipo de consulta.
Separa a lógica de classificação do gerenciamento de contexto.
"""
from typing import List
from loguru import logger


def classify_query(query: str, message_history: List = None) -> str:
    """
    Classifica o tipo de consulta com detecção de padrões mais inteligente.
    
    Args:
        query: Texto da consulta
        message_history: Histórico de mensagens (opcional, para detectar follow-up)
        
    Returns:
        str: Tipo da consulta ("alerta", "procedimento", "métrica", "status", "detalhamento", "geral")
    """
    query_lower = query.lower().strip()
    message_history = message_history or []
    
    # 0. Detectar padrões temporais (antes de tudo, para identificar queries que precisam de dados reais)
    temporal_keywords = [
        "hoje", "agora", "atualmente", "neste momento", "no momento",
        "essa semana", "este mês", "neste mês", "esta semana",
        "nesta semana", "este ano", "neste ano"
    ]
    has_temporal = any(keyword in query_lower for keyword in temporal_keywords)
    
    # 1. Detectar perguntas sobre STATUS/ESTADO ATUAL (prioridade alta)
    status_patterns = [
        "como está", "como vai", "qual o status", "qual a situação",
        "está funcionando", "está ativo", "está ok", "tem problema",
        "está tudo bem", "está tudo certo", "há problema", "tem alerta",
        "forneça o resultado do status", "forneça o status", "mostre o status",
        "apresente o status", "dê o status", "me dê o status"
    ]
    if any(pattern in query_lower for pattern in status_patterns):
        # Verificar se menciona operação/unidade (não é apenas cumprimento)
        operational_context = [
            "operação", "operacional", "unidade", "salvador", "recife",
            "bahia", "pernambuco", "métrica", "alerta", "procedimento",
            "logística", "entrega", "pedido", "cancelamento"
        ]
        if any(context_word in query_lower for context_word in operational_context):
            # Se tem padrão temporal, classificar como status_temporal (requer tool)
            if has_temporal:
                logger.debug(f"Query classificada como STATUS_TEMPORAL: '{query}'")
                return "status_temporal"
            logger.debug(f"Query classificada como STATUS: '{query}'")
            return "status"
    
    # 1.1. Detectar queries imperativas sobre status/resultado
    imperative_patterns = [
        "forneça", "mostre", "apresente", "dê", "me dê", "apresente"
    ]
    if any(pattern in query_lower for pattern in imperative_patterns):
        # Verificar se menciona status/resultado/dados
        status_keywords = ["status", "resultado", "dados", "informações", "situação"]
        operational_context = [
            "operação", "operacional", "unidade", "salvador", "recife",
            "bahia", "pernambuco"
        ]
        if any(keyword in query_lower for keyword in status_keywords):
            if any(context_word in query_lower for context_word in operational_context):
                logger.debug(f"Query classificada como STATUS (imperativa): '{query}'")
                return "status"
    
    # 2. Detectar perguntas sobre MÉTRICAS/DADOS
    # IMPORTANTE: Verificar padrões temporais ANTES de classificar como métrica geral
    temporal_keywords = [
        "hoje", "agora", "atualmente", "neste momento", "no momento",
        "essa semana", "este mês", "neste mês", "esta semana",
        "nesta semana", "este ano", "neste ano"
    ]
    has_temporal = any(keyword in query_lower for keyword in temporal_keywords)
    
    metric_patterns = [
        "quantos", "qual o valor", "qual o número", "qual a métrica",
        "mostre os dados", "dados de", "resultados de", "indicador",
        "kpi", "performance", "desempenho"
    ]
    if any(pattern in query_lower for pattern in metric_patterns):
        # Se tem padrão temporal, classificar como métrica_temporal (requer tool)
        if has_temporal:
            logger.debug(f"Query classificada como MÉTRICA_TEMPORAL: '{query}'")
            return "metrica_temporal"
        logger.debug(f"Query classificada como MÉTRICA: '{query}'")
        return "metrica"
    
    # 3. Detectar PROCEDIMENTOS (antes de alertas - "como fazer" tem prioridade)
    if "como fazer" in query_lower:
        # Verificar se menciona ação específica
        action_keywords = [
            "contenção", "resolver", "corrigir", "implementar",
            "procedimento", "passo", "instrução", "processo"
        ]
        if any(keyword in query_lower for keyword in action_keywords):
            logger.debug(f"Query classificada como PROCEDIMENTO: '{query}'")
            return "procedimento"
    
    # 4. Detectar queries sobre unidades específicas (deve ser status executivo)
    # IMPORTANTE: Verificar ANTES de alertas/detalhamento para evitar classificação incorreta
    unit_keywords = ["salvador", "recife", "bahia", "pernambuco", "unidade"]
    query_about_unit_patterns = [
        "fale sobre", "fale de", "conte sobre", "sobre", "informações sobre",
        "status de", "situação de", "como está"
    ]
    # Se menciona padrão de consulta sobre unidade E menciona unidade específica
    if any(pattern in query_lower for pattern in query_about_unit_patterns):
        if any(unit in query_lower for unit in unit_keywords):
            # Se menciona período específico, pode ser detalhamento (verificar depois)
            # Mas se NÃO menciona período, é status executivo
            has_period = any(month in query_lower for month in [
                "janeiro", "fevereiro", "março", "abril", "maio", "junho",
                "julho", "agosto", "setembro", "outubro", "novembro", "dezembro"
            ])
            if not has_period:
                logger.debug(f"Query classificada como STATUS (sobre unidade): '{query}'")
                return "status"
    
    # 5. Detectar DETALHAMENTO (pedidos de mais informações sobre algo mencionado)
    # IMPORTANTE: Verificar ANTES de alertas para evitar classificação incorreta
    # Agora só captura se for claramente um pedido de detalhamento E menciona período específico
    detalhamento_patterns = [
        "detalhe", "detalhes", "mais detalhes", "mais informações", "explique",
        "o que significa", "o que é", "como funciona", "me diga mais",
        "detalhe isso", "explique isso", "o que quer dizer",
        "forneça mais", "mostre mais", "apresente mais",
        "quais são os detalhes", "quais são as informações", "quais são os problemas"
    ]
    # Remover "fale mais sobre" e "conte mais" dos padrões (já tratado acima como status)
    if any(pattern in query_lower for pattern in detalhamento_patterns):
        # Verificar se menciona período específico OU há histórico de conversa (follow-up)
        has_period = any(month in query_lower for month in [
            "janeiro", "fevereiro", "março", "abril", "maio", "junho",
            "julho", "agosto", "setembro", "outubro", "novembro", "dezembro"
        ])
        # Detalhamento requer período específico OU ser follow-up claro
        if has_period or len(message_history) > 0:
            logger.debug(f"Query classificada como DETALHAMENTO: '{query}'")
            return "detalhamento"
    
    # 6. Detectar ALERTAS (após verificar procedimentos e detalhamento)
    alert_keywords = [
        "alerta", "problema", "erro", "falha", "incidente", "urgente",
        "crítico"
    ]
    # Não classificar como alerta se for claramente um procedimento
    if "emergência" in query_lower and "como fazer" in query_lower:
        # "como fazer contenção de emergência" é procedimento, não alerta
        logger.debug(f"Query classificada como PROCEDIMENTO (emergência + como fazer): '{query}'")
        return "procedimento"
    
    if any(keyword in query_lower for keyword in alert_keywords):
        logger.debug(f"Query classificada como ALERTA: '{query}'")
        return "alerta"
    
    # 7. Verificar se menciona "como" mas não é procedimento (pode ser status)
    if "como" in query_lower:
        # Se menciona unidade/operação, provavelmente é status
        if any(word in query_lower for word in ["operação", "unidade", "salvador", "recife"]):
            logger.debug(f"Query classificada como STATUS (padrão 'como'): '{query}'")
            return "status"
    
    # 8. Padrão geral
    logger.debug(f"Query classificada como GERAL: '{query}'")
    return "geral"

