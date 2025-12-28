# Frontend - Treq Assistente Operacional

Next.js 15 frontend para o Assistente Operacional Treq.

## Setup

1. Instalar dependências:
```bash
npm install
```

2. Configurar variáveis de ambiente:
```bash
cp .env.example .env.local
# Editar .env.local com suas credenciais
```

3. Rodar servidor de desenvolvimento:
```bash
npm run dev
```

A aplicação estará disponível em: http://localhost:3000

## Estrutura

- `app/` - App Router do Next.js 15
  - `(chat)/` - Rotas do chat
    - `page.tsx` - Página principal do chat
  - `layout.tsx` - Layout raiz
  - `globals.css` - Estilos globais
- `components/` - Componentes React
  - `Header.tsx` - Cabeçalho da aplicação
  - `MessageList.tsx` - Lista de mensagens
  - `MessageBubble.tsx` - Bolha de mensagem individual
  - `FormattedMessage.tsx` - Renderização de markdown com suporte a CoT
  - `InputArea.tsx` - Área de input com upload e áudio
  - `QuickActions.tsx` - Ações rápidas (botões de ação)
  - `Toast.tsx` - Sistema de notificações
- `hooks/` - Custom hooks
  - `useChat.ts` - Hook principal do chat (com streaming)
  - `useTTS.ts` - Text-to-Speech
  - `useAudioRecorder.ts` - Gravação de áudio
  - `useAudioTranscription.ts` - Transcrição de áudio
  - `useDocumentUpload.ts` - Upload de documentos
  - `useToast.ts` - Gerenciamento de toasts

## Funcionalidades Principais

### 1. Chat com Streaming
- **Streaming em tempo real:** Respostas aparecem incrementalmente
- **Server-Sent Events (SSE):** Consumo de stream do backend
- **Fallback automático:** Se streaming falhar, usa modo não-streaming

### 2. Chain of Thought (CoT) Parser
- **Renderização diferenciada:** Pensamento e resposta separados
- **Seção colapsável:** Pensamento do assistente pode ser expandido/recolhido
- **Visual discreto:** Pensamento em seção cinza, resposta formatada normalmente

### 3. Upload de Documentos
- **Botão de anexar:** Ícone de clipe na área de input
- **Formatos suportados:** PDF, DOCX, PPTX, Excel (.xlsx, .xls)
- **Feedback visual:** Toasts de sucesso/erro
- **Upload automático:** Inicia ao selecionar arquivo

### 4. Áudio
- **Gravação:** Botão de microfone para gravar áudio
- **Transcrição:** STT automático (Groq Whisper)
- **TTS:** Reprodução de áudio das respostas (Google Gemini TTS)
- **Controles:** Play, pause, resume, stop

### 5. Quick Actions
- **Ações rápidas:** Botões pré-configurados (Alertas Ativos, Status Recife, etc.)
- **Envio automático:** Clica no botão → envia query automaticamente

## Tecnologias

- **Next.js 15** (App Router)
- **TypeScript** (Strict Mode)
- **Tailwind CSS** (Estilização)
- **Shadcn/ui** (Componentes)
- **React Markdown** (Renderização de markdown)
- **Lucide React** (Ícones)

## Variáveis de Ambiente

```bash
# Backend API URL
NEXT_PUBLIC_API_URL=http://localhost:8000
```

## Componentes Principais

### FormattedMessage
Renderiza mensagens markdown com suporte especial para:
- **Chain of Thought:** Parser de `<pensamento>` e `<resposta>`
- **Status badges:** ✅ ⚠️ 🔴 com cores diferenciadas
- **Ações:** Cards destacados para recomendações
- **Markdown completo:** Títulos, listas, código, etc.

### InputArea
Área de input com múltiplas funcionalidades:
- Input de texto
- Botão de anexar documento
- Botão de gravação de áudio
- Botão de enviar
- Estados de loading (upload, transcrição, envio)

## Fluxo de Dados

1. **Usuário envia mensagem** → `InputArea` → `useChat.sendMessage()`
2. **Streaming ativado** → Consome SSE do backend
3. **Chunks recebidos** → Atualiza mensagem incrementalmente
4. **Parser CoT** → `FormattedMessage` detecta e renderiza tags
5. **Upload de documento** → `useDocumentUpload` → Backend → Indexação RAG

