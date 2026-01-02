-- =============================================================================
-- Script de Otimização da Base de Conhecimento RAG - Projeto Treq
-- Executar no SQL Editor do Supabase
-- =============================================================================

-- 1. Habilitar a extensão pgvector se ainda não estiver habilitada
CREATE EXTENSION IF NOT EXISTS vector;

-- 2. Recriar a função match_documents (precisa dropar antes se a assinatura/retorno mudou)
DROP FUNCTION IF EXISTS match_documents(vector, float, int, jsonb);

CREATE OR REPLACE FUNCTION match_documents (
  query_embedding vector(384),
  match_threshold float,
  match_count int,
  filter_metadata jsonb DEFAULT '{}'
) RETURNS TABLE (
  id uuid,
  content text,
  metadata jsonb,
  similarity float,
  created_at timestamp
)
LANGUAGE plpgsql
AS $$
BEGIN
  RETURN QUERY
  SELECT
    kb.id,
    kb.content,
    kb.metadata,
    (1 - (kb.embedding <=> query_embedding))::float AS similarity,
    kb.created_at
  FROM knowledge_base kb
  WHERE (1 - (kb.embedding <=> query_embedding)) > match_threshold
    AND (filter_metadata = '{}' OR kb.metadata @> filter_metadata)
  ORDER BY kb.embedding <=> query_embedding
  LIMIT match_count;
END;
$$;

-- 3. Criar índice HNSW para busca vetorial otimizada
-- HNSW (Hierarchical Navigable Small World) é muito mais rápido que busca sequencial
-- m=16: número de conexões por nó (padrão recomendado)
-- ef_construction=64: qualidade do índice durante construção (maior = melhor precisão, mais lento para construir)
DROP INDEX IF EXISTS knowledge_base_embedding_idx;

CREATE INDEX knowledge_base_embedding_idx 
ON knowledge_base 
USING hnsw (embedding vector_cosine_ops)
WITH (m = 16, ef_construction = 64);

-- 4. Criar índice GIN para buscas por metadata (filtros híbridos)
CREATE INDEX IF NOT EXISTS knowledge_base_metadata_idx 
ON knowledge_base 
USING gin (metadata);

-- 5. Analisar a tabela para atualizar estatísticas do query planner
ANALYZE knowledge_base;

-- =============================================================================
-- Verificação: Execute após o script para confirmar que tudo está correto
-- =============================================================================
-- 
-- Verificar função:
-- SELECT routine_name FROM information_schema.routines WHERE routine_name = 'match_documents';
--
-- Verificar índices:
-- SELECT indexname, indexdef FROM pg_indexes WHERE tablename = 'knowledge_base';
--
-- Teste rápido da função (substitua o embedding de exemplo):
-- SELECT * FROM match_documents(
--   '[0.1, 0.2, ...]'::vector(384),
--   0.5,
--   5,
--   '{}'::jsonb
-- );
-- =============================================================================
