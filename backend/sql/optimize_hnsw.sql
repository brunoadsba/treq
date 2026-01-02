-- =============================================================================
-- Otimização do Índice HNSW - Execute no Supabase SQL Editor
-- =============================================================================

-- 1. Configurar ef_search para sessão (afeta queries)
-- Valor menor = mais rápido, menos preciso
-- Valor maior = mais lento, mais preciso
-- Default é 40, vamos usar 32 para balance
SET hnsw.ef_search = 32;

-- 2. Verificar se o índice está sendo usado
-- Execute este EXPLAIN para ver o plano de execução
EXPLAIN (ANALYZE, BUFFERS)
SELECT 
    id,
    content,
    metadata,
    (1 - (embedding <=> '[0.1, 0.1, ...]'::vector(384))) AS similarity
FROM knowledge_base
ORDER BY embedding <=> '[0.1, 0.1, ...]'::vector(384)
LIMIT 5;

-- 3. Verificar estatísticas do índice
SELECT 
    indexrelname,
    idx_scan,
    idx_tup_read,
    idx_tup_fetch
FROM pg_stat_user_indexes
WHERE schemaname = 'public' AND tablename = 'knowledge_base';

-- 4. Se o índice não está sendo usado, pode ser necessário:
-- a) Dropar e recriar com parâmetros diferentes
-- b) Forçar uso do índice com SET enable_seqscan = off;
