# Relatório de Análise Crítica: Treq Enterprise (Sprint 4)

## 1. Análise da Imagem (Evidência)
A captura de tela mostra o seguinte comportamento:
- **Input do Usuário:** "oi"
- **Resposta do Agente:** Uma listagem de diretórios (`sotrec/`, `DADOS`, `ANÁLISE`, `DOCUMENTAÇÃO`) contendo arquivos como `Base_Operacional_Sotreq_Desafio.xlsx` e `analise_sotreq.ipynb`.

### Problemas Identificados (Críticos):
1.  **Violação de Marca (Rename Incompleto):** O termo "Sotreq" (e até "sotrec") aparece explicitamente na resposta. Isso prova que, embora tenhamos renomeado o código-fonte, **o conteúdo da Base de Conhecimento (RAG) continua sujo**. O agente está recuperando documentos legados do desafio técnico original.
2.  **Falha de Relevância (RAG Hallucination):** Para uma saudação simples ("oi"), o agente não deveria invocar metadados técnicos de estrutura de pastas. Isso indica que o **Prompt do Sistema** ou o **Retrieval** está mal calibrado, forçando contexto onde não é necessário, ou o "Greeting" não está sendo tratado pelo nível 1 do roteador (Llama 8B) corretamente, caindo num fallback RAG desnecessário.
3.  **Vazamento de Contexto Técnico:** A resposta expõe arquivos internos (`.ipynb`, `.parquet`, `roteiro_video`), o que quebra a imersão de um "Assistente Operacional" profissional.

---

## 2. Documentação vs. Realidade

| Característica | O que a Documentação Diz | O que a Realidade Mostra | Status |
| :--- | :--- | :--- | :--- |
| **Identidade** | "Assistente Operacional Treq" | Responde com dados da "Sotreq". | 🔴 FALHA |
| **Interação** | Chat natural e contextual. | Responde "oi" com uma árvore de arquivos XML/Markdown crua. | 🔴 FALHA |
| **Sanitização** | "Remover todas referências a Sotreq". | Referências abundantes encontradas no conteúdo recuperado. | 🔴 FALHA |
| **Governança** | "Filtragem de conteúdo sensível". | Vazamento de nomes de arquivos internos e estrutura de dados. | ⚠️ ALERTA |

---

## 3. Investigação e Oportunidades de Melhoria

### Falhas Raiz:
1.  **Dados do RAG não higienizados:** O script de rename (`replace_file_content`) atuou apenas no sistema de arquivos local (`backend/app`, `frontend/src`). Ele **não tocou** no banco de dados Supabase onde os chunks vetoriais estão armazenados.
2.  **Prompt System Inadequado:** O prompt provavelmente instrui o modelo a "usar o contexto recuperado" de forma muito agressiva, mesmo para saudações.
3.  **Falta de Roteamento de "Greeting":** O `llm_model_selector` deveria identificar "oi" como `greeting` e responder sem RAG.

### Plano de Correção (Necessário Aprovação):
1.  **Sanitização do Banco de Dados:** Executar um script SQL ou Python para fazer um `UPDATE` massivo na tabela `knowledge_base`, substituindo "Sotreq" por "Treq" no `content` e `metadata`.
2.  **Ajuste Fino do Prompt:** Modificar o System Prompt para ser mais conversacional em saudações e proibir listar arquivos internos a menos que explicitamente solicitado.
3.  **Revisão do Roteador:** Garantir que inputs curtos (< 5 chars) ou saudações não disparem busca vetorial.

---

## 4. Conclusão Parcial
O sistema **NÃO** está pronto para uso produtivo conforme documentado. A camada de aplicação (código) está correta, mas a camada de dados (conteúdo) compromete a identidade do produto. Precisa de intervenção imediata na base de dados.
