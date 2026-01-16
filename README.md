# Treq Enterprise - Assistente Operacional Inteligente

Plataforma de inteligência artificial para operações Sotreq, evoluída para uma arquitetura agêntica baseada em grafos.

## 🚀 Novidades na Versão 2.0 (Enterprise)

- **Agentes Autônomos (LangGraph):** Arquitetura baseada em grafos para raciocínio complexo (Planning -> Retrieval -> Execution).
- **Conectores de Dados:** Integração nativa com Confluence, Slack e Jira (em breve).
- **Governança:** Tracing completo via LangSmith, Rate Limiting por usuário e RLS (Row Level Security).
- **Segurança:** Filtragem de conteúdo sensível no nível do banco de dados (Supabase RLS).

---

## 📋 Funcionalidades

| Módulo | Status | Descrição |
|--------|--------|-----------|
| **Agent Core** | ✅ Completo | Orquestração via LangGraph, memória persistente |
| **Connectors** | ✅ Completo (Mock) | Confluence (Páginas/Espaços), Slack (Mensagens/Canais) |
| **RAG Legacy** | ✅ Completo | Busca vetorial clássica (mantida para compatibilidade) |
| **LLM Hub** | ✅ Completo | Roteamento dinâmico (Llama 3 70B, GLM-4, Gemini) |
| **Audio** | ✅ Completo | STT (Whisper) e TTS (Gemini) |
| **Vision** | ✅ Completo | Análise de imagens operacionais |

## 🏗️ Nova Arquitetura de Backend

A versão Enterprise adota uma estrutura baseada em `features` verticais para melhor escalabilidade:

```
backend/app/
├── core/               # Governança, Config, Security
├── features/
│   ├── agent/          # Lógica do Agente (LangGraph)
│   ├── connectors/     # Integrações (Slack, Confluence)
│   └── chat/           # (Futuro) Chat v2
├── services/           # Serviços compartilhados (LLM, RAG)
└── api/                # Rotas legado (v1)
```

## 📡 Novos Endpoints (v2)

### Agent
- `POST /agent/chat`: Chat inteligente com capacidade de uso de ferramentas.

### Connectors
- `GET /connectors/status`: Status das integrações.
- `POST /connectors/slack/send`: Envio de mensagens (via Agente).
- `POST /connectors/confluence/sync`: Sincronização de conhecimento.

## 🛠️ Setup Atualizado

1. **Instalar Dependências:**
```bash
pip install -r backend/requirements.txt
```
*Nota: Requer `langgraph`, `langchain-groq`, `langsmith`.*

2. **Configurar Governança (.env):**
```bash
LANGCHAIN_TRACING_V2=true
LANGCHAIN_PROJECT=treq-enterprise
```

3. **Executar Backend:**
```bash
uvicorn app.main:app --host 0.0.0.0 --port 8002 --reload
```

---

**Versão:** 2.0.0-enterprise
**Última Atualização:** Janeiro 2026

