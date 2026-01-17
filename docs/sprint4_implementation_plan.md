# Implementação Sprint 4: Interface do Agente (Frontend)

Este documento detalha o plano de execução para a Sprint 4, focado na integração do frontend com o Agente Enterprise. O plano segue rigorosamente os padrões de `Context-Engineering`, definindo Histórias de Usuário, Arquitetura e Passos de Implementação Atômicos (GSD).

## 1. Visão Geral e Objetivos
**Objetivo:** Prover uma interface de chat moderna e responsiva para que operadores interajam com o Agente Treq Enterprise, visualizando não apenas texto, mas ações estruturadas (Ferramentas).

**Escopo (In-Scope):**
- Chat Interface (Input, Lista de Mensagens, Scroll).
- Renderização de Respostas Textuais (Markdown).
- Renderização de Tool Outputs (Cards visuais para Jira/Slack).
- Feedback de Estado (Loading, Error, Rate Limit).
- Integração com endpoint `/agent/chat`.

**Fora do Escopo (Out-of-Scope):**
- Histórico persistente de conversas anteriores (sessões salvas no menu lateral).
- Autenticação avançada (já coberto pelo middleware existente).
- Upload de arquivos no chat.

---

## 2. Histórias de Usuário (User Stories)

### US-010: Interação Básica de Chat
**Persona:** Operador
**Prioridade:** Must Have
**Story Points:** 5

**Como** Operador,
**quero** enviar perguntas em linguagem natural e receber respostas textuais,
**para que** eu possa obter informações operacionais sem navegar em menus complexos.

#### Critérios de Aceite (Gherkin)
```gherkin
Funcionalidade: Chat Básico

  Cenário: Enviar mensagem de texto
    Dado que estou na página "/agent"
    Quando digito "Como resolvo erro X?" no campo de input
    E pressiono Enter
    Então vejo minha mensagem aparecer imediatamente na lista (otimista)
    E vejo um indicador de "Agente pensando..."
    E recebo uma resposta textual em Markdown formatado
```

### US-011: Visualização de Ações (Tool Cards)
**Persona:** Operador
**Prioridade:** Must Have
**Story Points:** 8

**Como** Operador,
**quero** ver confirmações visuais quando o agente executa uma ação (ex: postar no Slack),
**para que** eu tenha certeza do que foi feito e os detalhes da operação.

#### Critérios de Aceite
```gherkin
Funcionalidade: Tool Output Rendering

  Cenário: Agente executa ação no Slack
    Dado que pedi "Avise o time no Slack"
    Quando o agente processa o pedido
    Então vejo um card visual "Slack Notification" na timeline do chat
    E o card mostra o Canal (#geral) e o Status (Sucesso)
    E o card tem um ícone distintivo do Slack

  Cenário: Agente abre ticket no Jira
    Dado que pedi "Abra um chamado sobre vazamento"
    Quando o agente cria o ticket
    Então vejo um card visual "Jira Ticket"
    E o card mostra a Chave do Ticket (TREQ-123) e um link clicável
```

### US-012: Feedback de Estado e Erros
**Persona:** Operador
**Prioridade:** Should Have
**Story Points:** 3

**Como** usuário do sistema,
**quero** ser informado se houver lentidão ou erros,
**para que** eu não fique esperando indefinidamente.

#### Critérios de Aceite
```gherkin
Funcionalidade: Feedback de Estado

  Cenário: Rate Limit Excedido
    Dado que enviei muitas mensagens rapidamente
    Quando recebo um erro 429 da API
    Então vejo um toast ou mensagem no chat: "Muitas requisições. Aguarde um momento."
    E o input é temporariamente bloqueado ou sinalizado
```

---

## 3. Arquitetura Frontend (Tech Stack)

### Diretórios e Arquivos
```
frontend/src/features/agent/
├── api/
│   └── agentService.ts       # Cliente HTTP (fetch/axios) para /agent/chat
├── components/
│   ├── AgentChat.tsx         # Container principal (State Manager)
│   ├── ChatInput.tsx         # Campo de entrada com auto-resize
│   ├── MessageList.tsx       # Renderizador de lista com auto-scroll
│   ├── bubbles/
│   │   ├── UserBubble.tsx    # Balão do usuário
│   │   └── AgentBubble.tsx   # Balão do agente (Markdown + Tools)
│   └── tools/
│       ├── ToolCard.tsx      # Wrapper genérico para cards
│       ├── JiraCard.tsx      # Card específico do Jira
│       └── SlackCard.tsx     # Card específico do Slack
├── hooks/
│   └── useAgentChat.ts       # Lógica de state (messages, loading, error)
└── types.ts                  # Definições Zod/TypeScript
```

### Contrato de Dados (Types)
```typescript
interface AgentMessage {
  id: string;
  role: 'user' | 'assistant';
  content: string;
  timestamp: Date;
  toolsUsed?: ToolOutput[]; // Apenas para assistant
}

interface ToolOutput {
  tool: 'jira_create_ticket' | 'slack_notify';
  result: Record<string, any>;
}

interface AgentState {
  messages: AgentMessage[];
  isLoading: boolean;
  error: string | null;
}
```

---

## 4. Plano de Execução (GSD - Atomic Steps)

Seguindo a filosofia GSD, cada passo deve ser um commit isolado e testável.

### Passo 1: Fundação (Types & Service)
- **Ação:** Criar `frontend/src/features/agent/types.ts` e `frontend/src/features/agent/api/agentService.ts`.
- **Detalhe:** Definir interfaces TypeScript e implementar a chamada `POST /agent/chat` usando `fetch` e tratamento de erro básico.
- **Validação:** Teste unitário simples do service (mockando fetch).

### Passo 2: Componentes Unitários (Bubbles & Input)
- **Ação:** Criar `UserBubble`, `AgentBubble` (sem tools ainda) e `ChatInput`.
- **Detalhe:** Usar `shadcn/ui` para estilização básica. `react-markdown` para renderizar texto do agente.
- **Validação:** Storybook ou renderização em página de teste.

### Passo 3: Gerenciamento de Estado (Hook)
- **Ação:** Implementar `hooks/useAgentChat.ts`.
- **Detalhe:** Gerenciar array de mensagens, status de loading e função `sendMessage` que chama a API e atualiza o estado otimista.
- **Validação:** Teste do hook com `renderHook`.

### Passo 4: Container Principal e Página
- **Ação:** Criar `AgentChat.tsx` integrando o hook e os componentes visuais. Criar página `app/agent/page.tsx`.
- **Detalhe:** Montar o layout final. Garantir scroll automático para última mensagem.
- **Validação:** Navegar para `/agent` e enviar mensagem (verificar log do console se API responder).

### Passo 5: Renderização de Tool Cards (Features Visuais)
- **Ação:** Implementar `ToolCard`, `JiraCard` e `SlackCard`.
- **Detalhe:** Atualizar `AgentBubble` para iterar sobre `toolsUsed` e renderizar os cards apropriados ABAIXO do texto.
- **Validação:** Mockar uma resposta com tools e verificar renderização visual.

### Passo 6: Tratamento de Erros e Rate Limit
- **Ação:** Melhorar `useAgentChat` para tratar 429 e erros de rede.
- **Detalhe:** Exibir Toasts (`sonner` ou `toast`) em caso de erro.
- **Validação:** Forçar erro no backend e verificar UI.

---

## 5. Critérios de "Done" (DOD)
1.  Todas as User Stories implementadas.
2.  Código TypeScript sem erros (strict mode).
3.  Design responsivo (Mobile/Desktop).
4.  Commit history limpo e atômico.
5.  Passar no teste manual E2E (Fluxo de Chat + Ação).
