# PLANO DE EXECUÇÃO: CHECKLIST DE VIABILIDADE
**Data:** 2026-01-17  
**Responsável:** Time de Desenvolvimento  
**Prazo:** 3 dias úteis

---

## OVERVIEW

Este documento detalha a execução dos **8 checks críticos** identificados na auditoria antes de iniciar o roadmap de 12 semanas.

**Objetivo:** Validar se a base de código atual suporta a implementação enterprise-grade planejada.

---

## FASE 1: PREPARAÇÃO DO AMBIENTE (2h)

### ETAPA 1.1: Setup de Scripts de Auditoria
```bash
# Da raiz do projeto Treq:
cd /caminho/para/treq

# Criar script de auditoria
cat > audit_check_critical.py << 'EOF'
[Conteúdo do artifact audit_check_1]
EOF

chmod +x audit_check_critical.py

# Criar script de teste RLS
mkdir -p backend/scripts
cat > backend/scripts/test_rls_real.py << 'EOF'
[Conteúdo do artifact test_rls_script]
EOF

chmod +x backend/scripts/test_rls_real.py
```

**Critério de Sucesso:**
- [ ] Scripts criados e executáveis
- [ ] Python 3.11 disponível no PATH

---

### ETAPA 1.2: Validar Variáveis de Ambiente
```bash
# Criar .env.test para validação
cat > .env.test << EOF
SUPABASE_URL=your_url_here
SUPABASE_ANON_KEY=your_anon_key_here
SUPABASE_SERVICE_KEY=your_service_key_here
GROQ_API_KEY=your_groq_key_here
GEMINI_API_KEY=your_gemini_key_here
JWT_SECRET_KEY=$(openssl rand -hex 32)
EOF

# Carregar variáveis
source .env.test
```

**Critério de Sucesso:**
- [ ] Todas as variáveis preenchidas
- [ ] JWT_SECRET_KEY gerado (64 caracteres hex)

---

## FASE 2: EXECUÇÃO DOS CHECKS (4h)

### CHECK 1: Auditoria Geral (30min)

**Comando:**
```bash
python3 audit_check_critical.py
```

**Saídas Esperadas:**

#### Cenário IDEAL (90%+ score):
```
✓ PASS | 1. Ambiente WSL2/Linux
✓ PASS | 2. RLS Supabase
✓ PASS | 3. SSOT Configuração
✓ PASS | 4. Mocks em Produção
✓ PASS | 5. Secrets Hardcoded
✓ PASS | 6. CI/CD GitHub Actions
✗ FAIL | 7. Autenticação OAuth2 (esperado se não implementado)
✗ FAIL | 8. Docker Setup (esperado se não implementado)

Score: 75.0%
⚠️ ATENÇÃO: Resolver falhas críticas antes de prosseguir
```

#### Cenário PROBLEMÁTICO (<70% score):
```
✗ FAIL | 1. Ambiente WSL2/Linux
      WSL2 detectado com problemas: psycopg3: [Errno...]
✗ FAIL | 2. RLS Supabase
      service_role key encontrado em 3 arquivos
...
Score: 37.5%
🔴 CRÍTICO: Sistema não está pronto para produção enterprise
```

**Ações Corretivas por Falha:**

| Falha | Ação Imediata | Tempo |
|-------|---------------|-------|
| WSL2 Problems | Executar Fase 3 (Dockerização) | 16h |
| RLS Broken | Executar CHECK 2 detalhado | 4h |
| SSOT Issues | Refatorar config.py | 8h |
| Mocks in Prod | Substituir por implementações reais | 24h |
| Secrets Hardcoded | Mover para .env e gitignore | 2h |
| No CI/CD | Executar Fase 4 (GitHub Actions) | 8h |

---

### CHECK 2: Validação de RLS (1h)

**Comando:**
```bash
python3 backend/scripts/test_rls_real.py
```

**Saídas Esperadas:**

#### APROVADO:
```
✓ PASS | Service Key Detection
      Nenhum uso de service_role em código de produção
✓ PASS | RLS Policies Exist
      5 políticas RLS ativas
✓ PASS | Cross-User Access Prevention
      RLS bloqueou acesso cross-user corretamente
✓ PASS | Authenticated Client Implementation
      Implementação encontrada em supabase.py
✓ PASS | JWT Generation for RLS
      JWT sendo gerado para Supabase

✅ RLS CONFIGURADO CORRETAMENTE
```

#### REPROVADO:
```
✗ FAIL | Service Key Detection
      service_role key usado em 3 arquivos de produção: graph.py
✗ FAIL | Cross-User Access Prevention
      CRÍTICO: Usuário anônimo conseguiu acessar dados de outro usuário!

❌ RLS NÃO CONFIGURADO
CRÍTICO: Sistema vulnerável a acesso cross-user
```

**Ação Corretiva se REPROVADO:**
```python
# ETAPA CORRETIVA 2.1: Implementar Client Autenticado
# backend/app/db/supabase.py

from supabase import create_client
from app.config import settings
import jwt
from datetime import datetime, timedelta

def get_user_supabase_client(user_id: str):
    """Cria client Supabase com RLS ativo para usuário específico"""
    
    # Gerar JWT para Supabase
    payload = {
        "sub": user_id,
        "role": "authenticated",
        "iat": datetime.utcnow(),
        "exp": datetime.utcnow() + timedelta(hours=1)
    }
    
    supabase_jwt = jwt.encode(
        payload,
        settings.JWT_SECRET_KEY.get_secret_value(),
        algorithm="HS256"
    )
    
    # Client com JWT (RESPEITA RLS)
    return create_client(
        settings.SUPABASE_URL,
        settings.SUPABASE_ANON_KEY,
        options={
            "headers": {
                "Authorization": f"Bearer {supabase_jwt}"
            }
        }
    )

# ETAPA CORRETIVA 2.2: Refatorar TODOS os usos
# backend/app/features/agent/nodes/retriever.py

from app.db.supabase import get_user_supabase_client

async def retriever_node(state: AuthenticatedState):
    user_id = state["user_id"]
    
    # ANTES (INSEGURO):
    # client = supabase_service  # ❌ Bypassa RLS
    
    # DEPOIS (SEGURO):
    client = get_user_supabase_client(user_id)  # ✅ Respeita RLS
    
    results = client.table("documents")\
        .select("*")\
        .execute()
```

**Tempo Estimado:** 12h se falhar

---

### CHECK 3: Decisão sobre WSL2 (2h)

**Análise Manual:**
```bash
# Testar imports problemáticos:
python3 -c "import psycopg; print('✅ psycopg3 OK')" || echo "❌ FALHOU"
python3 -c "import sentence_transformers; print('✅ sentence-transformers OK')" || echo "❌ FALHOU"

# Verificar versão do kernel WSL2:
uname -r  # Deve conter 'microsoft'

# Testar estabilidade (rodar por 5min):
cd backend
for i in {1..10}; do
    python -m pytest tests/test_rag.py || echo "FALHA #$i"
    sleep 30
done
```

**Critérios de Decisão:**

| Resultado | Decisão |
|-----------|---------|
| 0 falhas em 10 execuções | ✅ WSL2 estável, continuar |
| 1-3 falhas | ⚠️ Dockerizar (risco médio) |
| 4+ falhas | 🔴 Dockerizar OBRIGATÓRIO |

**Se Dockerização Necessária:**
→ Executar **FASE 3** completa (16h)

---

### CHECK 4: Validação de SSOT (30min)

**Comando:**
```bash
# Contar usos de getenv fora de config.py:
grep -r "os.getenv\|os.environ" backend/app/ \
  --exclude-dir=__pycache__ \
  --exclude="config.py" \
  | wc -l

# Resultado esperado: < 10
```

**Se > 15 ocorrências:**
```python
# ETAPA CORRETIVA 4.1: Centralizar config
# backend/app/config.py

from pydantic_settings import BaseSettings
from pydantic import SecretStr

class Settings(BaseSettings):
    # Database
    SUPABASE_URL: str
    SUPABASE_ANON_KEY: SecretStr
    SUPABASE_SERVICE_KEY: SecretStr
    
    # Redis
    REDIS_URL: str = "redis://localhost:6379/0"
    
    # LLM APIs
    GROQ_API_KEY: SecretStr
    GEMINI_API_KEY: SecretStr
    ZHIPU_API_KEY: SecretStr | None = None
    
    # Auth
    JWT_SECRET_KEY: SecretStr
    JWT_ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    
    # Observability
    LANGSMITH_API_KEY: SecretStr | None = None
    LANGSMITH_PROJECT: str = "treq-enterprise"
    
    class Config:
        env_file = ".env"
        case_sensitive = True

settings = Settings()

# ETAPA CORRETIVA 4.2: Substituir todos os usos
# ANTES:
# groq_key = os.getenv("GROQ_API_KEY")

# DEPOIS:
from app.config import settings
groq_key = settings.GROQ_API_KEY.get_secret_value()
```

**Tempo Estimado:** 8h se falhar

---

### CHECK 5: Identificação de Mocks (30min)

**Comando:**
```bash
# Procurar padrões de mock:
grep -r "mock\|Mock\|fake\|Fake" backend/app/features/connectors/ \
  --include="*.py" \
  | grep -v "test_"
```

**Se mocks encontrados:**
```python
# ETAPA CORRETIVA 5.1: Implementar Conector Real
# backend/app/features/connectors/confluence.py

from atlassian import Confluence

class ConfluenceConnector:
    def __init__(self):
        self.client = Confluence(
            url=settings.CONFLUENCE_URL,
            token=settings.CONFLUENCE_API_TOKEN.get_secret_value()
        )
    
    async def search(self, query: str, limit: int = 10):
        try:
            results = self.client.cql(
                f'text ~ "{query}"',
                limit=limit
            )
            
            return [
                {
                    "title": r["title"],
                    "content": r["body"]["storage"]["value"],
                    "url": r["_links"]["webui"]
                }
                for r in results.get("results", [])
            ]
        except Exception as e:
            logger.error(f"Confluence search failed: {e}")
            # Fallback gracioso
            return []
```

**Tempo Estimado:** 24h (3 dias) se mocks encontrados

---

### CHECK 6-8: Validações Rápidas (1h)

**Check 6: Secrets Hardcoded**
```bash
grep -r "sk-\|API.*=.*['\"]AI" backend/ --include="*.py"
# Resultado esperado: Nenhum match
```

**Check 7: CI/CD**
```bash
ls -la .github/workflows/*.yml
# Resultado esperado: Pelo menos 1 arquivo
```

**Check 8: Docker**
```bash
ls -la docker-compose.yml Dockerfile
# Resultado esperado: Ambos existem
```

---

## FASE 3: DOCKERIZAÇÃO (16h - SE NECESSÁRIO)

### DIA 1: Setup Básico (8h)

#### ETAPA 3.1: Criar Dockerfiles (3h)
```bash
# Backend
cat > backend/Dockerfile << 'EOF'
[Conteúdo do artifact backend_dockerfile]
EOF

# Frontend
cat > frontend/Dockerfile << 'EOF'
FROM node:18-alpine
WORKDIR /app
COPY package*.json ./
RUN npm ci
COPY . .
RUN npm run build
EXPOSE 3000
CMD ["npm", "start"]
EOF
```

#### ETAPA 3.2: Criar docker-compose.yml (2h)
```bash
cat > docker-compose.yml << 'EOF'
[Conteúdo do artifact docker_setup]
EOF
```

#### ETAPA 3.3: Criar Entrypoint (1h)
```bash
cat > backend/docker-entrypoint.sh << 'EOF'
[Conteúdo do artifact docker_entrypoint]
EOF
chmod +x backend/docker-entrypoint.sh
```

#### ETAPA 3.4: Testar Build (2h)
```bash
# Build imagens
docker-compose build

# Testar startup
docker-compose up -d

# Verificar saúde
curl http://localhost:8002/health
curl http://localhost:3000

# Ver logs
docker-compose logs -f backend
```

**Critérios de Sucesso:**
- [ ] Build sem erros
- [ ] Todos os serviços UP (backend, frontend, redis)
- [ ] /health retorna 200
- [ ] Logs sem erros críticos

---

### DIA 2: Testes e Ajustes (8h)

#### ETAPA 3.5: Configurar Hot Reload (3h)
```yaml
# docker-compose.override.yml (dev only)
services:
  backend:
    volumes:
      - ./backend:/app
    command: uvicorn app.main:app --reload --host 0.0.0.0
  
  frontend:
    volumes:
      - ./frontend:/app
      - /app/node_modules
    command: npm run dev
```

#### ETAPA 3.6: Rodar Testes (3h)
```bash
# Testes unitários dentro do container
docker-compose exec backend pytest tests/ -v

# Testes E2E
docker-compose exec frontend npm run test:e2e
```

#### ETAPA 3.7: Documentação (2h)
```markdown
# README.md - Adicionar seção Docker

## Desenvolvimento com Docker

### Setup Inicial
```bash
docker-compose up -d
```

### Rodar Testes
```bash
docker-compose exec backend pytest
```

### Logs
```bash
docker-compose logs -f backend
```
```

---

## FASE 4: CONFIGURAR CI/CD (8h - SE NECESSÁRIO)

### ETAPA 4.1: Criar Workflow do GitHub Actions (4h)
```bash
mkdir -p .github/workflows
cat > .github/workflows/ci-enterprise.yml << 'EOF'
[Conteúdo do artifact github_workflow]
EOF
```

### ETAPA 4.2: Configurar Secrets no GitHub (1h)
```bash
# Via interface GitHub:
# Settings > Secrets and variables > Actions > New repository secret

Secrets necessários:
- SUPABASE_URL
- SUPABASE_ANON_KEY
- GROQ_API_KEY
- SNYK_TOKEN (opcional)
- DOCKER_USERNAME
- DOCKER_PASSWORD
- SLACK_WEBHOOK_URL (opcional)
```

### ETAPA 4.3: Testar Pipeline (3h)
```bash
# Fazer commit para trigger:
git add .github/workflows/ci-enterprise.yml
git commit -m "ci: add enterprise CI/CD pipeline"
git push origin enterprise

# Acompanhar em:
# https://github.com/brunoadsba/treq/actions
```

---

## FASE 5: VALIDAÇÃO FINAL (2h)

### CHECKLIST DE APROVAÇÃO

```bash
# Executar novamente auditoria completa:
python3 audit_check_critical.py

# Score esperado: >= 90%
```

**Critérios de Aprovação:**
- [ ] Score auditoria >= 90%
- [ ] RLS 100% funcional
- [ ] Docker operacional (se aplicável)
- [ ] CI/CD passando
- [ ] Zero secrets hardcoded
- [ ] Documentação atualizada

**Se APROVADO:**
→ Criar branch `audit/enterprise-hardening`
→ Commitar todas as mudanças
→ Abrir PR para `enterprise`
→ **INICIAR ROADMAP DE 12 SEMANAS**

**Se REPROVADO:**
→ Resolver pendências críticas
→ Re-executar checklist
→ NÃO iniciar roadmap até aprovação

---

## CRONOGRAMA RESUMIDO

| Fase | Duração | Dependência |
|------|---------|-------------|
| 1. Preparação | 2h | Nenhuma |
| 2. Checks | 4h | Fase 1 |
| 3. Docker (condicional) | 16h | Check 3 falhar |
| 4. CI/CD (condicional) | 8h | Check 6 falhar |
| 5. Validação Final | 2h | Todas anteriores |

**Melhor caso:** 8h (sem Docker/CI pendências)  
**Caso realista:** 24h (Docker necessário)  
**Pior caso:** 32h (Docker + CI/CD + correções)

---

## PRÓXIMOS PASSOS APÓS APROVAÇÃO

1. **Criar branch de trabalho:**
   ```bash
   git checkout enterprise
   git pull origin enterprise
   git checkout -b audit/enterprise-hardening
   ```

2. **Iniciar FASE 1 do Roadmap:**
   - Semana 1: Autenticação OAuth2
   - Semana 2: Rate Limiting e Segurança de API

3. **Daily standups:**
   - Reportar progresso dos checks
   - Escalar bloqueadores imediatamente

---

**Responsável:** [Nome do Dev Lead]  
**Aprovador:** [Nome do CTO/Tech Lead]  
**Data de Início:** [Preencher]  
**Data Esperada de Conclusão:** [Início + 3 dias]