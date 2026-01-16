"""
Modelos Pydantic para Slack.
"""

from pydantic import BaseModel
from typing import Optional, List
from datetime import datetime


class SlackChannel(BaseModel):
    """Canal do Slack."""
    id: str
    name: str
    is_private: bool = False
    num_members: int = 0


class SlackMessage(BaseModel):
    """Mensagem do Slack."""
    ts: str  # Timestamp único do Slack
    channel_id: str
    user_id: str
    text: str
    timestamp: datetime
    thread_ts: Optional[str] = None  # Se for reply
    reactions: List[str] = []
    
    def to_chunk_metadata(self) -> dict:
        """
        Converte para metadados de chunk RAG.
        """
        return {
            "source": f"slack:{self.channel_id}",
            "message_ts": self.ts,
            "user_id": self.user_id,
            "document_type": "slack_message",
            "indexed_at": datetime.utcnow().isoformat(),
            "classification": "internal",
            "allowed_users": ["*"],
            "department": "geral"
        }


class SlackWebhookPayload(BaseModel):
    """Payload de webhook do Slack."""
    type: str
    challenge: Optional[str] = None  # Para verificação
    event: Optional[dict] = None
