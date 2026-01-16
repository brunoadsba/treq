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
    slack = get_slack_client()
    
    return {
        "connectors": [
            confluence.get_status(),
            slack.get_status()
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


# ============================================================================
# SLACK
# ============================================================================

from .slack import SlackClient

_slack_client: SlackClient = None


def get_slack_client() -> SlackClient:
    """Retorna instância do cliente Slack."""
    global _slack_client
    if _slack_client is None:
        _slack_client = SlackClient(mock=True)
    return _slack_client


@router.post("/slack/connect")
async def slack_connect(api_key: str = Depends(verify_api_key)):
    """Conecta ao Slack."""
    client = get_slack_client()
    success = await client.connect()
    
    if not success:
        raise HTTPException(status_code=500, detail="Falha ao conectar")
    
    return {"status": "connected", "mock": client.mock}


@router.get("/slack/channels")
async def slack_channels(api_key: str = Depends(verify_api_key)):
    """Lista canais do Slack."""
    client = get_slack_client()
    
    if not client.is_connected:
        await client.connect()
    
    channels = await client.get_channels()
    return {"channels": [c.model_dump() for c in channels]}


@router.get("/slack/messages")
async def slack_messages(
    channel_id: str = None,
    limit: int = 10,
    api_key: str = Depends(verify_api_key)
):
    """Lista mensagens do Slack."""
    client = get_slack_client()
    
    if not client.is_connected:
        await client.connect()
    
    messages = await client.get_messages(channel_id=channel_id, limit=limit)
    return [m.model_dump() for m in messages]


@router.post("/slack/send")
async def slack_send(
    channel: str,
    text: str,
    api_key: str = Depends(verify_api_key)
):
    """Envia mensagem para um canal do Slack."""
    client = get_slack_client()
    
    if not client.is_connected:
        await client.connect()
    
    result = await client.post_message(channel=channel, text=text)
    return result


@router.post("/slack/sync")
async def slack_sync(api_key: str = Depends(verify_api_key)):
    """Sincroniza mensagens do Slack para a base RAG."""
    client = get_slack_client()
    
    if not client.is_connected:
        await client.connect()
    
    logger.info("Iniciando sincronização do Slack...")
    result = await client.sync()
    
    return result.model_dump()
