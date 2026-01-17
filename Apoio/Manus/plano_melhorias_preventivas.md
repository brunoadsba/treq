# Plano de Melhorias Estruturais e Preventivas

Este documento consolida as propostas de melhoria baseadas na análise pós-Sprint 4, visando robustez, manutenibilidade e prevenção de regressões.

---

## 1. Persistência de Marca Antiga no RAG
**Objetivo:** Garantir integridade da base de conhecimento após refatorações.

### ✅ Ações Propostas
- [ ] **Pipeline de Sincronização:** Criar hook CI/CD que compara termos sensíveis entre código e KB.
- [ ] **Versionamento de KB:** Adicionar `kb_schema_version` nos metadados dos chunks.
- [ ] **Ingestão Defensiva:** Implementar pré-processador de normalização de termos na ingestão de documentos.

---

## 2. Vazamento de Estrutura Interna
**Objetivo:** Blindar a identidade do agente e evitar exposição técnica.

### ✅ Ações Propostas
- [x] **Classificação Pré-RAG:** Implementar classificador de intenção leve (Regex/Keyword) antes de invocar o RAG. *(Implementado no planner.py)*
- [x] **Prompt Engineering Defensivo:** Adicionar regras explícitas de não-divulgação de caminhos/arquivos no System Prompt. *(Implementado no prompts.py)*
- [x] **Filtro Pós-Recuperação:** Implementar *Post-Retrieval Filter* para remover chunks com padrões de sistema de arquivos. *(Implementado no responder.py)*

---

## 3. Contrato de API e Validação
**Objetivo:** Garantir estabilidade na comunicação Frontend-Backend.

### ✅ Ações Propostas
- [ ] **OpenAPI/Swagger:** Adotar geração automática de clientes via OpenAPI.
- [ ] **Testes de Contrato:** Criar testes que validam payloads contra schemas Pydantic reais.
- [ ] **Compatibilidade Retroativa:** Implementar wrapper no endpoint para aceitar formatos legados (`messages` vs `query`) com warning.

---

## 4. Infraestrutura de Testes (E2E)
**Objetivo:** Viabilizar testes end-to-end confiáveis em qualquer ambiente.

### ✅ Ações Propostas
- [ ] **Dockerização:** Empacotar testes Playwright em container Docker com dependências de OS.
- [x] **Pirâmide de Testes:** Separar testes de integração (Requests) de testes de interface (Playwright). *(Implementado básico com scripts e Playwright configurado)*
- [ ] **Detecção de Ambiente:** Script de teste deve pular etapas de UI se binários não estiverem presentes (Graceful Degradation).

---

## 5. Diretriz Transversal: Checklist de Refatoração
**Objetivo:** Padronizar grandes mudanças de domínio.

### ✅ Checklist Padrão
Toda mudança de domínio (ex: rebranding) deve incluir validação em:
1.  [ ] Código-fonte (Backend/Frontend)
2.  [ ] Base de Conhecimento (Conteúdo Vetorial)
3.  [ ] Dados de Mock/Teste
4.  [ ] Prompts e Configurações de LLM
5.  [ ] Variáveis de Ambiente e Infraestrutura

---
*Gerado em: 17/01/2026*
