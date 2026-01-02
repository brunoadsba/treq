-- Habilitar a extensão pgvector se ainda não estiver habilitada
create extension if not exists vector;

-- Recriar a função match_documents (precisa dropar antes se a assinatura/retorno mudou)
drop function if exists match_documents(vector, float, int, jsonb);

create or replace function match_documents (
  query_embedding vector(384),
  match_threshold float,
  match_count int,
  filter_metadata jsonb default '{}'
) returns table (
  id uuid,
  content text,
  metadata jsonb,
  similarity float,
  created_at timestamp
)
language plpgsql
as $$
begin
  return query
  select
    kb.id,
    kb.content,
    kb.metadata,
    (1 - (kb.embedding <=> query_embedding))::float as similarity,
    kb.created_at
  from knowledge_base kb
  where (1 - (kb.embedding <=> query_embedding)) > match_threshold
    and (filter_metadata = '{}' or kb.metadata @> filter_metadata)
  order by kb.embedding <=> query_embedding
  limit match_count;
end;
$$;
