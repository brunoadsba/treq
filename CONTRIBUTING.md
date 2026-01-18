# Guia de Contribuição Treq Enterprise (5S)

Bem-vindo ao projeto Treq Enterprise. Para manter a excelência técnica e a agilidade, seguimos rigorosamente os princípios do 5S aplicado ao software.

## 📋 Regras de Ouro (Checklist de PR)

Todo Pull Request deve ser validado contra este checklist antes do merge:

1.  **Arquitetura (Seiton)**:
    *   Novos recursos DEVEM ficar em `src/features/[NOME_DA_FEATURE]`.
    *   Não crie pastas genéricas como `services/`, `controllers/` ou `pages/` na raiz do `src`.
    *   Componentes reutilizáveis devem ser promovidos para `src/components/ui`.

2.  **Tamanho de Arquivos (Seiso)**:
    *   Nenhum arquivo deve exceder **200 linhas** (Regra #5).
    *   Se um arquivo crescer demais, extraia lógica para hooks (`use...`) ou sub-componentes.

3.  **Segurança e Validação (Seiketsu)**:
    *   Todo input de formulário ou API deve ter um schema **Zod** para validação.
    *   Mutações de estado críticas devem ter log de auditoria (LGPD).

4.  **DRY & KISS (Shitsuke)**:
    *   Não repita código. Abstraia imediatamente.
    *   Escolha a solução mais simples que atenda aos requisitos (YAGNI).

## 🛠️ Stack Tecnológica

*   **Frontend**: Next.js 15 (App Router), Tailwind CSS, React Hook Form + Zod, Lucide React.
*   **Backend**: FastAPI, LangGraph (Agentes), Supabase (DB/Auth), Redis (Cache).

## 🚀 Fluxo de Trabalho

1.  **Instalação**: Utilize `docker compose up -d --build` para subir o ambiente completo.
2.  **Linting**: 
    *   No frontend: `npm run lint`.
    *   No backend: `ruff check`.
3.  **Testes**: 
    *   Frontend (E2E): `npx playwright test`.
    *   Backend: `pytest`.

## 📂 Estrutura de Diretórios Padronizada

### Frontend (`frontend/src/`)
```text
src/
├── app/               # Rotas Next.js (minimalista)
├── features/          # O CORE organizado por feature (Chat, Auth, Vision)
│   └── [feature]/
│       ├── components/
│       ├── hooks/
│       ├── types.ts
│       └── .context.md
├── components/ui/     # Primitivos reutilizáveis
├── hooks/             # Hooks globais
└── lib/               # Clientes (API, Supabase)
```

### Backend (`backend/app/`)
```text
app/
├── api/               # Integradores de rotas
├── features/          # Domínios de negócio (Agent, Vision, Connectors)
│   └── [feature]/
│       ├── nodes/     # Nós do grafo (se aplicável)
│       ├── routes.py
│       ├── models.py
│       └── .context.md
├── core/              # Governança e Configurações
└── services/          # Motores compartilhados (LLM, RAG)
```

---
*Manter a disciplina (Shitsuke) é o que garante a evolução sustentável do Treq.*
