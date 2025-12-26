"""
Serviço RAG (Retrieval-Augmented Generation) usando PGVector.
Busca semântica de documentos indexados no Supabase.
"""
from typing import List, Dict, Optional, Any
from loguru import logger
from app.services.supabase_service import get_supabase_client
from app.services.embedding_service import generate_embedding
from app.config import get_settings

settings = get_settings()


class RAGService:
    """Serviço RAG para busca semântica de documentos."""
    
    def __init__(self):
        self.supabase = get_supabase_client()
        self.embedding_dimension = settings.embedding_dimension
    
    def search_similar(
        self,
        query: str,
        top_k: int = 3,
        similarity_threshold: float = 0.7,
        filters: Optional[Dict[str, Any]] = None
    ) -> List[Dict[str, Any]]:
        """
        Busca documentos similares usando busca vetorial.
        
        Nota: Para MVP, busca todos e calcula similaridade em memória.
        Futuro: Criar função SQL no Supabase para busca otimizada.
        
        Args:
            query: Texto da consulta
            top_k: Número de documentos a retornar
            similarity_threshold: Limite mínimo de similaridade (0-1)
            filters: Filtros opcionais por metadata
            
        Returns:
            List[Dict]: Lista de documentos encontrados com metadata
        """
        try:
            # Gerar embedding da query
            query_embedding = generate_embedding(query)
            
            # Buscar documentos do banco
            query_builder = self.supabase.table('knowledge_base').select('*')
            
            # Aplicar filtros de metadata se fornecidos
            if filters:
                for key, value in filters.items():
                    query_builder = query_builder.eq(f'metadata->>{key}', value)
            
            result = query_builder.execute()
            
            if not result.data:
                logger.info("Nenhum documento encontrado")
                return []
            
            # Calcular similaridade em memória (para MVP)
            import numpy as np
            from numpy.linalg import norm
            
            documents_with_similarity = []
            query_vec = np.array(query_embedding)
            
            for row in result.data:
                if not row.get('embedding'):
                    continue
                
                doc_embedding = row['embedding']
                
                # Converter embedding para array numpy (pode vir como string ou lista)
                if isinstance(doc_embedding, str):
                    # Se for string, tentar parsear como JSON
                    import json
                    try:
                        doc_embedding = json.loads(doc_embedding)
                    except:
                        continue
                
                doc_vec = np.array(doc_embedding, dtype=np.float32)
                
                # Verificar se dimensões são compatíveis
                if len(doc_vec) != len(query_vec):
                    logger.warning(f"Dimensões incompatíveis: query={len(query_vec)}, doc={len(doc_vec)}")
                    continue
                
                # Calcular similaridade de cosseno
                similarity = np.dot(query_vec, doc_vec) / (norm(query_vec) * norm(doc_vec))
                
                if similarity >= similarity_threshold:
                    documents_with_similarity.append({
                        'id': row['id'],
                        'content': row['content'],
                        'metadata': row.get('metadata', {}),
                        'similarity': float(similarity),
                        'created_at': row.get('created_at')
                    })
            
            # Ordenar por similaridade (maior primeiro) e retornar top_k
            documents_with_similarity.sort(key=lambda x: x['similarity'], reverse=True)
            documents = documents_with_similarity[:top_k]
            
            logger.info(f"Busca RAG retornou {len(documents)} documentos para query: {query[:50]}...")
            return documents
            
        except Exception as e:
            logger.error(f"Erro na busca RAG: {e}")
            import traceback
            logger.error(traceback.format_exc())
            return []
    
    def index_document(
        self,
        content: str,
        metadata: Optional[Dict[str, Any]] = None
    ) -> Optional[str]:
        """
        Indexa um documento no banco de dados.
        
        Args:
            content: Conteúdo do documento
            metadata: Metadata adicional (tipo, versão, etc.)
            
        Returns:
            Optional[str]: ID do documento indexado ou None em caso de erro
        """
        try:
            # Validar frescor dos dados (se metadata contém valid_from/valid_until)
            if metadata:
                from datetime import datetime, timedelta
                
                # Verificar se dados são muito antigos (mais de 7 dias sem atualização)
                indexed_at = metadata.get('indexed_at')
                if indexed_at:
                    try:
                        indexed_date = datetime.fromisoformat(indexed_at.replace('Z', '+00:00'))
                        days_old = (datetime.now(indexed_date.tzinfo) - indexed_date).days
                        
                        if days_old > 7:
                            logger.warning(
                                f"Dados antigos detectados ({days_old} dias). "
                                "Considere atualizar a fonte."
                            )
                    except Exception:
                        pass  # Ignorar erros de parsing de data
                
                # Verificar valid_from e valid_until
                valid_from = metadata.get('valid_from')
                valid_until = metadata.get('valid_until')
                
                if valid_until:
                    try:
                        until_date = datetime.fromisoformat(valid_until.replace('Z', '+00:00'))
                        if datetime.now(until_date.tzinfo) > until_date:
                            logger.warning(
                                f"Dados expirados (valid_until: {valid_until}). "
                                "Não indexando."
                            )
                            return None
                    except Exception:
                        pass
            
            # Gerar embedding do conteúdo
            embedding = generate_embedding(content)
            
            # Preparar dados para inserção
            data = {
                'content': content,
                'metadata': metadata or {},
                'embedding': embedding
            }
            
            # Inserir no Supabase
            result = self.supabase.table('knowledge_base').insert(data).execute()
            
            if result.data:
                doc_id = result.data[0]['id']
                logger.debug(f"Documento indexado: {doc_id[:8]}...")
                return doc_id
            else:
                logger.error("Erro ao indexar documento: nenhum dado retornado")
                return None
                
        except Exception as e:
            logger.error(f"Erro ao indexar documento: {e}")
            import traceback
            logger.error(traceback.format_exc())
            return None

