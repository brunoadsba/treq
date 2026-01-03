-- =============================================================================
-- FIX CONSOLIDADO (SÊNIOR) - Problemas de Busca Vetorial & Deploy
-- Executar no SQL Editor do Supabase
-- =============================================================================

-- 1. Garante que a extensão vector esteja no schema public para evitar ambiguidades
-- O erro "extensions.vector <=> extensions.vector" geralmente ocorre por descompasso de schemas
CREATE EXTENSION IF NOT EXISTS vector WITH SCHEMA public;

-- 2. Limpeza de funções legadas (evita conflitos de assinatura)
DROP FUNCTION IF EXISTS match_documents(vector, float, int, jsonb);

-- 3. Função match_documents com CASTS EXPLÍCITOS (Solução Definitiva)
-- Adicionamos ::vector nos operadores para garantir que o Postgres use a extensão correta
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
SET search_path = public
AS $$
BEGIN
  RETURN QUERY
  SELECT
    kb.id,
    kb.content,
    kb.metadata,
    (1 - (kb.embedding::vector <=> query_embedding::vector))::float AS similarity,
    kb.created_at
  FROM knowledge_base kb
  WHERE (1 - (kb.embedding::vector <=> query_embedding::vector)) > match_threshold
    AND (filter_metadata = '{}' OR kb.metadata @> filter_metadata)
  ORDER BY kb.embedding::vector <=> query_embedding::vector
  LIMIT match_count;
END;
$$;

-- 4. Índice HNSW (Hierarchical Navigable Small World)
-- Essencial para o modo 100% Free, pois reduz o uso de CPU durante buscas
DROP INDEX IF EXISTS knowledge_base_embedding_idx;
CREATE INDEX knowledge_base_embedding_idx 
ON knowledge_base 
USING hnsw (embedding vector_cosine_ops);

-- 5. Otimização de busca por metadados
CREATE INDEX IF NOT EXISTS knowledge_base_metadata_idx 
ON knowledge_base 
USING gin (metadata);

-- 6. Atualização de estatísticas do Query Planner
ANALYZE knowledge_base;

-- =============================================================================
-- TESTE DE VALIDAÇÃO (Opcional):
-- SELECT * FROM match_documents(array_fill(0, array[384])::vector, 0.5, 1);
-- =============================================================================
