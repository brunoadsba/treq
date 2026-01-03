"""
Serviço de embeddings para busca semântica.
Usa Google Gemini Embeddings (API) para 100% de compatibilidade com Free Tier do Render.
Truncado para 384 dimensões para manter compatibilidade com o banco de dados atual.
"""
from typing import List, Optional, Any
from loguru import logger
from app.config import get_settings

settings = get_settings()

# Instância singleton do cliente (tipo Any para evitar import no topo)
_genai_client: Optional[Any] = None

def get_genai_client() -> Any:
    """Retorna o cliente Gemini GenAI."""
    global _genai_client
    if _genai_client is None:
        try:
            from google import genai
            if not settings.gemini_api_key:
                logger.error("❌ GEMINI_API_KEY não configurada!")
                raise ValueError("GEMINI_API_KEY é obrigatória para embeddings.")
                
            _genai_client = genai.Client(api_key=settings.gemini_api_key)
        except ImportError:
            logger.error("❌ google-genai não instalado!")
            raise
    return _genai_client

async def generate_embedding(text: str) -> List[float]:
    """
    Gera embedding para um texto usando a API do Gemini.
    
    Args:
        text: Texto para gerar embedding
        
    Returns:
        List[float]: Vetor de embedding (384 dimensões)
    """
    if not text or not text.strip():
        return [0.0] * settings.embedding_dimension

    try:
        from app.core.cache import cache_manager
        
        # 1. Tentar Cache
        cached_embedding = await cache_manager.get("emb", text)
        if cached_embedding:
            return cached_embedding

        client = get_genai_client()
        # Higienização básica
        clean_text = text.replace("\n", " ")
        
        # ... (restante da lógica de chamada da API)
        # (Omitido para brevidade, mas mantendo a lógica de chamada)
        from google.genai import types
        
        result = client.models.embed_content(
            model="text-embedding-004",
            contents=clean_text,
            config=types.EmbedContentConfig(
                output_dimensionality=settings.embedding_dimension
            )
        )
        
        if result and result.embeddings:
            embedding = [float(v) for v in result.embeddings[0].values]
            # 2. Gravar no Cache (TTL de 24h para embeddings já que são estáticos)
            await cache_manager.set("emb", text, embedding, ttl=86400)
            return embedding
            
        logger.error(f"Erro na resposta de embeddings do Gemini para: {text[:50]}...")
        return [0.0] * settings.embedding_dimension
        
    except Exception as e:
        logger.error(f"Erro ao gerar embedding via API Gemini: {e}")
        # Retornar vetor nulo como fallback para não quebrar o pipeline, 
        # mas o ideal é falhar ou ter cache.
        return [0.0] * settings.embedding_dimension

def get_embedding_model() -> Any:
    """Mock para manter compatibilidade com código que espera o objeto do modelo."""
    return "Gemini API Model (text-embedding-004)"
