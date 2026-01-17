# Registro de Dificuldades, Erros e Ajustes (Sprint 4)

Este documento registra os principais desafios técnicos enfrentados durante a implementação da Sprint 4 (Frontend Integration & Global Rename), bem como as soluções aplicadas.

## 1. Persistência de Marca Antiga (Sotreq) no RAG

### 🔴 O Problema
Apesar de uma refatoração global no código-fonte (`backend/app`, `frontend/src`) substituindo "Sotreq" por "Treq", o Agente continuava respondendo com referências à "Sotreq" e listando arquivos legados (ex: `Base_Operacional_Sotreq_Desafio.xlsx`).

### 🔎 Causa Raiz
A renomeação foi aplicada apenas em **pre-flight** (código estático). O conteúdo vetorial armazenado no banco de dados (Supabase, tabela `knowledge_base`) permaneceu inalterado. O chunk recuperado continha o texto original sujo.

### ✅ Ajuste (Solução)
Desenvolvimento e execução do script `scripts/sanitize_knowledge_base.py`.
- **Ação:** UPDATE direto no SQL via Python/Supabase Client.
- **Escopo:** Campos `content` e `metadata`.
- **Resultado:** 77 chunks higienizados.

---

## 2. Vazamento de Estrutura Interna no Prompt

### 🔴 O Problema
Ao receber uma saudação simples ("oi"), o Agente respondia listando a estrutura de diretórios do sistema de arquivos (`sotrec/DADOS/...`), quebrando a imersão e expondo detalhes técnicos.

### 🔎 Causa Raiz
O *System Prompt* instruía o modelo a usar o contexto recuperado de forma muito agressiva. Como o termo "oi" não tinha relevância semântica forte, o RAG trazia documentos genéricos de "Status" que continham a árvore de arquivos, e o LLM obedecia cegamente o comando de usar o contexto.

### ✅ Ajuste (Solução)
Implementação de **Greeting Detection** no `planner.py`.
- **Lógica:** Se input for saudação (< 5 chars ou palavras-chave), pula o RAG (`call_rag`) e direciona para resposta imediata (`respond`).
- **Refinamento:** O `responder.py` agora tem um template específico para saudações, ignorando contexto poluído.

---

## 3. Erro de Validação API (Http 422)

### 🔴 O Problema
O script de verificação `verify_fix.py` falhou com erro 422 Unprocessable Entity.

### 🔎 Causa Raiz
Mismatch de Schema entre o Cliente de Teste e a API Pydantic.
- **API (`routes.py`):** Esperava `AgentChatRequest(query: str, ...)`
- **Script Teste:** Enviava payload legado `{ "messages": [...] }`

### ✅ Ajuste (Solução)
Atualização do script de teste para respeitar o contrato da API (`query` em vez de `messages`).

---

## 4. Dependências de Teste (Playwright)

### 🔴 O Problema
Dificuldade em executar testes E2E devido à falta de binários de navegador e dependências de sistema no ambiente Linux.
- Erro: `Please run the following command to download new browsers: npx playwright install`
- Falha subsequente: Dependências de sistema (bibliotecas .so) ausentes após install parcial.

### ⚠️ Status/Ajuste
Adicionado `playwright` no `backend/requirements.txt` para garantir disponibilidade no Python, mas a execução via Node (`npx`) requer instalação de dependências de S.O. que podem exigir `sudo`, o que é restrito.
- **Workaround:** Criado script de teste E2E em Python (`scripts/test_sanity.py`) usando `requests` puro para validar a lógica sem depender de renderização de navegador pesado.

---

## Resumo Estatístico
- **Arquivos impactados:** 5 (Planner, Responder, Graph, Routes, Scripts)
- **Chunks de banco corrigidos:** 77
- **Tempo de resolução:** ~25 minutos
