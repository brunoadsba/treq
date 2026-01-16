"""
BaseConnector - Interface para conectores externos.

Define o contrato que todos os conectores devem implementar.
"""

from abc import ABC, abstractmethod
from typing import List, Dict, Any, Optional
from datetime import datetime
from pydantic import BaseModel


class SyncResult(BaseModel):
    """Resultado de uma sincronização."""
    connector: str
    pages_synced: int
    pages_failed: int
    started_at: datetime
    completed_at: datetime
    errors: List[str] = []


class BaseConnector(ABC):
    """
    Interface base para conectores com sistemas externos.
    
    Todos os conectores (Confluence, Slack, Jira) devem implementar esta interface.
    """
    
    def __init__(self, name: str):
        self.name = name
        self.is_connected = False
        self.last_sync: Optional[datetime] = None
    
    @abstractmethod
    async def connect(self) -> bool:
        """
        Estabelece conexão com o sistema externo.
        
        Returns:
            True se conectado com sucesso
        """
        pass
    
    @abstractmethod
    async def disconnect(self) -> None:
        """Encerra a conexão."""
        pass
    
    @abstractmethod
    async def test_connection(self) -> bool:
        """
        Testa se a conexão está ativa.
        
        Returns:
            True se conexão OK
        """
        pass
    
    @abstractmethod
    async def fetch_items(
        self,
        limit: int = 100,
        since: Optional[datetime] = None
    ) -> List[Dict[str, Any]]:
        """
        Busca itens do sistema externo.
        
        Args:
            limit: Número máximo de itens
            since: Buscar apenas itens modificados após esta data
            
        Returns:
            Lista de itens
        """
        pass
    
    @abstractmethod
    async def sync(self) -> SyncResult:
        """
        Executa sincronização completa.
        
        Returns:
            Resultado da sincronização
        """
        pass
    
    def get_status(self) -> Dict[str, Any]:
        """Retorna status do conector."""
        return {
            "name": self.name,
            "is_connected": self.is_connected,
            "last_sync": self.last_sync.isoformat() if self.last_sync else None
        }
