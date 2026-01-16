# Memória do Projeto: Treq Enterprise

**Última Atualização:** 2026-01-16T18:02

---

## Status Atual

### Branch Ativa: `enterprise`
- Último commit: `1b6a5f4` - feat: add Confluence connector

### Progresso das Sprints

| Sprint | Marco | Status | Testes |
|--------|-------|--------|--------|
| 1.1 | LangGraph Core | ✅ Completo | 6 |
| 1.2 | RLS no Supabase | ✅ Completo | 6 |
| 1.3 | Primeira Ferramenta | ✅ Completo (mock) | - |
| 2.1 | Conector Confluence | ✅ Completo (mock) | 5 |
| 2.2 | Conector Slack | ⏳ Pendente | - |
| 2.3 | Ferramentas de Ação | ⏳ Pendente | - |

**Total de Testes:** 30 passando

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

### Sprint 2.2 - Conector Slack
- [ ] Criar SlackClient com mock
- [ ] Modelo de mensagem
- [ ] Endpoint de webhook

### Sprint 2.3 - Ferramentas de Ação
- [ ] JiraCreateTicketTool real (API)
- [ ] SlackPostMessageTool real (API)
- [ ] ConfluenceSearchTool

### Sprint 3 - Governança
- [ ] LangSmith tracing
- [ ] Token counting
- [ ] Rate limiting por usuário

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
