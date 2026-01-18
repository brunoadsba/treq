# Memória do Projeto: Treq Enterprise

**Última Atualização:** 2026-01-17T10:48

---

## Documentação de Referência
- **Master Technical Overview:** `Apoio/Manus/treq_enterprise_documentation/technical_overview_2026.md`
- **Guia de Estabilidade (WSL2):** `Apoio/Manus/solucao-definitiva-segmentation-fault.md`
- **Arquitetura Visual:** `Apoio/Manus/treq_enterprise_documentation/treq_visual_recommendations_2026.md`

---

## Status Atual

### Branch Ativa: `infra/docker-setup`
- Status: 🔵 Em Desenvolvimento (Enterprise Hardening & Dockerization)
- Saúde: 🟢 Saudável (Containers Backend, Frontend, Redis e Nginx operacionais)

### Progresso das Sprints

| Sprint | Marco | Status | Testes |
|--------|-------|--------|--------|
| ... | ... | ... | ... |
| 7.1 | RAG Refinement | ✅ Completo | E2E |
| 8.1 | Dockerização Total | ✅ Completo | Compose |
| 8.2 | Auth JWT + RLS | ✅ Completo | E2E Auth |
| 8.3 | Enterprise Infra | 🏗️ Em Progresso | Health |

**Total de Testes:** 42 (Unidade + Integração) + Suite E2E Playwright (Auth inclusive)

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

## Decisões Arquiteturais e de Segurança (Sprint 8)

| Decisão | Escolha | Motivo de Segurança/Qualidade |
|---------|---------|--------|
| **Next.js Standalone** | Docker Multistage | Reduz tamanho da imagem e resolve conflitos de arquivos ausentes (`required-server-files.json`) no runtime Docker. |
| **JWT Local Mock** | OAuth2 Bearer | Permite desenvolvimento offline sem depender de um provedor externo, injetando `user_id` nativo para RLS. |
| **Auth Guards** | React useEffect | Bloqueia acesso a rotas privadas antes de qualquer renderização de dados sensíveis. |
| **Resiliência 401** | Token Clearance | Garante que sessões expiradas não resultem em comportamentos indefinidos, forçando re-auth. |

---

## Próximos Passos (Roadmap Atualizado)

### Sprint 8 - Enterprise Hardening (Em Progresso)
- [x] Dockerização Completa (Compose Finalizado)
- [x] Autenticação JWT Roundtrip (Frontend <-> Backend)
- [x] Proteção de Rotas e Persistência de Sessão
- [ ] Configurar Rate Limiting no Nginx (Fase 4)
- [ ] Implementar Healthchecks (Fase 4)

### Pendências Técnicas (Backlog)
- [ ] Implementar Auditoria de Log LGPD (Fase 3)
- [ ] Configurar CI no GitHub Actions com Docker imagens
- [ ] Refinar UI da página de login (Paleta Treq Yellow/Black)

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
