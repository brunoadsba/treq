# Componentes do Design System Treq

Documentação completa dos componentes React do Treq Assistente Operacional.

## Índice

- [Header](#header)
- [Logo](#logo)
- [MessageList](#messagelist)
- [MessageBubble](#messagebubble)
- [FormattedMessage](#formattedmessage)
- [InputArea](#inputarea)
- [QuickActions](#quickactions)
- [Toast](#toast)
- [ContextSuggestions](#contextsuggestions)

---

## Header

**Arquivo:** `app/components/Header.tsx`

Componente de cabeçalho principal da aplicação.

### Props

```typescript
interface HeaderProps {
  title?: string; // Título exibido (padrão: "Treq Assistente Operacional")
}
```

### Uso

```tsx
import { Header } from "../components/Header";

<Header />
// ou
<Header title="Meu Título Customizado" />
```

### Características

- Fundo preto (`bg-treq-black`)
- Logo Treq integrada
- Toggle de modo alto contraste
- Altura: 64px (desktop), 56px (mobile)
- Padding: 16px

### Acessibilidade

- Botão de alto contraste com `aria-label`
- Navegação por teclado suportada

---

## Logo

**Arquivo:** `app/components/Logo.tsx`

Componente de logo do Treq com múltiplas variantes.

### Props

```typescript
interface LogoProps {
  variant?: "horizontal" | "vertical" | "icon";
  size?: "sm" | "md" | "lg";
  className?: string;
}
```

### Uso

```tsx
import { Logo } from "../components/Logo";

// Horizontal (padrão)
<Logo variant="horizontal" size="md" />

// Apenas ícone
<Logo variant="icon" size="sm" />

// Vertical
<Logo variant="vertical" size="lg" />
```

### Variantes

- **horizontal**: Logo + texto lado a lado (padrão)
- **vertical**: Logo acima do texto
- **icon**: Apenas o símbolo

### Tamanhos

- **sm**: Ícone 24px, texto `text-lg`
- **md**: Ícone 32px, texto `text-xl` (padrão)
- **lg**: Ícone 40px, texto `text-2xl`

### Características

- SVG inline (sem dependências externas)
- Cores adaptáveis via `currentColor`
- Acessível (aria-hidden no SVG)

---

## MessageList

**Arquivo:** `app/components/MessageList.tsx`

Container para lista de mensagens do chat.

### Props

```typescript
interface MessageListProps {
  messages: ChatMessage[];
  isLoading?: boolean;
}
```

### Uso

```tsx
import { MessageList } from "../components/MessageList";

<MessageList messages={messages} isLoading={isLoading} />
```

### Características

- Scroll automático
- Estado vazio com mensagem de boas-vindas
- Indicador de loading quando assistente está pensando
- Espaçamento: 24px entre mensagens
- Padding: 16px (mobile), 24px (desktop)
- Fundo: `bg-treq-gray-50`

### Estados

- **Vazio**: Mensagem de boas-vindas centralizada
- **Com mensagens**: Lista scrollável
- **Loading**: Indicador com spinner amarelo

---

## MessageBubble

**Arquivo:** `app/components/MessageBubble.tsx`

Componente de bolha de mensagem individual.

### Props

```typescript
interface MessageBubbleProps {
  message: ChatMessage; // { role: "user" | "assistant", content: string, timestamp?: string }
}
```

### Uso

```tsx
import { MessageBubble } from "../components/MessageBubble";

<MessageBubble message={message} />
```

### Características

- **Mensagem do usuário:**
  - Fundo amarelo (`bg-treq-yellow`)
  - Texto preto
  - Alinhada à direita
  - Padding: 16px

- **Mensagem do assistente:**
  - Fundo branco com borda
  - Texto preto
  - Alinhada à esquerda
  - Padding: 20px horizontal, 16px vertical
  - Controles de áudio (TTS)

### Funcionalidades

- Controle de reprodução de áudio (play/pause/stop)
- Controle de velocidade de reprodução
- Timestamp formatado
- Animações de entrada suaves

### Acessibilidade

- Botões com `aria-label`
- Estados com `aria-pressed`
- Foco visível em todos os controles

---

## FormattedMessage

**Arquivo:** `app/components/FormattedMessage.tsx`

Renderiza mensagens markdown com suporte especial para Chain of Thought (CoT).

### Props

```typescript
interface FormattedMessageProps {
  content: string; // Conteúdo markdown com tags <pensamento> e <resposta>
}
```

### Uso

```tsx
import { FormattedMessage } from "../components/FormattedMessage";

<FormattedMessage content={messageContent} />
```

### Funcionalidades

- **Chain of Thought (CoT):**
  - Parser de tags `<pensamento>` e `<resposta>`
  - Seção de pensamento colapsável
  - Visual diferenciado (fundo cinza claro, borda amarela)

- **Markdown completo:**
  - Títulos (h1, h2, h3)
  - Listas (ordenadas e não ordenadas)
  - Código inline e blocos
  - Links
  - Ênfase (negrito, itálico)

- **Elementos especiais:**
  - Status badges (✅ ⚠️ 🔴)
  - Cards de ação destacados
  - Formatação de listas com bullets amarelos

### Acessibilidade

- Seção de pensamento com `role="alert"`
- Ícones decorativos com `aria-hidden="true"`

---

## InputArea

**Arquivo:** `app/components/InputArea.tsx`

Área de input com múltiplas funcionalidades (texto, áudio, documentos).

### Props

```typescript
interface InputAreaProps {
  onSend: (message: string) => void;
  isLoading?: boolean;
  placeholder?: string;
  userId?: string;
  conversationId?: string;
  onDocumentUploaded?: (fileName: string, chunksIndexed: number) => void;
  onDocumentUploadError?: (error: string) => void;
}
```

### Uso

```tsx
import { InputArea } from "../components/InputArea";

<InputArea 
  onSend={handleSend}
  isLoading={isLoading}
  onDocumentUploaded={(fileName, chunks) => console.log(fileName, chunks)}
/>
```

### Funcionalidades

- **Input de texto:**
  - Placeholder descritivo
  - Touch target mínimo 48px
  - Suporte a modo alto contraste

- **Upload de documentos:**
  - Formatos: PDF, DOCX, PPTX, Excel
  - Feedback visual durante upload
  - Toast de sucesso/erro

- **Gravação de áudio:**
  - Botão de gravar com feedback visual
  - Área de áudio gravado com preview
  - Transcrição automática

- **Botão enviar:**
  - Estados de loading
  - Desabilitado quando vazio
  - Touch target 48px mínimo

### Características Industriais

- Botões com tamanho mínimo 48px (touch targets)
- Feedback visual claro em todos os estados
- Suporte a uso com luvas
- Modo alto contraste funcional

### Acessibilidade

- Todos os botões com `aria-label`
- Input com `aria-describedby` quando necessário
- Navegação por teclado completa
- Foco visível em todos os elementos

---

## QuickActions

**Arquivo:** `app/components/QuickActions.tsx`

Botões de ações rápidas pré-configuradas.

### Props

```typescript
interface QuickActionsProps {
  onActionClick: (query: string) => void;
  disabled?: boolean;
}
```

### Uso

```tsx
import { QuickActions } from "../components/QuickActions";

<QuickActions 
  onActionClick={handleAction} 
  disabled={isLoading} 
/>
```

### Ações Disponíveis

1. **Alertas Ativos** - "Quais alertas críticos estão ativos?"
2. **Status Recife** - "Qual o status operacional de Recife?"
3. **Status Salvador** - "Qual o status operacional de Salvador?"
4. **Procedimentos** - "Quais são os procedimentos operacionais?"
5. **Consultoria** - "consultoria:"

### Características

- Scroll horizontal em mobile
- Espaçamento: 8px entre botões
- Padding: 16px horizontal, 8px vertical
- Fundo cinza claro com hover

### Acessibilidade

- `role="toolbar"` no container
- Cada botão com `aria-label` descritivo
- Navegação por teclado (Enter/Space)
- Foco visível

---

## Toast

**Arquivo:** `app/components/Toast.tsx`

Sistema de notificações toast.

### Props

```typescript
interface ToastProps {
  message: string;
  type?: "success" | "error" | "warning" | "info";
  duration?: number; // em milissegundos (padrão por tipo)
  onClose: () => void;
}
```

### Uso

```tsx
import { Toast } from "../components/Toast";

<Toast 
  message="Operação realizada com sucesso!"
  type="success"
  duration={5000}
  onClose={() => removeToast(id)}
/>
```

### Tipos e Durações Padrão

- **success**: 5000ms (5s) - Verde
- **error**: 7000ms (7s) - Vermelho
- **warning**: 6000ms (6s) - Laranja
- **info**: 5000ms (5s) - Azul

### Características

- Animação slide-in da direita
- Posicionamento: canto inferior direito
- Responsivo (mobile: bottom-4 right-4, desktop: bottom-6 right-6)
- Stack de múltiplos toasts
- Fechamento manual ou automático

### Acessibilidade

- `role="alert"` para erros
- `aria-live="polite"` para outros tipos
- Botão de fechar com `aria-label`

---

## ContextSuggestions

**Arquivo:** `app/components/ContextSuggestions.tsx`

Sugestões contextuais para gestores operacionais.

### Props

```typescript
interface ContextSuggestionsProps {
  onSelectSuggestion: (text: string) => void;
  userId?: string;
}
```

### Uso

```tsx
import { ContextSuggestions } from "../components/ContextSuggestions";

<ContextSuggestions 
  onSelectSuggestion={setMessage}
  userId="user-123"
/>
```

### Sugestões Disponíveis

1. "Status atual de todas as unidades"
2. "Comparar desempenho SP vs RJ"
3. "Alertas críticos não resolvidos"
4. "Métricas de cancelamentos por unidade"
5. "Procedimento de contenção operacional"

### Características

- Layout flex wrap
- Botões pequenos e discretos
- Foco automático no input após seleção
- Suporte a modo alto contraste

### Acessibilidade

- `role="region"` no container
- Cada botão com `aria-label`
- Navegação por teclado (Enter/Space)

---

## Padrões de Uso

### Importação

```tsx
// Importar componentes individuais
import { Header } from "../components/Header";
import { MessageBubble } from "../components/MessageBubble";

// Ou importar múltiplos
import { Header, MessageList, InputArea } from "../components";
```

### Estilização

Todos os componentes usam classes Tailwind com tokens `treq-*`. Para customização:

```tsx
// Usar className para adicionar estilos
<Header className="custom-class" />

// Ou usar variantes quando disponíveis
<Logo variant="icon" size="lg" />
```

### Acessibilidade

Todos os componentes seguem padrões WCAG 2.1 AA:

- Foco visível em elementos interativos
- aria-labels em botões sem texto
- Navegação por teclado funcional
- Suporte a screen readers

### Modo Alto Contraste

Componentes críticos suportam modo alto contraste via hook `useHighContrast`:

```tsx
import { useHighContrast } from "../hooks/useHighContrast";

const isHighContrast = useHighContrast();
// Aplicar estilos condicionais
```

---

## Boas Práticas

1. **Sempre use os componentes do Design System** ao invés de criar novos
2. **Mantenha consistência** usando tokens de cores e espaçamento
3. **Teste acessibilidade** com navegação por teclado e screen readers
4. **Respeite touch targets** mínimos de 48px para ambiente industrial
5. **Use aria-labels** em todos os botões sem texto descritivo

---

**Última atualização:** Dezembro 2024  
**Versão:** 1.0
