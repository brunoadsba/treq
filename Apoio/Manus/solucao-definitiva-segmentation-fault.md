# Solução Definitiva: Segmentation Fault no WSL2 (Ambiente TREQ)

Este documento descreve o diagnóstico técnico e o passo a passo da solução para os erros de `Segmentation fault (core dumped)` encontrados no desenvolvimento do backend.

## 1. O Problema
Durante a execução do servidor FastAPI (Uvicorn) e testes E2E, o processo terminava abruptamente com `Segmentation fault`. O erro ocorria de forma intermitente, mas tornava-se fatal ao carregar módulos do LangChain ou ao iniciar o loop de eventos assíncronos.

### O que causa isso?
Em ambientes Python, um *Segmentation Fault* quase sempre ocorre em **extensões compiladas (C/C++/Rust)**, e não no código Python puro. No contexto do WSL2, os principais causadores são:
1.  **Incompatibilidade de Syscalls**: Bibliotecas como `uvloop` tentam usar chamadas de sistema Linux de baixa latência que o kernel do WSL2 nem sempre emula com 100% de fidelidade, resultando em acessos de memória inválidos.
2.  **Multiprocessamento e Threads no Loguru**: O parâmetro `enqueue=True` do Loguru cria filas de processamento que, em certas versões do Python (como a 3.12 no WSL2), causam conflitos de memória ao tentar compartilhar contextos C entre threads.
3.  **Conflito de ABI (Application Binary Interface)**: Versões muito recentes do Python (3.12) combinadas com extensões binárias (`pydantic-core`, `psycopg2-binary`) podem ter incompatibilidades com as bibliotecas de sistema (`glibc`) distribuídas no Ubuntu do WSL2.

---

## 2. Passo a Passo da Solução Implementada

Para resolver o problema sem sacrificar a funcionalidade, adotamos uma estratégia de "estabilização de infraestrutura":

### Passo 1: Reversão para Versão Estável do Python
Embora o projeto suporte 3.12, o ambiente virtual em `/venv` (Python 3.11) demonstrou ser significativamente mais estável para os bindings do LangChain no WSL2.
- **Ação**: O servidor deve ser sempre iniciado usando o executável do venv: `/home/brunoadsba/treq/venv/bin/python`.

### Passo 2: Remoção do `uvloop`
O `uvloop` é uma biblioteca de performance que substitui o loop padrão do Python. No WSL2, ela é o principal vetor de instabilidade.
- **Ação**: Removemos `uvicorn[standard]` (que traz o uvloop) e instalamos apenas `uvicorn`. Nas configurações de execução, forçamos o uso do loop padrão: `--loop asyncio`.

### Passo 3: Safe Logging (Loguru)
Desativamos a complexidade de threads de rede/arquivo durante o logging.
- **Ação**: No arquivo `backend/app/main.py`, alteramos `logger.add(..., enqueue=False)`. Isso torna o log síncrono, protegendo a memória do processo contra condições de corrida fatais.

### Passo 4: Redirecionamento de Stream
Alguns crashes no WSL2 ocorrem devido ao buffering do `stdout` ao lidar com caracteres especiais de bibliotecas como `rich` ou `loguru`.
- **Ação**: Redirecionamos o log principal para `sys.stderr`, que possui um flushing mais agressivo e menos buffering de sistema.

### Passo 5: Pinagem de Dependências Críticas
Fixamos versões que possuem binários (wheels) estáveis para Linux x86_64:
- `pydantic==2.9.2`
- `numpy==1.26.4` (evitando a V2 que quebra compatibilidade com versões antigas do LangChain).

---

## 3. Como Manter o Ambiente Estável
Para evitar o retorno deste erro, siga estas diretrizes:
1.  **Nunca use `uvloop`** em desenvolvimento no WSL2.
2.  **Mantenha logs simples** (sem processamento em background via `enqueue=True`).
3.  **Use o binário do Python do venv (/venv/bin/python)** para garantir que as bibliotecas compiladas correspondam à versão correta do interpretador.
