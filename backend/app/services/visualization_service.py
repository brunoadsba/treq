"""
Visualization Service: Gera dados estruturados para gráficos.

Este serviço transforma dados do MetricsTool/AlertsTool em formato
compatível com bibliotecas de gráficos (Chart.js/Recharts).
"""
import json
import asyncio
from datetime import datetime
from typing import Dict, Any, List, Optional
from loguru import logger

from app.core.tools.metrics_tool import MetricsTool
# from app.core.tools.alerts_tool import AlertsTool  # Se existir


class VisualizationService:
    """Serviço para gerar dados de visualização gráfica"""
    
    def __init__(self):
        self.metrics_tool = MetricsTool()
        # self.alerts_tool = AlertsTool()  # Se existir
    
    @staticmethod
    def translate_period(period: str) -> str:
        """Traduz período de inglês para português brasileiro"""
        period_translations = {
            "today": "Hoje",
            "yesterday": "Ontem",
            "this_week": "Esta semana",
            "last_week": "Semana passada",
            "this_month": "Este mês",
            "last_month": "Mês passado",
            "this_year": "Este ano",
            "last_year": "Ano passado"
        }
        return period_translations.get(period, period)
    
    async def generate_chart_data(
        self,
        action_id: str,
        period: str = "today",
        unit: Optional[str] = None,
        **kwargs
    ) -> Optional[Dict[str, Any]]:
        """
        Gera dados estruturados para gráfico baseado no action_id.
        
        Args:
            action_id: ID da ação rápida ("alertas", "status-recife", "status-salvador")
            period: Período ("today", "this_week", "this_month", "this_year")
            unit: Unidade específica (ex: "PE-Recife", "BA-Salvador")
            **kwargs: Parâmetros adicionais
            
        Returns:
            Dict com estrutura de chart_data ou None em caso de erro
        """
        try:
            logger.info(
                f"[VISUALIZATION] generate_chart_data chamado: "
                f"action_id={action_id}, period={period}, unit={unit}"
            )
            
            if action_id == "alertas":
                result = await self._get_alerts_chart(period, **kwargs)
                logger.info(f"[VISUALIZATION] Gráfico de alertas: {'sucesso' if result else 'falha'}")
                return result
            elif action_id == "status-recife":
                result = await self._get_status_chart("PE-Recife", period, **kwargs)
                logger.info(f"[VISUALIZATION] Gráfico status Recife: {'sucesso' if result else 'falha'}")
                return result
            elif action_id == "status-salvador":
                result = await self._get_status_chart("BA-Salvador", period, **kwargs)
                logger.info(f"[VISUALIZATION] Gráfico status Salvador: {'sucesso' if result else 'falha'}")
                return result
            else:
                logger.warning(f"[VISUALIZATION] Action ID desconhecido: {action_id}")
                return None
                
        except Exception as e:
            logger.error(f"[VISUALIZATION] Erro ao gerar chart_data para {action_id}: {e}")
            import traceback
            logger.error(traceback.format_exc())
            return None
    
    async def _get_alerts_chart(
        self,
        period: str = "today",
        **kwargs
    ) -> Optional[Dict[str, Any]]:
        """
        Gera dados para gráfico de pizza de alertas por severidade.
        """
        try:
            logger.info(f"[VISUALIZATION] Gerando gráfico de alertas: period={period}")
            
            # TODO: Integrar com AlertsTool quando disponível
            # Por enquanto, usar dados mockados para teste
            # NOTA: Estes são dados de teste. Substituir por AlertsTool quando disponível.
            mock_data = {"Crítico": 5, "Alto": 12, "Médio": 8, "Baixo": 3}
            
            logger.warning(
                "[VISUALIZATION] Usando dados MOCKADOS para gráfico de alertas. "
                "Integrar AlertsTool real quando disponível."
            )
            
            labels = list(mock_data.keys())
            values = list(mock_data.values())
            total = sum(values)
            
            logger.info(f"[VISUALIZATION] Gráfico de alertas gerado: total={total} alertas")
            
            return {
                "type": "pie_chart",
                "title": "Alertas Críticos Ativos",
                "subtitle": f"Total: {total} alertas operacionais",
                "description": "Distribuição dos alertas críticos ativos por nível de severidade. Monitora métricas operacionais como pedidos cancelados, pedidos em atraso, tempo médio de entrega e entregas no prazo. Cada segmento representa a proporção de alertas em uma categoria específica (Crítico, Alto, Médio, Baixo).",
                "data": {
                    "labels": labels,
                    "datasets": [{
                        "data": values,
                        "backgroundColor": [
                            "#EF4444",  # Crítico - vermelho
                            "#F59E0B",  # Alto - laranja
                            "#3B82F6",  # Médio - azul
                            "#10B981"   # Baixo - verde
                        ],
                        "borderColor": "#FFFFFF",
                        "borderWidth": 2
                    }]
                },
                "options": {
                    "responsive": True,
                    "maintainAspectRatio": False,
                    "plugins": {
                        "legend": {
                            "display": True,
                            "position": "right"
                        },
                        "tooltip": {
                            "enabled": True
                        }
                    }
                },
                "metadata": {
                    "total_alerts": total,
                    "period": period,
                    "last_updated": datetime.utcnow().isoformat() + "Z",
                    "is_mock_data": True,  # Flag para indicar que são dados mockados
                    "warning": "Dados mockados - integrar AlertsTool quando disponível",
                    "alert_types": [
                        "Pedidos cancelados acima do limite estabelecido",
                        "Pedidos em atraso",
                        "Tempo médio de entrega acima da meta",
                        "Entregas abaixo do prazo estabelecido",
                        "Desvios significativos de métricas operacionais"
                    ],
                    "severity_levels": {
                        "Crítico": "Requer ação imediata - desvio muito acima do normal",
                        "Alto": "Requer atenção - desvio acima do normal",
                        "Médio": "Monitoramento necessário - desvio leve do normal",
                        "Baixo": "Situação normal - dentro dos limites esperados"
                    }
                }
            }
        except Exception as e:
            logger.error(f"[VISUALIZATION] Erro ao gerar gráfico de alertas: {e}")
            import traceback
            logger.error(traceback.format_exc())
            return None
    
    async def _get_status_chart(
        self,
        unit: str,
        period: str = "today",
        **kwargs
    ) -> Optional[Dict[str, Any]]:
        """
        Gera dados para gráfico de barras com métricas operacionais.
        """
        try:
            logger.info(f"[VISUALIZATION] Iniciando geração de gráfico de status: unit={unit}, period={period}")
            
            # Métricas a buscar
            metrics_to_fetch = [
                "pedidos_cancelados",
                "pedidos_em_atraso",
                "tempo_medio_entrega",
                "entregas_no_prazo"
            ]
            
            # Buscar métricas via MetricsTool em PARALELO (melhoria de performance)
            logger.info(f"[VISUALIZATION] Buscando {len(metrics_to_fetch)} métricas em paralelo...")
            
            # Criar tasks para execução paralela
            tasks = [
                self.metrics_tool.execute(
                    metric_name=metric_name,
                    period=period,
                    unit=unit,
                    **kwargs
                )
                for metric_name in metrics_to_fetch
            ]
            
            # Executar todas as chamadas em paralelo
            results = await asyncio.gather(*tasks, return_exceptions=True)
            
            # Processar resultados com logs detalhados
            metrics_data = {}
            failed_metrics = []
            
            for metric_name, result in zip(metrics_to_fetch, results):
                # Tratar exceções
                if isinstance(result, Exception):
                    logger.error(f"[VISUALIZATION] Exceção ao buscar métrica '{metric_name}': {result}")
                    import traceback
                    logger.error(traceback.format_exc())
                    failed_metrics.append({
                        "metric": metric_name,
                        "error": str(result),
                        "type": "exception"
                    })
                    continue
                
                # Logar resultado
                logger.info(
                    f"[VISUALIZATION] Métrica '{metric_name}': "
                    f"success={result.success}, "
                    f"has_data={result.data is not None}"
                )
                
                if result.success and result.data:
                    logger.debug(
                        f"[VISUALIZATION] Dados '{metric_name}': "
                        f"keys={list(result.data.keys()) if isinstance(result.data, dict) else 'not_dict'}, "
                        f"value={result.data.get('value') if isinstance(result.data, dict) else 'N/A'}"
                    )
                    metrics_data[metric_name] = result.data
                else:
                    error_msg = result.error or result.message or "Desconhecido"
                    logger.warning(
                        f"[VISUALIZATION] Falha ao buscar '{metric_name}': {error_msg}"
                    )
                    failed_metrics.append({
                        "metric": metric_name,
                        "error": error_msg,
                        "type": "tool_failure"
                    })
            
            logger.info(
                f"[VISUALIZATION] Resultado: {len(metrics_data)}/{len(metrics_to_fetch)} métricas encontradas"
            )
            
            if failed_metrics:
                logger.warning(
                    f"[VISUALIZATION] Métricas com falha ({len(failed_metrics)}): "
                    f"{[m['metric'] for m in failed_metrics]}"
                )
            
            if not metrics_data:
                # Verificar se há dados na tabela (para diagnóstico)
                total_records = None
                try:
                    check_query = self.metrics_tool.supabase.table("operational_data").select("id", count="exact").limit(1)
                    check_result = check_query.execute()
                    total_records = check_result.count if hasattr(check_result, 'count') else None
                    logger.info(f"[VISUALIZATION] Total de registros na tabela operational_data: {total_records}")
                except Exception as e:
                    logger.debug(f"[VISUALIZATION] Erro ao verificar total de registros: {e}")
                
                # Retornar gráfico vazio com mensagem detalhada
                error_summary = ", ".join([f"{m['metric']}: {m['error']}" for m in failed_metrics[:3]])
                logger.warning(
                    f"[VISUALIZATION] Nenhuma métrica encontrada para unit={unit}, period={period}. "
                    f"Erros: {error_summary}. Total de registros na tabela: {total_records}"
                )
                
                # Mensagem mais útil para o usuário
                if total_records == 0:
                    message = f"A tabela operational_data está vazia. Insira dados de teste usando o SQL fornecido na documentação."
                else:
                    message = f"Não há dados disponíveis para {unit.split('-')[-1]} no período selecionado. Total de registros na tabela: {total_records}"
                
                period_display = self.translate_period(period)
                
                return {
                    "type": "bar_chart",
                    "title": f"Status Operacional - {unit.split('-')[-1]}",
                    "subtitle": f"Nenhum dado disponível para o período '{period_display}'",
                    "description": f"Gráfico de status operacional para {unit.split('-')[-1]}. Compara valores atuais com metas estabelecidas para métricas como pedidos cancelados, atrasos, tempo médio de entrega e entregas no prazo.",
                    "data": {
                        "labels": [],
                        "datasets": []
                    },
                    "options": {},
                    "metadata": {
                        "empty": True,
                        "message": message,
                        "period": period,
                        "unit": unit,
                        "failed_metrics": failed_metrics[:5],  # Limitar a 5 para não sobrecarregar
                        "total_records_in_table": total_records,
                        "suggestion": "Consulte treq/Docs/inserir-dados-teste.md para inserir dados de teste"
                    }
                }
            
            # Extrair valores atuais com validação robusta
            current_values = []
            labels = []
            extraction_errors = []
            
            # Mapear métricas para labels amigáveis
            metric_labels = {
                "pedidos_cancelados": "Pedidos Cancelados",
                "pedidos_em_atraso": "Pedidos em Atraso",
                "tempo_medio_entrega": "Tempo Médio (dias)",
                "entregas_no_prazo": "Entregas no Prazo (%)"
            }
            
            # Valores de meta (hardcoded por enquanto, pode vir de config)
            meta_values = {
                "pedidos_cancelados": 30,
                "pedidos_em_atraso": 100,
                "tempo_medio_entrega": 60,
                "entregas_no_prazo": 85
            }
            
            for metric_name in metrics_to_fetch:
                if metric_name not in metrics_data:
                    continue
                
                metric_data = metrics_data[metric_name]
                
                # Validar que é um dict
                if not isinstance(metric_data, dict):
                    logger.warning(
                        f"[VISUALIZATION] Dados inválidos para '{metric_name}': "
                        f"tipo={type(metric_data)}, esperado=dict"
                    )
                    extraction_errors.append({
                        "metric": metric_name,
                        "error": f"Tipo inválido: {type(metric_data)}"
                    })
                    continue
                
                # Tentar extrair valor com múltiplas estratégias
                value = (
                    metric_data.get("value") or 
                    metric_data.get("current_value") or
                    metric_data.get("mean")  # Fallback para média se disponível
                )
                
                if value is None:
                    logger.warning(
                        f"[VISUALIZATION] Valor não encontrado para '{metric_name}'. "
                        f"Chaves disponíveis: {list(metric_data.keys())}"
                    )
                    extraction_errors.append({
                        "metric": metric_name,
                        "error": f"Valor não encontrado. Chaves: {list(metric_data.keys())}"
                    })
                    continue
                
                # Converter para float com tratamento de erro
                try:
                    float_value = float(value)
                    current_values.append(float_value)
                    labels.append(metric_labels[metric_name])
                    logger.debug(
                        f"[VISUALIZATION] Valor extraído '{metric_name}': {float_value}"
                    )
                except (ValueError, TypeError) as e:
                    logger.error(
                        f"[VISUALIZATION] Erro ao converter valor de '{metric_name}': "
                        f"value={value}, type={type(value)}, error={e}"
                    )
                    extraction_errors.append({
                        "metric": metric_name,
                        "error": f"Erro de conversão: {e}"
                    })
                    continue
            
            if extraction_errors:
                logger.warning(
                    f"[VISUALIZATION] Erros na extração de valores ({len(extraction_errors)}): "
                    f"{extraction_errors}"
                )
            
            if not current_values:
                logger.error(
                    f"[VISUALIZATION] Nenhum valor válido extraído. "
                    f"Métricas disponíveis: {list(metrics_data.keys())}, "
                    f"Erros de extração: {extraction_errors}"
                )
                return {
                    "type": "bar_chart",
                    "title": f"Status Operacional - {unit.split('-')[-1]}",
                    "subtitle": "Erro ao processar dados",
                    "description": f"Gráfico de status operacional para {unit.split('-')[-1]}. Compara valores atuais com metas estabelecidas para métricas operacionais.",
                    "data": {
                        "labels": [],
                        "datasets": []
                    },
                    "options": {},
                    "metadata": {
                        "empty": True,
                        "message": "Erro ao processar dados das métricas",
                        "period": period,
                        "unit": unit,
                        "extraction_errors": extraction_errors
                    }
                }
            
            # Determinar nome da unidade para título
            unit_names = {
                "PE-Recife": "Recife",
                "BA-Salvador": "Salvador"
            }
            unit_display = unit_names.get(unit, unit)
            
            period_display = self.translate_period(period)
            
            return {
                "type": "bar_chart",
                "title": f"Status Operacional - {unit_display}",
                "subtitle": f"Período: {period_display}",
                "description": f"Comparação entre valores atuais (barras amarelas) e metas estabelecidas (linha verde) para as principais métricas operacionais da unidade {unit_display}. Permite identificar rapidamente quais indicadores estão acima ou abaixo das metas.",
                "data": {
                    "labels": labels,
                    "datasets": [
                        {
                            "label": "Valor Atual",
                            "data": current_values,
                            "backgroundColor": "#FFCD00",
                            "borderColor": "#E6B800",
                            "borderWidth": 2
                        },
                        {
                            "label": "Meta",
                            "data": [meta_values.get(m, 0) for m in metrics_to_fetch if m in metrics_data],
                            "backgroundColor": "#10B981",
                            "borderColor": "#059669",
                            "borderWidth": 2,
                            "type": "line"  # Linha de meta
                        }
                    ]
                },
                "options": {
                    "responsive": True,
                    "maintainAspectRatio": False,
                    "scales": {
                        "y": {
                            "beginAtZero": True
                        }
                    },
                    "plugins": {
                        "legend": {
                            "display": True,
                            "position": "top"
                        },
                        "tooltip": {
                            "enabled": True
                        }
                    }
                },
                "metadata": {
                    "period": period,
                    "unit": unit,
                    "last_updated": datetime.utcnow().isoformat() + "Z"
                }
            }
            
        except Exception as e:
            logger.error(f"Erro ao gerar gráfico de status para {unit}: {e}")
            import traceback
            logger.error(traceback.format_exc())
            return None
