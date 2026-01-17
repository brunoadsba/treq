# Diagnóstico Técnico: Segmentation Fault no Ambiente WSL2 (TREQ)

## 1. Visão Geral
Este documento detalha a causa raiz, os sintomas e as mitigações aplicadas para o erro `Segmentation fault (core dumped)` que paralisou o desenvolvimento do Backend no ambiente local (WSL2 + Python 3.12).

## 2. Sintomas Observados
O erro manifesta-se em três cenários críticos:
1. **Inicialização do Uvicorn:** Falha imediata ao tentar subir o servidor FastAPI.
2. **Execução de Testes Unitários:** Falha ao carregar módulos do LangChain ou LangGraph.
3. **Módulos de Avaliação:** Falha ao processar logs assíncronos via Loguru.

### Stack Trace Relevante (via faulthandler):
```text
Fatal Python error: Segmentation fault
Thread 0x... (most recent call first):
  File "/usr/lib/python3.12/multiprocessing/connection.py", line 395 in _recv
  File "/home/brunoadsba/.local/lib/python3.12/site-packages/loguru/_handler.py", line 300 in _queued_writer
...
Current thread 0x... (most recent call first):
  File "/home/brunoadsba/.local/lib/python3.12/site-packages/uvicorn/main.py", line 594 in run
```

## 3. Causa Raiz
A investigação aponta para um conflito de **Binary Extensions (C-Extensions)** compiladas que tentam acessar recursos de memória ou registradores de CPU bloqueados ou mal mapeados pelo kernel do WSL2.

### Bibliotecas Envolvidas:
- **`loguru` (enqueue=True):** Usa threads e filas de multiprocessamento. O crash ocorre especificamente no `_queued_writer`.
- **`uvloop`:** Substituição do loop de eventos padrão do asyncio. É conhecido por causar instabilidade no WSL2 devido a chamadas de sistema (syscalls) específicas do Linux que o subsistema Windows às vezes não emula perfeitamente.
- **`pydantic-core` (Rust extension):** A validação de esquemas complexos do LangChain/LangGraph exige alta performance e acessos diretos que podem causar falhas se houver incompatibilidade de versões de GLIBC entre o binário compilado e o sistema.
- **`psycopg` (v3):** O driver C exige a `libpq` atualizada, gerando conflitos com as versões binárias já instaladas do `psycopg2`.

## 4. Soluções e Mitigações

### 4.1. Removidas Bibliotecas Instáveis
- **`uvloop` desinstalado:** O Uvicorn agora utiliza o loop de eventos padrão do `asyncio`. Isso reduz a performance teórica, mas garante a estabilidade no Windows/WSL2.
- **`langchain-postgres` evitado:** Reversão para `langchain-community.vectorstores.PGVector` para manter compatibilidade com o driver `psycopg2-binary`, que é mais resiliente no WSL.

### 4.2. Ajustes de Configuração
- **Loguru (Safe Mode):** Desativada a opção `enqueue=True` em ambientes de desenvolvimento onde o multiprocessamento falha.
- **Pydantic Validation:** Adicionado campo `database_url` explicitamente na classe `Settings` para evitar erros de validação que forçavam o Pydantic a percorrer árvores de objetos complexas (o que às vezes acionava o segfault).

### 4.3. Pinagem de Versões
Forçamos versões específicas que comprovadamente funcionam juntas no WSL2 Ubuntu:
- `pydantic==2.9.2`
- `numpy==1.26.4` (Versões 2.x do NumPy causaram quebras em dependências do LangChain).

## 5. Próximos Passos
> [!IMPORTANT]
> Se o erro persistir em produção (Render), deve-se verificar se o `/etc/security/limits.conf` do container está restringindo o stack size.
> Para desenvolvimento local, recomenda-se o uso de **Containers Docker** (devcontainers) para isolar completamente os bindings C do sistema host Windows.
