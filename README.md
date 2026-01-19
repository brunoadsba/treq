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

## 🏗️ Arquitetura Consolidada (Padrão 5S)

O projeto segue a metodologia **5S (Sort, Set in Order, Shine, Standardize, Sustain)**, organizando o código em features verticais:

### Backend (`/backend/app/`)
- `core/`: Governança, Configurações (`config.py`), Segurança.
- `features/`: Lógica de negócio isolada (Agent, Connectors, Vision, Security).
- `services/`: Motores compartilhados (LLM, RAG, Audio).
- `utils/`: Utilitários globais e sanitizadores.

### Frontend (`/frontend/src/`)
- `app/`: Roteamento Next.js (minimalista).
- `features/`: Componentes, hooks e tipos específicos por domínio (Chat, Auth, Vision).
- `components/ui/`: Primitivos de UI reutilizáveis.
- `hooks/`: Hooks globais utilitários.
- `context/`: Estados globais compartilhados.

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

---

## Desenvolvimento Frontend (Hot-reload)

Para trabalhar na interface com recarregamento instantâneo:

```bash
docker compose up -d frontend
```
*O container usará o target `development` do Dockerfile, mapeando os volumes do host.*

## 🔒 Segurança & Hardening (Sprint 1 Elite)
- **Prompt Guard (Layer 7):** Defesa contra Injeção de Prompt e Jailbreak com detecção heurística e segregação XML Instruction-Data.
- **Whitelisting Agressivo:** Validação rigorosa de inputs com Pydantic e sanitização especializada em todos os endpoints críticos.
- **Secrets Protection:** Auditoria automática via `gitleaks` integrada aos git hooks para prevenir vazamento de credenciais.
- **Auth:** OAuth2 + JWT (Gerido em `backend/app/core/security.py`).
- **SSOT:** Configurações centralizadas em `backend/app/config.py`.
- **Isolamento:** Native RLS aplicado em todas as camadas (DB + Agente).
- **Audit:** Tracing automático via LangSmith e logs de auditoria LGPD.

---

**Versão:** 2.0.0-enterprise
**Última Atualização:** Janeiro 2026

