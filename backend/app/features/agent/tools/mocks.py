"""
Ferramentas Mock para Sprint 1.3.

Permite desenvolvimento do grafo sem dependência de APIs externas.
Substituir por implementações reais na Sprint 2.
"""

from typing import Dict, Any
from loguru import logger
from .base import BaseTool


class JiraCreateTicketTool(BaseTool):
    """Mock da ferramenta de criação de tickets no Jira."""
    
    def __init__(self):
        super().__init__(
            name="jira_create_ticket",
            description="Cria um ticket no Jira quando um problema é reportado."
        )
    
    async def execute(
        self,
        summary: str,
        description: str,
        priority: str = "Medium"
    ) -> Dict[str, Any]:
        """
        Simula criação de ticket no Jira.
        
        Args:
            summary: Título do ticket
            description: Descrição detalhada
            priority: Prioridade (Low, Medium, High)
            
        Returns:
            Dict com ID do ticket criado (mock)
        """
        logger.info(f"[MOCK JIRA] Criando ticket: {summary}")
        
        return {
            "status": "success",
            "ticket_id": "TREQ-123",
            "url": "https://sotreq.atlassian.net/browse/TREQ-123",
            "message": "Ticket TREQ-123 criado com sucesso"
        }


class SlackNotifyTool(BaseTool):
    """Mock da ferramenta de notificação no Slack."""
    
    def __init__(self):
        super().__init__(
            name="slack_notify",
            description="Envia notificação para um canal do Slack."
        )
    
    async def execute(
        self,
        channel: str,
        message: str
    ) -> Dict[str, Any]:
        """
        Simula envio de mensagem no Slack.
        
        Args:
            channel: Canal de destino
            message: Conteúdo da mensagem
            
        Returns:
            Dict com confirmação de envio (mock)
        """
        logger.info(f"[MOCK SLACK] Enviando para {channel}: {message[:50]}...")
        
        return {
            "status": "success",
            "channel": channel,
            "timestamp": "1705416000",
            "message": f"Mensagem enviada para {channel}"
        }
