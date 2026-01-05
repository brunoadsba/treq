# 🚀 Deploy Automático - Treq no Render

## 📋 Deploy em 3 Minutos (Blueprint)

### Opção 1: Deploy Automático (Recomendado) ⚡

1. **Acesse o Render Blueprint**
   - Clique aqui: **[Deploy no Render](https://render.com/deploy?repo=brunoadsba/treq)**
   - Ou acesse: https://dashboard.render.com → "New" → "Blueprint"

2. **Conecte o GitHub**
   - Authorize acesso ao repositório `brunoadsba/treq`
   - Selecione o branch `main`

3. **Configure as Environment Variables**

   **Importante:** Você precisa adicionar estas API keys:

   ```bash
   # Supabase (obrigatório)
   SUPABASE_URL=https://taidcwtolloreyxjvegi.supabase.co
   SUPABASE_SERVICE_ROLE_KEY=eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...
   SUPABASE_ANON_KEY=eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...

   # Groq API (obrigatório)
   GROQ_API_KEY=gsk_wm5CTNbnVdgSvzy2U12kWGdyb3FY1KlrYayBtF8...

   # Gemini (obrigatório)
   GEMINI_API_KEY=AIzaSyBU2jCBTilyjPB-k6iNsoDcjHUo8lbRKzI

   # Zhipu AI (opcional)
   ZHIPU_API_KEY=5aa3fec9311446f6b692263f8146d47d.taZ20qQpNd2plDKB
   ```

4. **Clique em "Apply Blueprint"**
   - Render criará 3 serviços automaticamente:
     - ✅ `treq-backend` (FastAPI)
     - ✅ `treq-frontend` (Next.js)
     - ✅ `treq-cache` (Redis)

5. **Aguarde o build** (~5-10 minutos)
   - Backend: https://treq-backend.onrender.com
   - Frontend: https://treq-frontend.onrender.com

---

### Opção 2: Deploy Manual Passo a Passo

Se preferir configurar manualmente, siga o guia completo: **[DEPLOY.md](./DEPLOY.md)**

---

## ✅ Verificar Deploy

### 1. Health Check
```bash
curl https://treq-backend.onrender.com/health
```

Resposta esperada:
```json
{"status": "ok", "service": "treq-backend", "up": true}
```

### 2. Testar Chat
```bash
curl -X POST https://treq-backend.onrender.com/chat/ \
  -H "Content-Type: application/json" \
  -d '{"message": "Qual é o SLA para alertas Nível 2?", "user_id": "test", "stream": false}'
```

### 3. Acessar Frontend
Abra: https://treq-frontend.onrender.com

---

## 🐛 Troubleshooting

### Backend não inicia

**Verifique os logs:**
1. Render Dashboard → treq-backend → Logs
2. Procure por erros de startup

**Comum:**
- Missing `SUPABASE_URL` → Adicione nas env vars
- Missing `GROQ_API_KEY` → Adicione nas env vars

### Frontend não conecta no backend

**Problema:** CORS error

**Solução:**
1. Adicione URL do frontend nas `CORS_ORIGINS` do backend
2. Re-deploy o backend

### Chat não responde

**Diagnóstico:**
```bash
# Ver se backend está healthy
curl https://treq-backend.onrender.com/health

# Ver logs do backend
# Dashboard → treq-backend → Logs
```

---

## 📊 Monitoramento

### Logs em Tempo Real
```
Render Dashboard → treq-backend → Logs (Live)
```

### Métricas
```
Render Dashboard → treq-backend → Metrics
```

---

## 🎉 Sucesso!

Se tudo funcionou, você terá:

```
✅ Backend: https://treq-backend.onrender.com
✅ Frontend: https://treq-frontend.onrender.com
✅ Chat funcionando
✅ RAG com 258 documentos
✅ Streaming ativo
✅ Custo: $0.00/mês (FREE tier)
```

---

## 🔄 Deploy Futuros

Após o primeiro deploy, qualquer push para `main` dispara automaticamente um novo deploy!

```bash
git add .
git commit -m "feat: nova funcionalidade"
git push
```

Render detecta e deploya automaticamente. 🚀

---

**Pronto para apresentar seu MVP!** 🎊
