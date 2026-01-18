# Relatório de Erro: Tela de Login Inacesível no Ambiente Docker

Este documento detalha os problemas técnicos encontrados ao tentar implementar e acessar a nova tela de login no ambiente Treq Enterprise.

## 1. Descrição do Problema
Após a implementação da funcionalidade de autenticação JWT e da rota `/login`, o frontend falha ao renderizar a página, retornando **Internal Server Error (500)** ou uma página em branco, impedindo o acesso ao sistema.

## 2. Evidências Técnicas (Logs e Diagnósticos)

### A. Erro de Arquivos Ausentes no Runtime
Os logs do container `treq-frontend` mostram falhas críticas ao carregar metadados do Next.js:
```text
treq-frontend  | ⨯ [Error: ENOENT: no such file or directory, open '/app/.next/required-server-files.json'] {
treq-frontend  |   errno: -2,
treq-frontend  |   syscall: 'open',
treq-frontend  |   path: '/app/.next/required-server-files.json'
treq-frontend  | }
```
**Causa Relacionada:** Conflito de volumes. O mapeamento `./frontend:/app` no `docker-compose.yml` sobrepõe o diretório de trabalho do container, e a persistência de volumes para `.next` está mantendo estados inconsistentes entre o build e o runtime.

### B. Falha no Parse de CSS (Tailwind)
Ao tentar rodar em modo `dev` para depuração, o Next.js falha ao processar o arquivo global de estilos:
```text
treq-frontend  | ⨯ ./app/globals.css
treq-frontend  | Module parse failed: Unexpected character '@' (1:0)
treq-frontend  | > @tailwind base;
```
**Observação:** Isso sugere que as dependências de PostCSS/Tailwind ou a configuração do `next.config.js` não estão sendo aplicadas corretamente dentro do ambiente isolado do container.

### C. Conflito de Permissões (EACCES)
Testes automatizados via Playwright falham devido a permissões de escrita no sistema de arquivos mapeado:
```text
[WebServer] [Error: EACCES: permission denied, mkdir '/home/brunoadsba/treq/frontend/.next/cache']
```
**Causa:** Os arquivos dentro do container são gerados pelo usuário `nextjs` (UID 1001), enquanto o host tenta acessá-los com o usuário local, resultando em bloqueios de escrita na pasta `.next`.

## 3. Configuração do Ambiente Docker

O problema está concentrado no `docker-compose.yml` e `Dockerfile` do frontend:

1.  **Dockerfile Multistage:** Realiza build em produção, mas o `docker-compose.override.yml` estava tentando forçar um `npm start` sobre volumes mapeados do host que não continham o build atualizado.
2.  **Mapeamentos de Volume Atuais:**
    ```yaml
    volumes:
      - ./frontend:/app
      - /app/node_modules
      - /app/.next
    ```
    *   Este conjunto de volumes tenta isolar `node_modules` e `.next`, mas cria um "limbo" onde o código novo no host não reflete o build dentro do container sem um `--build` completo e limpeza manual de cache no host.

## 4. Tentativas de Correção Realizadas
1.  Execução de `docker compose up -d --build` para forçar recompilação.
2.  Mudança de `npm start` para `npm run dev` no override para tentar hot-reload (falhou devido ao erro de parse de CSS).
3.  Remoção manual da pasta `.next` no host para forçar regeneração.

## 5. Próximos Passos Sugeridos para o Desenvolvedor
1.  **Sincronização de UID/GID:** Ajustar o Dockerfile para usar o mesmo UID do host ou garantir que as permissões de volume permitam escrita em `.next`.
2.  **Limpeza de Estratégia de Volumes:** Avaliar se o mapeamento de `./frontend:/app` é necessário em todos os cenários ou se deve ser removido no modo de produção para usar o conteúdo interno da imagem.
3.  **Verificação de Configuração PostCSS:** Garantir que o `postcss.config.js` seja detectado corretamente pelo Next.js no container para evitar o erro de `@tailwind`.
