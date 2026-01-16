# Configuração do Goose com GLM-4.7

## Resumo da Instalação

**Status:** ✅ Configurado e funcionando

**Data:** 2026-01-10

---

## Detalhes da Configuração

### API
- **Provider:** OpenAI-compatible
- **API Key:** `YOUR_GLM_API_KEY_HERE`
- **Endpoint:** `https://api.z.ai/api/coding/paas/v4`
- **Modelo:** `GLM-4.7`

### Variáveis de Ambiente
Adicionadas ao `~/.bashrc`:

```bash
export OPENAI_API_KEY="YOUR_GLM_API_KEY_HERE"
export OPENAI_HOST="https://api.z.ai"
export OPENAI_BASE_PATH="api/coding/paas/v4"
```

---

## Como Usar o Goose

### 1. Teste Rápido
```bash
# Teste via API direta
curl -X POST "https://api.z.ai/api/coding/paas/v4/chat/completions" \
-H "Content-Type: application/json" \
-H "Authorization: Bearer YOUR_GLM_API_KEY_HERE" \
-d '{
  "model": "GLM-4.7",
  "messages": [
    {"role": "user", "content": "Olá!"}
  ]
}'
```

### 2. Via Variáveis de Ambiente
```bash
# As variáveis já estão no ~/.bashrc
# Para recarregar:
source ~/.bashrc

# Iniciar sessão do Goose:
goose session
```

### 3. Script de Teste
```bash
# Script de teste criado em: ~/test-goose-glm.sh
~/test-goose-glm.sh
```

---

## Observações Importantes

### Endpoint Correto
O endpoint correto para a API do GLM-4.7 é:
- ✅ `https://api.z.ai/api/coding/paas/v4`
- ❌ `https://open.bigmodel.cn/api/paas/v4` (não funciona)

### Modelo GLM-4.7
O identificador correto do modelo é:
- ✅ `GLM-4.7` (com hífen)
- ❌ `glm-4-plus` ou `glm-4-flash` (não reconhecido)

---

## Integração com Cursor

O Cursor já está usando o GLM-4.7 através do servidor MCP local:

**Arquivo de Configuração MCP:**
```json
{
  "glm-4.7": {
    "command": "python",
    "args": [
      "/home/brunoadsba/estagio/mcp-glm-server/mcp_glm_server.py"
    ],
    "env": {
      "ZAI_API_KEY": "YOUR_GLM_API_KEY_HERE",
      "GLM_MODEL": "GLM-4.7"
    }
  }
}
```

---

## Troubleshooting

### Erro "No provider configured"
Assegure-se de que as variáveis de ambiente estão setadas:

```bash
echo $OPENAI_API_KEY
echo $OPENAI_HOST
echo $OPENAI_BASE_PATH
```

### Erro de Conexão
Verifique se o endpoint está correto:

```bash
# Deve ser:
https://api.z.ai/api/coding/paas/v4

# NÃO:
https://open.bigmodel.cn/api/paas/v4
```

---

## Comandos Úteis

```bash
# Ver configuração do Goose
goose info

# Verificar variáveis de ambiente
env | grep OPENAI

# Testar API via curl (com jq instalado)
curl -X POST "https://api.z.ai/api/coding/paas/v4/chat/completions" \
-H "Content-Type: application/json" \
-H "Authorization: Bearer $OPENAI_API_KEY" \
-d '{"model":"GLM-4.7","messages":[{"role":"user","content":"Teste"}]}' | jq .
```

---

**Última Atualização:** 2026-01-10
**Versão:** 1.0
