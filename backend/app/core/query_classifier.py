"""
Classificador de queries para determinar o tipo de consulta.
Separa a lógica de classificação do gerenciamento de contexto.
"""
from typing import List
from loguru import logger
import re


def classify_query(query: str, message_history: List = None) -> str:
    """
    Classifica o tipo de consulta com detecção de padrões mais inteligente.
    
    Args:
        query: Texto da consulta
        message_history: Histórico de mensagens (opcional, para detectar follow-up)
        
    Returns:
        str: Tipo da consulta ("alerta", "procedimento", "métrica", "status", "detalhamento", "capacidade", "geral")
    """
    query_lower = query.lower().strip()
    message_history = message_history or []
    
    # 0. Detectar perguntas sobre CAPACIDADES DO ASSISTENTE (prioridade máxima)
    # Essas perguntas devem ser respondidas diretamente, sem buscar no RAG
    # EXCEÇÃO: Se for um comando direto ou anexo automático, NÃO é capacidade.
    if re.search(r"^(analise|leia|veja|processe|\[arquivo:)\s*(o\s+)?(arquivo|isso|imagem|foto|pdf)?", query_lower):
        logger.debug(f"Query identificada como COMANDO OU ANEXO, ignorando categoria capacidade: '{query}'")
    else:
        capability_patterns = [
            r"você\s+(é|está|pode|consegue|faz|realiza|analisa|extrai|lê|le)",
            r"(você|vc)\s+(pode|consegue|faz|realiza|analisa|extrai|lê|le)",
            r"que\s+tipo\s+(de\s+)?(arquivo|documento|formato)",
            r"quais\s+(tipos|formatos)\s+(de\s+)?(arquivo|documento)",
            r"você\s+(aceita|suporta|trabalha\s+com)",
            r"(é|está)\s+capaz\s+(de|de\s+extrair|de\s+ler|de\s+analisar)",
            r"capaz\s+(de|de\s+extrair|de\s+ler|de\s+analisar)",
            r"que\s+(você|vc)\s+(pode|consegue|faz)",
            r"o\s+que\s+(você|vc)\s+(pode|consegue|faz)",
            r"quais\s+(são\s+)?(suas\s+)?(capacidades|funcionalidades|recursos)",
        ]
        
        for pattern in capability_patterns:
            if re.search(pattern, query_lower):
                # Verificar se menciona arquivos/documentos/formats/imagens
                file_related_keywords = [
                    "arquivo", "documento", "pdf", "docx", "pptx", "excel", "xlsx",
                    "formato", "tipo", "extrair", "ler", "le", "analisar", "processar",
                    "imagem", "imagens", "jpeg", "jpg", "png", "gif", "bmp", "tiff", "webp",
                    "foto", "fotos", "fotografia", "ocr", "reconhecimento"
                ]
                if any(keyword in query_lower for keyword in file_related_keywords):
                    logger.debug(f"Query classificada como CAPACIDADE (sobre arquivos): '{query}'")
                    return "capacidade"
    
    # Verificar também no histórico se é follow-up sobre capacidades
    if message_history:
        last_assistant_msg = None
        for msg in reversed(message_history):
            if isinstance(msg, dict) and msg.get("role") == "assistant":
                last_assistant_msg = msg.get("content", "").lower()
                break
        
        if last_assistant_msg and any(keyword in last_assistant_msg for keyword in ["capacidade", "arquivo", "documento", "pdf", "formato", "imagem", "jpeg", "png"]):
            # Se a última resposta foi sobre capacidades e a query atual é uma continuação
            continuation_patterns = [
                r"e\s+(você|vc)\s+(pode|consegue|faz)",
                r"também\s+(pode|consegue|faz)",
                r"além\s+(disso|disso\s+você)",
                r"outros?\s+(tipos?|formatos?)",
            ]
            if any(re.search(pattern, query_lower) for pattern in continuation_patterns):
                logger.debug(f"Query classificada como CAPACIDADE (follow-up): '{query}'")
                return "capacidade"
    
    # 0. Detectar padrões temporais (antes de tudo, para identificar queries que precisam de dados reais)
    temporal_keywords = [
        "hoje", "agora", "atualmente", "neste momento", "no momento",
        "essa semana", "este mês", "neste mês", "esta semana",
        "nesta semana", "este ano", "neste ano"
    ]
    has_temporal = any(keyword in query_lower for keyword in temporal_keywords)
    
    # 1. Detectar perguntas sobre STATUS/ESTADO ATUAL (prioridade alta)
    # Primeiro, verificar padrões específicos de "status de/das" (não requerem contexto operacional)
    status_direct_patterns = [
        "status de ", "status das ", "status de todas ", "status das unidades ",
        "status operacional", "status das operações", "status geral"
    ]
    if any(pattern in query_lower for pattern in status_direct_patterns):
        # Se tem padrão temporal, classificar como status_temporal (requer tool)
        if has_temporal:
            logger.debug(f"Query classificada como STATUS_TEMPORAL: '{query}'")
            return "status_temporal"
        logger.debug(f"Query classificada como STATUS: '{query}'")
        return "status"
    
    # Depois, verificar outros padrões de status (requerem contexto operacional)
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
        "quantos", "qual o valor", "qual o número", "qual a métrica", "quais as métricas",
        "métrica de", "métricas de", "indicador", "indicadores",
        "mostre os dados", "dados de", "resultados de",
        "kpi", "performance", "desempenho", "valor de", "valor da"
    ]
    if any(pattern in query_lower for pattern in metric_patterns) or \
       (any(word in query_lower for word in ["métrica", "métricas", "indicador"]) and \
        any(op in query_lower for op in ["cancelamento", "atraso", "entrega", "estoque"])):
        # Se tem padrão temporal, classificar como métrica_temporal (requer tool)
        if has_temporal:
            logger.debug(f"Query classificada como MÉTRICA_TEMPORAL: '{query}'")
            return "metrica_temporal"
        logger.debug(f"Query classificada como MÉTRICA: '{query}'")
        return "metrica"
    
    # 3. Detectar PROCEDIMENTOS (antes de alertas - "como fazer" tem prioridade)
    # Padrões mais amplos para detectar procedimentos
    procedimento_patterns = [
        r"como\s+(fazer|executar|realizar|implementar|aplicar)",
        r"(qual|quais)\s+(?:são\s+)?(?:o|a|os|as)?\s*(procedimento|procedimentos|processo|processos|passo|passos|método|forma)",
        r"(passo\s+a\s+passo|passos\s+para|instruções\s+para)",
        r"como\s+(devo|devemos|posso|podemos)\s+",
        r"(procedimento|procedimentos|protocolo|processo)\s+(de|para|para fazer)",
        r"como\s+(fazer|executar|realizar)\s+\w+",  # "como fazer X" - captura qualquer ação
    ]
    
    for pattern in procedimento_patterns:
        if re.search(pattern, query_lower):
            logger.debug(f"Query classificada como PROCEDIMENTO (pattern: {pattern}): '{query}'")
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
    
    # 6. Detectar MODO CONSULTORIA (quando query começa com "consultoria:")
    if query_lower.startswith("consultoria:"):
        logger.debug(f"Query classificada como CONSULTORIA: '{query}'")
        return "consultoria"
    
    # 7. Detectar ALERTAS (após verificar procedimentos e detalhamento)
    alert_keywords = [
        "alerta", "problema", "erro", "falha", "incidente", "urgente",
        "crítico"
    ]
    # Não classificar como alerta se for claramente um procedimento
    # Verificar padrões de procedimento antes de classificar como alerta
    if any(re.search(pattern, query_lower) for pattern in procedimento_patterns):
        logger.debug(f"Query classificada como PROCEDIMENTO (antes de alerta): '{query}'")
        return "procedimento"
    
    if any(keyword in query_lower for keyword in alert_keywords):
        logger.debug(f"Query classificada como ALERTA: '{query}'")
        return "alerta"
    
    # 8. Verificar se menciona "como" mas não é procedimento (pode ser status)
    if "como" in query_lower:
        # Se menciona unidade/operação, provavelmente é status
        if any(word in query_lower for word in ["operação", "unidade", "salvador", "recife"]):
            logger.debug(f"Query classificada como STATUS (padrão 'como'): '{query}'")
            return "status"
    
    # 9. Padrão geral
    logger.debug(f"Query classificada como GERAL: '{query}'")
    return "geral"

