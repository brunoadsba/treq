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

## Quick Start (Docker)

O Treq Enterprise opera 100% conteinerizado para garantir paridade entre desenvolvimento e produção.

1. **Clone e configure as envs**:
   ```bash
   git clone [url]
   cp .env.example .env # E preencha as chaves
   ```

2. **Suba o ambiente**:
   ```bash
   docker compose up -d --build
   ```

3. **Acesso**:
   - **Interface**: http://localhost:3000
   - **Documentação API**: http://localhost:8002/docs

4. **Autenticação (Desenvolvimento)**:
   - O sistema iniciará na tela de Login.
   - **Usuário**: `admin`
   - **Senha**: `admin123`

---

## Desenvolvimento Frontend (Hot-reload)

Para trabalhar na interface com recarregamento instantâneo:

```bash
docker compose up -d frontend
```
*O container usará o target `development` do Dockerfile, mapeando os volumes do host.*

## Segurança & Compliance
O sistema utiliza **JWT + RLS (Row Level Security)** nativo. Todas as requisições ao backend são filtradas pelo `user_id` extraído do token, garantindo isolamento total de dados entre diferentes usuários.

## 🔒 Segurança & Hardening
- **Auth:** OAuth2 + JWT (Gerido em `backend/app/core/security.py`).
- **SSOT:** Configurações centralizadas em `backend/app/config.py`.
- **Isolamento:** Native RLS aplicado em todas as camadas (DB + Agente).
- **Audit:** Tracing automático via LangSmith.

---

**Versão:** 2.0.0-enterprise
**Última Atualização:** Janeiro 2026

