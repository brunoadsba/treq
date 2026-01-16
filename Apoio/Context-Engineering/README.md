# Context Engineering - Master Harnesses para LLMs e Agentes de IA

## Visão Geral

Este repositório contém Master Harnesses - documentos padrão para guiar LLMs e agentes de IA em processos de engenharia de software. Cada harness segue padrões da indústria e implementa uma stack tecnológica moderna e consistente.

## Stack Tecnológica Padrão

- **Framework**: Next.js 15 (App Router)
- **Linguagem**: TypeScript (Strict Mode)
- **Estilização**: Tailwind CSS + Shadcn/ui
- **Banco de Dados**: Supabase/Neon (PostgreSQL)
- **ORM**: Drizzle ORM
- **Autenticação**: Supabase Auth ou Clerk
- **State Management**: Nuqs (URL state) antes de useState
- **Testes**: Vitest (Unit/Integração) + Playwright (E2E)
- **Deploy**: Vercel
- **Monitoramento**: Sentry + Vercel Analytics

## Estrutura do Projeto

A documentação está organizada em três fases estratégicas que seguem um fluxo de desenvolvimento natural:

- Fase 1: Alta Prioridade (PRD, ADR, User Stories, TDD/BDD, Code Review)
- Fase 2: Média Prioridade (API Design, Database Design, CI/CD Pipeline)
- Fase 3: Estratégica (Domain-Driven Design, Security Review, Performance Review)

## Sistema de Indexação e Guia de Desenvolvimento

Para otimizar o uso dos Master Harnesses por LLMs, foram implementados três sistemas complementares:

1. **Indexação Inteligente no Cursor AI** (`INDEXACAO_CURSOR.md`) - Sistema de chunks semânticos para reduzir token usage
2. **Guia de Desenvolvimento com LLMs** (`LLM_DESENVOLVIMENTO.md`) - Como aplicar os harnesses em projetos reais
3. **Protocolo de Consulta Humana** (`CONSULTA_HUMANA.md`) - Quando a resposta da LLM for insuficiente

Para mais detalhes, consulte os arquivos específicos.
