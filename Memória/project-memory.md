# Memória do Projeto: Treq Enterprise

**Última Atualização:** 2026-01-18T16:00

---

## Documentação de Referência
- **Master Technical Overview:** `Apoio/Manus/treq_enterprise_documentation/technical_overview_2026.md`
- **Guia de Estabilidade (WSL2):** `Apoio/Manus/solucao-definitiva-segmentation-fault.md`
- **Arquitetura Visual:** `Apoio/Manus/treq_enterprise_documentation/treq_visual_recommendations_2026.md`

---

## Status Atual

### Branch Ativa: `infra/docker-setup`
- Status: ✅ Estável & Auditado (Finalização Sprint 8)
- Saúde: 🟢 Saudável (Containers Backend, Frontend, Redis e Nginx operacionais)

### Progresso das Sprints

| Sprint | Marco | Status | Testes |
|--------|-------|--------|--------|
| ... | ... | ... | ... |
| 7.1 | RAG Refinement | ✅ Completo | E2E |
| 8.1 | Dockerização Total | ✅ Completo | Compose |
| 8.2 | Auth JWT + RLS | ✅ Completo | E2E Auth |
| 8.3 | Enterprise Infra | ✅ Completo | Health |
| 8.4 | LGPD & Audit | ✅ Completo | Log Audit |
| 8.5 | Branding & UX (Login) | ✅ Completo | Login UI |
| 8.7 | Global Chat Persistence | ✅ Completo | context-isolation |
| 9.1 | Cognitive Activation (L6+) | ✅ Completo | Brain Shift / ReAct |
| 9.2 | Docker-Centric Doctrine | ✅ Completo | Standardization |
| 9.3 | IPv4 Pooler Fallback | ✅ Completo | Supabase 6543 |

**Total de Testes:** 46 (Unidade + Integração) + Deep Healthcheck (Redis/Supabase)

### Testes E2E Atuais (SSOT)
- **Frontend (Interface/Playwright):** [agent.spec.ts](file:///home/brunoadsba/treq/frontend/e2e/agent.spec.ts) - Valida fluxo completo de login e chat.
- **Backend (API/Python):** [test_e2e_enterprise.py](file:///home/brunoadsba/treq/backend/scripts/test_e2e_enterprise.py) - Valida orquestração de agentes e ferramentas.
- **Nota técnica:** 5 arquivos de testes obsoletos (legados `/chat/`) removidos/movidos para `obsolete/tests/`.


## Endpoints Implementados (Destaques)

### Agent Enterprise (`/agent/`)
| Método | Endpoint | Descrição |
|--------|----------|-----------|
| GET | `/agent/health` | Status do agente LangGraph |
| POST | `/agent/chat` | Chat com orquestração de agentes (Suporta RAG Defensivo) |

### Connectors (`/connectors/`)
*Mantidos conforme histórico anterior (Confluence/Slack)*

---

## Estrutura de Features e Segurança

```
backend/app/features/
66: backend/app/features/
56: ├── agent/                    # Architecture (Robust & Secure)
57: │   ├── .context.md           # [DOC] Contexto da Feature
58: │   ├── graph.py              # StateGraph (Planner -> [Executor|Retriever|Responder])
59: │   ├── prompts.py            # [NEW] Defensive System Prompts + Date Injection
60: │   ├── nodes/
61: │   │   ├── planner.py        # [MOD] Greeting optimized routing
62: │   │   ├── responder.py      # [MOD] Post-Retrieval Filtering + Date Injection
63: │   │   └── ...
```

---

| **Brain Shift (L6+)** | ReAct Cognitive Graph | Transição de orquestração estática para raciocínio dinâmico (Planner -> Executor -> Responder). |
| **Branding Enforcer** | Post-LLM Regex Filter | Proteção de marca "Treq" e supressão de termos internos (Brain, Planner, IA) em todas as saídas. |
| **ResponseMode** | Conditional UI (text/tool/hybrid) | Desduplicação de mensagens: suprime texto automático quando cards visuais (Jira/Slack) são exibidos. |
| **IPv4 Pooler Fallback** | Supabase Pooler (6543) | Solução definitiva para erro de rede no WSL2/Docker redirecionando para poolers IPv4 regionais. |
| **Docker-Centric Doctrine** | Host-First Isolation | Estabelecido que o Docker é o único ambiente de execução suportado para evitar falhas de binários no WSL2. |
| **Postgres Checkpointer** | Persistent Saver w/ Fallback | Memória do agente persistida em DB com fallback instantâneo para MemorySaver em caso de indisponibilidade. |

---

## Próximos Passos (Roadmap Atualizado)

### Sprint 8 - Enterprise Hardening (Finalizada)
- [x] Dockerização e Multistage Builds (Standalone)
- [x] Autenticação JWT e Proteção de Rotas
- [x] Refinamento UI Login (Paleta Treq Yellow/Black)
- [x] Implementar Auditoria de Log LGPD (Fase 3)
- [x] Configurar Rate Limiting Estratégico no Nginx (Fase 4)
- [x] Implementar Healthchecks de Dependência (Redis/Supabase)
- [x] Implementar Saudação Dinâmica e Localizada (Chat UX)
- [x] Implementar Persistência de Conversa (Global Context + State Isolation)

### Pendências Técnicas (Backlog)
- [ ] Configurar CI no GitHub Actions com Docker imagens
- [ ] Integrar LangSmith com metadados de usuário (Observabilidade)
- [ ] Refinar formulários de ação nos cards do Jira/Slack (Modais reais)
- [ ] Iniciar Planejamento Sprint 9 - Billing (Stripe)

## Erros e Soluções Frequentes

| Erro | Causa | Solução Definitiva |
| :--- | :--- | :--- |
| `Segmentation fault` | Conflito de `uvloop` ou `loguru(enqueue=True)` no WSL2. | Usar Python 3.11 do `/venv`, desativar `uvloop` e usar `enqueue=False`. |
| `thread_id` missing | Checkpointer do LangGraph sem identificador de sessão. | Garantir que le o `trace_config` inclua `configurable: {"thread_id": "uuid"}`. |
| `Network unreachable` | Problemas de DNS/IPv6 no WSL2 ao conectar ao Supabase. | Redirecionar para Pooler IPv4 (`aws-0-us-east-1.pooler.supabase.com:6543`) via `database.py`. |

---

## Notas Críticas (Atualizadas)

1. **Segurança de Marca:** O regex de sanitização (`sanitize_response` em `responder.py`) é a última linha de defesa. Nunca o remova.
2. **Contexto Temporal:** O agente agora "sabe" que dia é hoje. Injetado dinamicamente no `responder_node`.
3. **Padrão de Qualidade:** Qualquer nova feature DEVE ter teste E2E correspondente no Playwright.
4. **Limitações de Ambiente (WSL2):** O projeto roda em WSL2 (Ubuntu), que possui limitações conhecidas. **Uso de Docker é OBRIGATÓRIO** para execução.
5. **Doutrina Docker:** "WSL2 é o motor, Docker é o host". Não rodar comandos `npm`/`pip` diretamente no shell WSL2 para execução de projeto.
5. **E2E Strategy:** Testes obsoletos foram movidos para `obsolete/tests/` para manter o diretório de scripts limpo e focado no pipeline Enterprise.
