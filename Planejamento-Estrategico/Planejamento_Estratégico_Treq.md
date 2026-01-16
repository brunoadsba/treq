# Planejamento Estratégico: Treq - Custom Enterprise AI Agent

Este planejamento detalha a estratégia de evolução do Treq, utilizando a base existente (FastAPI, Next.js, Roteamento de LLM) para alcançar o nível de um Agente de IA Enterprise de alto valor.

## 1. Visão Estratégica (Onde queremos chegar)

| Aspecto | Treq Atual (MVP) | Treq Enterprise (Meta $50k+) |
| :--- | :--- | :--- |
| **Função Principal** | Chat com documentos (RAG Monolítico). | Agente de Automação e Conhecimento (RAG + Tools). |
| **Escopo de Dados** | Documentos carregados manualmente (PDF, Excel). | Ecossistema de Conhecimento (Confluence, Jira, Slack, Google Drive). |
| **Segurança** | Autenticação básica (não implementada). | **Permission-Aware RAG** (RLS) e OAuth2. |
| **Arquitetura** | Roteamento de LLM (3 níveis). | **Orquestração de Agentes** (LangGraph). |
| **Valor de Mercado** | Portfólio de entrada. | Solução de nicho para problemas corporativos. |

## 2. Planejamento de Execução (Fases e Marcos)

O planejamento é dividido em 4 Sprints principais, cada uma focada em um pilar do valor Enterprise.

### Sprint 1: Fundação de Agentes e RLS (4 Semanas)

**Objetivo:** Transição arquitetural para LangGraph e implementação da segurança básica de dados.

| Marco | Tarefas Chave | Habilidades Focadas |
| :--- | :--- | :--- |
| **1.1. LangGraph Core** | Migrar a lógica de `chat` para o `StateGraph`. Implementar os nós `planner_node` e `retriever_node`. | LangGraph, Tool Calling, Prompt Engineering. |
| **1.2. RLS no Supabase** | Modificar o schema do Supabase para incluir metadados de permissão (`allowed_users`). Implementar a função `query_rls` no serviço Supabase. | PostgreSQL RLS, Busca Vetorial com Filtro. |
| **1.3. Primeira Ferramenta** | Criar a ferramenta simulada `jira_create_ticket` e integrá-la ao `executor_node`. | Python Tooling, FastAPI Integration. |

### Sprint 2: Conectores e Sincronização (6 Semanas)

**Objetivo:** Conectar o Treq ao ecossistema corporativo e manter os dados atualizados.

| Marco | Tarefas Chave | Habilidades Focadas |
| :--- | :--- | :--- |
| **2.1. Conector Confluence** | Implementar a autenticação OAuth2 para a API da Atlassian. Criar um script de sincronização (cron job) para buscar páginas e indexá-las no Supabase (com metadados RLS). | OAuth2, API REST, Sincronização Assíncrona. |
| **2.2. Conector Slack** | Criar um Slack Bot que escuta eventos (`message.channels`) e indexa as mensagens. | Slack API, Webhooks, Indexação de Conversas. |
| **2.3. Ferramentas de Ação** | Criar as ferramentas reais `slack_post_message` e `confluence_search` para o Agente Executor. | Tool Use Avançado, Tratamento de Erros de API. |

### Sprint 3: Governança e Polimento (4 Semanas)

**Objetivo:** Adicionar a camada de auditoria, controle de custos e refinar a experiência do usuário.

| Marco | Tarefas Chave | Habilidades Focadas |
| :--- | :--- | :--- |
| **3.1. Auditoria LangSmith** | Garantir que o *trace* do LangSmith capture o fluxo completo do LangGraph (Planner → Retriever/Executor). | LangSmith Tracing, Debugging de Agentes. |
| **3.2. Controle de Custos** | Implementar *token counting* e *rate limiting* por usuário/cliente no backend. Refinar o roteamento de LLM para otimizar o uso do GLM 4.7. | Otimização de Custos de LLM, Middleware FastAPI. |
| **3.3. UX de Agente** | No Frontend (Next.js), criar uma interface para visualizar o *Chain of Thought* do Planner e o resultado das ações (ex: "Ticket JIRA-123 criado"). | Next.js UX, Visualização de Dados. |

### Sprint 4: Venda e Portfólio (2 Semanas)

**Objetivo:** Transformar o projeto técnico em um ativo de vendas.

| Marco | Tarefas Chave | Habilidades Focadas |
| :--- | :--- | :--- |
| **4.1. Documentação** | Gerar a documentação da API (Swagger/Redoc) e criar um `README.md` de nível Enterprise. | Technical Writing, Documentação de API. |
| **4.2. Case Study** | Escrever um *Case Study* focado em "Como o Treq resolve o problema de fragmentação de conhecimento e segurança de dados em empresas". | Storytelling, Marketing de Soluções. |
| **4.3. Lançamento** | Publicar o projeto no GitHub e no Vercel/Render, e começar a usá-lo como prova social em propostas do Upwork. | Branding Pessoal, Estratégia de Freelancing. |
