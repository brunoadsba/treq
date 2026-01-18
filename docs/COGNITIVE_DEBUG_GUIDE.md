# Guia de Transparência Cognitiva & Depuração

Este documento detalha o sistema de **Rastro Cognitivo** e os **Modais de Ação** implementados no Treq Enterprise, projetados para fornecer transparência total sobre o raciocínio da IA e controle humano sobre execuções críticas.

## 🧠 Fluxo Cognitivo (Brain Shift)

O Treq evoluiu de um sistema de buscas para um **Agente de Raciocínio**. Cada interação percorre um grafo de estados (LangGraph) que decide dinamicamente o próximo passo:

1.  **Planner**: Analisa a consulta, gera um pensamento interno (`thought`) e decide uma intenção (`intent`).
2.  **Retriever**: Busca conhecimento técnico se houver dúvidas.
3.  **Executor**: Prepara ações (Jira/Slack) e extrai parâmetros (Slot Filling).
4.  **Responder**: Sintetiza a resposta final em linguagem natural.

## 🐞 Modo Debug (Developer Mode)

Para desenvolvedores e auditores, o Treq expõe seu "sistema nervoso" através do Modo Debug.

### Como Ativar
- **Atalho**: Pressione `Ctrl + Shift + D` em qualquer tela de chat.
- **Interface**: Clique no ícone de "Raio" (`Zap`) no canto inferior direito.

### Funcionalidades do Debug
- **Real-time Thought**: Exibição do pensamento bruto do agente enquanto ele "decide" o que fazer.
- **Execution Timeline**: Uma trilha visual (`ThoughtTimeline`) mostrando cada nó do grafo percorrido, com tempos de execução e payloads JSON de entrada/saída.
- **Trace Context**: Identificação visual do estado atual (EX: `PLANEJANDO`, `RECURSANDO`, `EXECUTANDO`).

## 🛠️ Modais de Ação (Aprovações)

Ações que alteram dados externos (Criar Ticket Jira, Enviar Slack) agora exigem validação humana por padrão.

### Fluxo de Trabalho
1. Quando o agente decide por uma ação, ele exibe o card: **"Ação automatizada disponível. Deseja revisar?"**.
2. Ao clicar em **"REVISAR E EXECUTAR"**, abre-se um modal interativo.
3. **Slot Filling**: O modal inicia pré-preenchido com os dados que a IA extraiu da sua conversa.
4. **Edição**: Você pode ajustar o título, descrição ou canal antes de confirmar.
5. **Execução Manual**: A confirmação dispara o endpoint `/agent/tools/execute`, que realiza a chamada final com os dados validados por você.

## 📝 Auditoria e Segurança
- Todos os passos do agente são registrados no campo `execution_trace`.
- Ações manuais via modais são logadas com o prefixo `MANUAL_EXECUTE_TOOL`.
- A identidade visual do sistema preserva o nome **Treq**, ocultando termos técnicos internos (planner, node, executor) da resposta final do usuário comum.

---
*Documentação atualizada em: 18 de Janeiro de 2026*
