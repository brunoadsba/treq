"""
Metrics Tool: Busca métricas operacionais em tempo real do Supabase.

Esta tool consulta a tabela operational_data para obter métricas atualizadas,
ao invés de usar apenas conhecimento estático do RAG.

Suporta cálculo de desvio estatístico para métricas como ticket médio, comparando valores atuais com a média histórica.
"""
from typing import Optional
from loguru import logger

from app.core.tools.base import Tool, ToolResult
from app.services.supabase_service import get_supabase_client
from app.core.tools.metrics_utils import (
    calculate_period_filters,
    process_generic_metrics
)
from app.core.tools.ticket_medio_calculator import calculate_ticket_medio_stats


class MetricsTool(Tool):
    """
    Tool para buscar métricas operacionais em tempo real.
    
    Exemplos de uso:
    - get_metric("pedidos_cancelados", period="today")
    - get_metric("entregas_atrasadas", period="this_month", unit="BA-Salvador")
    """
    
    def __init__(self):
        super().__init__(
            name="metrics",
            description="Busca métricas operacionais em tempo real do Supabase"
        )
        self.supabase = get_supabase_client()
    
    async def execute(
        self,
        metric_name: str,
        period: str = "today",
        unit: Optional[str] = None,
        **kwargs
    ) -> ToolResult:
        """
        Busca uma métrica específica.
        
        Args:
            metric_name: Nome da métrica (ex: "pedidos_cancelados")
            period: Período ("today", "this_week", "this_month", "this_year")
            unit: Unidade específica (ex: "BA-Salvador", "PE-Recife")
            **kwargs: Parâmetros adicionais
            
        Returns:
            ToolResult: Resultado com dados da métrica
        """
        try:
            # Validar parâmetros
            is_valid, error = self.validate_params(["metric_name"], metric_name=metric_name)
            if not is_valid:
                return ToolResult(success=False, error=error)
            
            # Calcular período
            period_filters = calculate_period_filters(period)
            if not period_filters:
                return ToolResult(
                    success=False,
                    error=f"Período inválido: {period}. Use: today, this_week, this_month, this_year"
                )
            
            # Construir query
            # Schema real: id, data_type, data (jsonb), version, valid_from, valid_until, created_at, updated_at
            query = self.supabase.table("operational_data").select("*")
            
            # Aplicar filtros de período usando valid_from (timestamp)
            if period_filters.get("start_date"):
                query = query.gte("valid_from", period_filters["start_date"])
            if period_filters.get("end_date"):
                query = query.lte("valid_from", period_filters["end_date"])
            
            # Filtrar apenas registros válidos (valid_until NULL ou futuro)
            from datetime import datetime
            query = query.or_("valid_until.is.null,valid_until.gte." + datetime.utcnow().isoformat())
            
            # Aplicar filtro de unidade se fornecido (dentro do JSONB data)
            # PostgREST suporta filtros em JSONB usando notação: data->>'campo'
            # Como não podemos usar OR facilmente, vamos buscar sem filtro de unidade primeiro
            # e filtrar depois no processamento (mais flexível para diferentes estruturas JSONB)
            # Nota: Se necessário, podemos adicionar filtro JSONB depois quando soubermos a estrutura exata
            
            # Executar query
            result = query.execute()
            
            # Se não encontrou dados, tentar estratégias de fallback progressivas
            if not result.data:
                logger.info(f"Nenhum dado encontrado para '{metric_name}' no período '{period}', tentando fallbacks...")
                from datetime import datetime, timedelta
                
                # Fallback 1: Últimos 30 dias (sem filtro de período)
                fallback_start_30d = (datetime.utcnow() - timedelta(days=30)).isoformat()
                fallback_query_30d = self.supabase.table("operational_data").select("*")
                fallback_query_30d = fallback_query_30d.gte("valid_from", fallback_start_30d)
                now_iso = datetime.utcnow().isoformat()
                fallback_query_30d = fallback_query_30d.or_(f"valid_until.is.null,valid_until.gte.{now_iso}")
                
                fallback_result_30d = fallback_query_30d.execute()
                if fallback_result_30d.data:
                    logger.info(f"Fallback 30 dias encontrou {len(fallback_result_30d.data)} registros")
                    result = fallback_result_30d
                else:
                    # Fallback 2: Últimos 90 dias
                    logger.info(f"Fallback 30 dias vazio, tentando 90 dias...")
                    fallback_start_90d = (datetime.utcnow() - timedelta(days=90)).isoformat()
                    fallback_query_90d = self.supabase.table("operational_data").select("*")
                    fallback_query_90d = fallback_query_90d.gte("valid_from", fallback_start_90d)
                    fallback_query_90d = fallback_query_90d.or_(f"valid_until.is.null,valid_until.gte.{now_iso}")
                    
                    fallback_result_90d = fallback_query_90d.execute()
                    if fallback_result_90d.data:
                        logger.info(f"Fallback 90 dias encontrou {len(fallback_result_90d.data)} registros")
                        result = fallback_result_90d
                    else:
                        # Fallback 3: Qualquer registro válido (sem filtro de data)
                        logger.info(f"Fallback 90 dias vazio, tentando qualquer registro válido...")
                        fallback_query_any = self.supabase.table("operational_data").select("*")
                        fallback_query_any = fallback_query_any.or_(f"valid_until.is.null,valid_until.gte.{now_iso}")
                        fallback_query_any = fallback_query_any.order("valid_from", desc=True).limit(100)
                        
                        fallback_result_any = fallback_query_any.execute()
                        if fallback_result_any.data:
                            logger.info(f"Fallback 'qualquer registro' encontrou {len(fallback_result_any.data)} registros")
                            result = fallback_result_any
            
            if not result.data:
                logger.warning(f"Nenhum dado encontrado para métrica '{metric_name}' no período '{period}'")
                return ToolResult(
                    success=False,
                    message=f"Nenhum dado encontrado para '{metric_name}' no período '{period}'"
                )
            
            # Extrair dados do JSONB 'data' e filtrar por metric_name e unit
            # O campo 'data' é JSONB e contém os dados reais
            processed_records = []
            for record in result.data:
                json_data = record.get('data', {})
                if not isinstance(json_data, dict):
                    continue
                
                # Extrair unidade do JSONB
                record_unit = (
                    json_data.get('unidade') or 
                    json_data.get('unit') or 
                    json_data.get('codigo_unidade') or
                    json_data.get('filial') or
                    json_data.get('codigo_filial')
                )
                
                # Filtrar por unidade se especificada
                # Suportar múltiplos formatos: "PE-Recife", "Recife", "PE", etc.
                if unit:
                    if record_unit:
                        # Normalizar comparação (remover espaços, case insensitive)
                        record_unit_normalized = record_unit.strip().upper()
                        unit_normalized = unit.strip().upper()
                        
                        # Verificar correspondência exata ou parcial
                        # Ex: "PE-Recife" deve corresponder a "Recife" também
                        unit_parts = unit_normalized.split('-')
                        matches_unit = (
                            record_unit_normalized == unit_normalized or
                            (len(unit_parts) > 1 and record_unit_normalized.endswith(unit_parts[-1])) or
                            ('-' in record_unit_normalized and unit_normalized.endswith(record_unit_normalized.split('-')[-1]))
                        )
                        
                        if not matches_unit:
                            continue
                    else:
                        # Se unit foi especificado mas record não tem unidade, pular
                        continue
                
                # Verificar se este registro corresponde à métrica buscada
                # Pode estar em json_data['indicador'], json_data['metric'], etc.
                indicador = (
                    json_data.get('indicador') or 
                    json_data.get('metric') or 
                    json_data.get('metric_name') or
                    json_data.get('tipo') or
                    json_data.get('tipo_indicador')
                )
                
                # Verificar correspondência com metric_name
                # Se há indicador, deve corresponder; se não há, aceitar todos
                matches_metric = True
                if indicador:
                    # Tentar correspondência flexível
                    indicador_lower = str(indicador).lower()
                    metric_lower = metric_name.lower()
                    matches_metric = (
                        metric_lower in indicador_lower or
                        indicador_lower in metric_lower or
                        metric_lower.replace('_', ' ') in indicador_lower.replace('_', ' ')
                    )
                
                if matches_metric:
                    # Criar registro processado com estrutura esperada
                    processed_record = {
                        'valor': json_data.get('valor') or json_data.get('value'),
                        'indicador': indicador or metric_name,
                        'unidade': record_unit,
                        'area': json_data.get('area'),
                        'data': record.get('valid_from') or record.get('created_at'),
                        # Incluir todos os campos do JSONB para compatibilidade
                        **json_data
                    }
                    processed_records.append(processed_record)
            
            if not processed_records:
                logger.warning(f"Nenhum registro processado para métrica '{metric_name}' após extração do JSONB")
                return ToolResult(
                    success=False,
                    message=f"Nenhum dado válido encontrado para '{metric_name}' no período '{period}'"
                )
            
            # Processar dados com lógica específica por tipo de métrica
            if "ticket" in metric_name.lower() and "medio" in metric_name.lower():
                # Usar cálculo específico para ticket médio com análise de desvio estatístico
                metrics_data = calculate_ticket_medio_stats(
                    processed_records,
                    period,
                    unit,
                    self.supabase
                )
            else:
                # Usar processamento genérico com estatísticas básicas
                metrics_data = process_generic_metrics(processed_records, metric_name)
            
            logger.info(
                f"✅ Métrica '{metric_name}' encontrada: {metrics_data.get('value', metrics_data.get('current_value', 'N/A'))} "
                f"(período: {period}, registros: {len(result.data)})"
            )
            
            return ToolResult(
                success=True,
                data=metrics_data,
                message=f"Métrica '{metric_name}' encontrada"
            )
            
        except Exception as e:
            logger.error(f"Erro ao buscar métrica '{metric_name}': {e}")
            import traceback
            logger.error(traceback.format_exc())
            return ToolResult(
                success=False,
                error=f"Erro ao buscar métrica: {str(e)}"
            )

