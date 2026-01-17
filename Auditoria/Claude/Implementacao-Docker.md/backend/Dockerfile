# Multi-stage build para otimização
FROM python:3.11-slim as builder

# Evitar prompts interativos
ENV DEBIAN_FRONTEND=noninteractive

# Instalar dependências de build
RUN apt-get update && apt-get install -y --no-install-recommends \
    gcc \
    g++ \
    make \
    libpq-dev \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Criar venv
RUN python -m venv /opt/venv
ENV PATH="/opt/venv/bin:$PATH"

# Copiar requirements
WORKDIR /build
COPY requirements.txt .

# Instalar dependências Python
RUN pip install --no-cache-dir --upgrade pip setuptools wheel && \
    pip install --no-cache-dir -r requirements.txt

# ===== STAGE 2: Runtime =====
FROM python:3.11-slim

# Metadados
LABEL maintainer="Treq DevOps <devops@sotreq.com>"
LABEL description="Treq Enterprise Backend - FastAPI + LangGraph"

# Variáveis de ambiente
ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    PATH="/opt/venv/bin:$PATH" \
    WORKERS=4 \
    PORT=8002

# Instalar apenas runtime dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    libpq5 \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Copiar venv do builder
COPY --from=builder /opt/venv /opt/venv

# Criar usuário não-root
RUN useradd -m -u 1000 treq && \
    mkdir -p /app /app/logs && \
    chown -R treq:treq /app

# Mudar para usuário não-root
USER treq
WORKDIR /app

# Copiar código da aplicação
COPY --chown=treq:treq . .

# Healthcheck
HEALTHCHECK --interval=30s --timeout=10s --retries=3 --start-period=40s \
    CMD curl -f http://localhost:${PORT}/health || exit 1

# Expor porta
EXPOSE ${PORT}

# Script de entrypoint
COPY --chown=treq:treq docker-entrypoint.sh /app/
RUN chmod +x /app/docker-entrypoint.sh

ENTRYPOINT ["/app/docker-entrypoint.sh"]
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8002", "--workers", "4"]