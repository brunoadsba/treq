"""
Extrator de parâmetros para Tools a partir de queries do usuário.
Extrai nome de métrica, período temporal, unidade, etc.
"""
import re
from typing import Dict, Any, Optional
from datetime import datetime
from loguru import logger


def extract_metric_name(query: str) -> Optional[str]:
    """
    Extrai nome da métrica da query do usuário.
    
    Exemplos:
    - "Quantos pedidos cancelados temos hoje?" → "pedidos_cancelados"
    - "Qual o número de entregas atrasadas?" → "entregas_atrasadas"
    - "Quantas entregas no prazo essa semana?" → "entregas_no_prazo"
    
    Args:
        query: Query do usuário
        
    Returns:
        str: Nome da métrica normalizado (snake_case) ou None se não encontrado
    """
    query_lower = query.lower().strip()
    
    # Padrões melhorados para capturar métricas compostas (até 3 palavras)
    patterns = [
        # "quantos X Y [Z]" - captura até 3 palavras após "quantos", antes de verbo/período
        r"quantos?\s+(\w+(?:\s+\w+){0,2}?)\s+(?:temos|há|existe|tem|foram|estão|essa|este|hoje)",
        r"quantas?\s+(\w+(?:\s+\w+){0,2}?)\s+(?:temos|há|existe|tem|foram|estão|essa|este|hoje)",
        # "qual o número de X Y [Z]" - captura até 3 palavras após "de" (inclui até ?)
        r"qual\s+(?:o\s+)?(?:número|quantidade|valor)\s+(?:de\s+)?(\w+(?:\s+\w+){0,2}?)(?:\?|$)",
        # "mostre os dados de X Y [Z]"
        r"(?:mostre\s+os\s+)?dados\s+de\s+(\w+(?:\s+\w+){0,2}?)",
        # "X Y [Z] em/no/na" - captura até 3 palavras antes de preposição
        r"(\w+(?:\s+\w+){0,2}?)\s+(?:em|no|na|durante)\s+",
    ]
    
    for pattern in patterns:
        match = re.search(pattern, query_lower)
        if match:
            metric_text = match.group(1).strip()
            metric_name = _normalize_metric_name(metric_text)
            logger.debug(f"Métrica extraída: '{metric_text}' → '{metric_name}'")
            return metric_name
    
    # Fallback: buscar palavras-chave e capturar modificadores seguintes
    keywords = ["pedidos", "entregas", "cancelamentos", "atrasos", "alertas"]
    for keyword in keywords:
        if keyword in query_lower:
            # Capturar keyword + até 2 palavras seguintes (ex: "entregas atrasadas", "entregas no prazo")
            # Buscar padrão: keyword + palavra(s) seguintes até encontrar verbo, período ou fim
            pattern = rf"{keyword}\s+(\w+(?:\s+\w+)?)(?:\s+(?:temos|há|existe|tem|foram|estão|essa|este|hoje|semana|mês|ano|[?]))?"
            match = re.search(pattern, query_lower)
            if match and match.group(1):
                modifier = match.group(1).strip()
                metric_name = f"{keyword}_{modifier.replace(' ', '_')}"
            else:
                metric_name = keyword
            metric_name = _normalize_metric_name(metric_name)
            logger.debug(f"Métrica extraída (fallback): '{metric_name}'")
            return metric_name
    
    logger.warning(f"Não foi possível extrair nome de métrica da query: '{query}'")
    return None


def extract_temporal_period(query: str, entities: Optional[Dict[str, Any]] = None) -> str:
    """
    Extrai período temporal da query e mapeia para formato da Tool.
    Exemplos: "hoje" → "today", "essa semana" → "this_week", "este mês" → "this_month"
    """
    query_lower = query.lower().strip()
    
    # Mapeamento direto de palavras temporais (ordem: específico → geral)
    temporal_map = [
        ("essa semana", "this_week"), ("esta semana", "this_week"), ("nesta semana", "this_week"),
        ("este mês", "this_month"), ("neste mês", "this_month"),
        ("este ano", "this_year"), ("neste ano", "this_year"),
        ("hoje", "today"), ("agora", "today"), ("atualmente", "today"),
        ("neste momento", "today"), ("no momento", "today"),
    ]
    
    # Verificar mapeamento direto (buscar mais específico primeiro)
    for keyword, period in temporal_map:
        if keyword in query_lower:
            logger.debug(f"Período temporal extraído: '{keyword}' → '{period}'")
            return period
    
    # Verificar entities para período específico (mês/ano)
    if entities and entities.get("period"):
        period_info = entities["period"]
        current_date = datetime.now()
        if period_info.get("month") == current_date.month and period_info.get("year") == current_date.year:
            logger.debug(f"Período temporal extraído: mês atual → 'this_month'")
            return "this_month"
        logger.debug(f"Período temporal extraído: mês específico → 'this_month'")
        return "this_month"
    
    logger.debug(f"Período temporal não detectado, usando default: 'today'")
    return "today"


def extract_tool_params(
    query: str, query_type: str, entities: Optional[Dict[str, Any]] = None
) -> Dict[str, Any]:
    """
    Extrai todos os parâmetros necessários para executar uma Tool.
    Retorna dict com: metric_name, period, unit (se aplicável)
    """
    params: Dict[str, Any] = {}
    
    # Extrair nome da métrica (se aplicável)
    if query_type in ["metrica", "metrica_temporal", "status_temporal"]:
        metric_name = extract_metric_name(query)
        if metric_name:
            params["metric_name"] = metric_name
    
    # Extrair período temporal
    period = extract_temporal_period(query, entities)
    params["period"] = period
    
    # Extrair unidade (se disponível nas entities)
    if entities and entities.get("unit"):
        params["unit"] = entities["unit"]
    
    logger.info(f"Parâmetros extraídos para Tool: {params}")
    return params


def _normalize_metric_name(text: str) -> str:
    """
    Normaliza nome de métrica para snake_case preservando acentos.
    
    Exemplos:
    - "pedidos cancelados" → "pedidos_cancelados"
    - "entregas no prazo" → "entregas_no_prazo"
    - "alertas críticos" → "alertas_críticos"
    
    Args:
        text: Texto da métrica
        
    Returns:
        str: Nome normalizado em snake_case
    """
    # Se já tem underscores, separar
    if '_' in text:
        words = [w for part in text.split('_') for w in part.split()]
    else:
        words = text.split()
    
    # Remover artigos e preposições comuns (exceto "no" se parte de expressão como "no prazo")
    stop_words = {"de", "da", "do", "das", "dos", "em", "na", "nos", "nas", "a", "o", "as", "os"}
    filtered_words = []
    for i, w in enumerate(words):
        w_lower = w.lower()
        # Manter "no" se seguido de palavra significativa (ex: "no prazo", "no tempo")
        if w_lower == "no" and i + 1 < len(words) and len(words[i+1]) > 2:
            filtered_words.append(w_lower)
        elif w_lower not in stop_words:
            filtered_words.append(w_lower)
    
    if not filtered_words:
        filtered_words = [w.lower() for w in words if len(w) > 0]
    
    # Juntar com underscore e limpar caracteres inválidos (mas manter acentos)
    normalized = "_".join(filtered_words)
    # Manter letras (incluindo acentuadas), números e underscore
    normalized = re.sub(r'[^\w\u00C0-\u00FF]', '', normalized, flags=re.UNICODE)
    
    return normalized.lower() if normalized else "_".join(w.lower() for w in filtered_words if w)

