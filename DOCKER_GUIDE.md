# 🐳 Guia Rápido: Treq Docker (Local)

Este guia contém os comandos essenciais para gerenciar o ambiente Docker do Treq Enterprise.

## 🚀 Comandos de Inicialização

| Comando | Descrição |
|---------|-----------|
| `docker compose up -d` | Sobe todos os serviços em background (Nginx, FE, BE, Redis). |
| `docker compose up -d --build` | Força o rebuild das imagens e sobe os containers (use após mudar o `requirements.txt`). |
| `docker compose stop` | Para os containers sem removê-los. |
| `docker compose down` | Para e **remove** os containers e redes (limpeza). |

## Estratégia de Build (Multistage)
O projeto utiliza um `Dockerfile` multistage parra o frontend:
- **development**: Focado em produtividade, com `npm run dev` e volumes mapeados para hot-reload.
- **runner (production)**: Focado em estabilidade, utiliza o modo `standalone` do Next.js (servidor Node.js otimizado) para servir os arquivos compilados.

## Comandos Essenciais

### 1. Iniciar Ambiente de Produção
Recomendado para testes de integração e validação final:
```bash
docker compose up -d --build
```

### 2. Iniciar Ambiente de Desenvolvimento (Hot-reload)
Permite que alterações no código local reflitam instantaneamente no container:
```bash
# O docker-compose.override.yml já está configurado para o target 'development'
docker compose up -d frontend
```

### 3. Limpeza de Cache Crítica
Se encontrar erros de permissão (`EACCES`) ou arquivos ausentes no Next.js:
```bash
sudo rm -rf frontend/.next frontend/node_modules
docker compose down -v
docker compose up -d --build
```

## Troubleshooting
- **Portas**: O sistema concentra o tráfego na porta **80 (Nginx)**. O Frontend responde diretamente na **3000** para debug.
- **Login**: Se receber erro 401 ou Internal Server Error, verifique se o token JWT foi gerado no login e se as variáveis `JWT_SECRET_KEY` estão sincronizadas entre `backend/.env` e raiz `.env`.

## 📊 Monitoramento e Logs

| Comando | Descrição |
|---------|-----------|
| `docker ps` | Lista os containers rodando e suas portas. |
| `docker compose logs -f` | Logs de todos os serviços em tempo real. |
| `docker compose logs -f backend` | Logs apenas do Backend. |
| `docker compose logs -f frontend` | Logs apenas do Frontend. |

## 🛠️ Interação e Debug

| Comando | Descrição |
|---------|-----------|
| `docker compose exec backend bash` | Abre um terminal dentro do container do Backend. |
| `docker compose restart backend` | Reinicia apenas o serviço de Backend. |
| `docker compose exec backend python scripts/audit_check_critical.py` | Executa o script de auditoria no ambiente correto. |

## 🧹 Limpeza de Cache (Se algo der errado)

| Comando | Descrição |
|---------|-----------|
| `docker system prune -f` | Remove containers parados e imagens sem uso. |
| `docker volume prune -f` | Remove volumes (CUIDADO: remove dados do Redis/Postgres local). |

---

**Nota:** Garanta que seu arquivo `.env` na raiz esteja sempre atualizado com as chaves reais.

## 7. Autenticação (Desenvolvimento)
Para acesso local em ambiente de teste:
- **Usuário**: `admin`
- **Senha**: `admin123`
