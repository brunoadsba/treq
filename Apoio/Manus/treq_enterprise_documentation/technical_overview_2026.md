# Documentação Técnica: Treq Enterprise 2026

Esta documentação descreve a arquitetura, estrutura e padrões do ecossistema **Treq Enterprise**, atualizada após a implementação do **Agentic RAG Refinement** e estabilização de infraestrutura.

## 1. Arquitetura do Sistema

O Treq Enterprise opera em uma stack moderna focada em performance e auto-gerenciamento da IA.

### 1.1. Backend (FastAPI + LangGraph)
- **Agente Principal:** Orquestrado via **LangGraph**, utilizando um fluxo de planejamento (`Planner`), busca (`Retriever`) e resposta (`Responder`).
- **Base de Conhecimento:** RAG (Retrieval-Augmented Generation) sobre **PGvector** (PostgreSQL) para busca semântica.
- **Memória & Persistência:** Integração com **LangGraph Checkpointers** para persistência de estado de longa duração por `thread_id`.
- **Governança:** Módulo central de tracing e tags para monitoramento (LangSmith).

### 1.2. Frontend (Next.js + Tailwind)
- **Arquitetura de Features:** Organizado por domínios em `src/features/`.
- **UI/UX 2026:** Design minimalista, bordas arredondadas e ausência de linhas divisórias rígidas para uma experiência fluida.
- **Micro-interações:**
    - **Badge de Estado:** Indicador visual de processamento na navegação principal.
    - **Skeleton Adaptativo:** Carregamento contextual (texto, cards, listas).
    - **Scroll Lock Inteligente:** Pausa o auto-scroll durante a leitura ativa do histórico.
- **Multimodalidade:** Suporte nativo para Voz (STT/TTS), Imagens (Vision) e Documentos.

---

## 2. Estrutura do Projeto (Frontend)

O diretório `frontend/` segue a estrutura Enterprise:

- `app/`: Estrutura de roteamento Next.js (App Router).
  - `agent/`: Interface do Agente LangGraph.
  - `chat/`: Interface de Chat Legacy/Multimodal.
- `components/`: Componentes globais e UI (Shadcn).
- `src/features/`: Lógica de domínio isolada.
  - `agent/`: Componentes, hooks e serviços específicos do Agente Enterprise.
  - `chat/`: Lógica central de mensagens.
  - `vision/`: Componentes de captura e processamento de imagem.
- `hooks/`: Hooks globais (tema, auth, áudio).
- `lib/`: Utilitários e instâncias de clientes (Supabase, API).

---

## 3. Guia de Desenvolvimento & Estabilidade (WSL2)

Devido a limitações conhecidas do kernel WSL2 com extensões C, siga estes padrões:

1.  **Versão Python:** Use preferencialmente **Python 3.11** (disponível no `/venv` do projeto).
2.  **Logging Seguro:** Sempre use `enqueue=False` no Loguru para evitar crashes de thread no WSL2.
3.  **Loop do Servidor:** Evite `uvloop`. Use o loop padrão do `asyncio` (`uvicorn --loop asyncio`).
4.  **Conexões Externas:** Em caso de `Network unreachable` para o banco de dados no WSL2, verifique as configurações de DNS do subsistema.

---

## 4. Novas Features Implementadas

- **Self-Correction (Agente):** O agente agora detecta buscas vazias no RAG e decide entre reformular a query ou responder diretamente, evitando alucinações.
- **Branding Consolidado:** Sanitização automática ("Treq" vs "Sotreq") em todas as saídas do agente.
- **Limpeza Visual:** Interfaces de entrada sem bordas horizontais divisórias, alinhadas com o mock-up "Enterprise 2026".
