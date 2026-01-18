# Treq Enterprise - Assistente Operacional Inteligente

Plataforma de inteligência artificial para operações Treq, evoluída para uma arquitetura agêntica baseada em grafos.

## 🚀 Novidades na Versão 2.0 (Enterprise)

- **Agentes Autônomos (LangGraph):** Arquitetura baseada em grafos para raciocínio complexo (Planning -> Retrieval -> Execution).
- **Rastro Cognitivo (Modo Debug):** Visualização em tempo real do pensamento (`thought`) e timeline de execução (`trace`) do agente. Use `Ctrl+Shift+D`.
- **Ações Interativas (Human-in-the-Loop):** Revisão e edição de parâmetros de ferramentas (Jira/Slack) via modais antes da execução final.
- **Conectores de Dados:** Integração nativa com Confluence, Slack e Jira.
- **Governança:** Tracing completo via LangSmith, Rate Limiting por usuário e RLS (Row Level Security).

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

## 🐳 Doutrina Docker-Centric (Regra de Ouro)

Este projeto foi desenhado sob a premissa **Docker-First**. Para garantir a estabilidade (especialmente no ambiente WSL2) e evitar erros clássicos de rede ou bibliotecas nativas, o Docker é o único ambiente de execução e desenvolvimento suportado.

> [!IMPORTANT]
> **WSL2 é o motor, Docker é o host.** Nunca execute `npm install` ou `pip install` diretamente no shell do WSL2 para rodar o projeto. Use sempre os containers.

### Quick Start

1. **Clone e configure as envs**:
   ```bash
   git clone [url]
   cp .env.example .env # Preencha as chaves conforme necessário
   ```

2. **Suba o ambiente completo**:
   ```bash
   docker compose up -d --build
   ```

3. **Acesso**:
   - **Interface**: [http://localhost:3000](http://localhost:3000)
   - **Documentação API**: [http://localhost:8002/docs](http://localhost:8002/docs)
   - **Painel de Controle**: [http://localhost:8002/agent/health](http://localhost:8002/agent/health)

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

