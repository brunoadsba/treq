-- =============================================================================
-- EXECUTE ESTE SQL NO SUPABASE - Correção da Função match_documents
-- =============================================================================

-- Dropar função antiga se existir
DROP FUNCTION IF EXISTS match_documents(vector, float, int, jsonb);

-- Criar função corrigida
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
