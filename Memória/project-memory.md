# Memória do Projeto: Treq Enterprise

**Última Atualização:** 2026-01-16T17:47

---

## Status Atual

### Branch Ativa: `enterprise`
- Commit anterior: `6d780c0` - feat: implement langgraph core
- Pendente: testes RLS e Agent

### Sprints Concluídas

#### Sprint 1.1 - LangGraph Core ✅
- [x] Instalar langgraph e configurar ambiente
- [x] Definir AgentState com user_id para RLS
- [x] Implementar planner_node (decisão RAG vs Tool)
- [x] Implementar retriever_node (integração com RAGService)
- [x] Implementar executor_node (ferramentas)
- [x] Implementar responder_node (resposta final)
- [x] Criar rota /agent/chat paralela ao /chat/
- [x] Testar fluxo RAG e Tool (Jira/Slack mocks)

#### Sprint 1.2 - RLS no Supabase ✅ (Parcial)
- [x] Campo `allowed_users` nos metadados
- [x] Filtro `_filter_by_rls()` no RAGService
- [x] Políticas RLS ativadas no Supabase
- [x] 272 chunks atualizados com metadados RLS

---

## Arquitetura Implementada

```
backend/app/features/agent/
├── state.py          # AgentState (TypedDict)
├── graph.py          # StateGraph com LangGraph
├── routes.py         # Endpoint /agent/chat
├── nodes/
│   ├── planner.py    # Decide RAG vs Tool
│   ├── retriever.py  # Integra com RAGService
│   ├── executor.py   # Executa ferramentas
│   └── responder.py  # Gera resposta final
└── tools/
    ├── base.py       # Interface BaseTool
    └── mocks.py      # Jira/Slack mock
```

---

## Decisões Arquiteturais

| Decisão | Escolha | Motivo |
|---------|---------|--------|
| Rota paralela | `/agent/chat` separado | Não quebra MVP |
| Providers LLM | Groq + Zhipu AI | Sem dependência OpenAI |
| Ferramentas Sprint 1 | Mock | Independência de APIs externas |
| RLS | Filtro na aplicação + Supabase | Camada dupla de segurança |

---

## Próximos Passos

### Sprint 1.3 - Primeira Ferramenta Real
- [ ] Implementar JiraCreateTicketTool real (API Atlassian)
- [ ] Testes E2E com criação de ticket real
- [ ] Documentar fluxo de autenticação OAuth2

### Sprint 2.1 - Conector Confluence
- [ ] Registrar app OAuth2 na Atlassian
- [ ] Implementar sincronização de páginas
- [ ] Indexar com metadados RLS

---

## Dependências Críticas

- `langgraph>=0.0.15` - Orquestração de agentes
- `langchain>=0.3.27` - Framework LLM
- `supabase==2.11.0` - Vector store + RLS

---

## Testes Validados

| Endpoint | Cenário | Resultado |
|----------|---------|-----------|
| `/agent/health` | Disponibilidade | ✅ `langgraph_available: true` |
| `/agent/chat` | Query RAG | ✅ 5 documentos recuperados |
| `/agent/chat` | Criar ticket Jira | ✅ `TREQ-123 criado` |
| `/agent/chat` | Notificar Slack | ✅ `Mensagem enviada` |
| `pytest` | 13 testes | ✅ 13 passed |

---

## Notas Importantes

1. **Não fazer deploy sem autorização** - Branch `enterprise` é para desenvolvimento
2. **Arquivos < 200 linhas** - Padrão do projeto
3. **Padrão de features** - `backend/app/features/[nome]/`
4. **RLS obrigatório** - user_id deve ser propagado em todos os nodes
