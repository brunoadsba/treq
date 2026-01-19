#!/usr/bin/env python3
"""
Otimização Treq: Aplicar padrões do guia AI-Ready
Execução: python3 optimize_treq_db.py
"""
import os
import psycopg2
from urllib.parse import urlparse

def get_db_connection():
    """Conecta ao Supabase usando DATABASE_URL do .env"""
    # Tentar via container backend primeiro
    try:
        import subprocess
        result = subprocess.run([
            "docker", "compose", "exec", "-T", "backend", 
            "python3", "-c", 
            "import os; print(os.getenv('DATABASE_URL', 'NOT_FOUND'))"
        ], capture_output=True, text=True, cwd="/home/brunoadsba/treq")
        
        if result.returncode == 0 and "postgresql://" in result.stdout:
            db_url = result.stdout.strip()
            print(f"✅ Usando DATABASE_URL do container: {db_url[:50]}...")
            return psycopg2.connect(db_url)
    except:
        pass
    
    # Fallback para .env local
    db_url = "postgresql://postgres:%23%40Br88080187@db.taidcwtolloreyxjvegi.supabase.co:5432/postgres"
    print(f"⚠️ Usando DATABASE_URL local: {db_url[:50]}...")
    return psycopg2.connect(db_url)

def optimize_indexes():
    """Aplica índices HNSW otimizados do guia AI-Ready"""
    print("🚀 OTIMIZANDO ÍNDICES TREQ...")
    
    conn = get_db_connection()
    cur = conn.cursor()
    
    try:
        # 1. Verificar se pgvector está instalado
        cur.execute("CREATE EXTENSION IF NOT EXISTS vector;")
        print("✅ Extensão vector verificada")
        
        # 2. Criar índice HNSW otimizado (se não existir)
        cur.execute("""
            CREATE INDEX IF NOT EXISTS knowledge_base_embedding_hnsw_idx 
            ON knowledge_base USING hnsw (embedding vector_cosine_ops) 
            WITH (m = 16, ef_construction = 64);
        """)
        print("✅ Índice HNSW criado/verificado")
        
        # 3. Índices de metadados para filtragem rápida
        cur.execute("""
            CREATE INDEX IF NOT EXISTS kb_classification_idx 
            ON knowledge_base USING GIN ((metadata->'classification'));
        """)
        
        cur.execute("""
            CREATE INDEX IF NOT EXISTS kb_allowed_users_idx 
            ON knowledge_base USING GIN ((metadata->'allowed_users'));
        """)
        print("✅ Índices de metadados criados")
        
        # 4. Índice operacional
        cur.execute("""
            CREATE INDEX IF NOT EXISTS kb_created_at_idx 
            ON knowledge_base (created_at DESC) 
            WHERE metadata->>'classification' != 'deleted';
        """)
        print("✅ Índices operacionais criados")
        
        conn.commit()
        print("🎉 OTIMIZAÇÃO DE ÍNDICES CONCLUÍDA!")
        
    except Exception as e:
        print(f"❌ Erro na otimização: {e}")
        conn.rollback()
    finally:
        conn.close()

def create_optimized_search_function():
    """Cria função de busca otimizada do guia AI-Ready"""
    print("🔍 CRIANDO FUNÇÃO DE BUSCA OTIMIZADA...")
    
    conn = get_db_connection()
    cur = conn.cursor()
    
    try:
        # Função de busca nativa otimizada
        cur.execute("""
            CREATE OR REPLACE FUNCTION search_knowledge_optimized(
                query_embedding vector(768),
                similarity_threshold float DEFAULT 0.35,
                max_results int DEFAULT 10,
                user_id text DEFAULT 'anonymous',
                filters jsonb DEFAULT '{}'::jsonb
            )
            RETURNS TABLE (
                id uuid,
                content text,
                metadata jsonb,
                similarity float,
                created_at timestamptz
            ) AS $$
            BEGIN
                RETURN QUERY
                SELECT 
                    kb.id,
                    kb.content,
                    kb.metadata,
                    (1 - (kb.embedding <=> query_embedding))::float as similarity,
                    kb.created_at
                FROM knowledge_base kb
                WHERE 
                    -- RLS: Verificar permissões
                    (
                        kb.metadata->>'classification' = 'public' OR
                        kb.metadata->'allowed_users' ? user_id OR
                        kb.metadata->'allowed_users' ? '*'
                    )
                    -- Similaridade mínima
                    AND (1 - (kb.embedding <=> query_embedding)) > similarity_threshold
                    -- Filtros adicionais
                    AND (filters = '{}'::jsonb OR kb.metadata @> filters)
                    -- Não incluir deletados
                    AND COALESCE(kb.metadata->>'classification', '') != 'deleted'
                ORDER BY kb.embedding <=> query_embedding
                LIMIT max_results;
            END;
            $$ LANGUAGE plpgsql;
        """)
        
        print("✅ Função search_knowledge_optimized criada")
        
        # Função de estatísticas
        cur.execute("""
            CREATE OR REPLACE FUNCTION get_knowledge_stats()
            RETURNS TABLE (
                total_docs bigint,
                avg_content_length numeric,
                classifications jsonb,
                sources jsonb
            ) AS $$
            BEGIN
                RETURN QUERY
                SELECT 
                    COUNT(*) as total_docs,
                    AVG(LENGTH(content))::numeric as avg_content_length,
                    jsonb_agg(DISTINCT metadata->'classification') as classifications,
                    jsonb_agg(DISTINCT metadata->'source') as sources
                FROM knowledge_base
                WHERE COALESCE(metadata->>'classification', '') != 'deleted';
            END;
            $$ LANGUAGE plpgsql;
        """)
        
        print("✅ Função get_knowledge_stats criada")
        
        conn.commit()
        print("🎉 FUNÇÕES OTIMIZADAS CRIADAS!")
        
    except Exception as e:
        print(f"❌ Erro na criação de funções: {e}")
        conn.rollback()
    finally:
        conn.close()

def benchmark_performance():
    """Testa performance da busca otimizada"""
    print("⚡ TESTANDO PERFORMANCE...")
    
    conn = get_db_connection()
    cur = conn.cursor()
    
    try:
        import time
        
        # Embedding de teste (768D para Gemini)
        test_embedding = [0.1] * 768
        
        # Teste 1: Função otimizada
        start = time.time()
        cur.execute("""
            SELECT content, similarity 
            FROM search_knowledge_optimized(%s::vector, 0.3, 5, 'test_user')
        """, (test_embedding,))
        results = cur.fetchall()
        duration_optimized = (time.time() - start) * 1000
        
        print(f"✅ Busca otimizada: {duration_optimized:.1f}ms ({len(results)} resultados)")
        
        # Teste 2: Estatísticas
        cur.execute("SELECT * FROM get_knowledge_stats()")
        stats = cur.fetchone()
        
        if stats:
            print(f"📊 Total documentos: {stats[0]}")
            print(f"📊 Tamanho médio: {stats[1]:.0f} chars")
        
        # Verificar índices
        cur.execute("""
            SELECT indexname, idx_scan, idx_tup_read 
            FROM pg_stat_user_indexes 
            WHERE tablename = 'knowledge_base' 
            AND indexname LIKE '%hnsw%'
        """)
        
        index_stats = cur.fetchall()
        for idx in index_stats:
            print(f"📈 Índice {idx[0]}: {idx[1]} scans, {idx[2]} reads")
        
        if duration_optimized < 100:
            print("🎉 PERFORMANCE EXCELENTE (<100ms)")
        elif duration_optimized < 500:
            print("⚠️ Performance OK (100-500ms)")
        else:
            print("❌ Performance lenta (>500ms) - verificar índices")
            
    except Exception as e:
        print(f"❌ Erro no benchmark: {e}")
    finally:
        conn.close()

def main():
    """Executa otimização completa do Treq"""
    print("🚀 OTIMIZAÇÃO TREQ - APLICANDO PADRÕES AI-READY")
    print("=" * 60)
    
    try:
        optimize_indexes()
        print()
        create_optimized_search_function()
        print()
        benchmark_performance()
        
        print("\n" + "=" * 60)
        print("🎉 OTIMIZAÇÃO TREQ CONCLUÍDA!")
        print("📝 Próximos passos:")
        print("   1. Atualizar código Python para usar search_knowledge_optimized()")
        print("   2. Monitorar performance com get_knowledge_stats()")
        print("   3. Configurar alertas para queries >500ms")
        
    except Exception as e:
        print(f"❌ Erro geral: {e}")

if __name__ == "__main__":
    main()
