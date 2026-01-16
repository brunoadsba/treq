# Comandos e Informações Essenciais do Dia-a-Dia
## WSL + Cursor + GLM-4.7 + Goose CLI - Sistema Híbrido de Alta Performance

**Última Atualização:** 2026-01-10  
**Versão:** 1.0  
**Autor:** Bruno (especialista sênior em IA e infraestrutura)

---

## Índice

1. [Iniciar Novo Projeto](#1-iniciar-novo-projeto)
2. [Navegação e Arquivos](#2-navegação-e-arquivos)
3. [Git Operations](#3-git-operations)
4. [Agent Workflow](#4-agent-workflow)
5. [Goose CLI](#5-goose-cli)
6. [Aliases Úteis](#6-aliases-úteis)
7. [Troubleshooting](#7-troubleshooting)

---

## 1. Iniciar Novo Projeto

### Criar Estrutura Inicial

```bash
# 1. Criar diretório do projeto
cd ~/projects
mkdir meu-projeto
cd meu-projeto

# 2. Inicializar estrutura do agente
ainit

# 3. Validar ambiente
gvalidate

# 4. Definir objetivo
vim .agent/goal.md
```

### Inicializar Git

```bash
# Inicializar repositório
git init

# Configurar usuário (se ainda não configurado)
git config --global user.name "Seu Nome"
git config --global user.email "seu@email.com"

# Criar primeiro commit
git add .
git commit -m "Initial commit: Agente híbrido configurado"
```

### Criar Branch para Funcionalidade

```bash
# Criar branch
git checkout -b feature/nova-funcionalidade

# Ver branches
git branch -a
```

---

## 2. Navegação e Arquivos

### Verificar Estrutura do Projeto

```bash
# Árvore de diretórios (2 níveis)
tree -L 2

# Lista detalhada
ls -la

# Arquivos por tipo
find . -name "*.js" -o -name "*.ts" -o -name "*.py"
```

### Abrir Arquivos no Cursor

```bash
# Abrir projeto no Cursor
code .

# Abrir diretório .agent
code .agent/

# Abrir arquivo específico
code .agent/task.md
```

### Backup do Estado do Agente

```bash
# Backup do estado atual
cp -r .agent .agent-backup-$(date +%Y%m%d)

# Backup completo do projeto
tar -czf project-backup-$(date +%Y%m%d).tar.gz . --exclude='.git' --exclude='node_modules'
```

---

## 3. Git Operations

### Fluxo de Trabalho Diário

```bash
# 1. Verificar status
git status

# 2. Adicionar alterações
git add .
git add .agent/
git add src/

# 3. Commit com mensagem descritiva
git commit -m "feat: implementar funcionalidade X"

# 4. Push (se for remoto)
git push origin feature/nova-funcionalidade

# 5. Voltar para main
git checkout main
```

### Ver Histórico e Diff

```bash
# Ver histórico de commits
git log --oneline -10

# Diff de arquivo específico
git diff HEAD~1 src/main.js

# Diff entre branches
git diff main feature/nova-funcionalidade
```

### Resolver Conflitos

```bash
# Ver branches com merge
git branch --merged

# Rebase em branch
git rebase main

# Resolver conflito manualmente
git status
vim arquivo-com-conflito.js
git add arquivo-com-conflito.js
git rebase --continue
```

### Tags e Releases

```bash
# Criar tag de versão
git tag -a v1.0.0 -m "Versão 1.0.0"

# Push de tags
git push origin --tags

# Ver tags
git tag
```

---

## 4. Agent Workflow

### Iniciar Loop do Agente

```bash
# Iniciar loop principal
aloop

# Ou executar script diretamente
./agent-loop-hybrid.sh

# Aquecer contexto antes
gwarm
```

### Verificar Estado do Agente

```bash
# Ver estado atual
astate

# Ver plano de execução
aplan

# Ver tarefa atual
atask

# Ver objetivo imutável
agoal

# Ver protocolo de operação
arules

# Verificar conclusão ou bloqueio
gcheck

# Ver estatísticas
gstats
```

### Atualizar Estado do Agente

```bash
# Aquecer contexto
gwarm

# Validar ambiente
gvalidate

# Atualizar state.md manualmente
vim .agent/state.md

# Atualizar plan.md manualmente
vim .agent/plan.md

# Atualizar task.md manualmente
vim .agent/task.md
```

### Resetar Agente (se necessário)

```bash
# Backup do estado
cp -r .agent .agent-backup-$(date +%Y%m%d)

# Resetar state e task
cat > .agent/state.md << 'EOF'
# Estado do Projeto

Projeto resetado. Aguardando nova tarefa.

## Última Atualização
[10/01/2026 14:30]

## Bloqueios
- Nenhum
EOF

cat > .agent/task.md << 'EOF'
# Tarefa Atual

Analisar estado atual do projeto e criar plano.
EOF
```

---

## 5. Goose CLI

### Iniciar Sessão com System Prompt

```bash
# Sessão com prompt otimizado
gplan

# Ou comando direto
goose session --system .agent/harness.txt
```

### Executar Tarefa Específica

```bash
# Análise de código
goose run --system .agent/harness.txt --instructions "Analise src/main.py em busca de vulnerabilidades de segurança"

# Testes automatizados
goose run --system .agent/harness.txt --instructions "Execute pytest com coverage. Gere relatório HTML."

# Refatoração em massa
goose run --system .agent/harness.txt --instructions "Refatore todos arquivos .ts em src/ para seguir PEP8/ESLint."
```

### Debug e Troubleshooting

```bash
# Ver versão
goose --version

# Ver configuração
goose info

# Testar API diretamente
OPENAI_API_KEY="sua-chave" OPENAI_HOST="https://api.z.ai" OPENAI_BASE_PATH="api/coding/paas/v4" goose run --text "Teste!"

# Limpar cache do Goose
rm -rf ~/.local/state/goose/*
rm -rf ~/.local/share/goose/sessions/*
```

---

## 6. Aliases Úteis

### Aliases do Agente

```bash
ainit     # Criar estrutura do agente
aloop     # Iniciar loop do agente
astate    # Ver estado atual
aplan     # Ver plano de execução
atask     # Ver tarefa atual
agoal     # Ver objetivo imutável
arules    # Ver protocolo de operação
aedit     # Abrir .agent/ no Cursor
```

### Aliases Híbridos

```bash
gplan     # Iniciar sessão Goose com system prompt
gwarm     # Aquecer contexto
gvalidate  # Validar ambiente WSL
gsubagent  # Executar subtarefa via Goose
gcheck     # Verificar conclusão/bloqueio
gstats     # Ver estatísticas de tarefas
```

### Adicionar Novos Aliases

```bash
# Editar .bashrc
vim ~/.bashrc

# Adicionar alias
alias meu-novo-alias='comando-completo'

# Recarregar .bashrc
source ~/.bashrc

# Ver aliases configurados
alias
```

---

## 7. Troubleshooting

### Problemas do Cursor

#### Cursor não conecta ao WSL

```bash
# Verificar status do WSL
wsl --list --verbose

# Reiniciar WSL
wsl --shutdown
wsl

# No Cursor: Ctrl+Shift+P → "WSL: Reconnect"
```

#### Performance Lenta

```bash
# Ver localização de arquivos
pwd

# Se estiver em /mnt/c/, mover para /home/
mv /mnt/c/Users/Bruno/projeto ~/projects/

# Ver tamanho de node_modules
du -sh node_modules/
```

### Problemas do Agente

#### Loop travado em bloqueio

```bash
# Verificar state.md
cat .agent/state.md | grep "BLOQUEIO"

# Remover bloqueio
vim .agent/state.md
# Remova a linha de bloqueio e adicione resolução

# Continuar loop
aloop
```

#### Contexto não atualizando

```bash
# Verificar se context-cache.txt existe
ls -la .agent/context-cache.txt

# Regenerar
gwarm

# Ver timestamp
tail -n 5 .agent/context-cache.txt
```

### Problemas de Git

#### Merge conflicts

```bash
# Ver conflitos
git status

# Editar arquivos conflitantes
vim arquivo-com-conflito.js

# Marcar como resolvido
git add arquivo-com-conflito.js
git commit -m "fix: resolver conflitos de merge"
```

#### Commit com erro

```bash
# Desfazer último commit (mantendo alterações)
git reset --soft HEAD~1

# Desfazer completamente último commit
git reset --hard HEAD~1

# Desfazer múltiplos commits
git reset --hard HEAD~3
```

---

## 8. Comandos Essenciais do Dia-a-Dia

### Checklist Diário (Início do Dia)

```bash
# 1. Atualizar sistema
sudo apt update && sudo apt upgrade -y

# 2. Verificar projetos ativos
cd ~/projects
ls -la

# 3. Entrar no projeto
cd meu-projeto

# 4. Pull do branch atual
git pull origin main

# 5. Aquecer contexto
gwarm

# 6. Verificar estado do agente
gcheck
gstats

# 7. Iniciar trabalho
aloop
```

### Checklist Diário (Fim do Dia)

```bash
# 1. Commitar alterações
git add .
git commit -m "work: progresso do dia $(date +%Y-%m-%d)"

# 2. Push para remoto
git push origin feature/branch-atual

# 3. Backup do agente
cp -r .agent .agent-backup-$(date +%Y%m%d)

# 4. Validar ambiente
gvalidate

# 5. Relatório de progresso
echo "## Progresso do dia $(date +%Y-%m-%d)" >> .agent/logs/daily-$(date +%Y%m%d).log
echo "- Tarefas concluídas: $(grep -c "\[x\]" .agent/plan.md)" >> .agent/logs/daily-$(date +%Y%m%d).log
echo "- Blocos resolvidos: $(grep -c "BLOQUEIO RESOLVIDO" .agent/state.md)" >> .agent/logs/daily-$(date +%Y%m%d).log
```

---

## 9. Integração Rápida

### Comandos Mais Usados

```bash
# Criar novo projeto
cd ~/projects && mkdir novo-proj && cd novo-proj && ainit

# Iniciar workflow
cd meu-projeto && gwarm && aloop

# Ver status do dia
gcheck && gstats

# Commit diário
git add . && git commit -m "work: progresso do dia"

# Solução rápida de problemas
gvalidate && gwarm
```

---

## 10. Referência Rápida

| Situação | Comando |
|----------|----------|
| Criar projeto | `cd ~/projects && mkdir nome && cd nome && ainit` |
| Iniciar agente | `aloop` ou `./agent-loop-hybrid.sh` |
| Aquecer contexto | `gwarm` ou `./warm-context.sh` |
| Validar ambiente | `gvalidate` ou `./validate-wsl.sh` |
| Ver estado | `astate` ou `cat .agent/state.md` |
| Ver plano | `aplan` ou `cat .agent/plan.md` |
| Ver tarefa | `atask` ou `cat .agent/task.md` |
| Commit | `git add . && git commit -m "mensagem"` |
| Pull | `git pull origin main` |
| Push | `git push origin branch` |
| Abrir Cursor | `code .` ou `code .agent/` |
| Backup | `cp -r .agent .agent-backup-$(date +%Y%m%d)` |

---

**Nota:** Para instruções completas e detalhadas, consulte o [`stack-otimizada.md`](GuiaStack/stack-otimizada.md).

---

**Última Atualização:** 2026-01-10  
**Versão:** 1.0  
**Status:** ✅ Comandos essenciais organizados