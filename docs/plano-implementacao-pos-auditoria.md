# Plano de Implementação: Hardening Pós-Auditoria (Treq 2.0)

Este plano detalha como as vulnerabilidades e oportunidades identificadas no relatório `auditoria-claude-002` serão endereçadas.

## 🎯 Objetivo
Elevar a maturidade do projeto Treq Enterprise de 7.5 para 9.0+, focando em segurança defensiva, resiliência de infraestrutura e automação de testes.

---

## 🏗️ 1. Segurança Defensiva (P0)

### 1.1 Validação de Input & Sanitização
- **Ação**: Implementar schemas Pydantic rigorosos em todos os endpoints do FastAPI.
- **Diferencial**: Além de tipos simples, usar regex para UUIDs e `validator` para remover tags HTML/scripts suspeitos de mensagens de chat.
- **Localização**: `backend/app/core/validators.py`

### 1.2 Prompt Injection Guard (Layer 7 for AI)
- **Ação**: Criar um middleware/service que intercepta mensagens de usuários antes de chegarem ao LangGraph.
- **Filtros**: Detecção de termos como "ignore previous instructions", "forget rules" e tentativas de exfiltração de sistema.

### 1.3 Auditoria de Secrets
- **Ação**: Configurar `gitleaks` no pipeline de CI e adicionar pre-commit hooks para evitar commits de chaves Supabase/Groq reais.

---

## 🧪 2. Qualidade & Automação (P0)

### 2.1 Baseline de Testes
- **Backend**: Implementar `pytest` com fixtures para Supabase Mocked e Redis. Focar em testar o grafo do LangGraph (fluxos de decisão).
- **Frontend**: Expandir Playwright para cobrir caminhos de erro (401, 429, 500) além do "happy path".

---

## ⚡ 3. Resiliência & Performance (P1)

### 3.1 Caching Inteligente
- **Camada RAG**: Cachear resultados de embeddings para perguntas idênticas por 30min no Redis.
- **Camada LLM**: Cachear respostas de perguntas triviais/saudações.

### 3.2 Circuit Breaker & Retry
- **Conectores**: Slack/Jira/Confluence terão Circuit Breakers. Se uma API cair, o agente informa o usuário imediatamente sem "travar" o loop de raciocínio.

---

## 📊 4. Observabilidade (P1)

### 4.1 OpenTelemetry
- Integrar tracing distribuído para que possamos ver o tempo gasto em cada nó do LangGraph vs tempo gasto em chamadas de API externas.

---

## 📅 Cronograma Proposto

| Sprint | Foco | Complexidade |
| :--- | :--- | :--- |
| **S1** | Hardening de Segurança & CI | Alta |
| **S2** | Resiliência (Circuit Breaker/Cache) | Média |
| **S3** | Observabilidade & Métricas | Média |
| **S4** | Documentação & Webhooks | Baixa |

---
> [!IMPORTANT]
> A implementação começará em **19/01/2026**. Nenhuma alteração de código será feita hoje, apenas o planejamento e configuração de ambiente.
