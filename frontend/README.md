# Frontend - Treq Assistente Operacional

Next.js 15 frontend para o Assistente Operacional Treq.

## 🐳 Setup via Docker (Recomendado)

O desenvolvimento do frontend deve ser feito via Docker para garantir que a versão do Node.js e as dependências nativas sejam idênticas em todos os ambientes.

1. **Subir o serviço com Hot-Reload**:
   ```bash
   docker compose up -d frontend
   ```

2. **Verificar Logs**:
   ```bash
   docker logs -f treq-frontend
   ```

A aplicação estará disponível em: [http://localhost:3000](http://localhost:3000)

## ⚠️ Setup Manual (Alternativo)

> [!NOTE]
> Use este método apenas se tiver o Node.js 20+ instalado localmente no WSL2 e desejar evitar a sobrecarga do Docker.

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

A aplicação estará disponível em: http://localhost:3000 (Certifique-se que o backend está na 8002)

## Estrutura

```
frontend/
├── app/                        # App Router do Next.js 15
│   ├── chat/                   # Rotas do chat
│   │   └── page.tsx            # Página principal do chat
│   ├── layout.tsx              # Layout raiz
│   ├── page.tsx                # Redireciona para /chat
│   └── globals.css             # Estilos globais
├── src/features/               # Funcionalidades modulares
│   └── vision/                 # Feature Vision (Câmera, OCR, Imagens)
├── components/                 # Componentes React
│   ├── Header.tsx              # Cabeçalho da aplicação
│   ├── MessageList.tsx         # Lista de mensagens
│   ├── MessageBubble.tsx       # Bolha de mensagem individual
│   ├── FormattedMessage.tsx    # Renderização de markdown com CoT
│   ├── InputArea.tsx           # Área de input com upload e áudio
│   ├── QuickActions.tsx        # Ações rápidas (botões de ação)
│   ├── ChartMessage.tsx        # Visualização de gráficos
│   └── Toast.tsx               # Sistema de notificações
├── hooks/                      # Custom hooks
│   ├── useChat.ts              # Hook principal do chat (streaming)
│   ├── useTTS.ts               # Text-to-Speech
│   ├── useAudioRecorder.ts     # Gravação de áudio
│   ├── useAudioTranscription.ts # Transcrição de áudio
│   ├── useDocumentUpload.ts    # Upload de documentos
│   ├── useTheme.ts             # Gerenciamento de tema
│   ├── useHighContrast.ts      # Modo alto contraste
│   └── useToast.ts             # Gerenciamento de toasts
├── lib/                        # Utilitários
│   ├── api.ts                  # Cliente de API
│   └── supabase.ts             # Cliente Supabase
├── design-system/              # Sistema de design
│   ├── components/             # Componentes base
│   └── tokens/                 # Design tokens
└── package.json                # Dependências npm
```


## Funcionalidades Principais

### 1. Chat com Streaming
- **Streaming em tempo real:** Respostas aparecem incrementalmente
- **Server-Sent Events (SSE):** Consumo de stream do backend
- **Fallback automático:** Se streaming falhar, usa modo não-streaming

### 2. Chain of Thought (CoT) Parser
- **Renderização diferenciada:** Pensamento e resposta separados
- **Seção colapsável:** Pensamento do assistente pode ser expandido/recolhido
- **Visual discreto:** Pensamento em seção cinza, resposta formatada normalmente

### 3. Vision & Upload de Documentos
- **Captura de Câmera:** Botão de câmera com interface premium e guias de enquadramento
- **Formatos suportados:** PDF, DOCX, PPTX, Excel, JPG, PNG, WEBP
- **Análise Multimodal:** Extração de tabelas e leitura inteligente de imagens via Gemini Vision
- **Feedback visual:** Toasts de sucesso/erro e efeito de flash na captura

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
# Backend API URL (Obrigatório para Vision e Chat)
NEXT_PUBLIC_API_URL=http://localhost:8002
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

