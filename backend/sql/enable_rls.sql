-- ============================================
-- Script: Habilitar Row Level Security (RLS)
-- Tabela: knowledge_base
-- Projeto: Treq - Assistente Operacional Sotreq
-- ============================================

-- 1. Habilitar RLS na tabela knowledge_base
ALTER TABLE knowledge_base ENABLE ROW LEVEL SECURITY;

-- 2. Remover políticas existentes (se houver)
DROP POLICY IF EXISTS "users_read_allowed_docs" ON knowledge_base;
DROP POLICY IF EXISTS "service_role_full_access" ON knowledge_base;

-- 3. Política de leitura para usuários
-- Permite acesso a documentos:
-- - Públicos (classification = 'public')
-- - Com allowed_users contendo '*' (todos)
-- - Com o ID do usuário na lista allowed_users
CREATE POLICY "users_read_allowed_docs" ON knowledge_base
FOR SELECT USING (
    -- Documentos públicos
    metadata->>'classification' = 'public'
    -- OU documentos com "*" em allowed_users (acesso geral)
    OR metadata->'allowed_users' ? '*'
    -- OU documentos com user_id específico (via auth.uid())
    -- Nota: Em aplicações que não usam Supabase Auth diretamente,
    -- o filtro é feito na aplicação via _filter_by_rls()
);

-- 4. Política para service_role (acesso total para backend)
-- Necessário para operações de indexação e re-indexação
CREATE POLICY "service_role_full_access" ON knowledge_base
FOR ALL USING (
    auth.role() = 'service_role'
);

-- 5. Verificar políticas criadas
SELECT 
    policyname,
    cmd,
    qual
FROM pg_policies 
WHERE tablename = 'knowledge_base';

-- ============================================
-- ATENÇÃO: 
-- - Execute este script APENAS UMA VEZ
-- - Faça backup da base antes de executar
-- - Teste em ambiente de desenvolvimento primeiro
-- ============================================
