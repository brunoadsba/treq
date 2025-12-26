"""
Módulo de Tools para buscar dados em tempo real.

Tools são ferramentas que consultam sistemas externos ou bancos de dados
para obter informações atualizadas, ao invés de usar apenas conhecimento
estático do RAG.
"""
from app.core.tools.base import Tool, ToolResult
from app.core.tools.metrics_tool import MetricsTool

__all__ = ["Tool", "ToolResult", "MetricsTool"]

