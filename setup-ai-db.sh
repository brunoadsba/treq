#!/bin/bash
# Setup AI-Ready Database - Executável em 5 minutos
set -e

# Configurações (editáveis)
EMBEDDING_DIM=${EMBEDDING_DIM:-1536}  # OpenAI default, use 768 para modelos menores
DB_NAME=${DB_NAME:-ai_ready_db}
DB_USER=${DB_USER:-postgres}

echo "🚀 SETUP AI DATABASE - INICIANDO..."
echo "📊 Configuração: ${EMBEDDING_DIM}D embeddings, DB: ${DB_NAME}"

# Detectar OS e instalar dependências
if [[ "$OSTYPE" == "linux-gnu"* ]]; then
    echo "📦 Instalando PostgreSQL + pgvector (Ubuntu/Debian)..."
    sudo apt update -qq
    sudo apt install -y postgresql postgresql-contrib python3-pip
    
    # Instalar pgvector
    sudo apt install -y postgresql-15-pgvector || {
        echo "⚠️  pgvector via apt falhou, compilando..."
        sudo apt install -y build-essential postgresql-server-dev-15
        git clone --branch v0.5.1 https://github.com/pgvector/pgvector.git /tmp/pgvector
        cd /tmp/pgvector && make && sudo make install
    }
    
elif [[ "$OSTYPE" == "darwin"* ]]; then
    echo "📦 Instalando PostgreSQL + pgvector (macOS)..."
    brew install postgresql pgvector python3
    brew services start postgresql
else
    echo "❌ OS não suportado. Use Docker: docker run -d --name ai-db -p 5432:5432 -e POSTGRES_PASSWORD=postgres ankane/pgvector"
    exit 1
fi

# Instalar dependências Python
pip3 install psycopg2-binary numpy --quiet

# Configurar PostgreSQL
sudo -u postgres createdb ai_ready_db 2>/dev/null || echo "⚠️  Database já existe"
sudo -u postgres psql ai_ready_db -c "CREATE EXTENSION IF NOT EXISTS vector;" -q

echo "✅ Dependências instaladas!"

# Criar estrutura
echo "🏗️  Criando estrutura..."
sudo -u postgres psql ${DB_NAME} << EOF
-- Tabela otimizada com dimensão configurável
CREATE TABLE IF NOT EXISTS knowledge_base (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    content TEXT NOT NULL,
    content_hash VARCHAR(64) UNIQUE NOT NULL,
    embedding vector(${EMBEDDING_DIM}),
    metadata JSONB NOT NULL DEFAULT '{"classification":"public","allowed_users":["*"],"source":"unknown"}',
    created_at TIMESTAMPTZ DEFAULT NOW(),
    status VARCHAR(10) DEFAULT 'active'
);

-- RLS simples
ALTER TABLE knowledge_base ENABLE ROW LEVEL SECURITY;
CREATE POLICY IF NOT EXISTS kb_policy ON knowledge_base FOR ALL USING (
    metadata->>'classification' = 'public' OR 
    current_user = '${DB_USER}'
);

-- Índice crítico
CREATE INDEX IF NOT EXISTS kb_embedding_idx ON knowledge_base 
USING hnsw (embedding vector_cosine_ops) WITH (m = 16, ef_construction = 64);

-- Função de busca configurável
CREATE OR REPLACE FUNCTION search_kb(query_embedding vector(${EMBEDDING_DIM}), limit_results int DEFAULT 5)
RETURNS TABLE (content text, similarity float) AS \$\$
BEGIN
    RETURN QUERY
    SELECT kb.content, (1 - (kb.embedding <=> query_embedding))::float
    FROM knowledge_base kb
    WHERE kb.status = 'active'
    ORDER BY kb.embedding <=> query_embedding
    LIMIT limit_results;
END;
\$\$ LANGUAGE plpgsql;
EOF

echo "✅ Estrutura criada!"

# Teste rápido
echo "🧪 Testando..."
sudo -u postgres psql ${DB_NAME} -c "
INSERT INTO knowledge_base (content, content_hash, embedding) VALUES 
('Documento teste', 'test123', array_fill(0.1, ARRAY[${EMBEDDING_DIM}])::vector);

SELECT content, similarity FROM search_kb(array_fill(0.1, ARRAY[${EMBEDDING_DIM}])::vector, 1);

DELETE FROM knowledge_base WHERE content_hash = 'test123';
" -q

echo "🎉 BASE AI-READY CONFIGURADA COM SUCESSO!"
echo "📊 Conecte em: postgresql://${DB_USER}@localhost:5432/${DB_NAME}"
echo "⚡ Performance: Busca vetorial otimizada com HNSW (${EMBEDDING_DIM}D)"
echo "🔒 Segurança: RLS habilitado"
echo ""
echo "💡 Configurações disponíveis:"
echo "   EMBEDDING_DIM=768 ./setup-ai-db.sh  # Para modelos menores"
echo "   DB_NAME=minha_base ./setup-ai-db.sh  # Nome customizado"
