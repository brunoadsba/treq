# Guia Técnico: Soluções para Segmentation Faults em C-Extensions (psycopg/loguru) no WSL2

**Data:** 17 de Janeiro de 2026
**Autor:** Manus AI
**Contexto:** Mitigação de erros `Segmentation fault (core dumped)` em ambientes de desenvolvimento Python no WSL2 (Windows Subsystem for Linux), especificamente envolvendo bibliotecas com extensões C como `psycopg2`, `loguru` e *event loops* de alta performance como `uvloop`.

## 1. Diagnóstico e Causa Raiz (Padrão da Indústria)

O erro de *Segmentation Fault* (falha de segmentação) em bibliotecas Python que utilizam extensões C (C-Extensions) no WSL2 é um problema comum e bem documentado na comunidade de desenvolvimento. Ele geralmente ocorre devido a uma combinação de fatores:

1.  **Conflito de Binários (Shared Libraries):** Bibliotecas como `psycopg2-binary` empacotam suas próprias cópias de bibliotecas de sistema (como `libssl` e `libpq`) [1]. Em ambientes como o WSL2, onde o kernel Linux é emulado sobre o Windows, essas cópias podem entrar em conflito com as bibliotecas do sistema operacional hospedeiro ou com outras extensões C, especialmente em cenários de concorrência ou multiprocessamento.
2.  **Instabilidade em Chamadas de Sistema (Syscalls):** Componentes de alta performance como `uvloop` ou o mecanismo `enqueue=True` do `loguru` [2] dependem de chamadas de sistema de baixo nível (como `fork` ou manipulação de *file descriptors* e *pipes* de multiprocessamento) que podem não ser perfeitamente emuladas ou serem instáveis no kernel do WSL2.
3.  **Incompatibilidade de Versão:** A transição para novas versões do Python (ex: 3.12) ou de bibliotecas base (ex: NumPy 2.x, Pydantic 2.x) frequentemente expõe *bugs* ou incompatibilidades nas extensões C, que são mais sensíveis a mudanças no *ABI* (Application Binary Interface) do Python.

## 2. Soluções Possíveis e Nível de Maturidade

A tabela a seguir apresenta as soluções, categorizadas pelo seu nível de aderência aos padrões de produção e estabilidade da indústria.

| Solução | Descrição | Nível de Maturidade | Aplicação Recomendada |
| :--- | :--- | :--- | :--- |
| **1. Isolamento Total (Docker/DevContainers)** | Utilizar o Docker ou DevContainers (VS Code) para isolar o ambiente de desenvolvimento. O código é executado em um container Linux puro, eliminando a camada de emulação do WSL2. | **Best Practice (Padrão Ouro)** | Desenvolvimento Local e Pré-Produção. |
| **2. Build a partir do Código Fonte** | Instalar `psycopg` (v3) ou `psycopg2` (v2) **sem** o sufixo `-binary`. Isso força a compilação da biblioteca no ambiente WSL2, garantindo que ela use as bibliotecas de sistema (`libssl`, `libpq`) corretas e compatíveis. | **Standard Practice (Produção)** | Ambientes de Produção (Render, AWS, etc.) e Desenvolvimento Estável. |
| **3. Desativação de Features de Concorrência** | Desativar o uso de *event loops* de terceiros (`uvloop`) e o modo de *logging* assíncrono (`loguru` com `enqueue=True`). | **Quick Fix / Workaround** | Mitigação imediata para continuar o desenvolvimento. |
| **4. Pinagem de Versões Estáveis** | Fixar versões de bibliotecas críticas (ex: `pydantic`, `numpy`, `psycopg2-binary`) que são conhecidas por serem estáveis em uma determinada versão do Python/WSL2. | **Standard Practice (Manutenção)** | Controle de dependências para garantir a reprodutibilidade. |
| **5. Uso de Drivers Puros Python** | Em casos extremos, substituir o driver C (`psycopg`) por um driver puro Python (ex: `asyncpg` ou `psycopg2` com `pure-python` ativado), sacrificando performance por estabilidade. | **Last Resort / Niche** | Projetos com baixíssima carga de DB ou onde o *segfault* é irresolúvel. |

## 3. Detalhamento das Soluções Recomendadas

### 3.1. Solução Padrão Ouro: Isolamento com DevContainers

O uso de **DevContainers** (ou Docker Compose) é o padrão da indústria para garantir que o ambiente de desenvolvimento local seja idêntico ao ambiente de produção (Princípio *Dev/Prod Parity*).

**Ação:**
1.  Criar um arquivo `Dockerfile` e `.devcontainer/devcontainer.json`.
2.  Configurar o *container* para usar uma imagem base Linux (ex: `python:3.12-slim-bookworm`).
3.  Instalar as dependências do sistema (`libpq-dev`, `gcc`, etc.) no `Dockerfile` para permitir o *build* a partir do código fonte (Solução 3.2).
4.  Executar o projeto dentro do *container*.

**Comando Exemplo (Build from Source):**
```bash
# No Dockerfile ou script de setup do DevContainer
RUN apt-get update && apt-get install -y libpq-dev gcc
RUN pip install psycopg  # Instala a versão v3, que exige build
```

### 3.2. Solução Padrão de Produção: Build a partir do Código Fonte

Para ambientes de produção (como o Render, que é um Linux puro), a melhor prática é instalar a biblioteca sem o `-binary`, forçando a compilação.

**Ação:**
1.  Remover `psycopg2-binary` ou `psycopg-binary` do `requirements.txt`.
2.  Adicionar `psycopg` (v3) ou `psycopg2` (v2) sem o sufixo.
3.  Garantir que as dependências de *build* (`libpq-dev`, `gcc`, `python3-dev`) estejam instaladas no ambiente de *deploy*.

**Comando Exemplo (requirements.txt):**
```text
# Substituir psycopg2-binary por:
psycopg>=3.1.0  # Para a versão mais moderna
# OU
psycopg2>=2.9.0 # Para a versão 2.x, exigindo build
```

### 3.3. Soluções de Mitigação Imediata (Quick Fixes)

Estas são as soluções que já foram aplicadas no seu diagnóstico e são válidas para manter a estabilidade no WSL2, mas introduzem débito técnico ou reduzem a performance.

#### A. Loguru (Desativação de Concorrência)
O `enqueue=True` é o ponto de falha. Desativá-lo remove o *segfault* ao custo de tornar o *logging* bloqueante (o que pode afetar a latência do servidor).

**Ação:**
```python
# Antes:
# logger.add(sys.stderr, enqueue=True)

# Depois (Solução aplicada):
logger.add(sys.stderr, enqueue=False) 
```

#### B. Uvicorn (Remoção de uvloop)
`uvloop` é conhecido por ser instável em ambientes emulados. Reverter para o *event loop* padrão do Python (`asyncio`) é a solução mais segura.

**Ação:**
1.  Desinstalar `uvloop` (se instalado).
2.  Garantir que o Uvicorn não esteja configurado para usá-lo explicitamente.

#### C. Pinagem de Versões
A pinagem de versões é crucial para evitar regressões.

**Ação:**
Manter as versões fixadas no `requirements.txt` conforme o diagnóstico:
```text
pydantic==2.9.2
numpy==1.26.4
```

## 4. Referências

[1] Psycopg Documentation. *Installation: psycopg vs psycopg-binary*. Disponível em: [https://www.psycopg.org/docs/install.html](https://www.psycopg.org/docs/install.html)
[2] Loguru Documentation. *Logger: enqueue parameter*. Disponível em: [https://loguru.readthedocs.io/en/stable/api/logger.html](https://loguru.readthedocs.io/en/stable/api/logger.html)
[3] GitHub Issue. *Segfault in uvloop*. Disponível em: [https://github.com/MagicStack/uvloop/issues/706](https://github.com/MagicStack/uvloop/issues/706)
[4] Python Discuss. *Psycopg2 isnt working in python 3.12.0*. Disponível em: [https://discuss.python.org/t/psycopg2-isnt-working-in-python-3-12-0/35884](https://discuss.python.org/t/psycopg2-isnt-working-in-python-3-12-0/35884)
