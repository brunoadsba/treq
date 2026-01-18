import os
from typing import List
from loguru import logger
from langchain_community.vectorstores import PGVector
from langchain_core.embeddings import Embeddings
from app.config import get_settings
from app.core.database import get_database_url
from google import genai
from google.genai import types

settings = get_settings()

class CustomGeminiEmbeddings(Embeddings):
    """
    Wrapper para Google GenAI Embeddings compatível com LangChain.
    Usa o cliente oficial google-genai (v1.2.0+) já instalado.
    """
    def __init__(self):
        if not settings.gemini_api_key:
            raise ValueError("GEMINI_API_KEY não configurada.")
        self.client = genai.Client(api_key=settings.gemini_api_key)
        self.model = "text-embedding-004"
        self.dimensions = settings.embedding_dimension or 768 # Default fallback

    def embed_documents(self, texts: List[str]) -> List[List[float]]:
        """Gera embeddings para uma lista de documentos."""
        embeddings = []
        for text in texts:
            embeddings.append(self.embed_query(text))
        return embeddings

    def embed_query(self, text: str) -> List[float]:
        """Gera embedding para uma única query."""
        try:
            clean_text = text.replace("\n", " ")
            result = self.client.models.embed_content(
                model=self.model,
                contents=clean_text,
                config=types.EmbedContentConfig(
                    output_dimensionality=self.dimensions
                )
            )
            if result and result.embeddings:
                return [float(v) for v in result.embeddings[0].values]
            return [0.0] * self.dimensions
        except Exception as e:
            logger.error(f"Erro no embedding Gemini: {e}")
            return [0.0] * self.dimensions

# Configuração da Connection String (Enterprise SSOT)
DB_CONNECTION = get_database_url()
if not DB_CONNECTION:
    logger.warning("DATABASE_URL não resolvida. RAG operará em modo degradado.")

# Nome da coleção (Enterprise Namespace)
COLLECTION_NAME = "treq_knowledge_base"

def get_embeddings() -> Embeddings:
    """Retorna o modelo de embeddings configurado."""
    return CustomGeminiEmbeddings()

def get_vector_store() -> PGVector:
    """
    Retorna uma instância configurada do PGVector (Community).
    """
    embeddings = get_embeddings()
    
    try:
        vector_store = PGVector(
            embedding_function=embeddings,
            collection_name=COLLECTION_NAME,
            connection_string=DB_CONNECTION,
        )
        return vector_store
    except Exception as e:
        logger.error(f"Falha ao inicializar PGVector: {e}")
        raise e
