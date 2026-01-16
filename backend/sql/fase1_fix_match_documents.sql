-- =============================================================================
-- FASE 1.1 - FIX DEFINITIVO: match_documents
-- VERSÃO CORRIGIDA PARA SCHEMA extensions
-- Executar no SQL Editor do Supabase (https://supabase.com/dashboard)
-- Data: 2026-01-16
-- =============================================================================

-- PASSO 1: Dropar funções legadas para evitar conflitos
DROP FUNCTION IF EXISTS match_documents(vector, float, int, jsonb);
DROP FUNCTION IF EXISTS match_documents(extensions.vector, float, int, jsonb);
DROP FUNCTION IF EXISTS match_documents(extensions.vector, double precision, integer, jsonb);
DROP FUNCTION IF EXISTS public.match_documents(vector, float, int, jsonb);

-- PASSO 2: Criar função usando extensions.vector (schema onde pgvector está instalado)
CREATE OR REPLACE FUNCTION match_documents (
  query_embedding extensions.vector(384),
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
SECURITY DEFINER
SET search_path = public, extensions
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

-- PASSO 3: Criar índice HNSW para performance (se não existir)
DROP INDEX IF EXISTS knowledge_base_embedding_idx;
CREATE INDEX knowledge_base_embedding_idx 
ON knowledge_base 
USING hnsw (embedding extensions.vector_cosine_ops);

-- PASSO 4: Índice para busca por metadados
CREATE INDEX IF NOT EXISTS knowledge_base_metadata_idx 
ON knowledge_base 
USING gin (metadata);

-- PASSO 5: Atualizar estatísticas
ANALYZE knowledge_base;

-- =============================================================================
-- TESTE DE VALIDAÇÃO (Execute após os passos acima):
-- 
-- SELECT * FROM match_documents(
--   (SELECT embedding FROM knowledge_base LIMIT 1),
--   0.3,
--   5,
--   '{}'
-- );
-- =============================================================================
