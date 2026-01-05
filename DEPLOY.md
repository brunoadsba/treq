# 🚀 Guia de Deploy - Treq no Render

## 📋 Pré-requisitos

Antes de começar, certifique-se de ter:
- [x] Conta no GitHub (repo já existe)
- [ ] Conta no [Render](https://render.com)
- [x] Código atualizado no GitHub
- [ ] API Keys configuradas

---

## 🔑 Passo 1: Configurar API Keys no Render

### 1.1. Criar conta no Render
1. Acesse: https://render.com
2. Clique em "Sign Up" ou "Login with GitHub"
3. Conecte sua conta do GitHub

### 1.2. Adicionar variáveis de ambiente

No painel do Render, vá em: **Dashboard** → **treq-backend** → **Environment**

Adicione as seguintes variáveis:

```bash
# Supabase
SUPABASE_URL=https://taidcwtolloreyxjvegi.supabase.co
SUPABASE_SERVICE_ROLE_KEY=eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...
SUPABASE_ANON_KEY=eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...

# Groq API
GROQ_API_KEY=gsk_wm5CTNbnVdgSvzy2U12kWGdyb3FY1KlrYayBtF8...

# Gemini API
GEMINI_API_KEY=AIzaSyBU2jCBTilyjPB-k6iNsoDcjHUo8lbRKzI

# Zhipu AI (opcional)
ZHIPU_API_KEY=5aa3fec9311446f6b692263f8146d47d.taZ20qQpNd2plDKB

# Configurações
LOG_LEVEL=INFO
```

---

## 📦 Passo 2: Deploy do Backend

### 2.1. Conectar repositório GitHub

1. No Render Dashboard, clique em **"New +"**
2. Selecione **"Web Service"**
3. Conecte seu repositório GitHub: `brunoadsba/treq`
4. Branch: `main`

### 2.2. Configurar o serviço

Preencha conforme abaixo:

| Campo | Valor |
|-------|-------|
| **Name** | treq-backend |
| **Environment** | Python 3 |
| **Region** | Oregon (us-west) |
| **Branch** | main |
| **Root Directory** | (deixe vazio) |
| **Build Command** | `pip install -r backend/requirements.txt` |
| **Start Command** | `cd backend && uvicorn app.main:app --host 0.0.0.0 --port $PORT` |

### 2.3. Plano

Selecione **"Free"** (sufficiente para MVP)

### 2.4. Environment Variables

Adicione as mesmas variáveis do Passo 1.

### 2.5. Deploy

Clique em **"Create Web Service"**

⏱️ **Tempo estimado:** 5-10 minutos

✅ **Se funcionar:** Seu backend estará em: `https://treq-backend.onrender.com`

---

## 🎨 Passo 3: Deploy do Frontend

### 3.1. Criar novo serviço

1. Clique em **"New +"** → **"Web Service"**
2. Selecione o MESMO repositório: `brunoadsba/treq`

### 3.2. Configurar

| Campo | Valor |
|-------|-------|
| **Name** | treq-frontend |
| **Environment** | Node |
| **Region** | Oregon (us-west) |
| **Branch** | main |
| **Root Directory** | (deixe vazio) |
| **Build Command** | `cd frontend && npm install && npm run build` |
| **Start Command** | `cd frontend && npm start` |

### 3.3. Environment Variables

```bash
NEXT_PUBLIC_API_URL=https://treq-backend.onrender.com
NODE_VERSION=18
```

### 3.4. Deploy

Clique em **"Create Web Service"**

⏱️ **Tempo estimado:** 3-5 minutos

✅ **Se funcionar:** Seu frontend estará em: `https://treq-frontend.onrender.com`

---

## 🔧 Passo 4: Testar Deploy

### 4.1. Verificar health check

```bash
curl https://treq-backend.onrender.com/health
```

Resposta esperada:
```json
{"status": "ok", "service": "treq-backend", "up": true}
```

### 4.2. Testar chat

```bash
curl -X POST https://treq-backend.onrender.com/chat/ \
  -H "Content-Type: application/json" \
  -d '{
    "message": "Qual é o SLA para alertas Nível 2?",
    "user_id": "test-deploy",
    "stream": false
  }'
```

Resposta esperada:
```json
{
  "response": "24 horas",
  "sources": [...]
}
```

### 4.3. Acessar frontend

Abra no navegador: `https://treq-frontend.onrender.com`

---

## 🐛 Troubleshooting

### Problema: Build falha

**Verifique:**
- [ ] `requirements.txt` existe no backend
- [ ] `package.json` existe no frontend
- [ ] Environment variables configuradas

**Logs:** Render Dashboard → Services → treq-backend → Logs

### Problema: CORS error

**Solução:**
1. Verifique `CORS_ORIGINS` no backend
2. Adicione URL do frontend
3. Re-deploy o backend

### Problema: Chat não responde

**Verifique:**
1. Backend health check
2. Supabase connection (logs)
3. API keys válidas

---

## 📊 Monitoramento

### Logs em tempo real
Render Dashboard → Services → treq-backend → **Logs**

### Métricas
Render Dashboard → Services → treq-backend → **Metrics**

---

## 🎉 Sucesso!

Se tudo der certo, você terá:

```
✅ Backend: https://treq-backend.onrender.com
✅ Frontend: https://treq-frontend.onrender.com
✅ Chat respondendo
✅ Custo: $0.00/mês (FREE tier)
```

---

## 📝 Próximos Passos

Após deploy bem-sucedido:

1. **Testar todas as funcionalidades**
   - Chat com streaming
   - Upload de documentos
   - Transcrição de áudio
   - Vision (imagens)

2. **Monitorar logs**
   - Verificar erros
   - Otimizar performance

3. **Re-enable features**
   - Grounding validator (com threshold ajustado)
   - LangSmith tracing (opcional)

---

**Boa sorte com o deploy! 🚀**
