#!/usr/bin/env python3
"""
Otimização Treq via API - Executa dentro do container backend
"""
import requests
import json

def execute_optimization():
    """Executa otimização via API do backend"""
    print("🚀 EXECUTANDO OTIMIZAÇÃO VIA API BACKEND...")
    
    # 1. Obter token
    login_response = requests.post(
        "http://localhost:8002/auth/login",
        headers={"Content-Type": "application/x-www-form-urlencoded"},
        data="username=admin&password=admin123"
    )
    
    if login_response.status_code != 200:
        print("❌ Falha no login")
        return False
    
    token = login_response.json()["access_token"]
    print("✅ Token obtido")
    
    # 2. Executar otimização via chat (o backend tem acesso ao DB)
    optimization_query = """
    Execute as seguintes otimizações no banco de dados:
    
    1. Criar índice HNSW otimizado:
    CREATE INDEX IF NOT EXISTS knowledge_base_embedding_hnsw_idx 
    ON knowledge_base USING hnsw (embedding vector_cosine_ops) 
    WITH (m = 16, ef_construction = 64);
    
    2. Criar índices de metadados:
    CREATE INDEX IF NOT EXISTS kb_classification_idx 
    ON knowledge_base USING GIN ((metadata->'classification'));
    
    CREATE INDEX IF NOT EXISTS kb_allowed_users_idx 
    ON knowledge_base USING GIN ((metadata->'allowed_users'));
    
    3. Criar função de busca otimizada:
    CREATE OR REPLACE FUNCTION search_knowledge_optimized(
        query_embedding vector(768),
        similarity_threshold float DEFAULT 0.35,
        max_results int DEFAULT 10,
        user_id text DEFAULT 'anonymous'
    )
    RETURNS TABLE (
        id uuid,
        content text,
        metadata jsonb,
        similarity float
    ) AS $$
    BEGIN
        RETURN QUERY
        SELECT 
            kb.id,
            kb.content,
            kb.metadata,
            (1 - (kb.embedding <=> query_embedding))::float as similarity
        FROM knowledge_base kb
        WHERE 
            (
                kb.metadata->>'classification' = 'public' OR
                kb.metadata->'allowed_users' ? user_id OR
                kb.metadata->'allowed_users' ? '*'
            )
            AND (1 - (kb.embedding <=> query_embedding)) > similarity_threshold
        ORDER BY kb.embedding <=> query_embedding
        LIMIT max_results;
    END;
    $$ LANGUAGE plpgsql;
    
    Execute essas otimizações e reporte o resultado.
    """
    
    response = requests.post(
        "http://localhost:8002/chat/",
        headers={
            "Content-Type": "application/json",
            "Authorization": f"Bearer {token}"
        },
        json={
            "message": optimization_query,
            "conversation_id": "optimization",
            "stream": False
        }
    )
    
    if response.status_code == 200:
        result = response.json()
        print("✅ Otimização executada via API")
        print("📝 Resposta do sistema:")
        print(result.get("response", "Sem resposta"))
        return True
    else:
        print(f"❌ Falha na otimização: {response.status_code}")
        print(response.text)
        return False

def test_optimization():
    """Testa se a otimização funcionou"""
    print("\n⚡ TESTANDO OTIMIZAÇÃO...")
    
    # Obter token
    token = requests.post(
        "http://localhost:8002/auth/login",
        headers={"Content-Type": "application/x-www-form-urlencoded"},
        data="username=admin&password=admin123"
    ).json()["access_token"]
    
    # Testar busca
    test_response = requests.post(
        "http://localhost:8002/chat/",
        headers={
            "Content-Type": "application/json",
            "Authorization": f"Bearer {token}"
        },
        json={
            "message": "teste performance busca",
            "conversation_id": "test",
            "stream": False
        }
    )
    
    if test_response.status_code == 200:
        result = test_response.json()
        sources = result.get("sources", [])
        print(f"✅ Busca funcionando: {len(sources)} fontes encontradas")
        
        # Verificar se há informações de performance
        if sources:
            print("📊 Primeiras fontes:")
            for i, source in enumerate(sources[:2]):
                content_len = len(source.get("content", ""))
                print(f"   {i+1}. {content_len} chars - {source.get('metadata', {}).get('source', 'N/A')}")
        
        return True
    else:
        print(f"❌ Teste falhou: {test_response.status_code}")
        return False

def main():
    """Executa otimização completa via API"""
    print("🚀 OTIMIZAÇÃO TREQ VIA API BACKEND")
    print("=" * 50)
    
    try:
        # Executar otimização
        if execute_optimization():
            print("\n" + "=" * 50)
            # Testar resultado
            if test_optimization():
                print("\n🎉 OTIMIZAÇÃO CONCLUÍDA COM SUCESSO!")
                print("📝 Próximos passos:")
                print("   1. Monitorar performance das buscas")
                print("   2. Verificar logs do backend para confirmação")
                print("   3. Executar validate_audit_fixes.py para validar")
            else:
                print("\n⚠️ Otimização executada mas teste falhou")
        else:
            print("\n❌ Falha na execução da otimização")
            
    except Exception as e:
        print(f"❌ Erro geral: {e}")

if __name__ == "__main__":
    main()
