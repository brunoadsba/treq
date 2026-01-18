#!/bin/bash
set -e

echo "🚀 Treq Backend - Starting..."

# Validar variáveis de ambiente obrigatórias
required_vars=(
    "SUPABASE_URL"
    "SUPABASE_ANON_KEY"
    "GROQ_API_KEY"
    "JWT_SECRET_KEY"
)

for var in "${required_vars[@]}"; do
    if [ -z "${!var}" ]; then
        echo "❌ ERROR: $var is not set"
        exit 1
    fi
done

echo "✅ Environment variables validated"

# Aguardar Redis estar pronto
if [ -n "$REDIS_URL" ]; then
    echo "⏳ Waiting for Redis..."
    while ! nc -z redis 6379; do
        sleep 1
    done
    echo "✅ Redis is ready"
fi

# Executar migrations se necessário
if [ "$RUN_MIGRATIONS" = "true" ]; then
    echo "🔄 Running database migrations..."
    python -m alembic upgrade head
fi

# Executar comando passado
echo "🎯 Executing: $@"
exec "$@"