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
