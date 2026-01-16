"""
Ferramentas de Integração com Jira.
"""

from typing import Dict, Any
from .base import BaseTool
from loguru import logger


# TODO: Criar JiraConnector na Sprint 3
class JiraCreateTicketTool(BaseTool):
    """Ferramenta para criar tickets no Jira."""
    
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
        Cria ticket no Jira. (Mock temporário)
        """
        logger.info(f"[JIRA TOOL] Criando ticket: {summary}")
        
        # Simula delay e API call
        return {
            "status": "success",
            "ticket_id": "TREQ-123",
            "url": "https://sotreq.atlassian.net/browse/TREQ-123",
            "message": "Ticket TREQ-123 criado com sucesso (Integration)"
        }
