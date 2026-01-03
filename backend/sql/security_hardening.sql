-- =============================================================================
-- SECURITY HARDENING - Projeto Treq
-- Corrige alertas do Supabase Linter (Security & Best Practices)
-- =============================================================================

-- 1. Correção: Function Search Path Mutable
-- Recomendação de segurança: Definir search_path explicitamente em funções
-- para evitar ataques de sequestro de schema.
ALTER FUNCTION public.match_documents(vector, float, int, jsonb) SET search_path = public;

-- 2. Correção: RLS Disabled in Public (Table: feedbacks)
-- Ativa o Row Level Security na tabela de feedbacks.
ALTER TABLE public.feedbacks ENABLE ROW LEVEL SECURITY;

-- 3. Políticas de Segurança para a tabela feedbacks
-- Permite que qualquer pessoa insira feedbacks (uso anônimo no frontend)
-- Mas impede que usuários anônimos leiam ou deletem feedbacks de outros.
DROP POLICY IF EXISTS "Permitir inserção anônima" ON public.feedbacks;
CREATE POLICY "Permitir inserção anônima" ON public.feedbacks 
FOR INSERT WITH CHECK (true);

-- Permite leitura apenas para a role de serviço (backend) ou administrador
DROP POLICY IF EXISTS "Leitura restrita ao serviço" ON public.feedbacks;
CREATE POLICY "Leitura restrita ao serviço" ON public.feedbacks 
FOR SELECT USING (auth.role() = 'service_role');

-- 4. Garantia de RLS na knowledge_base (Boa prática)
ALTER TABLE public.knowledge_base ENABLE ROW LEVEL SECURITY;

DROP POLICY IF EXISTS "Leitura pública da knowledge_base" ON public.knowledge_base;
CREATE POLICY "Leitura pública da knowledge_base" ON public.knowledge_base 
FOR SELECT USING (true);

DROP POLICY IF EXISTS "Escrita restrita à knowledge_base" ON public.knowledge_base;
CREATE POLICY "Escrita restrita à knowledge_base" ON public.knowledge_base 
FOR ALL USING (auth.role() = 'service_role');

-- 5. Atualização de estatísticas
ANALYZE public.feedbacks;
ANALYZE public.knowledge_base;

-- =============================================================================
-- Verificação:
-- SELECT relname, relrowsecurity FROM pg_class WHERE relname IN ('feedbacks', 'knowledge_base');
-- =============================================================================
