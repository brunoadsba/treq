"""
Testes para a feature Connectors.
"""

import pytest
from datetime import datetime


class TestConfluenceModels:
    """Testes para modelos Confluence."""
    
    def test_confluence_page_to_chunk_metadata(self):
        """ConfluencePage gera metadados corretos para RLS."""
        from app.features.connectors.confluence.models import ConfluencePage
        
        page = ConfluencePage(
            id="123",
            title="Teste",
            space_key="ENG",
            content="Conteúdo",
            url="https://example.com",
            created_at=datetime.utcnow(),
            updated_at=datetime.utcnow(),
            labels=["label1"]
        )
        
        meta = page.to_chunk_metadata()
        
        assert meta["source"] == "confluence:ENG"
        assert meta["classification"] == "internal"
        assert meta["allowed_users"] == ["*"]
        assert "indexed_at" in meta


class TestConfluenceClient:
    """Testes para ConfluenceClient."""
    
    @pytest.mark.asyncio
    async def test_connect_mock(self):
        """Conexão mock funciona."""
        from app.features.connectors.confluence import ConfluenceClient
        
        client = ConfluenceClient(mock=True)
        result = await client.connect()
        
        assert result is True
        assert client.is_connected is True
    
    @pytest.mark.asyncio
    async def test_get_spaces_mock(self):
        """Retorna espaços mock."""
        from app.features.connectors.confluence import ConfluenceClient
        
        client = ConfluenceClient(mock=True)
        await client.connect()
        
        spaces = await client.get_spaces()
        
        assert len(spaces) == 3
        assert spaces[0].key == "TREQ"
    
    @pytest.mark.asyncio
    async def test_get_pages_mock(self):
        """Retorna páginas mock."""
        from app.features.connectors.confluence import ConfluenceClient
        
        client = ConfluenceClient(mock=True)
        await client.connect()
        
        pages = await client.get_pages(limit=2)
        
        assert len(pages) == 2
        assert pages[0].title == "Manual de Manutenção Preventiva"
    
    @pytest.mark.asyncio
    async def test_sync_mock(self):
        """Sincronização mock funciona."""
        from app.features.connectors.confluence import ConfluenceClient
        
        client = ConfluenceClient(mock=True)
        await client.connect()
        
        result = await client.sync()
        
        assert result.connector == "confluence"
        assert result.pages_synced == 3
        assert result.pages_failed == 0
        assert len(result.errors) == 0

class TestSlackModels:
    """Testes para modelos Slack."""
    
    def test_slack_message_to_chunk_metadata(self):
        """SlackMessage gera metadados corretos para RLS."""
        from app.features.connectors.slack.models import SlackMessage
        
        message = SlackMessage(
            ts="123.456",
            channel_id="C001",
            user_id="U001",
            text="Mensagem de teste",
            timestamp=datetime.utcnow()
        )
        
        meta = message.to_chunk_metadata()
        
        assert meta["source"] == "slack:C001"
        assert meta["document_type"] == "slack_message"
        assert meta["classification"] == "internal"
        assert meta["allowed_users"] == ["*"]


class TestSlackClient:
    """Testes para SlackClient."""
    
    @pytest.mark.asyncio
    async def test_connect_mock(self):
        """Conexão mock funciona."""
        from app.features.connectors.slack import SlackClient
        
        client = SlackClient(mock=True)
        result = await client.connect()
        
        assert result is True
        assert client.is_connected is True
    
    @pytest.mark.asyncio
    async def test_get_channels_mock(self):
        """Retorna canais mock."""
        from app.features.connectors.slack import SlackClient
        
        client = SlackClient(mock=True)
        await client.connect()
        
        channels = await client.get_channels()
        
        assert len(channels) == 4
        assert channels[0].name == "geral"
    
    @pytest.mark.asyncio
    async def test_get_messages_mock(self):
        """Retorna mensagens mock."""
        from app.features.connectors.slack import SlackClient
        
        client = SlackClient(mock=True)
        await client.connect()
        
        messages = await client.get_messages(limit=2)
        
        assert len(messages) == 2
        assert messages[0].user_id == "U001"

    @pytest.mark.asyncio
    async def test_send_message_mock(self):
        """Envio de mensagem mock."""
        from app.features.connectors.slack import SlackClient
        
        client = SlackClient(mock=True)
        await client.connect()
        
        result = await client.post_message(channel="C001", text="Teste")
        
        assert result["ok"] is True
        assert result["channel"] == "C001"
    
    @pytest.mark.asyncio
    async def test_sync_mock(self):
        """Sincronização mock funciona."""
        from app.features.connectors.slack import SlackClient
        
        client = SlackClient(mock=True)
        await client.connect()
        
        result = await client.sync()
        
        assert result.connector == "slack"
        assert result.pages_synced == 3
        assert result.pages_failed == 0
