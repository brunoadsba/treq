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
  - `layout.tsx` - Layout raiz
  - `globals.css` - Estilos globais
- `components/` - Componentes React
  - `ui/` - Componentes Shadcn/ui
  - `chat/` - Componentes específicos do chat
- `lib/` - Utilitários e helpers

## Tecnologias

- Next.js 15 (App Router)
- TypeScript
- Tailwind CSS
- Shadcn/ui
- Supabase Client

