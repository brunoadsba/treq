from app.services.supabase_service import get_supabase_client
from app.services.embedding_service import generate_embedding
import json

def audit_rag():
    supabase = get_supabase_client()
    
    # 1. Verificar contagem de documentos
    try:
        res = supabase.table('knowledge_base').select('id', count='exact').execute()
        count = res.count if hasattr(res, 'count') else len(res.data)
        print(f"Total de documentos na 'knowledge_base': {count}")
        
        if count > 0:
            print(f"Amostra do primeiro documento: {res.data[0]}")
            
            # 2. Verificar se a função RPC match_documents funciona
            print("\nTestando RPC match_documents...")
            test_query = "procedimentos operacionais"
            vec = generate_embedding(test_query)
            
            rpc_res = supabase.rpc(
                'match_documents',
                {
                    'query_embedding': vec,
                    'match_threshold': 0.1, # Threshold super baixo para teste
                    'match_count': 5,
                    'filter_metadata': {}
                }
            ).execute()
            
            print(f"Resultados do RPC (threshold 0.1): {len(rpc_res.data)}")
            if rpc_res.data:
                for doc in rpc_res.data:
                    print(f"- ID: {doc['id']}, Sim: {doc.get('similarity')}, Content: {doc['content'][:50]}...")
            else:
                print("⚠️ RPC não retornou nada mesmo com threshold 0.1")
        else:
            print("❌ Tabela 'knowledge_base' está VAZIA ou inacessível.")
            
    except Exception as e:
        print(f"❌ Erro na auditoria: {str(e)}")

if __name__ == "__main__":
    audit_rag()
