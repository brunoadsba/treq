# Consulta Humana - Context Engineering

## Visão Geral

Este documento orienta desenvolvedores humanos sobre como e quando consultar a documentação dos Master Harnesses do repositório **Context-Engineering** quando a resposta de LLM (Large Language Model) for insuficiente, incorreta ou necessitar de especialização humana.

---

## Quando Consultar Humano

### ❓ Critérios para Consulta

Consulte um especialista humano quando:

1. **A Resposta da LLM É Insuficiente**
   - LLM fornece resposta genérica ou vaga sem contexto específico
   - LLM ignora requisitos ou constraints documentados
   - LLM fornece resposta contraditória com Master Harnesses

2. **A Resposta da LLM É Incorreta**
   - LLM fornece informação técnica errada ou desatualizada
   - LLM sugere bibliotecas ou padrões obsoletos
   - LLM não segue padrões definidos no projeto

3. **A Resposta da LLM Não Responde à Pergunta**
   - LLM interpreta mal a pergunta ou responde algo diferente
   - LLM não fornece o que foi solicitado (off-topic)
   - LLM pula etapas críticas sem explicação

4. **Complexidade Alta Não Justificada**
   - LLM gera resposta complexa sem motivo claro
   - LLM usa abstrações desnecessárias para tarefas simples
   - LLM segue caminhos não otimizados ou ineficientes

5. **Contexto Perdido ou Inconsistente**
   - LLM não tem acesso a contexto recente (commits, ADRs, issues)
   - LLM usa contexto desatualizado ou conflitante
   - LLM não referencia versões corretas de dependências

6. **Necessita de Especialização Humana**
   - Problema técnico específico que LLM não consegue resolver (ex: bug obscuru, infraestrutura complexa)
   - Decisão arquitetural não coberta por Master Harnesses
   - Regulamento ou compliance não documentado

7. **Segurança ou Compliance**
   - LLM sugere algo que viola OWASP Top 10
   - LLM expõe dados sensíveis inadvertidamente
   - LLM não segue padrões de segurança da empresa

8. **Performance ou Escalabilidade**
   - LLM não escala conforme esperado em produção
   - LLM causa timeouts ou latência excessiva
   - LLM não segue melhores práticas de performance

---

## Fluxo de Consulta Humana

### Passo 1: Verificar Capacidade da LLM

Antes de consultar um humano, verifique:

1. **Revisar a Resposta da LLM**
   - A resposta está completa e coerente?
   - Há gaps óbvios de informação?

2. **Consultar Master Harnesses Relevantes**
   - Revise os Master Harnesses específicos ao problema
   - Busque keywords que possam resolver a questão
   - Considere o contexto do Treq (RAG multi-nível, backend instável)

3. **Refinar a Pergunta**
   - Se a resposta da LLM for insuficiente, reformule a pergunta com mais contexto
   - Adicione detalhes específicos do projeto Treq
   - Seja mais específico sobre qual Master Harness usar

### Passo 2: Documentar a Consulta

Se decidir consultar um humano, documente:

1. **Motivo da Consulta**
   - Por que a resposta da LLM não foi suficiente?
   - Qual Master Harness ou conceito não foi coberto adequadamente?

2. **Contexto Adicional**
   - Cite trechos relevantes dos Master Harnesses
   - Explique o que você tentou antes de consultar
   - Inclua logs ou mensagens de erro específicas

3. **Formato da Consulta**
   - Use o seguinte template no issue tracker (GitHub Issues, GitLab, etc.):
     ```markdown
     ## Consulta Humana
     
     **Contexto:** [Breve descrição do problema ou dúvida]
     
     **Master Harnesses Consultados:**
     - [x] PRD.md
     - [x] ADR.md
     - [x] Database Design.md
     
     **Pergunta ao LLM:**
     [Pergunta específica ou trecho]
     
     **Resposta do LLM:**
     - [Breve descrição ou trecho]
     - [Por que insuficiente?]
     
     **Esperado:**
     - [O que gostaria que o especialista faça?]
     - [Prioridade: Baixa, Média, Alta, Crítica]
     - [Canal preferido]: [Slack #treq-consultas, Email direto, GitHub Issues]
     
     **Tags:** #treq-consulta-humana, #llm-insuficiente, #necessita-especialista
     ```

4. **Categorizar a Consulta**
   - Classifique como funcionalidade, performance, segurança, arquitetura, etc.
   - Isso ajuda a direcionar para a pessoa certa

### Passo 3: Definir Prioridade

Ao categorizar a consulta, defina a prioridade:

- **Crítica:** Bloqueia funcionalidade principal do sistema
- **Alta:** Degradação significativa de performance ou UX
- **Média:** Documentação incompleta ou confusa
- **Baixa:** Otimização ou melhoria desejada mas não urgente

### Passo 4: Escolher Canal

Defina o canal preferido para comunicação:

- **Slack #treq-consultas-geral**: Para consultas gerais
- **Slack #treq-arquitetura**: Para decisões arquiteturais
- **Slack #treq-segurança**: Para problemas de segurança
- **Slack #treq-performance**: Para problemas de performance
- **Slack #treq-developers**: Para desenvolvimento
- **Email direto**: Para casos urgentes (SLA violação, downtime)

### Passo 5: Acompanhar Resposta

Após o especialista humano responder:

1. **Verificar se a Resposta Foi Suficiente**
   - O especialista consegui resolver o problema?
   - A solução está documentada?

2. **Documentar a Solução**
   - Se a solução envolveu mudança em código ou arquitetura
   - Atualize o Master Harness correspondente (PRD, ADR, etc.)
   - Crie um novo ADR se necessário

3. **Atualizar o Contexto Evolutivo**
   - Garanta que o LLM terá acesso a essa solução em consultas futuras
   - Adicione ao ACE se estiver usando o sistema

---

## Integração com Master Harnesses

### Como Consultar Especialista em Diferentes Contextos

**1. Consultar Product Owner (PRD.md)**
- Motivo: Requisitos ambíguos
- Ação: Use `/prd-refine` para clarificar escopo

**2. Consultar Architect (ADR.md)**
- Motivo: Decisão arquitetural não documentada
- Ação: Use `/adr-create` para documentar a decisão

**3. Consultar Database Designer (DatabaseDesign.md)**
- Motivo: Schema de banco de dados inadequado
- Ação: Use `/db-design` para revisar e otimizar

**4. Consultar Performance Engineer (PerformanceReview.md)**
- Motivo: Problemas de latência ou throughput
- Ação: Use `/perf-analyze` para investigar gargalos

**5. Consultar Security Engineer (SecurityReview.md)**
- Motivo: Vulnerabilidade de segurança
- Ação: Use `/sec-owasp`, `/sec-threat-model`, `/sec-scan`

---

## Melhores Práticas

### Para Especialistas

Ao responder a consulta humana:

1. **Seja Conciso e Direto**
   - Explique o problema claramente em 1-2 parágrafos
   - Forneça uma recomendação específica e acionável

2. **Use Evidências**
   - Cite logs, mensagens de erro ou trechos de código
   - Referencie Master Harnesses específicos

3. **Seja Humilde e Construtivo**
   - Reconheça limitações da IA atual
   - Sugira caminhos de melhoria em vez de apenas críticar

4. **Priorize Impacto**
   - Foque em soluções que resolvem problemas críticos primeiro
   - Considere custo/benefício antes de complexidade

5. **Documente para Futuro**
   - Registe a solução no ADR correspondente
   - Adicione ao contexto evolutivo (ACE) se estiver usando
   - Crie histórico para evitar os mesmos problemas futuramente

---

## Padrões de Comunicação

### Canais Disponíveis para Consulta Treq

| Canal | Descrição | Uso |
|--------|-----------|-----|
| **Slack #treq-consultas-geral** | Consultas gerais, dúvidas sobre funcionamento | Diário |
| **Slack #treq-arquitetura** | Decisões de design de sistema, escolha de tecnologias | Prioritário |
| **Slack #treq-segurança** | Vulnerabilidades, incidentes de segurança, OWASP ASVS | Urgência |
| **Slack #treq-performance** | Latência, throughput, crashes, Web Vitals | Semanal |
| **Slack #treq-developers** | Desenvolvimento, code reviews, debugging | Diário |
| **Email direto** | Assuntos críticos, SLA violations | Ocasional |

---

## Protocolos de Escalation

### Nível 1: Auto-Escalonamento

Se o especialista não conseguir resolver ou estiver ocupado:

1. **Aumentar Prioridade da Consulta**
   - Tag com `#treq-consulta-humana` e `#prioridade-alta`
   - Solicite resposta dentro de 4 horas úteis (SLA)

2. **Consultar Segundo Especialista**
   - Se o primeiro não responder, escalar para backup

### Nível 2: Escalonamento Manual

Para casos de baixa prioridade ou horários fora do expediente:

1. **Usar Canal Assíncrono**
   - Envie email ou abra issue no GitHub
   - Aguarde resposta dentro de 24 horas

2. **Agendar Consulta Regular**
   - Defina horários de disponibilidade do especialista
   - Consulte durante o dia útil quando ambos disponíveis

---

## Exemplos de Consultas

### Exemplo 1: Consulta sobre RAG Multi-nível

**Pergunta do Desenvolvedor:**
> "O backend está crashando com SIGTERM 139 quando usa RAG. Como configuro o roteamento inteligente para escolher o LLM certo (8B, 70B ou GLM-4)?"

**Resposta do Especialista:**
> Conforme [`Database Design.md`](../DatabaseDesign/DatabaseDesign.md) (seção "RAG Multi-nível") e [`ADR.md`](../ADR/ADR.md) (decisão de orquestração de agentes):
> 
> 1. Implemente lógica de classificação de queries no endpoint `/chat`
> 2. Configure timeouts diferentes para cada nível de LLM
>    - 8B: 30s (consultas rápidas)
>    - 70B: 60s (tarefas moderadas)
>    - GLM-4: 120s (análises executivas)
> 3. Adicione fallback para caso de falha de um nível
> 
> **Canal:** Use Slack #treq-performance para discutir métricas

**Canal Preferido:** Slack #treq-performance

---

### Exemplo 2: Consulta sobre Segurança

**Pergunta do Desenvolvedor:**
> "Encontrei uma vulnerabilidade OWASP Top 10 no código. Como devo corrigir?"

**Resposta do Especialista:**
> Conforme [`Security Review.md`](../SecurityReview/SecurityReview.md) (seção "OWASP ASVS"):
> 
> 1. Valide se a vulnerabilidade está listada no OWASP ASVS Level 1
> 2. Crie um patch que mitiga o risco
> 3. Documente a correção em ADR
> 4. Implemente teste de regressão
> 
> **Canal:** Use Slack #treq-segurança para revisão antes do deploy

**Canal Preferido:** Slack #treq-segurança

---

### Exemplo 3: Consulta sobre Performance

**Pergunta do Desenvolvedor:**
> "A resposta do LLM está demorando 5+ segundos. Como otimizo?"

**Resposta do Especialista:**
> Conforme [`Performance Review.md`](../PerformanceReview/PerformanceReview.md) (seção "Web Vitals"):
> 
> 1. Use Lighthouse CI para identificar gargalos
> 2. Implemente lazy loading de imagens
> 3. Otimize o critical rendering path (CSS, fontes)
> 4. Configure cache edge (Vercel)
> 5. Use streaming para dados grandes
> 
> **Canal:** Use Slack #treq-performance para discutir métricas

**Canal Preferido:** Slack #treq-performance

---

## Checklist para Especialistas

Antes de responder uma consulta humana, verifique:

- [ ] Entendi o problema ou contexto completo?
- [ ] Li os Master Harnesses relevantes?
- [ ] Consultei o time técnico apropriado?
- [ ] Forneço recomendação específica e acionável?
- [ ] Defini prioridade corretamente?
- [ ] Documentei a solução de forma clara?

---

## Conclusão

A documentação dos Master Harnesses do Context-Engineering fornece um framework completo para consultas humanas, garantindo que:

1. **Problemas sejam tratados de forma profissional e priorizada**
2. **Canais de comunicação estejam claramente definidos**
3. **Protocolos de escalation estejam estabelecidos**
4. **Integração com o contexto evolutivo do Treq seja mantida**

---

**Última Atualização:** 15/01/2026
**Versão:** 1.0.0
**Status:** Sistema de Guia de Consulta Humana Criado
