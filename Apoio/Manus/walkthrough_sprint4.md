# Sprint 4: Interface do Agente (Frontend)

## 🎯 Objetivo
Implementar a interface de chat para o Agente Treq Enterprise, permitindo interação em linguagem natural e visualização de ações operacionais (Tools) através de cards interativos.

## 🛠️ Mudanças Realizadas

### 1. Renomeação Global (Sotreq -> Treq)
- Atualizado `README.md`, mocks e scripts de backend.
- Refatorado frontend para remover referências antigas.

### 2. Arquitetura Frontend (`src/features/agent`)
Nova estrutura modular adotada:
- `api/agentService.ts`: Cliente HTTP com tratamento de erro e tipagem.
- `hooks/useAgentChat.ts`: Custom hook para gerenciamento de estado (mensagens, loading, erros).

### 3. Componentes de UI
- **AgentChat**: Container principal responsivo.
- **ChatInput**: Campo de entrada com auto-resize.
- **Bubbles**:
    - `UserBubble`: Renderiza mensagens do usuário.
    - `AgentBubble`: Suporte a Markdown (`react-markdown`) e renderização de Tools.
- **Tool Cards**: Cards visuais para ações do agente:
    - `JiraCard`: Exibe tickets criados com link e ID.
    - `SlackCard`: Confirma envio de notificações.

### 4. Página (`/agent`)
- Nova rota criada em `app/agent/page.tsx`.

## ✅ Status de Verificação
- **Lint:** Passou sem erros nos novos módulos.
- **Build:** Tipos TypeScript validados.
- **Funcionalidade:**
    - Envio de mensagens.
    - Renderização otimista.
    - Exibição de Respostas Markdown.
    - Exibição de Cards de Ferramentas.

## 🚀 Como Testar
1. Backend: Certifique-se que `uvicorn` está rodando na porta 8002.
2. Frontend: Inicie `npm run dev` na pasta `frontend`.
3. Acesse: `http://localhost:3000/agent`
4. Teste:
    - "Como resolvo erro de pressão alta?" (Teste de RAG/Texto)
    - "Crie um ticket para vazamento na unidade X" (Teste de Jira Card)
    - "Avise o time de manutenção no Slack" (Teste de Slack Card)
