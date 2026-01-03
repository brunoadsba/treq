"""
Serviço RAG (Retrieval-Augmented Generation) usando PGVector.
Busca semântica de documentos indexados no Supabase.
"""
from typing import List, Dict, Optional, Any
from loguru import logger
from app.services.supabase_service import get_supabase_client
from app.services.embedding_service import generate_embedding
from app.config import get_settings
from app.core.tracing import trace_rag_pipeline, tracing_metrics

import numpy as np
from numpy.linalg import norm
from cachetools import TTLCache, cached
from cachetools.keys import hashkey

settings = get_settings()

# Cache global para buscas RAG (200 itens, 1 minuto TTL)
rag_search_cache = TTLCache(maxsize=200, ttl=60)

class RAGService:
    """Serviço RAG para busca semântica de documentos."""
    
    def __init__(self):
        self.supabase = get_supabase_client()
        self.embedding_dimension = settings.embedding_dimension
    
    @trace_rag_pipeline(name="vector_search")
    @cached(cache=rag_search_cache, key=lambda self, query, top_k=3, similarity_threshold=0.7, filters=None: hashkey(query, top_k, similarity_threshold, str(filters)))
    def search_similar(
        self,
        query: str,
        top_k: int = 5,
        similarity_threshold: float = 0.35,
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
            from app.core.cache import cache_manager
            cached_results = await cache_manager.get("rag", f"{query}:{top_k}:{similarity_threshold}")
            if cached_results:
                logger.info(f"🎯 RAG Cache Hit para: {query[:50]}")
                return cached_results

            # Gerar embedding da query
            query_embedding = generate_embedding(query)
            
            # Preparar filtros de metadata para formato JSONB
            # Função SQL espera '{}' quando não há filtros, não None
            filter_metadata = filters if filters else {}
            
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
                
                # Registrar métricas RAG
                if documents:
                    tracing_metrics.log_rag_search(
                        query=query,
                        num_results=len(documents),
                        top_similarity=max(d['similarity'] for d in documents),
                        latency_ms=0,
                        search_type="vector"
                    )
                
                # GRAVAR NO CACHE (TTL de 10 minutos para buscas RAG)
                from app.core.cache import cache_manager
                await cache_manager.set("rag", f"{query}:{top_k}:{similarity_threshold}", documents, ttl=600)
                
                logger.info(
                    f"Busca RAG retornou {len(documents)} documentos para query: {query[:50]}..."
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
    
    @trace_rag_pipeline(name="hybrid_search")
    def search_hybrid(
        self,
        query: str,
        top_k: int = 5,
        similarity_threshold: float = 0.35,
        filters: Optional[Dict[str, Any]] = None,
        keyword_boost: float = 0.2
    ) -> List[Dict[str, Any]]:
        """
        Busca híbrida: combina busca vetorial (semântica) com busca por texto (keyword).
        
        Útil para termos exatos como códigos de erro, nomes de peças, etc.
        
        Args:
            query: Texto da consulta
            top_k: Número de documentos a retornar
            similarity_threshold: Limite mínimo de similaridade para busca vetorial
            filters: Filtros opcionais por metadata
            keyword_boost: Boost aplicado a documentos encontrados por keyword (0-1)
            
        Returns:
            List[Dict]: Lista de documentos encontrados, priorizando matches exatos
        """
        try:
            # 1. Busca vetorial (semântica)
            vector_results = self.search_similar(
                query=query,
                top_k=top_k * 2,  # Buscar mais para ter margem
                similarity_threshold=similarity_threshold,
                filters=filters
            )
            
            # 2. Busca por keyword (texto exato)
            keyword_results = self._search_by_keyword(
                query=query,
                top_k=top_k,
                filters=filters
            )
            
            # 3. Combinar resultados
            combined = self._merge_search_results(
                vector_results=vector_results,
                keyword_results=keyword_results,
                keyword_boost=keyword_boost,
                top_k=top_k
            )
            
            if combined:
                vector_count = sum(1 for d in combined if d.get('search_type') == 'vector')
                keyword_count = sum(1 for d in combined if d.get('search_type') == 'keyword')
                hybrid_count = sum(1 for d in combined if d.get('search_type') == 'hybrid')
                
                logger.info(
                    f"Busca híbrida retornou {len(combined)} documentos "
                    f"(vector: {vector_count}, keyword: {keyword_count}, hybrid: {hybrid_count})"
                )
            
            return combined
            
        except Exception as e:
            logger.error(f"Erro na busca híbrida: {e}")
            import traceback
            logger.error(traceback.format_exc())
            # Fallback para busca vetorial apenas
            return self.search_similar(query, top_k, similarity_threshold, filters)
    
    def _search_by_keyword(
        self,
        query: str,
        top_k: int = 5,
        filters: Optional[Dict[str, Any]] = None
    ) -> List[Dict[str, Any]]:
        """
        Busca por palavra-chave usando ILIKE do PostgreSQL.
        
        Args:
            query: Texto da consulta
            top_k: Número máximo de documentos
            filters: Filtros opcionais
            
        Returns:
            List[Dict]: Documentos que contêm as palavras-chave
        """
        try:
            # Extrair palavras-chave relevantes (>= 3 caracteres)
            keywords = [
                word.strip().lower() 
                for word in query.split() 
                if len(word.strip()) >= 3
            ]
            
            if not keywords:
                return []
            
            # Buscar documentos que contenham as palavras-chave
            # Usar a primeira palavra mais relevante para busca inicial
            primary_keyword = max(keywords, key=len)  # Palavra mais longa
            
            # Query builder com filtro ILIKE
            query_builder = self.supabase.table('knowledge_base').select(
                'id, content, metadata, created_at'
            ).ilike('content', f'%{primary_keyword}%').limit(top_k * 2)
            
            # Aplicar filtros de metadata se fornecidos
            if filters:
                for key, value in filters.items():
                    query_builder = query_builder.eq(f'metadata->>{key}', value)
            
            result = query_builder.execute()
            
            if not result.data:
                return []
            
            # Calcular score baseado em quantas keywords aparecem
            documents = []
            for row in result.data:
                content_lower = row.get('content', '').lower()
                
                # Contar matches de keywords
                keyword_matches = sum(1 for kw in keywords if kw in content_lower)
                keyword_score = keyword_matches / len(keywords)  # 0 a 1
                
                # Boost para matches exatos do query completo
                if query.lower() in content_lower:
                    keyword_score = min(1.0, keyword_score + 0.3)
                
                documents.append({
                    'id': row['id'],
                    'content': row['content'],
                    'metadata': row.get('metadata', {}),
                    'similarity': keyword_score,  # Usar score de keyword como "similaridade"
                    'created_at': row.get('created_at'),
                    'search_type': 'keyword',
                    'keyword_matches': keyword_matches
                })
            
            # Ordenar por score e retornar top_k
            documents.sort(key=lambda x: x['similarity'], reverse=True)
            return documents[:top_k]
            
        except Exception as e:
            logger.warning(f"Erro na busca por keyword: {e}")
            return []
    
    def _merge_search_results(
        self,
        vector_results: List[Dict[str, Any]],
        keyword_results: List[Dict[str, Any]],
        keyword_boost: float = 0.2,
        top_k: int = 5
    ) -> List[Dict[str, Any]]:
        """
        Combina resultados de busca vetorial e keyword.
        
        Estratégia:
        - Documentos encontrados por ambos: score máximo + boost
        - Documentos apenas vetorial: score vetorial
        - Documentos apenas keyword: score keyword com penalidade
        
        Args:
            vector_results: Resultados da busca vetorial
            keyword_results: Resultados da busca por keyword
            keyword_boost: Boost para documentos com match exato
            top_k: Número de documentos a retornar
            
        Returns:
            List[Dict]: Resultados combinados e re-rankeados
        """
        # Criar mapa por ID
        results_map = {}
        
        # Adicionar resultados vetoriais
        for doc in vector_results:
            doc_id = doc['id']
            doc['search_type'] = 'vector'
            results_map[doc_id] = doc
        
        # Processar resultados de keyword
        for doc in keyword_results:
            doc_id = doc['id']
            
            if doc_id in results_map:
                # Documento encontrado por ambos - aplicar boost
                existing = results_map[doc_id]
                existing['search_type'] = 'hybrid'
                existing['similarity'] = min(1.0, existing['similarity'] + keyword_boost)
                existing['keyword_matches'] = doc.get('keyword_matches', 0)
            else:
                # Documento apenas por keyword
                doc['similarity'] = doc['similarity'] * 0.8  # Pequena penalidade
                results_map[doc_id] = doc
        
        # Ordenar por score final e retornar top_k
        combined = list(results_map.values())
        combined.sort(key=lambda x: x['similarity'], reverse=True)
        
        return combined[:top_k]

    
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

    def delete_by_source(self, source: str) -> int:
        """
        Remove todos os chunks associados a uma fonte (arquivo).
        Faz correspondência por 'filename' ou 'source' no metadata.
        
        Args:
            source: Nome do arquivo/fonte a remover
            
        Returns:
            int: Número de chunks removidos
        """
        try:
            # Tentar por 'filename' e por 'source' no metadata JSONB
            # No PostgreSQL/Supabase, eq('metadata->>filename', source) funciona para JSONB
            res1 = self.supabase.table('knowledge_base').delete().eq('metadata->>filename', source).execute()
            count1 = len(res1.data) if res1.data else 0
            
            res2 = self.supabase.table('knowledge_base').delete().eq('metadata->>source', source).execute()
            count2 = len(res2.data) if res2.data else 0
            
            total = count1 + count2
            if total > 0:
                logger.info(f"🗑️ {total} chunks antigos removidos para a fonte: {source}")
            return total
        except Exception as e:
            logger.error(f"Erro ao remover chunks da fonte {source}: {e}")
            return 0

    def delete_by_ids(self, ids: List[str]) -> int:
        """
        Remove chunks específicos por uma lista de IDs.
        
        Args:
            ids: Lista de UUIDs para remover
            
        Returns:
            int: Número de chunks removidos
        """
        try:
            if not ids:
                return 0
            
            # Deletar em lotes se a lista for muito grande para evitar erros de limite de query
            batch_size = 100
            total_deleted = 0
            
            for i in range(0, len(ids), batch_size):
                batch = ids[i:i + batch_size]
                result = self.supabase.table('knowledge_base').delete().in_('id', batch).execute()
                total_deleted += len(result.data) if result.data else 0
                
            if total_deleted > 0:
                logger.debug(f"🗑️ {total_deleted} chunks removidos por ID")
            return total_deleted
        except Exception as e:
            logger.error(f"Erro ao deletar chunks por ID: {e}")
            return 0

    def clear_cache(self):
        """Limpa o cache de busca RAG."""
        rag_search_cache.clear()
        logger.info("🧹 Cache de busca RAG removido.")

