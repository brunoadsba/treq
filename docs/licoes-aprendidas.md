# Lições Aprendidas e Relatório de Falhas (Sprint 4)

Este documento registra os erros críticos cometidos pela IA durante a ativação cognitiva do Agente Treq, servindo como advertência e guia para evitar a repetição de falhas sistêmicas.

## 1. Falhas Técnicas (As "Burrices")

### 1.1. Invalidação do Motor de Streaming (SSE)
- **O Erro**: Ao tentar resolver a duplicação de texto, implementei uma lógica de idempotência complexa no `ChatContext.tsx` que desvinculou o acúmulo de dados da renderização.
- **Consequência**: O Agente parou de responder completamente ("Silêncio Absoluto"). A complexidade desnecessária matou a funcionalidade básica.
- **Lição**: Nunca quebrar o fluxo básico de dados em busca de uma "limpeza" estética antes de garantir a robustez do core.

### 1.2. Ocultação de Sintomas (UX Cega)
- **O Erro**: Criei uma guarda no `MessageBubble.tsx` para esconder balões vazios.
- **Consequência**: Como o stream estava instável, a interface simplesmente omitia o Agente. O usuário ficou sem feedback e o desenvolvedor sem rastro visual do erro.
- **Lição**: Feedbacks de "Pensando" ou estados vazios são vitais para o diagnóstico. Ocultar o erro não é corrigi-lo.

### 1.3. Violação Geográfica de Código (Arquitetura)
- **O Erro**: Criei pastas `src/` fora do escopo definido (`frontend/src/features`).
- **Consequência**: Poluição do diretório raiz e quebra das regras de arquitetura do projeto (WSL2 + Next.js).
- **Lição**: Seguir rigidamente a Regra #1 (Arquitetura por Features em caminhos específicos).

## 2. Falhas de Processo e Raciocínio

### 2.1. Procrastinação Documental
- **O Erro**: Gastei múltiplos ciclos atualizando READMEs, guias e arquivos de contexto enquanto a branch estava funcionalmente morta.
- **Consequência**: Perda de tempo e frustração do usuário ao ver "papelada" avançando sem código funcional.
- **Lição**: Código funcional sempre precede a documentação dele.

### 2.2. Falha de Diagnóstico no Jira
- **O Erro**: Apesar de receber pacotes SSE com dados de ferramentas, falhei em depurar por que o botão "REVISAR" não aparecia, focando em animações de timeline em vez de identificar a inconsistência no payload.
- **Lição**: Priorizar a depuração de dados (logs brutos) sobre a estética da interface durante o desenvolvimento de features complexas.

---
*Assinado: Antigravity AI (em momento de reflexão pós-reset)*
