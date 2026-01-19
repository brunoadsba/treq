

# Para usar exatamente a v0.6.0
npx @neuralnomads/codenomad@0.6.0 --launch



Ou simplesmente (vai pegar a latest):
npx @neuralnomads/codenomad --launch


3. Se estiver usando a versão @dev (desenvolvimento)
npx @neuralnomads/codenomad@dev --launch


___________________________________________


# Guia Resumido: Configuração Profissional do **OpenCode + CodeNomad** (Janeiro 2026)

Para desenvolvimento pesado e profissional (projetos longos, agentic workflows com MiniMax M2.1), use o **CodeNomad** como interface principal sobre o **OpenCode CLI**.

### 1. Instale o OpenCode CLI (backend obrigatório)
- Site oficial: https://opencode.ai/
- Comando principal (recomendado):
  ```
  curl -fsSL https://opencode.ai/install | bash
  ```
- Alternativas:
  - `npm i -g opencode-ai`
  - `bun add -g opencode-ai`
  - macOS: `brew install opencode` (se disponível)
- Verifique: `opencode --version`
- Docs CLI: https://opencode.ai/docs/cli/

### 2. Instale o CodeNomad (interface profissional recomendada)
CodeNomad é o frontend avançado (multi-tabs, plan view, caching eficiente) que roda sobre o OpenCode.

**Opção A: Desktop Native App (melhor para uso diário pesado – mais rápido e estável)**
- Acesse releases: https://github.com/NeuralNomadsAI/CodeNomad/releases (ou forks como NomadArch se preferir enhancements)
- Baixe a versão mais recente para seu OS (macOS .app, Windows .exe, Linux .AppImage)
- Extraia e execute o aplicativo diretamente (duplo clique ou via terminal)

**Opção B: Modo Web Server (flexível, remoto/multi-device)**
- Requisitos: Node.js instalado
- Comando:
  ```
  npx @neuralnomads/codenomad --launch
  ```
- Abre automaticamente no browser (http://localhost:3000 ou similar)
- Para dev/experimental: `npx @neuralnomads/codenomad@dev --launch`

### 3. Configuração Inicial Profissional
1. Na primeira execução do CodeNomad → configure API keys.
2. **Modelo recomendado**: MiniMax M2.1 (melhor reliability agentic)
   - Via **OpenRouter** (mais fácil e barato): https://openrouter.ai/keys
     - Crie conta → gere API key → cole no CodeNomad
     - Modelo: "MiniMax M2" ou "minimax/minimax-m2"
   - Link modelo: https://openrouter.ai/minimax/minimax-m2
3. Ative MCP tools essenciais:
   - filesystem, shell, github, docker, websearch, playwright etc.
   - Corrija erros comuns reiniciando ou testando comandos manualmente.
4. Dicas pro:
   - Use multi-sessions/tabs por projeto
   - Maximize caching (sessões longas = custo quase zero)
   - Prefira background_task com agents especializados (explore, librarian)
   - Desktop native para 80% do tempo; web para remoto

Com isso, você tem o setup mais equilibrado, moderno e produtivo para dev profissional em 2026. Teste e ajuste conforme seu workflow!