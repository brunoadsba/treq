# Treq Enterprise - Assistente Operacional Inteligente

Plataforma de inteligência artificial para operações Treq, evoluída para uma arquitetura agêntica baseada em grafos.

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

## 🛠️ Setup Local (Docker)

A versão Enterprise é Docker-first. Certifique-se de configurar o arquivo `.env` na raiz do projeto com as credenciais do Supabase e APIs LLM.

1. **Subir Infraestrutura:**
```bash
docker compose up -d
```
*Isso iniciará o Backend (8002), Frontend (3000), Redis e Nginx (80).*

2. **Testes E2E (Opcional):**
```bash
cd frontend
npx playwright test
```

3. **Logs em Tempo Real:**
```bash
docker compose logs -f backend
```

---

## 🔒 Segurança & Hardening
- **Auth:** OAuth2 + JWT (Gerido em `backend/app/core/security.py`).
- **SSOT:** Configurações centralizadas em `backend/app/config.py`.
- **Isolamento:** Native RLS aplicado em todas as camadas (DB + Agente).
- **Audit:** Tracing automático via LangSmith.

---

**Versão:** 2.0.0-enterprise
**Última Atualização:** Janeiro 2026

