"""
Otimização do Vector Store Treq
Substitui LangChain PGVector por implementação nativa otimizada
"""
import os
import psycopg2
from typing import List, Dict, Any, Optional
from loguru import logger
from app.config import get_settings

settings = get_settings()

class OptimizedVectorStore:
    """Vector Store otimizado usando funções SQL nativas"""
    
    def __init__(self):
        self.db_url = settings.database_url
        if not self.db_url:
            raise ValueError("DATABASE_URL não configurada")
    
    def _get_connection(self):
        """Obtém conexão com o banco"""
        return psycopg2.connect(self.db_url)
    
    def search_similar(
        self, 
        query_embedding: List[float], 
        user_id: str = "anonymous",
        limit: int = 5,
        similarity_threshold: float = 0.35,
        filters: Optional[Dict] = None
    ) -> List[Dict[str, Any]]:
        """
        Busca documentos similares usando função SQL otimizada
        
        Args:
            query_embedding: Embedding da query (768D para Gemini)
            user_id: ID do usuário para RLS
            limit: Número máximo de resultados
            similarity_threshold: Threshold mínimo de similaridade
            filters: Filtros adicionais de metadados
            
        Returns:
            Lista de documentos com content, metadata e similarity
        """
        conn = self._get_connection()
        cur = conn.cursor()
        
        try:
            # Usar função otimizada criada pelo script
            cur.execute("""
                SELECT id, content, metadata, similarity, created_at
                FROM search_knowledge_optimized(
                    %s::vector, %s, %s, %s, %s::jsonb
                )
            """, (
                query_embedding,
                similarity_threshold,
                limit,
                user_id,
                filters or {}
            ))
            
            results = []
            for row in cur.fetchall():
                results.append({
                    "id": str(row[0]),
                    "content": row[1],
                    "metadata": row[2],
                    "similarity": float(row[3]),
                    "created_at": row[4].isoformat() if row[4] else None
                })
            
            logger.info(f"Busca otimizada retornou {len(results)} documentos")
            return results
            
        except Exception as e:
            logger.error(f"Erro na busca otimizada: {e}")
            return []
        finally:
            conn.close()
    
    def get_stats(self) -> Dict[str, Any]:
        """Obtém estatísticas da base de conhecimento"""
        conn = self._get_connection()
        cur = conn.cursor()
        
        try:
            cur.execute("SELECT * FROM get_knowledge_stats()")
            stats = cur.fetchone()
            
            if stats:
                return {
                    "total_documents": int(stats[0]),
                    "avg_content_length": float(stats[1]) if stats[1] else 0,
                    "classifications": stats[2] or [],
                    "sources": stats[3] or []
                }
            return {}
            
        except Exception as e:
            logger.error(f"Erro ao obter estatísticas: {e}")
            return {}
        finally:
            conn.close()

# Função de compatibilidade com código existente
def get_optimized_vector_store() -> OptimizedVectorStore:
    """
    Substituto otimizado para get_vector_store()
    
    Usage:
        # Antes
        vector_store = get_vector_store()
        results = vector_store.similarity_search_with_score(query, k=5)
        
        # Depois  
        vector_store = get_optimized_vector_store()
        results = vector_store.search_similar(embedding, user_id, limit=5)
    """
    return OptimizedVectorStore()
