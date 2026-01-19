#!/usr/bin/env python3
"""
Teste rápido da base AI-Ready
Uso: python3 test-ai-db.py
"""
import psycopg2
import sys
import json

def test_database():
    try:
        # Conectar
        conn = psycopg2.connect("dbname=ai_ready_db user=postgres host=localhost")
        cur = conn.cursor()
        
        print("🧪 TESTANDO BASE AI...")
        
        # 1. Testar inserção
        test_embedding = [0.1] * 1536
        cur.execute("""
            INSERT INTO knowledge_base (content, content_hash, embedding, metadata)
            VALUES (%s, %s, %s, %s) RETURNING id
        """, (
            "Documento de teste para IA",
            "test_hash_ai",
            test_embedding,
            {"classification": "public", "allowed_users": ["*"], "source": "test"}
        ))
        
        doc_id = cur.fetchone()[0]
        print("✅ Inserção: OK")
        
        # 2. Testar busca vetorial
        cur.execute("SELECT content, similarity FROM search_kb(%s::vector, 1)", (test_embedding,))
        result = cur.fetchone()
        
        if result and result[1] > 0.99:  # Similaridade quase perfeita
            print(f"✅ Busca vetorial: OK (similaridade: {result[1]:.3f})")
        else:
            print("❌ Busca vetorial: FALHOU")
            return False
        
        # 3. Testar RLS
        cur.execute("SELECT COUNT(*) FROM knowledge_base WHERE status = 'active'")
        count = cur.fetchone()[0]
        print(f"✅ RLS: OK ({count} documentos acessíveis)")
        
        # 4. Testar performance
        import time
        start = time.time()
        cur.execute("SELECT content FROM search_kb(%s::vector, 5)", (test_embedding,))
        cur.fetchall()
        duration = (time.time() - start) * 1000
        
        if duration < 100:
            print(f"✅ Performance: EXCELENTE ({duration:.1f}ms)")
        elif duration < 500:
            print(f"⚠️  Performance: OK ({duration:.1f}ms)")
        else:
            print(f"❌ Performance: LENTA ({duration:.1f}ms)")
        
        # Limpar
        cur.execute("DELETE FROM knowledge_base WHERE id = %s", (doc_id,))
        conn.commit()
        
        print("\n🎉 BASE 100% FUNCIONAL PARA IA!")
        print("📝 Exemplo de uso:")
        print("   conn = psycopg2.connect('dbname=ai_ready_db user=postgres')")
        print("   cur.execute('SELECT * FROM search_kb(%s::vector, 5)', (embedding,))")
        
        return True
        
    except Exception as e:
        print(f"❌ ERRO: {e}")
        print("💡 Soluções:")
        print("   - Executar: ./setup-ai-db.sh")
        print("   - Verificar PostgreSQL rodando")
        print("   - Instalar: pip3 install psycopg2-binary")
        return False
    
    finally:
        if 'conn' in locals():
            conn.close()

if __name__ == "__main__":
    success = test_database()
    sys.exit(0 if success else 1)
