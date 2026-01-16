"""
Rotas para gestão de conectores.
"""

from fastapi import APIRouter, HTTPException, Depends
from typing import List
from loguru import logger

from app.middleware.simple_auth import verify_api_key
from .confluence import ConfluenceClient, ConfluencePage


router = APIRouter(prefix="/connectors", tags=["Connectors"])

# Cliente singleton (mock por padrão)
_confluence_client: ConfluenceClient = None


def get_confluence_client() -> ConfluenceClient:
    """Retorna instância do cliente Confluence."""
    global _confluence_client
    if _confluence_client is None:
        _confluence_client = ConfluenceClient(mock=True)
    return _confluence_client


@router.get("/status")
async def connectors_status(api_key: str = Depends(verify_api_key)):
    """Retorna status de todos os conectores."""
    confluence = get_confluence_client()
    
    return {
        "connectors": [
            confluence.get_status()
        ]
    }


@router.post("/confluence/connect")
async def confluence_connect(api_key: str = Depends(verify_api_key)):
    """Conecta ao Confluence."""
    client = get_confluence_client()
    success = await client.connect()
    
    if not success:
        raise HTTPException(status_code=500, detail="Falha ao conectar")
    
    return {"status": "connected", "mock": client.mock}


@router.get("/confluence/spaces")
async def confluence_spaces(api_key: str = Depends(verify_api_key)):
    """Lista espaços do Confluence."""
    client = get_confluence_client()
    
    if not client.is_connected:
        await client.connect()
    
    spaces = await client.get_spaces()
    return {"spaces": [s.model_dump() for s in spaces]}


@router.get("/confluence/pages", response_model=List[dict])
async def confluence_pages(
    space_key: str = None,
    limit: int = 10,
    api_key: str = Depends(verify_api_key)
):
    """Lista páginas do Confluence."""
    client = get_confluence_client()
    
    if not client.is_connected:
        await client.connect()
    
    pages = await client.get_pages(space_key=space_key, limit=limit)
    return [p.model_dump() for p in pages]


@router.post("/confluence/sync")
async def confluence_sync(api_key: str = Depends(verify_api_key)):
    """Sincroniza páginas do Confluence para a base RAG."""
    client = get_confluence_client()
    
    if not client.is_connected:
        await client.connect()
    
    logger.info("Iniciando sincronização do Confluence...")
    result = await client.sync()
    
    return result.model_dump()
