"""
Serviço de embeddings para busca semântica.
Usa sentence-transformers para gerar embeddings de texto.
"""
from typing import List, Optional, Any
from loguru import logger
# from sentence_transformers import SentenceTransformer (Movido para dentro da função para Lazy Loading)
from app.config import get_settings

settings = get_settings()

# Instância singleton do modelo de embeddings (tipo Any para evitar import no topo)
_embedding_model: Optional[Any] = None


def get_embedding_model() -> Any:
    """
    Retorna instância singleton do modelo de embeddings.
    
    Returns:
        SentenceTransformer: Modelo de embeddings configurado
    """
    global _embedding_model
    
    if _embedding_model is None:
        from sentence_transformers import SentenceTransformer
        model_name = settings.embedding_model
        logger.info(f"Carregando modelo de embeddings: {model_name}")
        
        try:
            _embedding_model = SentenceTransformer(
                model_name,
                device='cpu'  # CPU é suficiente para embeddings
            )
            logger.info("✅ Modelo de embeddings carregado com sucesso")
        except Exception as e:
            logger.error(f"Erro ao carregar modelo de embeddings: {e}")
            raise
    
    return _embedding_model


def generate_embedding(text: str) -> List[float]:
    """
    Gera embedding para um texto.
    
    Args:
        text: Texto para gerar embedding
        
    Returns:
        List[float]: Vetor de embedding (384 dimensões)
    """
    model = get_embedding_model()
    embedding = model.encode(text, normalize_embeddings=True)
    return embedding.tolist()

