"""
Metrics Tool: Busca métricas operacionais em tempo real do Supabase.

Esta tool consulta a tabela operational_data para obter métricas atualizadas,
ao invés de usar apenas conhecimento estático do RAG.
"""
from typing import Dict, Any, Optional, List
from datetime import datetime, timedelta
from loguru import logger

from app.core.tools.base import Tool, ToolResult
from app.services.supabase_service import get_supabase_client


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
            period_filters = self._calculate_period(period)
            if not period_filters:
                return ToolResult(
                    success=False,
                    error=f"Período inválido: {period}. Use: today, this_week, this_month, this_year"
                )
            
            # Construir query
            query = self.supabase.table("operational_data").select("*")
            
            # Aplicar filtros de período
            if period_filters.get("start_date"):
                query = query.gte("data", period_filters["start_date"])
            if period_filters.get("end_date"):
                query = query.lte("data", period_filters["end_date"])
            
            # Aplicar filtro de unidade se fornecido
            if unit:
                query = query.eq("unidade", unit)
            
            # Executar query
            result = query.execute()
            
            if not result.data:
                logger.warning(f"Nenhum dado encontrado para métrica '{metric_name}' no período '{period}'")
                return ToolResult(
                    success=False,
                    message=f"Nenhum dado encontrado para '{metric_name}' no período '{period}'"
                )
            
            # Processar dados
            metrics_data = self._process_metrics(result.data, metric_name)
            
            logger.info(
                f"✅ Métrica '{metric_name}' encontrada: {metrics_data.get('value', 'N/A')} "
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
    
    def _calculate_period(self, period: str) -> Dict[str, Any]:
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
    
    def _process_metrics(self, data: List[Dict[str, Any]], metric_name: str) -> Dict[str, Any]:
        """
        Processa dados brutos e extrai valor da métrica.
        
        Args:
            data: Lista de registros do Supabase
            metric_name: Nome da métrica
            
        Returns:
            Dict com valor processado da métrica
        """
        # Por enquanto, retorna estrutura básica
        # TODO: Implementar lógica específica por tipo de métrica
        return {
            "metric_name": metric_name,
            "value": len(data),  # Placeholder: contar registros
            "records": data,
            "count": len(data)
        }

