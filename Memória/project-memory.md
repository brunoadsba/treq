# Memória do Projeto: Treq Enterprise

**Última Atualização:** 2026-01-17T10:48

---

## Documentação de Referência
- **Master Technical Overview:** `Apoio/Manus/treq_enterprise_documentation/technical_overview_2026.md`
- **Guia de Estabilidade (WSL2):** `Apoio/Manus/solucao-definitiva-segmentation-fault.md`
- **Arquitetura Visual:** `Apoio/Manus/treq_enterprise_documentation/treq_visual_recommendations_2026.md`

---

## Status Atual

### Branch Ativa: `enterprise`
- Status: 🟢 Estável / Testada (E2E Frontend + Backend Sanity)

### Progresso das Sprints

| Sprint | Marco | Status | Testes |
|--------|-------|--------|--------|
| 1.1 | LangGraph Core | ✅ Completo | 6 |
| 1.2 | RLS no Supabase | ✅ Completo | 6 |
| 1.3 | Primeira Ferramenta | ✅ Completo (mock) | - |
| 2.1 | Conector Confluence | ✅ Completo (mock) | 5 |
| 2.2 | Conector Slack | ✅ Completo (mock) | 6 |
| 2.3 | Ferramentas de Ação | ✅ Completo (integrado) | - |
| 3.1 | LangSmith Tracing | ✅ Completo | 2 |
| 3.2 | Rate Limiting | ✅ Completo | - |
| 3.3 | Refatoração SSOT | ✅ Completo | E2E |
| 4.0 | Segurança & Branding | ✅ Completo | E2E UI |
| 7.0 | Agentic RAG Base | ✅ Completo | E2E Frontend |
| 7.1 | RAG Refinement | ✅ Completo | E2E + Manual |

**Total de Testes:** 36 de unidade + Script Sanity (`backend/scripts/test_sanity.py`) + Suite Playwright (`frontend/e2e/agent.spec.ts`)

---

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
├── agent/                    # Architecture (Robust & Secure)
│   ├── .context.md           # [DOC] Contexto da Feature
│   ├── graph.py              # StateGraph (Planner -> [Executor|Retriever|Responder])
│   ├── prompts.py            # [NEW] Defensive System Prompts + Date Injection
│   ├── nodes/
│   │   ├── planner.py        # [MOD] Greeting optimized routing
│   │   ├── responder.py      # [MOD] Post-Retrieval Filtering + Date Injection
│   │   └── ...
```

---

## Decisões Arquiteturais e de Segurança (Sprint 4)

| Decisão | Escolha | Motivo de Segurança/Qualidade |
|---------|---------|--------|
| **Defensive RAG** | Regex Pós-LLM | O LLM pode falhar em instruções negativas no prompt. Regex garante que nomes de arquivos internos ('.xlsx') nunca vazem. |
| **Greeting Optimization** | Planner Intercept | Inputs como "oi" não devem acionar embeddings/LLM caro. Roteamento direto melhora latência e UX. |
| **Contexto Temporal** | Injeção no Prompt (`prompts.py`) | O LLM não sabe "que dia é hoje". Data/Hora injetada on-the-fly resolve alucinações. |
| **Testes E2E UI** | Playwright | Garantir que o branding "Treq" e a sanitização funcionem visualmente para o usuário final. |

---

## Próximos Passos (Roadmap Atualizado)

### Sprint 5 - Consolidação e UX
- [ ] Refinar UI do Chat (Scroll, Loading States visuais)
- [ ] Integrar página `/agent` ao menu principal (Sidebar/Header)
- [ ] Melhorar feedback visual de ferramentas (Cards interativos)

### Pendências Técnicas (Backlog)
- [ ] Migrar testes unitários antigos para arquitetura nova
- [ ] Implementar Docker para testes E2E em CI/CD

---

## Erros e Soluções Frequentes

| Erro | Causa | Solução Definitiva |
| :--- | :--- | :--- |
| `Segmentation fault` | Conflito de `uvloop` ou `loguru(enqueue=True)` no WSL2. | Usar Python 3.11 do `/venv`, desativar `uvloop` e usar `enqueue=False`. |
| `thread_id` missing | Checkpointer do LangGraph sem identificador de sessão. | Garantir que o `trace_config` inclua `configurable: {"thread_id": "uuid"}`. |
| `Network unreachable` | Problemas de DNS/IPv6 no WSL2 ao conectar ao Supabase. | Verificar se o host do DB está correto e usar conexões via IP se persistir. |

---

## Notas Críticas (Atualizadas)

1. **Segurança de Marca:** O regex de sanitização (`sanitize_response` em `responder.py`) é a última linha de defesa. Nunca o remova.
2. **Contexto Temporal:** O agente agora "sabe" que dia é hoje. Injetado dinamicamente no `responder_node`.
3. **Padrão de Qualidade:** Qualquer nova feature DEVE ter teste E2E correspondente no Playwright.
4. **Limitações de Ambiente (WSL2):** O projeto roda em WSL2 (Ubuntu), que possui limitações conhecidas com bindings C++ complexos (como `pydantic-core`, `psycopg3`, `numpy` + `opencv`).
   - **Sintoma:** `Segmentation fault (core dumped)` aleatório em testes ou imports.
   - **Solução:** Reverter para versões "binary" ou pure-python quando possível (ex: `psycopg2-binary` em vez de `psycopg[binary]`). Evitar `langchain-postgres` por enquanto, pois exige `psycopg` v3 que conflita com libs C no WSL em alguns cenários.
   - **Referência:** Problema comum com bibliotecas compiladas no WSL2. Se falhar, use mocks de infraestrutura ou rode testes em Docker/Linux nativo.
