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
        Busca documentos similares usando busca vetorial nativa do PostgreSQL (pgvector).
        
        Usa função RPC match_documents no Supabase para busca otimizada.
        Isso é muito mais eficiente que calcular similaridade em memória.
        
        Args:
            query: Texto da consulta
            top_k: Número de documentos a retornar
            similarity_threshold: Limite mínimo de similaridade (0-1)
            filters: Filtros opcionais por metadata (dict com chave-valor)
            
        Returns:
            List[Dict]: Lista de documentos encontrados com metadata
        """
        try:
            # Gerar embedding da query
            query_embedding = generate_embedding(query)
            
            # Preparar filtros de metadata para formato JSONB
            filter_metadata = None
            if filters:
                filter_metadata = filters
            
            # Chamar função RPC do Supabase para busca vetorial nativa
            try:
                result = self.supabase.rpc(
                    'match_documents',
                    {
                        'query_embedding': query_embedding,
                        'match_threshold': similarity_threshold,
                        'match_count': top_k,
                        'filter_metadata': filter_metadata
                    }
                ).execute()
                
                if not result.data:
                    logger.info(f"Nenhum documento encontrado com threshold {similarity_threshold}")
                    return []
                
                # Converter resultado para formato esperado
                documents = []
                for row in result.data:
                    documents.append({
                        'id': row.get('id'),
                        'content': row.get('content', ''),
                        'metadata': row.get('metadata', {}),
                        'similarity': float(row.get('similarity', 0.0)),
                        'created_at': row.get('created_at')
                    })
                
                logger.info(
                    f"Busca RAG retornou {len(documents)} documentos para query: {query[:50]}... "
                    f"(threshold: {similarity_threshold}, similarity range: "
                    f"{min(d['similarity'] for d in documents):.3f}-{max(d['similarity'] for d in documents):.3f})"
                )
                return documents
                
            except Exception as rpc_error:
                # Fallback: Se função RPC não existir ou falhar, usar método antigo com warning
                logger.warning(
                    f"Erro ao chamar função RPC match_documents: {rpc_error}. "
                    "Usando fallback (cálculo em memória). "
                    "Execute o script SQL create_match_documents_function.sql no Supabase."
                )
                return self._search_similar_fallback(query, query_embedding, top_k, similarity_threshold, filters)
            
        except Exception as e:
            logger.error(f"Erro na busca RAG: {e}")
            import traceback
            logger.error(traceback.format_exc())
            return []
    
    def _search_similar_fallback(
        self,
        query: str,
        query_embedding: List[float],
        top_k: int,
        similarity_threshold: float,
        filters: Optional[Dict[str, Any]] = None
    ) -> List[Dict[str, Any]]:
        """
        Fallback: cálculo de similaridade em memória (método antigo).
        Usado apenas se função RPC não estiver disponível.
        
        Args:
            query: Texto da consulta (para logging)
            query_embedding: Embedding já gerado da query
            top_k: Número de documentos a retornar
            similarity_threshold: Limite mínimo de similaridade
            filters: Filtros opcionais por metadata
            
        Returns:
            List[Dict]: Lista de documentos encontrados
        """
        try:
            # Buscar documentos do banco
            query_builder = self.supabase.table('knowledge_base').select('*')
            
            # Aplicar filtros de metadata se fornecidos
            if filters:
                for key, value in filters.items():
                    query_builder = query_builder.eq(f'metadata->>{key}', value)
            
            result = query_builder.execute()
            
            if not result.data:
                logger.info("Nenhum documento encontrado (fallback)")
                return []
            
            # Calcular similaridade em memória
            import numpy as np
            from numpy.linalg import norm
            
            documents_with_similarity = []
            query_vec = np.array(query_embedding)
            
            for row in result.data:
                if not row.get('embedding'):
                    continue
                
                doc_embedding = row['embedding']
                
                # Converter embedding para array numpy
                if isinstance(doc_embedding, str):
                    import json
                    try:
                        doc_embedding = json.loads(doc_embedding)
                    except:
                        continue
                
                doc_vec = np.array(doc_embedding, dtype=np.float32)
                
                # Verificar dimensões
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
            
            # Ordenar e retornar top_k
            documents_with_similarity.sort(key=lambda x: x['similarity'], reverse=True)
            documents = documents_with_similarity[:top_k]
            
            logger.info(f"Busca RAG (fallback) retornou {len(documents)} documentos")
            return documents
            
        except Exception as e:
            logger.error(f"Erro no fallback de busca RAG: {e}")
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

