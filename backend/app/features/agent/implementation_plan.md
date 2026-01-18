# MASTER PLAN: Ativação Cognitiva do Agente Treq (L6+)Você quer que eu liste o código-fonte da tela de login (que estaria no projeto Treq)?

Este documento consolida a estratégia técnica, arquitetura e plano de execução para transformar o Agente Treq em um orquestrador operacional ativo.

---

## 1. Visão Geral e Justificativa
O Agente atual opera em modo passivo/heurístico, limitado a buscar documentos (RAG) ou disparar ferramentas via palavras-chave rígidas. O objetivo deste plano é implementar o **"Brain Shift"**: migrar a inteligência de decisão para uma camada de raciocínio dinâmico via LLM, permitindo que o Agente planeje passos e extraia parâmetros contextuais para agir de forma autônoma e precisa.

---

## 2. Arquitetura Alvo (Cognitive Graph)

### Fluxo de Raciocínio (ReAct):
1. **Planner (LLM)**: Analisa a intenção e decide a `next_action` (Retriever, Executor ou Responder).
2. **Executor (Dynamic Extraction)**: Se a ação for ferramenta, o LLM extrai os argumentos reais da fala do usuário (Slot Filling).
3. **Retriever (RLS Protected)**: Busca na base de conhecimento com proteção de dados por usuário.
4. **Responder (Final Synthesis)**: Consolida pensamentos, buscas e resultados de ações em uma resposta humana.

---

## 3. Impacto e Artefatos Afetados

| Componente | Arquivo | Alteração Principal |
| :--- | :--- | :--- |
| **State** | `agent/state.py` | Adição de campos `thought` e `plan` para transparência. |
| **Inteligência** | `agent/nodes/planner.py` | Substituição de `if/else` por inferência estruturada via LLM. |
| **Ação** | `agent/nodes/executor.py` | Implementação de Extração Dinâmica de Parâmetros (Slot Filling). |
| **Contrato** | `agent/routes.py` | Atualização do Response Model para incluir o `thought`. |
| **Branding** | `agent/prompts.py` | Novo `PLANNER_SYSTEM_PROMPT` e diretrizes ReAct. |

---

## 4. Plano de Implementação Detalhado

### Fase 1: Fundação e Contratos
- Atualizar `AgentState` para suportar rastreabilidade de raciocínio.
- Criar schemas Pydantic para `PlannerDecision` e `ToolArguments`.

### Fase 2: Ativação do Planner (O Cérebro)
- Refatorar o node do Planner para realizar chamadas ao `LLMService`.
- Implementar lógica de auto-correção: se o RAG falhar repetidamente, o Planner deve forçar uma resposta final para evitar loops.

### Fase 3: Ativação do Executor (As Mãos)
- Implementar extração de argumentos no Executor. Ex: Transformar "abre um jira de erro na bomba 4" em `summary="Erro na Bomba 4"`.
- Validar chamadas de ferramentas reais com parâmetros dinâmicos.

### Fase 4: Personalidade Operacional (O Tom)
- Refinar o `AGENT_SYSTEM_PROMPT` para injetar consciência temporal (data/hora) e postura proativa.

---

## 5. Checklist de Verificação (Critérios de Aceite)

- [ ] **Roteamento Inteligente**: O Agente diferencia saudações de pedidos de ação sem keywords fixas.
- [ ] **Extração Precisa**: Parâmetros de ferramentas (Jira/Slack) são preenchidos corretamente via contexto.
- [ ] **Transparência**: O campo `thought` na resposta da API explica a decisão tomada.
- [ ] **Segurança**: O `user_id` continua sendo a chave de autoridade em todas as buscas (RLS).
- [ ] **Auditoria**: Logs de `log_mutation` agora gravam detalhes das ações dinâmicas.

---

## 6. Risks and Strategy
- **Latência**: O uso de LLM no Planner adiciona ~500ms. *Mitigação*: Usar modelos otimizados para decisões rápidas.
- **Alucinação**: Risco de inventar argumentos. *Mitigação*: Validar schemas JSON rigorosamente no backend.

---
**Grau de Confiança Técnica: 95%**
**Status: Aguardando Início de Execução (Branch feat/agent-cognitive-activation criada)**
