"""
Database Verification Service
Verifica a saúde da conexão vetorial com o Supabase.
"""
import os
import sys
import psycopg2
from loguru import logger
from app.config import get_settings

settings = get_settings()

from app.core.database import get_database_url

def verify_vector_store_health():
    """Verifica se as tabelas de vetores existem e estão acessíveis."""
    db_url = get_database_url()
    if not db_url:
        logger.error("❌ DATABASE_URL não configurada e não foi possível derivar.")
        return False, "Configuration Error: DATABASE_URL missing"

    try:
        conn = psycopg2.connect(db_url)
        cur = conn.cursor()
        
        # 1. Verificar extensão vector
        cur.execute("SELECT * FROM pg_extension WHERE extname = 'vector';")
        if not cur.fetchone():
            return False, "Extension 'vector' not installed"

        # 2. Verificar tabelas (suporte a langchain ou treq_knowledge_base)
        cur.execute("""
            SELECT table_name 
            FROM information_schema.tables 
            WHERE table_schema = 'public';
        """)
        tables = [row[0] for row in cur.fetchall()]
        
        known_tables = ['langchain_pg_embedding', 'treq_knowledge_base']
        found = [t for t in known_tables if t in tables]
        
        if not found:
            return False, f"No vector tables found. Expected validation on: {known_tables}"
            
        cur.close()
        conn.close()
        return True, "Vector Store Healthy"
        
    except Exception as e:
        logger.error(f"❌ DB Health Check failed: {e}")
        return False, str(e)

if __name__ == "__main__":
    is_healthy, msg = verify_vector_store_health()
    if is_healthy:
        print(f"✅ {msg}")
        sys.exit(0)
    else:
        print(f"❌ {msg}")
        sys.exit(1)
