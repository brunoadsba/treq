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
    - `chat.py` - Chat e streaming de respostas
    - `audio.py` - STT e TTS
    - `documents.py` - Upload e processamento de documentos
  - `core/` - Lógica de negócio
    - `rag_service.py` - Serviço RAG (vector search)
    - `llm_service.py` - Serviço LLM (roteamento 3 níveis)
    - `query_classifier.py` - Classificação de queries
    - `context_manager.py` - Gerenciamento de contexto
    - `tools/` - Tools (Metrics, Procedures, Status)
  - `services/` - Serviços externos
    - `document_converter.py` - Conversão de documentos (PDF/Excel → Markdown)
    - `embedding_service.py` - Geração de embeddings
    - `supabase_service.py` - Cliente Supabase
  - `models/` - Schemas Pydantic

## Funcionalidades Principais

### 1. Chat com Streaming
- **Endpoint:** `POST /chat/`
- **Streaming:** Suporta Server-Sent Events (SSE) para respostas incrementais
- **Roteamento Inteligente:** 3 níveis de modelos LLM
  - Nível 1: Llama 8B (queries simples)
  - Nível 2: Llama 70B (queries complexas)
  - Nível 3: GLM 4 (tarefas pesadas)

### 2. Processamento de Documentos
- **Endpoint:** `POST /documents/upload`
- **Formatos Suportados:** PDF, DOCX, PPTX, Excel (.xlsx, .xls)
- **Conversão Automática:** PDF/Excel → Markdown
- **Indexação RAG:** Chunking semântico e indexação automática

### 3. Áudio (STT/TTS)
- **STT:** `POST /audio/transcribe` - Transcrição de áudio (Groq Whisper)
- **TTS:** `POST /audio/synthesize` - Síntese de voz (Google Gemini TTS)
- **Cache:** Cache de áudio TTS para melhor performance

### 4. RAG (Retrieval-Augmented Generation)
- Busca vetorial com Supabase (pgvector)
- Embeddings multilíngue (paraphrase-multilingual-MiniLM-L12-v2)
- Chunking semântico preservando hierarquia
- Hybrid search (semântico + filtros)

## Endpoints Principais

### Chat
- `POST /chat/` - Chat principal (suporta `stream: true/false`)
  - **Body:** `{ message, user_id, conversation_id?, context?, stream? }`
  - **Response:** JSON ou SSE stream

### Documentos
- `POST /documents/upload` - Upload e indexação de documentos
  - **Form Data:** `file` (obrigatório), `document_type` (opcional)
  - **Response:** `{ success, chunks_indexed, message }`

### Áudio
- `POST /audio/transcribe` - Transcrição de áudio
- `POST /audio/synthesize` - Síntese de voz

### Health
- `GET /health` - Health check
- `GET /chat/health` - Health check do chat
- `GET /documents/health` - Health check de documentos

## Testes

### Scripts de Teste Disponíveis
```bash
# Teste de streaming
python scripts/test_streaming.py

# Teste de parser CoT
python scripts/test_cot_parser.py

# Teste de lógica do parser frontend
python scripts/test_cot_parser_frontend_logic.py

# Teste completo de documentos
python scripts/test_marker.py
```

## Documentação

- **Swagger UI:** http://localhost:8000/docs
- **ReDoc:** http://localhost:8000/redoc

## Variáveis de Ambiente

Principais variáveis necessárias no `.env`:

```bash
# APIs
GROQ_API_KEY=your_key
GEMINI_API_KEY=your_key
ZHIPU_API_KEY=your_key  # Para GLM 4

# Supabase
SUPABASE_URL=your_url
SUPABASE_KEY=your_service_role_key
SUPABASE_ANON_KEY=your_anon_key

# App
ENVIRONMENT=development
DEBUG=True
```

## Arquitetura LLM

### Roteamento em 3 Níveis
1. **Llama 8B Instant** (Groq) - Queries simples e rápidas
2. **Llama 70B Versatile** (Groq) - Queries complexas padrão
3. **GLM 4.7** (Zhipu AI) - Tarefas pesadas (análises multi-dimensionais, cálculos complexos, sínteses executivas)

### Chain of Thought (CoT)
- Respostas incluem tags `<pensamento>` e `<resposta>`
- Permite visualização do raciocínio do assistente
- Renderização diferenciada no frontend

