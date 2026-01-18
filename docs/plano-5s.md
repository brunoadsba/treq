# Plano de Ação 5S: Treq Enterprise (2026)

**Status Final:** ✅ CONCLUÍDO (2026-01-18)
**Responsável Operacional:** Antigravity AI (Senior Full-Stack Engineer)

---

## 1. Seiri (Senso de Utilização / Descarte)
*Foco: "O que não serve, ocupa espaço e gera confusão."*

### Análise de Redundância:
1.  **Arquivos Legados de Infraestrutura**: `render.yaml` e `render-blueprint.yaml` (o projeto agora é Docker-first).
2.  **Duplicidade de Código (Backend)**: Pasta `backend/src/features/vision` coexistindo com `backend/app/features/`.
3.  **Redundância de Frontend**: Pasta `frontend/app` na raiz coexistindo com `frontend/src`.
4.  **Arquivos Temporários/Contexto**: `erro-login.md`, `page.tsx.bak`, `comparativo_versoes_treq.md` soltos na raiz.
5.  **Dependências Obsoletas**: `PyPDF2` (substituído por `pdfplumber`), `playwright` no backend (pertence ao frontend).

### Proposta de Descarte:
*   **Ação**: Deletar arquivos `.yaml` do Render e arquivos `.bak`.
*   **Ação**: Mover `vision` para dentro de `backend/app/features/` e remover `backend/src`.
*   **Ação**: Consolidar `frontend/app` dentro de `frontend/src/app`.
*   **Justificativa**: Redução de 15% no ruído visual do diretório, aceleração do build Docker (menos arquivos para copiar) e eliminação de confusão para novos desenvolvedores.

---

## 2. Seiton (Senso de Organização / Ordenação)
*Foco: "Um lugar para cada coisa e cada coisa em seu lugar."*

### Estrutura de Projeto:
*   **Backend**: Padronizar em `backend/app/features/[feature_name]`. Cada feature deve conter seu próprio `routes.py`, `models.py` e `.context.md`.
*   **Frontend**: Seguir a Regra #1: `frontend/src/features/[feature_name]`. Componentes compartilhados devem residir estritamente em `frontend/src/components/ui`.

### Convenções de Nomenclatura:
*   **Arquivos**: `kebab-case` para arquivos frontend, `snake_case` para arquivos backend.
*   **Componentes**: `PascalCase`.
*   **Variáveis/Funções**: `camelCase` (JS/TS), `snake_case` (Python).

### Acessibilidade:
*   **Mapa de Calor**: Criar um `INTERNAL_MAP.md` no root que descreva onde cada regra de negócio reside.

---

## 3. Seiso (Senso de Limpeza / Inspeção)
*Foco: "Limpar não é apenas remover sujeira, mas inspecionar e prevenir."*

### Dívida Técnica (Top 5):
1.  **ChatContext.tsx**: Gerenciamento de estado SSE muito complexo (> 250 linhas).
2.  **responder_node.py**: Lógica de sanitização por regex misturada com lógica de negócio.
3.  **Auth Guards**: Implementação ad-hoc em múltiplos componentes em vez de um middleware centralizado.
4.  **Magic Numbers**: Timeouts de 10s e 30s espalhados em chamadas de API sem constantes.
5.  **Loguru Overload**: Alguns logs de debug persistindo em produção.

### Plano de Limpeza:
*   **Refatoração**: Dividir `ChatContext` em hooks específicos (`useSSE`, `useMessageHistory`).
*   **Constantes**: Criar `core/constants.py` no backend e `lib/constants.ts` no frontend.
*   **Linting**: Rodar `ruff check --fix` no backend e `npm run lint` no frontend.

---

## 4. Seiketsu (Senso de Padronização / Saúde)
*Foco: "Tornar o estado de limpeza e organização um padrão visual."*

### Padrões de Codificação Obrigatórios:
1.  **Tamanho**: Máximo 200 linhas por arquivo (Regra #5).
2.  **Validadores**: Todo input deve passar por um Schema Zod (Regra #11/16).
3.  **Tipagem**: Proibir uso de `any` (TS) e exigir Type Hints em funções críticas (Python).
4.  **Erros**: Seguir o padrão `{ success: bool, data?: T, message?: string }` para todas as respostas de ações/services.

### Documentação:
*   Uso obrigatório de `.context.md` em toda nova feature (Regra #15).

### Ferramentas:
*   **Frontend**: ESLint + Prettier + Husky.
*   **Backend**: Ruff + Black + MyPy.

---

## 5. Shitsuke (Senso de Disciplina / Autodisciplina)
*Foco: "Fazer o que deve ser feito, mesmo sem supervisão."*

### Integração Contínua (CI):
*   Bloquear Merges no GitHub se o linting ou testes E2E (Playwright) falharem.
*   Auto-fix de formatação no commit via Husky.

### Revisão de Código (Checklist):
- [ ] O código está em `src/features`?
- [ ] Há novoSchema Zod para novos inputs?
- [ ] O arquivo excede 200 linhas?
- [ ] Existe log de auditoria para ações de mutação (LGPD)?

### Métricas de Saúde:
*   Manter cobertura de testes em `> 70%` nas pastas `features/`.
*   Zero warnings críticos no console do navegador em produção.
