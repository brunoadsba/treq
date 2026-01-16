"""
Modelos Pydantic para Confluence.
"""

from pydantic import BaseModel
from typing import Optional, List
from datetime import datetime


class ConfluenceSpace(BaseModel):
    """Espaço do Confluence."""
    key: str
    name: str
    type: str = "global"  # global, personal


class ConfluencePage(BaseModel):
    """Página do Confluence."""
    id: str
    title: str
    space_key: str
    content: str  # Conteúdo HTML ou Markdown
    url: str
    created_at: datetime
    updated_at: datetime
    author: Optional[str] = None
    labels: List[str] = []
    
    def to_chunk_metadata(self) -> dict:
        """
        Converte para metadados de chunk RAG.
        
        Inclui campos para RLS.
        """
        return {
            "source": f"confluence:{self.space_key}",
            "filename": self.title,
            "url": self.url,
            "document_type": "confluence_page",
            "confluence_id": self.id,
            "space_key": self.space_key,
            "labels": self.labels,
            "author": self.author,
            "indexed_at": datetime.utcnow().isoformat(),
            # RLS: páginas do Confluence são acessíveis a todos por padrão
            "classification": "internal",
            "allowed_users": ["*"],
            "department": "geral"
        }
