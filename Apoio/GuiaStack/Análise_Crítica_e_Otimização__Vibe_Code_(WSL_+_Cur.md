# Análise Crítica e Otimização: Vibe Code (WSL + Cursor + GLM-4.7)

Esta análise avalia o setup proposto para o uso do **Goose CLI** com o modelo **GLM-4.7**, integrando conceitos de "Harness" e diretrizes do Claude Code para um fluxo de trabalho de alta performance no **WSL** e **Cursor**.

---

## 1. Análise Crítica do Setup Atual

O setup original é sólido e utiliza boas práticas de engenharia de prompts. Abaixo, os pontos identificados:

### Pontos Fortes
*   **Estrutura de Planejamento**: A inclusão obrigatória de um modo `/plan` evita que o modelo comece a codificar sem entender o contexto completo.
*   **Modularidade**: O uso de subagentes e sessões paralelas no Goose é uma excelente forma de escalar tarefas complexas.
*   **Anti-Slop**: A preocupação com a estética e a redução de clichês de IA melhora a qualidade do código e da interface.

### Oportunidades de Melhoria
*   **Integração com Cursor**: O setup foca muito no Goose CLI, mas não explora como o **Cursor** (que já possui indexação de arquivos e terminal integrado) pode potencializar o GLM-4.7 via WSL.
*   **Contexto de Arquivos**: O uso de `INSTRUCTIONS.md` é bom, mas pode ser otimizado para que o modelo entenda a hierarquia do projeto automaticamente.
*   **Eficiência do GLM-4.7**: O modelo GLM-4.7 responde muito bem a instruções estruturadas em XML ou Markdown denso, o que pode ser mais explorado no Harness.

---

## 2. Vibe Code Otimizado (Harness v2.0)

Abaixo, apresento a versão ajustada do seu prompt de sistema, otimizada para o **GLM-4.7** e para o ambiente **WSL/Cursor**.

### Novo `~/harness_prompt.txt`

```markdown
Você é um Engenheiro de Software Principal (L6+) operando em ambiente WSL2.
Seu objetivo é entregar soluções prontas para produção com foco em performance e manutenibilidade.

### PROTOCOLO DE OPERAÇÃO (STRICT)

1. 🧠 PENSAMENTO ANALÍTICO (<thinking>)
   - Antes de qualquer ação, abra uma tag <thinking>.
   - Mapeie a árvore de dependências da tarefa.
   - Identifique potenciais conflitos com o ambiente WSL (permissões, caminhos de rede, etc.).

2. 🏗️ MODO ARQUITETO (/plan)
   - Liste todos os arquivos que serão criados ou modificados.
   - Defina o "Contrato de Interface" (APIs, Props, Schemas).
   - Valide se a solução respeita as restrições do projeto (ex: stack definida no Cursor).

3. 🛠️ EXECUÇÃO NO WSL
   - Prefira comandos `bash` diretos para exploração de arquivos.
   - Ao editar, use blocos de código precisos.
   - Sempre verifique a sintaxe com linters disponíveis no terminal antes de finalizar.

4. 🧪 CICLO DE FEEDBACK CURSOR
   - Após cada alteração significativa, sugira ao usuário o que verificar no editor Cursor (ex: "Verifique a definição de tipos no arquivo X").
   - Autocrítica: "Este código é idiomático para esta stack? Existe uma forma mais simples?"

### DIRETRIZES DE ESTILO (ANTI-SLOP)
- Respostas concisas e técnicas. Sem introduções genéricas.
- Estética: Código limpo, comentários apenas onde a lógica é complexa.
- Se a tarefa for ambígua, peça clarificação antes de agir.

Tarefa: [INSIRA AQUI]
```

---

## 3. Ajustes de Workflow e Dicas Adicionais

Para extrair o máximo do seu setup, considere estas otimizações:

| Categoria | Otimização Sugerida |
| :--- | :--- |
| **Integração Cursor** | Use o terminal do Cursor (Ctrl+`) para rodar o `goose session`. Isso permite que você veja as mudanças nos arquivos em tempo real enquanto a IA trabalha. |
| **Performance WSL** | Certifique-se de que seus projetos estão dentro do sistema de arquivos do Linux (`/home/ubuntu/...`) e não no `/mnt/c/...`, para evitar lentidão na indexação do Cursor e do Goose. |
| **GLM-4.7 Context** | O GLM-4.7 tem uma janela de contexto ampla. Ao iniciar uma sessão complexa, use `cat` para passar o conteúdo de arquivos cruciais logo no início para "aquecer" o contexto. |
| **Aliasing** | Adicione ao seu `.bashrc`: `alias gplan='goose session --system-prompt ~/harness_prompt.txt'`. Isso agiliza o início de novas tarefas. |

---

## 4. Próximos Passos Recomendados

1.  **Atualize seu arquivo de prompt**: Substitua o conteúdo do seu `~/harness_prompt.txt` pela versão otimizada acima.
2.  **Teste de Stress**: Tente uma tarefa de refatoração complexa usando o novo modo `<thinking>` para ver como o GLM-4.7 lida com a lógica.
3.  **Sincronia**: Use o `INSTRUCTIONS.md` especificamente para regras de negócio do projeto, deixando o `harness_prompt.txt` para regras de comportamento da IA.
