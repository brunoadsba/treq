"""
Ferramentas de Integração com Slack.

Substitui os mocks da Sprint 1.3 por integração via SlackClient.
"""

from typing import Dict, Any
from .base import BaseTool
from ...connectors.routes import get_slack_client


class SlackSendMessageTool(BaseTool):
    """Ferramenta para enviar mensagens no Slack usando o SlackClient."""
    
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
        Envia mensagem usando o SlackClient.
        """
        client = get_slack_client()
        if not client.is_connected:
            await client.connect()
            
        result = await client.post_message(channel, message)
        
        if result.get("ok"):
            return {
                "status": "success",
                "channel": result.get("channel"),
                "timestamp": result.get("ts"),
                "message": f"Mensagem enviada para {channel}"
            }
        
        return {
            "status": "error",
            "error": result.get("error", "Unknown error")
        }
