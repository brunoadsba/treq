# Backend - Treq Assistente Operacional

FastAPI backend para o Assistente Operacional Treq.

## Setup

1. Criar ambiente virtual:
```bash
python3 -m venv treq-venv
source treq-venv/bin/activate
```

2. Instalar dependências:
```bash
pip install -r requirements.txt
```

3. Configurar variáveis de ambiente:
```bash
cp .env.example .env
# Editar .env com suas credenciais
```

4. Rodar servidor:
```bash
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

## Estrutura

- `app/` - Código da aplicação
  - `main.py` - FastAPI app principal
  - `config.py` - Configurações (Pydantic Settings)
  - `api/routes/` - Endpoints HTTP
  - `core/` - Lógica de negócio (RAG, LLM, etc.)
  - `services/` - Serviços externos (Supabase, etc.)
  - `models/` - Schemas Pydantic
  - `middleware/` - Middlewares (rate limiting, etc.)

## Endpoints

- `GET /` - Informações da API
- `GET /health` - Health check

## Documentação

- Swagger UI: http://localhost:8000/docs
- ReDoc: http://localhost:8000/redoc

