"""
ConfluenceClient - Cliente para API do Confluence.

Suporta modo mock para desenvolvimento sem credenciais.
"""

from typing import List, Dict, Any, Optional
from datetime import datetime
from loguru import logger

from ..base import BaseConnector, SyncResult
from .models import ConfluencePage, ConfluenceSpace


class ConfluenceClient(BaseConnector):
    """
    Cliente para integração com Confluence.
    
    Modos:
    - mock=True: Retorna dados simulados (desenvolvimento)
    - mock=False: Usa API real (requer credenciais OAuth2)
    """
    
    def __init__(
        self,
        base_url: Optional[str] = None,
        client_id: Optional[str] = None,
        client_secret: Optional[str] = None,
        mock: bool = True
    ):
        super().__init__(name="confluence")
        self.base_url = base_url
        self.client_id = client_id
        self.client_secret = client_secret
        self.mock = mock
        self._access_token: Optional[str] = None
    
    async def connect(self) -> bool:
        """Conecta ao Confluence (mock ou real)."""
        if self.mock:
            logger.info("[MOCK] Confluence conectado")
            self.is_connected = True
            return True
        
        # TODO: Implementar OAuth2 real
        # 1. Trocar authorization code por access token
        # 2. Armazenar refresh token
        logger.warning("OAuth2 real não implementado. Use mock=True")
        return False
    
    async def disconnect(self) -> None:
        """Desconecta."""
        self._access_token = None
        self.is_connected = False
        logger.info("Confluence desconectado")
    
    async def test_connection(self) -> bool:
        """Testa conexão."""
        if self.mock:
            return True
        # TODO: Fazer request de teste para API
        return self.is_connected
    
    async def fetch_items(
        self,
        limit: int = 100,
        since: Optional[datetime] = None
    ) -> List[Dict[str, Any]]:
        """Busca páginas do Confluence."""
        pages = await self.get_pages(limit=limit)
        return [p.model_dump() for p in pages]
    
    async def get_spaces(self) -> List[ConfluenceSpace]:
        """Retorna espaços disponíveis."""
        if self.mock:
            return self._mock_spaces()
        
        # TODO: GET /wiki/rest/api/space
        return []
    
    async def get_pages(
        self,
        space_key: Optional[str] = None,
        limit: int = 100
    ) -> List[ConfluencePage]:
        """
        Busca páginas do Confluence.
        
        Args:
            space_key: Filtrar por espaço (opcional)
            limit: Número máximo de páginas
        """
        if self.mock:
            return self._mock_pages(limit)
        
        # TODO: GET /wiki/rest/api/content
        return []
    
    async def get_page_content(self, page_id: str) -> Optional[str]:
        """Busca conteúdo de uma página específica."""
        if self.mock:
            return self._mock_page_content(page_id)
        
        # TODO: GET /wiki/rest/api/content/{id}?expand=body.storage
        return None
    
    async def sync(self) -> SyncResult:
        """Sincroniza páginas para a base RAG."""
        started_at = datetime.utcnow()
        pages_synced = 0
        pages_failed = 0
        errors = []
        
        try:
            pages = await self.get_pages()
            
            for page in pages:
                try:
                    # TODO: Indexar no RAG via ChunkingService
                    logger.info(f"[SYNC] Página: {page.title}")
                    pages_synced += 1
                except Exception as e:
                    pages_failed += 1
                    errors.append(f"{page.title}: {str(e)}")
            
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
    
    def _mock_spaces(self) -> List[ConfluenceSpace]:
        """Dados mock de espaços."""
        return [
            ConfluenceSpace(key="TREQ", name="Treq Documentação", type="global"),
            ConfluenceSpace(key="ENG", name="Engenharia", type="global"),
            ConfluenceSpace(key="OPS", name="Operações", type="global"),
        ]
    
    def _mock_pages(self, limit: int = 10) -> List[ConfluencePage]:
        """Dados mock de páginas."""
        now = datetime.utcnow()
        pages = [
            ConfluencePage(
                id="12345",
                title="Manual de Manutenção Preventiva",
                space_key="ENG",
                content="# Manutenção Preventiva\n\nEste guia...",
                url="https://treq.atlassian.net/wiki/spaces/ENG/pages/12345",
                created_at=now,
                updated_at=now,
                author="bruno.ads",
                labels=["manutenção", "preventiva"]
            ),
            ConfluencePage(
                id="12346",
                title="Procedimento de Emergência",
                space_key="OPS",
                content="# Emergência\n\nEm caso de...",
                url="https://treq.atlassian.net/wiki/spaces/OPS/pages/12346",
                created_at=now,
                updated_at=now,
                author="operador",
                labels=["emergência", "segurança"]
            ),
            ConfluencePage(
                id="12347",
                title="Guia de Integração Treq",
                space_key="TREQ",
                content="# Integração\n\nPara integrar...",
                url="https://treq.atlassian.net/wiki/spaces/TREQ/pages/12347",
                created_at=now,
                updated_at=now,
                author="dev",
                labels=["integração", "api"]
            ),
        ]
        return pages[:limit]
    
    def _mock_page_content(self, page_id: str) -> str:
        """Conteúdo mock de uma página."""
        return f"# Conteúdo da Página {page_id}\n\nEste é o conteúdo..."
