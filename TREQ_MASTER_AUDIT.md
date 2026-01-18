# Treq Enterprise: Relatório Mestre de Auditoria (2026)

Este documento consolida todas as informações críticas de arquitetura, segurança e governança para facilitar o processo de auditoria técnica.

---

## 1. Visão Geral do Projeto
O **Treq Enterprise** é um assistente operacional agêntico baseado em grafos (**LangGraph**), projetado para escala corporativa com isolamento total de dados via **Row Level Security (RLS)** e autenticação **JWT**.

### 1.1 Stack Tecnológica
- **Linguagens**: Python 3.11 (Backend), TypeScript / Next.js 15 (Frontend).
- **Core**: FastAPI, LangChain, LangGraph.
- **Banco & Auth**: Supabase (PostgreSQL + pgvector).
- **Infraestrutura**: Docker (Multistage), Redis, Nginx (Hardening).

---

## 2. Governança e Metodologia 5S
O projeto aplica rigorosamente a metodologia 5S para manter a saúde do código:
1.  **Seiri (Sort)**: Eliminação de arquivos obsoletos (`render.yaml`, backups).
2.  **Seiton (Set in Order)**: Estrutura modular em `features/` (Regra #1).
3.  **Seiso (Shine)**: Refatoração de arquivos longos (Regra #5 - limite de 200 linhas).
4.  **Seiketsu (Standardize)**: Validação mandatória com **Zod** (Regra #11).
5.  **Shitsuke (Sustain)**: Checklist de PR em `CONTRIBUTING.md`.

---

## 3. Segurança e Conformidade (LGPD)
A segurança é tratada como prioridade no nível da arquitetura (**Security by Design**).

### 3.1 Isolamento de Dados
- **Mecanismo**: Filtro nativo por `user_id` em todas as queries SQL via RLS.
- **Identidade**: JWT extraído de tokens OAuth2 Bearer.

### 3.2 Proteção de IA
- **Sanitização**: Filtro de "metalanguage" e proteção de marca via `sanitizers.py`.
- **Tradução Técnica**: Normalização de termos (ex: Threshold -> Limite) para acessibilidade.

### 3.3 Auditoria (Audit Trail)
- Registro extensivo de mutações via `log_audit`, monitorando uploads e interações agênticas com carimbo de `user_id` e timestamp.

---

## 4. Arquitetura de Backend
O backend utiliza um fluxo de decisão em grafo:
- **Planner Node**: Classifica a intenção (Saudação, RAG, Tool, Vision).
- **Retriever Node**: Busca vetorial (RAG) com filtros de metadados.
- **Executor Node**: Acionamento de ferramentas (Slack, Jira, Confluence).
- **Responder Node**: Geração final com injeção de contexto temporal e sanitização.

---

## 5. Garantia de Qualidade (Testes)
- **E2E (Frontend)**: Testes de fluxo completo com Playwright (`frontend/e2e/`).
- **Scripts de Validação (Backend)**: Testes de healthcheck e integração agêntica (`backend/scripts/`).
- **Saúde**: Zero erros de linting e zero warnings críticos na branch `5S`.

---

## 6. Comandos Críticos de Administração
- **Subir Ambiente**: `docker compose up -d --build`
- **Executar Testes**: `pytest` (BE) / `npx playwright test` (FE)
- **Verificar Health**: `curl http://localhost:8002/health`

---
**Status**: Pronto para Auditoria.
**Última Revisão**: 18 de Janeiro de 2026.
**Responsável**: Antigravity AI.
