"""
Funções auxiliares para processamento de métricas.
"""
from typing import Dict, Any, List
from datetime import datetime, timedelta
from loguru import logger
import statistics


def calculate_period_filters(period: str) -> Dict[str, Any]:
    """
    Calcula filtros de data baseado no período.
    
    Args:
        period: Período ("today", "this_week", "this_month", "this_year")
        
    Returns:
        Dict com start_date e end_date, ou None se inválido
    """
    now = datetime.now()
    
    period_map = {
        "today": {
            "start_date": now.replace(hour=0, minute=0, second=0, microsecond=0).isoformat(),
            "end_date": now.isoformat()
        },
        "this_week": {
            "start_date": (now - timedelta(days=now.weekday())).replace(hour=0, minute=0, second=0, microsecond=0).isoformat(),
            "end_date": now.isoformat()
        },
        "this_month": {
            "start_date": now.replace(day=1, hour=0, minute=0, second=0, microsecond=0).isoformat(),
            "end_date": now.isoformat()
        },
        "this_year": {
            "start_date": now.replace(month=1, day=1, hour=0, minute=0, second=0, microsecond=0).isoformat(),
            "end_date": now.isoformat()
        }
    }
    
    return period_map.get(period.lower())


def extract_numeric_values(data: List[Dict[str, Any]], metric_name: str) -> List[float]:
    """
    Extrai valores numéricos dos registros.
    
    Args:
        data: Lista de registros
        metric_name: Nome da métrica (para buscar campos específicos)
        
    Returns:
        Lista de valores numéricos extraídos
    """
    values = []
    for record in data:
        # Tentar diferentes campos comuns para valores
        value = (
            record.get('valor') or 
            record.get('value') or 
            record.get(metric_name) or
            record.get('ticket_medio') or
            record.get('metric_value')
        )
        if value is not None:
            try:
                float_val = float(value)
                values.append(float_val)
            except (ValueError, TypeError):
                continue
    return values


def calculate_statistics(values: List[float]) -> Dict[str, float]:
    """
    Calcula estatísticas básicas de uma lista de valores.
    
    Args:
        values: Lista de valores numéricos
        
    Returns:
        Dict com mean, median, std_dev
    """
    if not values:
        return {"mean": 0.0, "median": 0.0, "std_dev": 0.0}
    
    mean = statistics.mean(values)
    median = statistics.median(values)
    std_dev = statistics.stdev(values) if len(values) > 1 else 0.0
    
    return {
        "mean": mean,
        "median": median,
        "std_dev": std_dev
    }


def calculate_deviation_level(deviation: float) -> tuple[str, str]:
    """
    Calcula nível de alerta baseado no desvio estatístico.
    
    Args:
        deviation: Desvio estatístico (número de desvios padrão)
        
    Returns:
        Tuple[alert_level, threshold_level]
    """
    abs_deviation = abs(deviation)
    
    if abs_deviation >= 3.0:
        return ("CRÍTICO", "Nível 2 (desvio grande - muito acima do normal)")
    elif abs_deviation >= 2.0:
        return ("ATENÇÃO", "Nível 1 (desvio moderado - acima do normal)")
    else:
        return ("NORMAL", "Dentro do normal")


def process_generic_metrics(data: List[Dict[str, Any]], metric_name: str) -> Dict[str, Any]:
    """
    Processa dados brutos e extrai valor da métrica com estatísticas básicas.
    
    Args:
        data: Lista de registros do Supabase
        metric_name: Nome da métrica
        
    Returns:
        Dict com valor processado da métrica, incluindo média, mediana, desvio padrão
    """
    # Extrair valores numéricos
    values = extract_numeric_values(data, metric_name)
    
    if not values:
        # Se não há valores numéricos, retornar estrutura básica
        return {
            "metric_name": metric_name,
            "value": len(data),
            "count": len(data),
            "records": data,
            "warning": "Nenhum valor numérico encontrado - retornando contagem de registros"
        }
    
    # Calcular estatísticas
    stats = calculate_statistics(values)
    mean = stats["mean"]
    std_dev = stats["std_dev"]
    
    # Valor atual (último valor ou média dos últimos valores)
    current_value = values[-1] if len(values) == 1 else statistics.mean(values[-3:]) if len(values) >= 3 else mean
    
    # Calcular desvio estatístico (se há desvio padrão)
    deviation_from_normal = None
    alert_level = None
    
    if std_dev > 0:
        deviation_from_normal = (current_value - mean) / std_dev
        alert_level, _ = calculate_deviation_level(deviation_from_normal)
    
    return {
        "metric_name": metric_name,
        "value": current_value,
        "mean": mean,
        "median": stats["median"],
        "std_dev": std_dev,
        "sigma_deviation": deviation_from_normal,  # Mantido para compatibilidade
        "deviation_from_normal": deviation_from_normal,
        "alert_level": alert_level or "NORMAL",
        "count": len(values),
        "records": data
    }
