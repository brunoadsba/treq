# Memória do Projeto: Treq Enterprise

**Última Atualização:** 2026-01-16T18:19

---

## Status Atual

### Branch Ativa: `enterprise`
- Último commit: `bb908eb` - feat: integrate Agent tools with Connectors

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

**Total de Testes:** 36 passando

---

## Endpoints Implementados

### Agent Enterprise (`/agent/`)
| Método | Endpoint | Descrição |
|--------|----------|-----------|
| GET | `/agent/health` | Status do agente LangGraph |
| POST | `/agent/chat` | Chat com orquestração de agentes |

### Connectors (`/connectors/`)
| Método | Endpoint | Descrição |
|--------|----------|-----------|
| GET | `/connectors/status` | Status de todos os conectores |
| POST | `/connectors/confluence/connect` | Conectar ao Confluence |
| GET | `/connectors/confluence/spaces` | Listar espaços |
| GET | `/connectors/confluence/pages` | Listar páginas |
| POST | `/connectors/confluence/sync` | Sincronizar para RAG |
| POST | `/connectors/slack/connect` | Conectar ao Slack |
| GET | `/connectors/slack/channels` | Listar canais do Slack |
| GET | `/connectors/slack/messages` | Listar mensagens |
| POST | `/connectors/slack/send` | Enviar mensagem |
| POST | `/connectors/slack/sync` | Sincronizar Slack para RAG |

---

## Estrutura de Features

```
backend/app/features/
├── agent/                    # Sprint 1
│   ├── state.py
│   ├── graph.py
│   ├── routes.py
│   ├── nodes/
│   │   ├── planner.py
│   │   ├── retriever.py
│   │   ├── executor.py
│   │   └── responder.py
│   └── tools/
│       ├── base.py
│       └── mocks.py
└── connectors/               # Sprint 2
    ├── base.py
    ├── routes.py
    └── confluence/
        ├── client.py
        └── models.py
```

---

## Decisões Arquiteturais

| Decisão | Escolha | Motivo |
|---------|---------|--------|
| Rota paralela | `/agent/` separado de `/chat/` | Não quebra MVP |
| Providers LLM | Groq + Zhipu AI | Sem dependência OpenAI |
| Ferramentas | Mock primeiro | Independência de APIs externas |
| RLS | Aplicação + Supabase | Camada dupla de segurança |
| Conectores | Mock mode | Desenvolvimento sem credenciais |

---

## Próximos Passos

### Sprint 3 - Governança e Observabilidade
- [x] Configurar LangSmith tracing (Sprint 3.1)
- [x] Implementar Rate Limiting por usuário (Sprint 3.2)
- [ ] Implementar contagem de tokens (Next)

### Sprint 4 - Frontend Integration
- [ ] Criar UI de chat do Agente
- [ ] Renderizar tool outputs (cards para Jira/Slack)
- [ ] Sincronização de estado via streaming

### Pendências (Backlog)
- [ ] ConfluenceSearchTool (Sprint 2.3 remanescente)
- [ ] Webhook real do Slack (Sprint 2.2 remanescente)

---

## Configuração Necessária (Produção)

```bash
# Confluence (quando tiver credenciais)
CONFLUENCE_CLIENT_ID=xxx
CONFLUENCE_CLIENT_SECRET=xxx
CONFLUENCE_BASE_URL=https://seu-site.atlassian.net

# Slack (quando tiver credenciais)
SLACK_BOT_TOKEN=xoxb-xxx
SLACK_SIGNING_SECRET=xxx
```

---

## Notas Importantes

1. **Não fazer deploy sem autorização**
2. **Arquivos < 200 linhas**
3. **Padrão de features**: `backend/app/features/[nome]/`
4. **RLS obrigatório**: user_id propagado em todos os nodes
5. **Mock first**: Desenvolver com mocks, integrar APIs depois
