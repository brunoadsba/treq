# Plano de Implementação Técnica: Treq Enterprise

**Projeto:** Evolução do Treq de MVP RAG → Agente de Automação Enterprise  
**Duração Total:** 16 semanas (4 Sprints)  
**Esforço Estimado:** ~320 horas

---

## Tabela de Implementação Detalhada

| Sprint | Marco | Tarefa Chave | Subtarefa Técnica | Esforço (h) | Dependências |
|:-------|:------|:-------------|:------------------|:-----------:|:-------------|
| **1** | **1.1** | **LangGraph Core** | 1.1.1. Instalar LangGraph e configurar ambiente de desenvolvimento | 4 | N/A |
| 1 | 1.1 | LangGraph Core | 1.1.2. Definir schema do `AgentState` (query, context, tools_output, messages) | 6 | 1.1.1 |
| 1 | 1.1 | LangGraph Core | 1.1.3. Implementar `planner_node` com prompt de decisão (RAG vs Tool) | 8 | 1.1.2 |
| 1 | 1.1 | LangGraph Core | 1.1.4. Implementar `retriever_node` usando `RAGService` existente | 6 | 1.1.3 |
| 1 | 1.1 | LangGraph Core | 1.1.5. Migrar endpoint `/chat/` para usar `StateGraph.compile()` | 8 | 1.1.4 |
| 1 | **1.2** | **RLS no Supabase** | 1.2.1. Adicionar campo `allowed_users` ao schema Supabase ✅ | - | Concluído |
| 1 | 1.2 | RLS no Supabase | 1.2.2. Criar função `query_rls` com filtro por user_id ✅ | - | Concluído |
| 1 | 1.2 | RLS no Supabase | 1.2.3. Implementar políticas RLS no PostgreSQL ✅ | - | Concluído |
| 1 | 1.2 | RLS no Supabase | 1.2.4. Criar testes de integração para validar permissões | 6 | 1.2.3 |
| 1 | 1.2 | RLS no Supabase | 1.2.5. Documentar fluxo de segurança em `.context.md` | 2 | 1.2.4 |
| 1 | **1.3** | **Primeira Ferramenta** | 1.3.1. Criar classe base `BaseTool` com interface padronizada | 4 | 1.1.5 |
| 1 | 1.3 | Primeira Ferramenta | 1.3.2. Implementar `JiraCreateTicketTool` (mock/simulado) | 6 | 1.3.1 |
| 1 | 1.3 | Primeira Ferramenta | 1.3.3. Criar `executor_node` que invoca tools e retorna resultados | 6 | 1.3.2 |
| 1 | 1.3 | Primeira Ferramenta | 1.3.4. Integrar executor ao grafo com edge condicional | 4 | 1.3.3 |
| 1 | 1.3 | Primeira Ferramenta | 1.3.5. Testar fluxo completo: query → planner → executor → response | 4 | 1.3.4 |
| **2** | **2.1** | **Conector Confluence** | 2.1.1. Registrar app OAuth2 na Atlassian Developer Console | 2 | N/A |
| 2 | 2.1 | Conector Confluence | 2.1.2. Implementar fluxo OAuth2 com token refresh automático | 8 | 2.1.1 |
| 2 | 2.1 | Conector Confluence | 2.1.3. Criar `ConfluenceConnector` para listar e buscar páginas | 8 | 2.1.2 |
| 2 | 2.1 | Conector Confluence | 2.1.4. Implementar extração de conteúdo HTML → Markdown | 6 | 2.1.3 |
| 2 | 2.1 | Conector Confluence | 2.1.5. Criar cron job de sincronização incremental (Celery/APScheduler) | 8 | 2.1.4 |
| 2 | **2.2** | **Conector Slack** | 2.2.1. Criar Slack App com Bot Token e Event Subscriptions | 4 | N/A |
| 2 | 2.2 | Conector Slack | 2.2.2. Implementar webhook handler para `message.channels` | 6 | 2.2.1 |
| 2 | 2.2 | Conector Slack | 2.2.3. Criar pipeline de indexação de mensagens com metadados | 6 | 2.2.2 |
| 2 | 2.2 | Conector Slack | 2.2.4. Implementar filtro de canais e threading | 4 | 2.2.3 |
| 2 | 2.2 | Conector Slack | 2.2.5. Adicionar RLS baseado em participantes do canal | 4 | 2.2.4, 1.2.3 |
| 2 | **2.3** | **Ferramentas de Ação** | 2.3.1. Implementar `SlackPostMessageTool` com API real | 6 | 2.2.1 |
| 2 | 2.3 | Ferramentas de Ação | 2.3.2. Implementar `ConfluenceSearchTool` | 6 | 2.1.3 |
| 2 | 2.3 | Ferramentas de Ação | 2.3.3. Criar `JiraCreateTicketTool` real (substituir mock) | 6 | 2.1.1 |
| 2 | 2.3 | Ferramentas de Ação | 2.3.4. Implementar tratamento de erros e retry para APIs externas | 4 | 2.3.1-3 |
| 2 | 2.3 | Ferramentas de Ação | 2.3.5. Criar testes E2E para cada ferramenta | 6 | 2.3.4 |
| **3** | **3.1** | **Auditoria LangSmith** | 3.1.1. Configurar tracing LangSmith para StateGraph | 4 | 1.1.5 |
| 3 | 3.1 | Auditoria LangSmith | 3.1.2. Adicionar spans customizados para cada node | 4 | 3.1.1 |
| 3 | 3.1 | Auditoria LangSmith | 3.1.3. Implementar logging de tool calls com input/output | 4 | 3.1.2 |
| 3 | 3.1 | Auditoria LangSmith | 3.1.4. Criar dashboard de métricas (latência, tokens, erros) | 6 | 3.1.3 |
| 3 | **3.2** | **Controle de Custos** | 3.2.1. Implementar token counting com tiktoken | 4 | N/A |
| 3 | 3.2 | Controle de Custos | 3.2.2. Criar middleware de rate limiting por usuário | 6 | 3.2.1 |
| 3 | 3.2 | Controle de Custos | 3.2.3. Adicionar budget por cliente no metadata Supabase | 4 | 3.2.2 |
| 3 | 3.2 | Controle de Custos | 3.2.4. Otimizar roteamento LLM (priorizar modelos baratos) | 6 | 3.2.3 |
| 3 | 3.2 | Controle de Custos | 3.2.5. Criar alertas de uso próximo ao limite | 4 | 3.2.4 |
| 3 | **3.3** | **UX de Agente** | 3.3.1. Criar componente `AgentThinking` para exibir CoT | 6 | N/A |
| 3 | 3.3 | UX de Agente | 3.3.2. Implementar visualização de tool execution (`ToolResult`) | 6 | 3.3.1 |
| 3 | 3.3 | UX de Agente | 3.3.3. Adicionar progress indicators para operações longas | 4 | 3.3.2 |
| 3 | 3.3 | UX de Agente | 3.3.4. Criar feedback visual para ações (ticket criado, msg enviada) | 4 | 3.3.3 |
| **4** | **4.1** | **Documentação** | 4.1.1. Gerar OpenAPI/Swagger atualizado | 4 | N/A |
| 4 | 4.1 | Documentação | 4.1.2. Criar README.md Enterprise com arquitetura e setup | 6 | 4.1.1 |
| 4 | 4.1 | Documentação | 4.1.3. Documentar fluxo de agentes com diagramas Mermaid | 4 | 4.1.2 |
| 4 | 4.1 | Documentação | 4.1.4. Escrever guia de configuração de conectores | 4 | 4.1.3 |
| 4 | **4.2** | **Case Study** | 4.2.1. Definir narrativa do problema (fragmentação de conhecimento) | 4 | N/A |
| 4 | 4.2 | Case Study | 4.2.2. Documentar métricas de impacto (tempo economizado, etc) | 4 | 4.2.1 |
| 4 | 4.2 | Case Study | 4.2.3. Criar visual assets (screenshots, vídeos demo) | 6 | 4.2.2 |
| 4 | **4.3** | **Lançamento** | 4.3.1. Configurar deploy de produção (Render + Vercel) | 4 | N/A |
| 4 | 4.3 | Lançamento | 4.3.2. Configurar domínio customizado e SSL | 2 | 4.3.1 |
| 4 | 4.3 | Lançamento | 4.3.3. Publicar no GitHub com badges e CI/CD | 4 | 4.3.2 |
| 4 | 4.3 | Lançamento | 4.3.4. Criar proposta template para Upwork | 4 | 4.3.3 |

---

## Análise de Riscos por Sprint

### Sprint 1: Fundação de Agentes e RLS

- **Marco 1.1 (LangGraph Core):**
  - **Risco:** Curva de aprendizado do LangGraph pode atrasar a migração.
  - **Mitigação:** Implementar primeiro um grafo mínimo (2 nodes) antes de adicionar complexidade. Usar exemplos oficiais como referência.

- **Marco 1.2 (RLS no Supabase):** ✅ Mitigado
  - **Status:** Implementação básica concluída nesta sessão.
  - **Risco Residual:** Performance de queries com filtros JSONB.
  - **Mitigação:** Criar índice GIN em `metadata->'allowed_users'`.

- **Marco 1.3 (Primeira Ferramenta):**
  - **Risco:** Schema de tools incompatível com múltiplos LLMs (Groq vs GLM).
  - **Mitigação:** Usar formato OpenAI function calling como padrão, adaptar em adapters por provider.

---

### Sprint 2: Conectores e Sincronização

- **Marco 2.1 (Conector Confluence):**
  - **Risco:** Rate limiting da API Atlassian em sincronizações grandes.
  - **Mitigação:** Implementar backoff exponencial e sincronização incremental (delta sync).

- **Marco 2.2 (Conector Slack):**
  - **Risco:** Volume alto de mensagens pode sobrecarregar indexação.
  - **Mitigação:** Filtrar apenas canais relevantes e usar batch processing.

- **Marco 2.3 (Ferramentas de Ação):**
  - **Risco:** Erros de API externa (timeout, 500) podem quebrar o fluxo do agente.
  - **Mitigação:** Implementar circuit breaker e fallback graceful (informar erro ao usuário sem crash).

---

### Sprint 3: Governança e Polimento

- **Marco 3.1 (Auditoria LangSmith):**
  - **Risco:** Overhead de tracing impactar latência.
  - **Mitigação:** Usar sampling em produção (10% das requests) e tracing completo apenas em debug.

- **Marco 3.2 (Controle de Custos):**
  - **Risco:** Token counting incorreto levar a cobranças imprecisas.
  - **Mitigação:** Validar contagem com logs reais do provider (Groq, Zhipu).

- **Marco 3.3 (UX de Agente):**
  - **Risco:** Frontend não renderizar corretamente streaming de múltiplos nodes.
  - **Mitigação:** Implementar state machine no frontend para gerenciar transições.

---

### Sprint 4: Venda e Portfólio

- **Marco 4.1 (Documentação):**
  - **Risco:** Documentação desatualizada em relação ao código.
  - **Mitigação:** Gerar docs automaticamente a partir de docstrings (Sphinx/pydoc).

- **Marco 4.2 (Case Study):**
  - **Risco:** Métricas não serem confiáveis sem cliente real.
  - **Mitigação:** Usar métricas projetadas baseadas em benchmarks do setor.

- **Marco 4.3 (Lançamento):**
  - **Risco:** Deploy de produção expor vulnerabilidades de segurança.
  - **Mitigação:** Executar security scan (Snyk, Dependabot) antes do lançamento.

---

## Resumo de Esforço por Sprint

| Sprint | Foco | Esforço Total |
|--------|------|---------------|
| Sprint 1 | Fundação LangGraph + RLS | ~64h |
| Sprint 2 | Conectores + Sincronização | ~84h |
| Sprint 3 | Governança + UX | ~68h |
| Sprint 4 | Documentação + Lançamento | ~46h |
| **Total** | - | **~262h** |

> [!NOTE]
> Sprint 1.2 (RLS) já está parcialmente concluído com as implementações realizadas nesta sessão.

---

## Recomendações da Análise Técnica

### Melhorias Incorporadas

| Recomendação | Ação | Subtarefa Impactada |
|--------------|------|---------------------|
| Incluir `user_id` no `AgentState` | Garantir propagação de RLS em todos os nodes | 1.1.2 |
| Usar biblioteca `unstructured` para HTML→Markdown | Melhorar qualidade de extração do Confluence | 2.1.4 |
| Considerar Redis para rate limiting | Evitar inconsistência em múltiplos containers | 3.2.2 |
| Suportar `allowed_groups` além de `allowed_users` | Expandir RLS para ambientes enterprise | Backlog |

### Riscos Adicionais Identificados

1. **Latência de Agente** → Implementar streaming desde o primeiro node
2. **Consistência de Embeddings** → Versionar modelo de embedding nos metadados
3. **RLS por Grupos/Roles** → Adicionar ao backlog para expansão futura

### Métricas para Case Study (Sprint 4.2)

- Redução de alucinação via RAG contextualizado
- Segurança de dados (resultados dos testes E2E de hoje)
- Tempo de resposta com LangGraph vs monolítico
