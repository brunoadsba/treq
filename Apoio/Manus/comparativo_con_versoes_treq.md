# Comparativo de Inteligência: Treq Chat vs. Treq Agente

Este documento explica constrastes entre as duas versões do sistema apresentadas nas imagens, focando na evolução da inteligência por trás da interface.

## 1. O Que Se Vê (Frontend)

| **Imagem 1: Treq Chat (Interface Legado)** | **Imagem 2: Treq Agente (Nova Versão)** |
| :--- | :--- |
| **Foco em Consulta:** Possui muitos botões de atalho no topo ("Alertas", "Status", "Procedimentos"). É desenhado para quem precisa *buscar* uma informação rápida. | **Foco em Ação:** Interface limpa e minimalista. Não oferece atalhos fixos porque o Agente é capaz de entender *qualquer* pedido, sem precisar de botões pré-definidos. |
| **Estático:** A experiência é sempre "Pergunta e Resposta". | **Dinâmico:** A interface reage ao que acontece (se o agente está "pensando", "usando uma ferramenta" ou "escrevendo"). |

---

## 2. O Que Acontece "Por Trás" (Backend & Cérebro)

A diferença real não está nas cores, mas em como o sistema "pensa".

### 🧠 Treq Chat (Modelo RAG Tradicional)
**Como funciona:** Pense num **Bibliotecário muito eficiente**.
1. Você faz uma pergunta.
2. Ele corre até a estante (Base de Dados), pega os livros (Documentos/Manuais) que falam sobre o assunto.
3. Ele lê os trechos e resume a resposta para você.

**Limitação:** Ele só sabe *ler e responder*. Se você disser "Abra um chamado técnico", ele vai responder: "Desculpe, eu sou apenas um modelo de linguagem, não consigo acessar sistemas externos". Ele é **Passivo**.

### 🤖 Treq Agente (Modelo Agêntico / LangGraph)
**Como funciona:** Pense num **Analista Operacional Sênior**.
1. Você faz um pedido (que pode ser vago).
2. Ele **Planeja**: "Para resolver isso, primeiro preciso consultar o manual, e se for grave, preciso avisar o gerente".
3. Ele **Executa Ações**: Ele tem "braços". Ele consegue conectar no Jira para criar tickets ou no Slack para mandar mensagens.
4. Ele **Decide**: Se a primeira tentativa de resposta for ruim, ele pode tentar de novo ou buscar outra fonte, sem você pedir.

**Diferencial:** Ele é **Ativo**. Ele não apenas lê sobre o problema, ele pode ajudar a resolver o problema executando tarefas no mundo real.

---

## 3. Resumo das Capacidades

| Funcionalidade | Treq Chat (Legado) | Treq Agente (Enterprise) |
| :--- | :---: | :---: |
| **Consultar Manuais** | ✅ Sim | ✅ Sim |
| **Responder Dúvidas** | ✅ Sim | ✅ Sim |
| **Raciocínio Complexo** | ❌ Não (apenas resume) | ✅ Sim (planeja passos) |
| **Criar Tickets (Jira)** | ❌ Não | ✅ Sim |
| **Notificar Equipe (Slack)** | ❌ Não | ✅ Sim |
| **Memória da Conversa** | ⚠️ Limitada | ✅ Contínua |

## Conclusão

A **Imagem 1** representa um sistema de **Busca Inteligente**.
A **Imagem 2** representa um **Membro Digital da Equipe**.
