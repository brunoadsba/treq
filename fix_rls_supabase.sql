-- Script para corrigir dados RLS no Supabase
-- Execute este SQL no Supabase SQL Editor

-- 1. Verificar tabelas existentes
SELECT table_name 
FROM information_schema.tables 
WHERE table_schema = 'public' 
AND (table_name LIKE '%knowledge%' OR table_name LIKE '%embedding%' OR table_name LIKE '%langchain%');

-- 2. Verificar estrutura da tabela principal
\d treq_knowledge_base;

-- 3. Corrigir vazamento RLS (ajuste o nome da tabela conforme necessário)
-- OPÇÃO A: Se a tabela for treq_knowledge_base
UPDATE treq_knowledge_base 
SET metadata = jsonb_set(metadata, '{allowed_users}', '["admin"]') 
WHERE metadata->>'classification' = 'confidential' 
AND metadata->>'allowed_users' = '["*"]';

-- OPÇÃO B: Se a tabela for langchain_pg_collection
UPDATE langchain_pg_collection 
SET cmetadata = jsonb_set(cmetadata, '{allowed_users}', '["admin"]') 
WHERE cmetadata->>'classification' = 'confidential' 
AND cmetadata->>'allowed_users' = '["*"]';

-- OPÇÃO C: Se a tabela for langchain_pg_embedding  
UPDATE langchain_pg_embedding 
SET cmetadata = jsonb_set(cmetadata, '{allowed_users}', '["admin"]') 
WHERE cmetadata->>'classification' = 'confidential' 
AND cmetadata->>'allowed_users' = '["*"]';

-- 4. Verificar correção
SELECT 
    metadata->>'filename' as arquivo,
    metadata->>'classification' as classificacao,
    metadata->>'allowed_users' as usuarios_permitidos
FROM treq_knowledge_base 
WHERE metadata->>'classification' = 'confidential'
LIMIT 5;
