"""
Mocks de Ferramentas para Sprint 1.3
Permite o desenvolvimento do grafo sem dependência de APIs externas.
"""

from typing import Dict, Any

class BaseTool:
    """Interface padronizada para todas as ferramentas."""
    def __init__(self, name: str, description: str):
        self.name = name
        self.description = description

    async def execute(self, **kwargs) -> Dict[str, Any]:
        raise NotImplementedError("Subclasses devem implementar execute()")

class JiraCreateTicketTool(BaseTool):
    """Mock da ferramenta de criação de tickets no Jira."""
    def __init__(self):
        super().__init__(
            name="jira_create_ticket",
            description="Cria um ticket no Jira quando um problema técnico é reportado."
        )

    async def execute(self, summary: str, description: str, priority: str = "Medium") -> Dict[str, Any]:
        print(f"[MOCK JIRA] Criando ticket: {summary}")
        # Simula resposta da API do Jira
        return {
            "status": "success",
            "ticket_id": "TREQ-123",
            "url": "https://sotreq.atlassian.net/browse/TREQ-123",
            "message": "Ticket criado com sucesso (MOCK)"
        }

class SlackNotifyTool(BaseTool):
    """Mock da ferramenta de notificação no Slack."""
    def __init__(self):
        super().__init__(
            name="slack_notify",
            description="Envia uma notificação para um canal do Slack."
        )

    async def execute(self, channel: str, message: str) -> Dict[str, Any]:
        print(f"[MOCK SLACK] Enviando para {channel}: {message}")
        return {
            "status": "success",
            "channel": channel,
            "timestamp": "1705416000"
        }
