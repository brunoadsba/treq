# Guia Prático para Replicar o "Get Shit Done" (GSD) em Qualquer IDE

O GSD (Get Shit Done) é um sistema de meta-prompting originalmente criado para o Claude, focado em manter a alta qualidade do código gerado por IA em tarefas longas e complexas. Seus princípios, no entanto, são universais e podem ser aplicados em qualquer ambiente de desenvolvimento moderno, como o VS Code com extensões (GitHub Copilot, Continue.dev) ou JetBrains IDEs.

Este guia mostra como aplicar os três pilares do GSD:

1.  **Commits Atômicos:** A base para um projeto gerenciável.
2.  **Contexto Limpo:** A chave para evitar a degradação da IA.
3.  **Subagentes Isolados:** A estratégia para executar tarefas complexas com precisão.

---

## 1. Commits Atômicos: A Base de Tudo

**Princípio:** Cada commit no seu histórico do Git deve representar a **menor mudança lógica possível**. Nunca faça um commit de toda a saída da IA de uma só vez.

**Por que é crucial?**
*   **Revisão de Código:** Commits pequenos e focados são fáceis de revisar.
*   **Reversão Segura:** Permite reverter bugs sem afetar outras funcionalidades.
*   **Histórico Claro:** Transforma seu `git log` em uma documentação viva do projeto.

**Como implementar na prática:**
1.  **Commit de Ponto de Verificação:** Antes de pedir uma grande mudança à IA, faça um commit do seu trabalho atual.
    ```bash
    git commit -m "WIP: antes de refatorar o serviço de autenticação"
    ```
2.  **Divida a Saída da IA:** Trate o código gerado como um rascunho. Se a IA gerou uma nova classe, testes e uma interface, divida em três commits separados.
3.  **Use o Staging Interativo:** A ferramenta `git add -p` (ou a interface de "Source Control" do VS Code) é sua melhor amiga. Ela permite adicionar pequenas partes de um arquivo de cada vez.
4.  **Escreva Mensagens Claras:** Siga um padrão como o [Conventional Commits](https://www.conventionalcommits.org/ ) para dar semântica ao seu histórico.
    *   `feat(auth): adiciona método de login com Google`
    *   `fix(api): corrige tratamento de erro em endpoint de usuário`
    *   `test(auth): adiciona testes de unidade para o serviço de autenticação`

---

## 2. Contexto Limpo e Subagentes Isolados

**Princípio:** Evite a "degradação de contexto" (quando a IA se confunde com um histórico de chat longo) isolando cada tarefa em uma sessão de chat limpa e com um prompt focado. Pense nisso como criar "subagentes" temporários para cada tarefa.

**Como implementar na prática:**

A ideia é separar as fases de **Pesquisa**, **Planejamento** e **Implementação**.

**Método 1: Usando Múltiplas Janelas de Chat (Universal)**

1.  **Agente de Pesquisa (Janela 1):**
    *   **Objetivo:** Identificar os arquivos e o código relevantes.
    *   **Prompt Exemplo:** `"Preciso implementar a funcionalidade X. Analise o workspace @workspace e me diga quais arquivos preciso modificar e quais padrões de código existentes devo seguir."`

2.  **Agente de Planejamento (Janela 2 - NOVA):**
    *   **Objetivo:** Criar um plano de ação sem escrever código.
    *   **Prompt Exemplo:** `"@file:arquivo1.ts @file:arquivo2.ts Crie um plano passo a passo para implementar a funcionalidade X com base nestes arquivos. Não escreva o código ainda."`

3.  **Agente de Implementação (Janela 3 - NOVA ou por passo):**
    *   **Objetivo:** Executar um único passo do plano.
    *   **Prompt Exemplo:** `"Com base no @file:arquivo1.ts, execute o passo 1 do plano: 'Adicionar o método Y na classe Z'."`

**Método 2: Usando Ferramentas Nativas (VS Code / Continue.dev)**

*   **Agentes Customizados (`.agent.md`):** No VS Code, você pode definir agentes com instruções e capacidades específicas (ex: um agente `/test` que só sabe escrever testes).
*   **Slash Commands (`/`):** Em extensões como Continue.dev, crie comandos customizados (`/refactor`, `/docs`) que executam um prompt pré-definido sobre o código selecionado (`@selection`).
*   **Context Providers (`@`):** Use `@workspace`, `@file`, `@terminal` para fornecer à IA apenas o contexto estritamente necessário para a tarefa.

---

## Workflow Prático: Exemplo Completo

**Objetivo:** Adicionar login com Google a um aplicativo existente.

1.  **Commit de Segurança:**
    ```bash
    git commit -m "WIP: antes de iniciar a implementação do login com Google"
    ```

2.  **Fase de Pesquisa (Chat 1):**
    *   **Você:** `"Analise o @workspace e identifique os arquivos necessários para adicionar um novo provedor de OAuth."`
    *   **IA:** Retorna `auth.service.ts`, `user.model.ts`, `config.ts`.

3.  **Fase de Planejamento (Chat 2):**
    *   **Você:** `"@file:auth.service.ts @file:user.model.ts @file:config.ts Crie um plano para adicionar o login com Google."`
    *   **IA:** Gera um plano de 5 passos.

4.  **Fase de Implementação (Passo a Passo e com Commits Atômicos):**
    *   **Você (Chat 3):** `"Execute o Passo 1: Adicione as variáveis GOOGLE_CLIENT_ID e GOOGLE_CLIENT_SECRET ao @file:config.ts"`
    *   **IA:** Gera o código.
    *   **Você:** Revisa o código e faz o commit.
        ```bash
        git add config.ts
        git commit -m "feat(auth): adiciona variáveis de ambiente para Google OAuth"
        ```
    *   **Você (Chat 4):** `"Execute o Passo 2: Atualize o @file:user.model.ts para incluir um campo opcional 'googleId'."`
    *   **IA:** Gera o código.
    *   **Você:** Revisa e faz o commit.
        ```bash
        git add user.model.ts
        git commit -m "feat(auth): atualiza modelo de usuário com googleId"
        ```
    *   ...e assim por diante, até que todos os passos do plano sejam concluídos e commitados individualmente.

Adotar este fluxo de trabalho exige disciplina, mas resulta em um código de maior qualidade, um histórico de projeto mais limpo e um processo de desenvolvimento muito mais robusto e menos propenso a erros.
