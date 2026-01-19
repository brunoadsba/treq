#!/usr/bin/env python3
"""
Exemplo assíncrono para aplicações web modernas
Uso: pip install asyncpg && python3 async-example.py
"""
import asyncio
import asyncpg
import os

async def setup_async_connection():
    """Exemplo de conexão assíncrona otimizada para FastAPI/web apps"""
    
    # Pool de conexões para alta concorrência
    pool = await asyncpg.create_pool(
        host="localhost",
        port=5432,
        user="postgres",
        database=os.getenv("DB_NAME", "ai_ready_db"),
        min_size=5,
        max_size=20
    )
    
    return pool

async def insert_document(pool, content: str, embedding: list, metadata: dict):
    """Inserção assíncrona otimizada"""
    async with pool.acquire() as conn:
        return await conn.fetchval("""
            INSERT INTO knowledge_base (content, content_hash, embedding, metadata)
            VALUES ($1, $2, $3, $4) RETURNING id
        """, content, hash(content), embedding, metadata)

async def search_similar(pool, query_embedding: list, limit: int = 5):
    """Busca assíncrona com pool de conexões"""
    async with pool.acquire() as conn:
        return await conn.fetch(
            "SELECT content, similarity FROM search_kb($1::vector, $2)",
            query_embedding, limit
        )

async def main():
    """Exemplo de uso completo"""
    print("🔄 Testando conexão assíncrona...")
    
    pool = await setup_async_connection()
    
    # Teste de inserção
    embedding_dim = int(os.getenv("EMBEDDING_DIM", "1536"))
    test_embedding = [0.1] * embedding_dim
    
    doc_id = await insert_document(
        pool, 
        "Documento assíncrono de teste",
        test_embedding,
        {"classification": "public", "allowed_users": ["*"], "source": "async_test"}
    )
    
    print(f"✅ Documento inserido: {doc_id}")
    
    # Teste de busca
    results = await search_similar(pool, test_embedding, 1)
    print(f"✅ Busca executada: {len(results)} resultados")
    
    # Limpeza
    async with pool.acquire() as conn:
        await conn.execute("DELETE FROM knowledge_base WHERE id = $1", doc_id)
    
    await pool.close()
    print("🎉 Teste assíncrono concluído com sucesso!")

if __name__ == "__main__":
    asyncio.run(main())
