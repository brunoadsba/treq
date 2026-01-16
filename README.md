# Treq - Assistente Operacional Sotreq

Assistente operacional inteligente com RAG, LLM avançado, processamento de documentos e suporte completo a áudio (STT/TTS).

## 🚀 Visão Geral

O Treq é um assistente operacional desenvolvido para a Sotreq, combinando:
- **RAG (Retrieval-Augmented Generation)** para busca em documentos
- **Roteamento inteligente em 3 níveis** de modelos LLM (8B → 70B → GLM 4)
- **Streaming de respostas** para melhor UX
- **Processamento de documentos** (PDF, DOCX, Excel)
- **Suporte completo a áudio** (Speech-to-Text e Text-to-Speech)
- **Vision (Multimodal)** para análise de imagens e capturas de câmera
- **Chain of Thought** para transparência no raciocínio

## 📋 Status do Projeto

### ✅ Funcionalidades Implementadas

| Funcionalidade | Status | Descrição |
|----------------|--------|-----------|
| **RAG Core** | ✅ Completo | Busca vetorial com Supabase, embeddings multilíngue |
| **Query Classification** | ✅ Completo | 7 tipos de queries (alerta, procedimento, métrica, status, etc.) |
| **LLM Service** | ✅ Completo | Roteamento 3 níveis (8B/70B/GLM 4), streaming |
| **Streaming** | ✅ Completo | Server-Sent Events para respostas incrementais |
| **Chain of Thought** | ✅ Completo | Parser e renderização diferenciada |
| **Document Processing** | ✅ Completo (MVP) | PDF e Excel (nativo), conversão para Markdown |
| **Upload de Documentos** | ✅ Completo | Frontend integrado com backend |
| **Audio STT/TTS** | ✅ Completo | Groq Whisper + Google Gemini TTS |
| **Vision & Multimodal** | ✅ Completo | Captura de câmera, análise de imagens (OCR + Tabelas) |
| **Tools** | ✅ Completo | Metrics, Procedures, Status |
| **Observabilidade** | ✅ Completo | Tracing end-to-end com LangSmith |
| **Feedback Loop** | ✅ Completo | Botões 👍/👎 para melhoria contínua |
| **Frontend Completo** | ✅ Completo | Next.js 15, UX Premium, Captura Vision |

### ⚠️ Pendências

| Funcionalidade | Prioridade | Status |
|----------------|------------|--------|
| **Deploy** | Alta | 🟢 Em andamento |
| **Lógica específica de métricas** | Alta | Placeholder implementado |
| **Autenticação** | Média | Não implementado |
| **Suporte DOCX/PPTX** | Baixa | Não suportado no MVP |

## 🏗️ Arquitetura

### Backend (FastAPI)
```
treq/backend/
├── app/
│   ├── api/routes/      # Endpoints HTTP
│   ├── core/            # Lógica de negócio (RAG, LLM, Tools)
│   ├── services/        # Serviços externos
│   └── config.py        # Configurações
├── scripts/             # Scripts de teste
└── requirements.txt     # Dependências
```

### Frontend (Next.js 15)
```
treq/frontend/
├── app/
│   ├── (chat)/         # Rotas do chat
│   └── components/     # Componentes React
├── hooks/              # Custom hooks
└── lib/                # Utilitários
```

## 🔧 Setup

### Pré-requisitos
- Python 3.10+
- Node.js 18+
- Conta Supabase
- API Keys: Groq, Google Gemini, Zhipu AI (opcional para GLM 4)

### Backend

```bash
cd treq/backend

# Ambiente virtual
python3 -m venv treq-venv
source treq-venv/bin/activate

# Instalar dependências
pip install -r requirements.txt

# Configurar .env (copiar de .env.example)
# Preencher: GROQ_API_KEY, GEMINI_API_KEY, SUPABASE_URL, etc.

# Rodar servidor (Porta 8002 recomendada para Vision)
uvicorn app.main:app --reload --host 0.0.0.0 --port 8002
```

### Frontend

```bash
cd treq/frontend

# Instalar dependências
npm install

# Configurar .env.local (GPS de conexão)
NEXT_PUBLIC_API_URL=http://localhost:8002

# Rodar servidor
npm run dev
```

Acesse: http://localhost:3000

## 📡 APIs Principais

### Chat
```bash
POST /chat/
{
  "message": "Qual o procedimento para contenção?",
  "user_id": "user-123",
  "stream": true  # Ativa streaming SSE
}
```

### Upload de Documento
```bash
POST /documents/upload
Form Data:
  - file: [arquivo PDF/Excel]
  - document_type: "manual" (opcional)
```

### Transcrição de Áudio
```bash
POST /audio/transcribe?user_id=user-123&language=pt
Form Data:
  - audio_file: [arquivo de áudio]
```

## 🧪 Testes

### Executar Testes com Pytest

```bash
cd treq/backend

# Ativar ambiente virtual
source ../venv/bin/activate  # ou treq-venv/bin/activate

# Executar todos os testes
pytest

# Executar com cobertura
pytest --cov=app --cov-report=html

# Executar teste específico
pytest tests/test_fase1_correcoes.py -v

# Executar apenas testes unitários
pytest -m unit

# Executar apenas testes de integração
pytest -m integration
```

### Testes Disponíveis

| Arquivo | Descrição |
|---------|-----------|
| `test_fase1_correcoes.py` | Correções Fase 1 (JSON parsing, auth, retry) |
| `test_new_logic.py` | Lógica de classificação de queries |
| `test_query_classifier_status.py` | Classificador de status |
| `test_technical_terms_filter.py` | Filtro de termos técnicos |

### Scripts de Teste Manual

```bash
# Teste de streaming
python scripts/test_streaming.py

# Teste de parser CoT
python scripts/test_cot_parser.py

# Teste completo de documentos
python scripts/test_marker.py
```

## 📊 Roteamento LLM em 3 Níveis

### Nível 1: Llama 8B (Groq)
- **Uso:** Queries simples, respostas rápidas
- **Latência:** ~300ms
- **Custo:** Baixo

### Nível 2: Llama 70B (Groq)
- **Uso:** Queries complexas padrão (detalhamento, procedimentos, causas)
- **Latência:** ~500ms
- **Custo:** Médio

### Nível 3: GLM 4.7 (Zhipu AI)
- **Uso:** Tarefas pesadas (análises multi-dimensionais, cálculos complexos, sínteses executivas)
- **Latência:** ~2s
- **Custo:** Alto (mas bônus de 20M tokens disponível)

**Seleção automática** baseada em análise da query e tipo classificado.

## 🔄 Chain of Thought (CoT)

O assistente usa Chain of Thought para respostas transparentes:

```
<pensamento>
[Análise do contexto, raciocínio passo a passo]
</pensamento>

<resposta>
[Resposta formatada para o usuário]
</resposta>
```

**Frontend:** Renderiza pensamento em seção colapsável, resposta formatada normalmente.

## 📄 Processamento de Documentos

### Formatos Suportados (MVP)
- ✅ **PDF** (nativo) - PyPDF2/pdfplumber
- ✅ **Excel** (.xlsx, .xls) - pandas/openpyxl
- ❌ **DOCX/PPTX** - Não suportado no MVP (futuro)
- ❌ **PDF escaneado** - Não suportado no MVP (OCR futuro)

### Pipeline
1. Upload → Conversão para Markdown
2. Chunking semântico (preservando hierarquia)
3. Geração de embeddings
4. Indexação no Supabase (pgvector)

## 📊 Observabilidade e Monitoramento (LangSmith)

O Treq integra **LangSmith** para observabilidade total:
- **Tracing Completo:** Acompanhe o ciclo de vida de cada query (Retrieval → Reasoning → Generation → Validation).
- **Métricas de Token/Custo:** Monitoramento em tempo real do consumo de APIs.
- **Debugging de Alucinações:** Visualize o comportamento do *Grounding Validator* para cada resposta.
- **Feedback Loop:** Coleta de 👍/👎 dos usuários integrada ao dashboard para melhoria do RAG.
## 🎤 Áudio

### Speech-to-Text (STT)
- **Provider:** Groq Whisper
- **Endpoint:** `POST /audio/transcribe`
- **Idioma:** Português (pt)

### Text-to-Speech (TTS)
- **Provider:** Google Gemini 2.5 Flash TTS
- **Endpoint:** `POST /audio/synthesize`
- **Cache:** Cache de áudio para evitar regeneração
- **Formatos:** WAV, MP3

## 📚 Documentação Adicional

- [Backend README](backend/README.md) - Detalhes do backend
- [Frontend README](frontend/README.md) - Detalhes do frontend
- [Processamento de Documentos MVP](Docs/mvp-100-free-document-processing.md)
- [Roteamento GLM 4](Docs/GLM%204-2.md)

## 🛠️ Stack Tecnológica

### Backend
- FastAPI
- Python 3.10+
- Supabase (PostgreSQL + pgvector)
- Groq API (Llama models + Whisper)
- Google Gemini API (TTS)
- Zhipu AI (GLM 4)

### Frontend
- Next.js 15 (App Router)
- TypeScript (Strict)
- Tailwind CSS
- Shadcn/ui
- React Markdown

## 📝 Licença

Proprietário - Sotreq

---

**Última atualização:** Dezembro 2025  
**Versão:** 1.0.0 (MVP)

