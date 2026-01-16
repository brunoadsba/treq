"""
SlackClient - Cliente para API do Slack.

Suporta modo mock para desenvolvimento sem credenciais.
"""

from typing import List, Dict, Any, Optional
from datetime import datetime
from loguru import logger

from ..base import BaseConnector, SyncResult
from .models import SlackMessage, SlackChannel


class SlackClient(BaseConnector):
    """
    Cliente para integração com Slack.
    
    Modos:
    - mock=True: Retorna dados simulados
    - mock=False: Usa API real (requer Bot Token)
    """
    
    def __init__(
        self,
        bot_token: Optional[str] = None,
        signing_secret: Optional[str] = None,
        mock: bool = True
    ):
        super().__init__(name="slack")
        self.bot_token = bot_token
        self.signing_secret = signing_secret
        self.mock = mock
    
    async def connect(self) -> bool:
        """Conecta ao Slack."""
        if self.mock:
            logger.info("[MOCK] Slack conectado")
            self.is_connected = True
            return True
        
        # TODO: Validar token com auth.test
        logger.warning("API real não implementada. Use mock=True")
        return False
    
    async def disconnect(self) -> None:
        """Desconecta."""
        self.is_connected = False
        logger.info("Slack desconectado")
    
    async def test_connection(self) -> bool:
        """Testa conexão."""
        if self.mock:
            return True
        return self.is_connected
    
    async def fetch_items(
        self,
        limit: int = 100,
        since: Optional[datetime] = None
    ) -> List[Dict[str, Any]]:
        """Busca mensagens recentes."""
        messages = await self.get_messages(limit=limit)
        return [m.model_dump() for m in messages]
    
    async def get_channels(self) -> List[SlackChannel]:
        """Retorna canais disponíveis."""
        if self.mock:
            return self._mock_channels()
        
        # TODO: GET conversations.list
        return []
    
    async def get_messages(
        self,
        channel_id: Optional[str] = None,
        limit: int = 100
    ) -> List[SlackMessage]:
        """Busca mensagens de um canal."""
        if self.mock:
            return self._mock_messages(limit)
        
        # TODO: GET conversations.history
        return []
    
    async def post_message(
        self,
        channel: str,
        text: str,
        thread_ts: Optional[str] = None
    ) -> Dict[str, Any]:
        """Envia mensagem para um canal."""
        if self.mock:
            logger.info(f"[MOCK SLACK] Enviando para {channel}: {text[:50]}...")
            return {
                "ok": True,
                "ts": "1705416000.000001",
                "channel": channel,
                "message": {"text": text}
            }
        
        # TODO: POST chat.postMessage
        return {"ok": False, "error": "not_implemented"}
    
    async def sync(self) -> SyncResult:
        """Sincroniza mensagens para a base RAG."""
        started_at = datetime.utcnow()
        pages_synced = 0
        pages_failed = 0
        errors = []
        
        try:
            messages = await self.get_messages()
            
            for msg in messages:
                try:
                    logger.info(f"[SYNC] Mensagem: {msg.text[:30]}...")
                    pages_synced += 1
                except Exception as e:
                    pages_failed += 1
                    errors.append(f"{msg.ts}: {str(e)}")
            
            self.last_sync = datetime.utcnow()
            
        except Exception as e:
            errors.append(f"Erro geral: {str(e)}")
        
        return SyncResult(
            connector=self.name,
            pages_synced=pages_synced,
            pages_failed=pages_failed,
            started_at=started_at,
            completed_at=datetime.utcnow(),
            errors=errors
        )
    
    # --- Mock Data ---
    
    def _mock_channels(self) -> List[SlackChannel]:
        """Dados mock de canais."""
        return [
            SlackChannel(id="C001", name="geral", is_private=False, num_members=50),
            SlackChannel(id="C002", name="engenharia", is_private=False, num_members=15),
            SlackChannel(id="C003", name="suporte", is_private=False, num_members=10),
            SlackChannel(id="C004", name="rh-privado", is_private=True, num_members=5),
        ]
    
    def _mock_messages(self, limit: int = 10) -> List[SlackMessage]:
        """Dados mock de mensagens."""
        now = datetime.utcnow()
        messages = [
            SlackMessage(
                ts="1705416001.000001",
                channel_id="C001",
                user_id="U001",
                text="Bom dia equipe! Lembrem de verificar os equipamentos.",
                timestamp=now,
                reactions=["👍", "✅"]
            ),
            SlackMessage(
                ts="1705416002.000002",
                channel_id="C002",
                user_id="U002",
                text="Alguém pode revisar o procedimento de manutenção?",
                timestamp=now
            ),
            SlackMessage(
                ts="1705416003.000003",
                channel_id="C003",
                user_id="U003",
                text="Ticket #123 resolvido. Cliente satisfeito.",
                timestamp=now,
                reactions=["🎉"]
            ),
        ]
        return messages[:limit]
