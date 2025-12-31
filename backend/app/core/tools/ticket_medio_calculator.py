"""
Calculador específico para ticket médio com análise estatística avançada.
"""
from typing import Dict, Any, List, Optional
from datetime import datetime, timedelta
from loguru import logger
import statistics

from app.core.tools.metrics_utils import (
    calculate_period_filters,
    extract_numeric_values,
    calculate_deviation_level
)


def calculate_ticket_medio_stats(
    data: List[Dict[str, Any]],
    period: str,
    unit: Optional[str],
    supabase_client: Any
) -> Dict[str, Any]:
    """
    Calcula estatísticas específicas para ticket médio com análise de desvio estatístico.
    
    Usa janela histórica de 12 meses (ou disponível) para comparar valores atuais com a média histórica.
    Aplica thresholds do playbook: Nível 1 (desvio moderado) e Nível 2 (desvio grande).
    
    Args:
        data: Dados do período atual
        period: Período atual ("today", "this_week", "this_month", "this_year")
        unit: Unidade específica (opcional)
        supabase_client: Cliente Supabase para buscar dados históricos
        
    Returns:
        Dict com estatísticas completas incluindo análise de desvio estatístico
    """
    try:
        # Buscar dados históricos (12 meses) para comparação estatística
        now = datetime.now()
        current_period_start = calculate_period_filters(period)
        historical_start = (now - timedelta(days=365)).replace(day=1, hour=0, minute=0, second=0, microsecond=0)
        
        # Calcular data de corte para histórico (antes do período atual)
        current_start_dt = _extract_start_date(current_period_start, now)
        
        # Buscar dados históricos
        historical_data = _fetch_historical_data(
            supabase_client,
            historical_start,
            current_start_dt,
            unit
        )
        
        # Separar valores históricos e atuais
        historical_values, current_values = _separate_historical_and_current(
            historical_data,
            data,
            current_start_dt
        )
        
        # Garantir que há dados históricos suficientes
        if not historical_values or len(historical_values) < 2:
            historical_values, current_values = _fallback_values_split(data)
            if not historical_values or len(historical_values) < 2:
                return {
                    "metric_name": "ticket_medio",
                    "error": "Dados insuficientes para cálculo estatístico (mínimo 2 períodos históricos necessários)",
                    "count": len(data),
                    "value": len(data)
                }
        
        # Calcular estatísticas
        hist_mean = statistics.mean(historical_values)
        hist_std = statistics.stdev(historical_values) if len(historical_values) > 1 else 0
        
        # Valor atual (média do período atual ou último valor)
        current_mean = statistics.mean(current_values) if current_values else (
            historical_values[-1] if historical_values else hist_mean
        )
        
        # Calcular desvio estatístico
        deviation_from_normal = None
        alert_level = "NORMAL"
        threshold_level = "Dados insuficientes para análise"
        
        if hist_std > 0:
            deviation_from_normal = (current_mean - hist_mean) / hist_std
            alert_level, threshold_level = calculate_deviation_level(deviation_from_normal)
        
        # Mensagem formatada
        formatted_message = _format_ticket_medio_message(
            current_mean,
            hist_mean,
            deviation_from_normal,
            alert_level,
            threshold_level
        )
        
        return {
            "metric_name": "ticket_medio",
            "value": current_mean,
            "current_value": current_mean,
            "historical_mean": hist_mean,
            "historical_std": hist_std,
            "sigma_deviation": deviation_from_normal,  # Mantido para compatibilidade
            "deviation_from_normal": deviation_from_normal,
            "alert_level": alert_level,
            "threshold_level": threshold_level,
            "historical_periods": len(historical_values),
            "current_periods": len(current_values),
            "formatted_message": formatted_message,
            "count": len(historical_data) + len(data),
            "records": data
        }
        
    except Exception as e:
        logger.error(f"Erro ao calcular estatísticas de ticket médio: {e}")
        import traceback
        logger.error(traceback.format_exc())
        raise


def _extract_start_date(current_period_start: Optional[Dict[str, Any]], now: datetime) -> datetime:
    """Extrai data de início do período atual."""
    if current_period_start:
        current_start_str = current_period_start.get("start_date")
        try:
            if isinstance(current_start_str, str):
                return datetime.fromisoformat(current_start_str.split('+')[0].split('T')[0])
        except:
            pass
    return now.replace(day=1, hour=0, minute=0, second=0, microsecond=0)


def _fetch_historical_data(
    supabase_client: Any,
    historical_start: datetime,
    current_start_dt: datetime,
    unit: Optional[str]
) -> List[Dict[str, Any]]:
    """Busca dados históricos do Supabase."""
    try:
        # Schema real: usar valid_from para filtros de período
        query_historical = supabase_client.table("operational_data").select("*")
        query_historical = query_historical.gte("valid_from", historical_start.isoformat())
        query_historical = query_historical.lt("valid_from", current_start_dt.isoformat())
        
        # Nota: Filtro de unidade será feito após extrair dados do JSONB
        # PostgREST tem limitações com filtros JSONB complexos
        
        historical_result = query_historical.execute()
        historical_data = historical_result.data if historical_result.data else []
        
        # Extrair dados do JSONB e filtrar apenas ticket médio e unidade
        processed_data = []
        for record in historical_data:
            json_data = record.get('data', {})
            if not isinstance(json_data, dict):
                continue
            
            # Extrair unidade do JSONB
            record_unit = (
                json_data.get('unidade') or 
                json_data.get('unit') or 
                json_data.get('codigo_unidade') or
                json_data.get('filial')
            )
            
            # Filtrar por unidade se especificada
            if unit and record_unit:
                if record_unit.strip().upper() != unit.strip().upper():
                    continue
            
            indicador = (
                json_data.get('indicador') or 
                json_data.get('metric') or 
                json_data.get('metric_name')
            )
            
            # Filtrar apenas ticket médio
            if indicador and 'ticket' in str(indicador).lower():
                processed_record = {
                    'valor': json_data.get('valor') or json_data.get('value'),
                    'indicador': indicador,
                    'unidade': record_unit,
                    'data': record.get('valid_from'),
                    **json_data
                }
                processed_data.append(processed_record)
        
        return processed_data
    except Exception as e:
        logger.warning(f"Erro ao buscar dados históricos: {e}. Usando apenas dados atuais.")
        import traceback
        logger.debug(traceback.format_exc())
        return []


def _separate_historical_and_current(
    historical_data: List[Dict[str, Any]],
    current_data: List[Dict[str, Any]],
    current_start_dt: datetime
) -> tuple[List[float], List[float]]:
    """Separa valores históricos e atuais dos dados."""
    historical_values = []
    current_values = []
    all_data = historical_data + current_data
    
    for record in all_data:
        is_historical = record in historical_data
        record_date = record.get('data') or record.get('date')
        value = record.get('valor') or record.get('value') or record.get('ticket_medio')
        
        if value is None:
            continue
        
        try:
            float_val = float(value)
            
            if is_historical:
                historical_values.append(float_val)
            else:
                # Verificar se realmente é do período atual
                if record_date and current_start_dt:
                    try:
                        if isinstance(record_date, str):
                            record_date_dt = datetime.fromisoformat(
                                record_date.replace('Z', '+00:00').split('+')[0].split('T')[0]
                            )
                        else:
                            record_date_dt = record_date
                        
                        if record_date_dt >= current_start_dt:
                            current_values.append(float_val)
                        else:
                            historical_values.append(float_val)
                    except:
                        current_values.append(float_val)
                else:
                    current_values.append(float_val)
        except (ValueError, TypeError):
            continue
    
    # Fallback: se não há histórico separado, usar split temporal
    if not historical_values and len(all_data) > 6:
        all_values = extract_numeric_values(all_data, "ticket_medio")
        if all_values and len(all_values) >= 6:
            split_idx = max(6, int(len(all_values) * 0.75))
            historical_values = all_values[:split_idx]
            current_values = all_values[split_idx:]
    
    return historical_values, current_values


def _fallback_values_split(data: List[Dict[str, Any]]) -> tuple[List[float], List[float]]:
    """Fallback quando não há dados históricos suficientes."""
    all_values = extract_numeric_values(data, "ticket_medio")
    if all_values and len(all_values) >= 2:
        historical_values = all_values[:-1] if len(all_values) > 2 else all_values
        current_values = all_values[-1:] if len(all_values) > 2 else [statistics.mean(all_values)]
        return historical_values, current_values
    return [], []


def _format_ticket_medio_message(
    current_mean: float,
    hist_mean: float,
    deviation_from_normal: Optional[float],
    alert_level: str,
    threshold_level: str
) -> str:
    """Formata mensagem para ticket médio."""
    if deviation_from_normal is not None:
        abs_dev = abs(deviation_from_normal)
        deviation_desc = (
            "muito acima" if abs_dev >= 3.0 
            else "acima" if abs_dev >= 2.0 
            else "dentro"
        )
        return (
            f"Ticket médio: R${current_mean:.2f} | "
            f"Comparado com média histórica: R${hist_mean:.2f} ({deviation_desc} do normal) | "
            f"Status: {alert_level} ({threshold_level})"
        )
    else:
        return (
            f"Ticket médio: R${current_mean:.2f} | "
            f"Média histórica: R${hist_mean:.2f} | "
            f"Status: {alert_level} (dados insuficientes para análise)"
        )
