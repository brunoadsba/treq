# 🧠 Consultoria Técnica: Desafios de Engenharia Treq 2.0

Este documento reúne perguntas fundamentais para serem direcionadas a especialistas durante a implementação do **Plano Elite (Maturidade 9.5/10)**. O objetivo é obter diretrizes para os desafios técnicos mais complexos de sistemas agênticos em produção.

---

## 🔐 1. Segurança Layer 7 & AI Safety
- **Defesa em Profundidade**: Como mitigar ataques de *indirect prompt injection* originados do corpus de RAG (dados externos) e não apenas do input direto do usuário?
- **Jailbreak Detection**: Quais padrões semânticos ou modelos leves (ex: DeBERTa) recomendam para detectar ataques como o "Grandma exploit" mantendo latência mínima?
- **Sanitização Contextual**: Como garantir que a sanitização de mensagens não remova referências legítimas necessárias para o contexto de negócio (ex: logs técnicos)?

---

## ⚡ 2. Resiliência & Continuidade (BCP)
- **Failover Lógico**: Como garantir a paridade de comportamento (System Prompts e Tool use) entre modelos de famílias diferentes (OpenAI vs Anthropic) durante um failover automático?
- **Circuit Breaker P99**: Qual o threshold ideal de latência para acionar o corte de serviço antes que o usuário perceba a degradação e o sistema gaste recursos em queries fadadas ao timeout?
- **Rate-Limit Intelligence**: Como implementar uma gestão dinâmica de fila baseada nos limites nominais de múltiplas APIs externas sem introduzir gargalos de processamento?

---

## 📊 3. MLOps & Avaliação de IA
- **LLM Evaluation (Ragas/TruLens)**: Qual estratégia de amostragem de dados de produção é mais segura para realizar avaliações de "Fidelidade" sem expor dados sensíveis (PII) ao modelo juiz?
- **Data Drift no RAG**: Como correlacionar métricas de derivação de dados no banco vetorial com a queda de acurácia do agente antes que o usuário reporte erros?
- **ROI Tracking**: Como estruturar o custo por interação para identificar automaticamente queries caras que não resultaram em resolução útil?

---

## 🧪 4. Qualidade & Performance de Pipeline
- **Mutatest Incremental**: Como configurar a execução de testes de mutação no GitHub Actions para rodar apenas nas linhas modificadas, mantendo o pipeline abaixo de 5 minutos?
- **Limites de Radon**: Para lógica agêntica (naturalmente complexa), qual o teto aceitável de Complexidade Ciclomática que equilibra funcionalidade e manutenibilidade?

---

## 📖 5. Governança & Cultura
- **Kill Switches**: Quais os protocolos recomendados para o acionamento de um *kill switch* de Feature Flag em produção por um engenheiro não-SRE?
- **Versionamento de Contratos**: Em APIs de streaming (SSE), quais as melhores práticas para depreciação de campos sem quebrar o consumo de clientes legados?

---
> [!TIP]
> Use estas perguntas como guia durante as sessões de refinamento técnico das Sprints 1 a 4.
