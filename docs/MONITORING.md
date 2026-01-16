# 📊 Guia de Monitoramento - Treq

## 🎯 Visão Geral

O Treq possui um sistema completo de monitoramento com métricas em tempo real para:

- ✅ **Chat**: Requests, erros, tempo de resposta
- ✅ **RAG**: Buscas, similaridade, cache hits
- ✅ **LLM**: Chamadas, tokens, latência por modelo
- ✅ **Sistema**: CPU, memória, uptime

---

## 📡 Endpoints de Monitoramento

### 1. Métricas Completas
```bash
GET /monitoring/metrics
```

Retorna todas as métricas do sistema:
```json
{
  "timestamp": "2026-01-05T12:00:00",
  "uptime_seconds": 3600,
  "system": {
    "cpu_percent": 15.2,
    "memory_usage_mb": 256.5,
    "memory_available_mb": 2048.0,
    "threads": 4,
    "status": "healthy"
  },
  "chat": {
    "total_requests": 150,
    "successful_requests": 145,
    "failed_requests": 5,
    "avg_response_time_ms": 850.5,
    "rag_queries": 120,
    "rag_no_results": 8,
    "llm_calls": 145,
    "llm_tokens_used": 45000
  },
  "rag": {
    "total_searches": 120,
    "avg_similarity_score": 0.685,
    "avg_search_time_ms": 120.3,
    "cache_hits": 45,
    "cache_misses": 75
  },
  "llm": {
    "total_calls": 145,
    "total_tokens": 45000,
    "avg_latency_ms": 650.2,
    "model_8b_calls": 95,
    "model_70b_calls": 40,
    "model_glm4_calls": 10
  },
  "performance": {
    "error_rate": 3.33,
    "avg_response_time_ms": 850.5,
    "rag_success_rate": 93.33
  }
}
```

### 2. Resumo Executivo
```bash
GET /monitoring/stats/summary
```

Resumo otimizado para dashboards:
```json
{
  "uptime_hours": 1.5,
  "total_requests": 150,
  "success_rate_percent": 96.67,
  "avg_response_time_ms": 850.5,
  "rag_avg_similarity": 0.685,
  "llm_total_tokens": 45000,
  "llm_avg_latency_ms": 650.2,
  "system_status": "healthy"
}
```

### 3. Health Check
```bash
GET /monitoring/health
```

Status do serviço de monitoramento:
```json
{
  "status": "ok",
  "service": "treq-monitoring",
  "timestamp": "2026-01-05T12:00:00"
}
```

---

## 📈 Como Registrar Métricas

### No Chat Endpoint

Após cada requisição de chat, registre as métricas:

```python
from httpx import AsyncClient

async def record_metrics(success, response_time_ms, rag_found, tokens):
    async with AsyncClient() as client:
        await client.post(
            "http://localhost:8002/monitoring/chat/metrics",
            params={
                "success": success,
                "response_time_ms": response_time_ms,
                "rag_used": True,
                "rag_found": rag_found,
                "llm_tokens": tokens
            }
        )
```

### Exemplo Prático

```python
# No final do chat endpoint (chat.py)
start_time = time.time()

# ... processamento do chat ...

response_time_ms = (time.time() - start_time) * 1000

# Registrar métricas
from app.api.routes.monitoring import record_chat_metrics
await record_chat_metrics(
    success=True,
    response_time_ms=response_time_ms,
    rag_used=len(sources) > 0,
    rag_found=len(sources) > 0,
    llm_tokens=token_count
)
```

---

## 🔧 Configurar LangSmith (Opcional)

### 1. Criar conta LangSmith
- Acesse: https://smith.langchain.com
- Clique em "Sign Up"
- Crie um projeto (ex: "treq-assistente")

### 2. Configurar Environment Variables

No `.env` ou no Render Dashboard:

```bash
LANGCHAIN_TRACING_V2=true
LANGSMITH_API_KEY=ls-...
LANGCHAIN_PROJECT=treq-assistente
```

### 3. Benefícios do LangSmith

- ✅ Tracing end-to-end de cada query
- ✅ Visualização de Chain of Thought
- ✅ Debugging de retrievals e gerações
- ✅ Métricas de token e custo
- ✅ Feedback loop (👍/👎 dos usuários)

### 4. Visualizar Runs

Cada resposta de chat retorna um `run_id`. Use para acessar:

```bash
# No dashboard LangSmith
https://smith.langchain.com/o/default/projects/p/treq-assistente/r/{run_id}
```

---

## 📊 Dashboards Recomendados

### Render Dashboard (Básico)

O Render já fornece:
- Métricas de CPU, memória
- Logs em tempo real
- Alertas de erro

Acesse: `Dashboard → treq-backend → Metrics`

### Grafana + Prometheus (Avançado)

Para produção, considere configurar:
1. Prometheus para scraping de métricas
2. Grafana para dashboards personalizados

**Endpoints para scraping:**
```
/monitoring/metrics
/monitoring/stats/summary
```

---

## 🔔 Alertas Configuráveis

### 1. Alta Taxa de Erro
```python
if error_rate > 10%:
    send_alert("Taxa de erro acima de 10%")
```

### 2. RAG com Baixa Similaridade
```python
if rag_avg_similarity < 0.5:
    send_alert("Similaridade RAG muito baixa")
```

### 3. Alta Latência LLM
```python
if llm_avg_latency_ms > 2000:
    send_alert("Latência LLM acima de 2s")
```

### 4. Alto Consumo de Memória
```python
if memory_usage_mb > 4000:
    send_alert("Uso de memória acima de 4GB")
```

---

## 🧪 Testar Monitoramento

### 1. Verificar métricas atuais
```bash
curl http://localhost:8002/monitoring/metrics | jq
```

### 2. Testar registro de métrica
```bash
curl -X POST "http://localhost:8002/monitoring/chat/metrics?success=true&response_time_ms=500&rag_used=true&rag_found=true&llm_tokens=100"
```

### 3. Ver resumo
```bash
curl http://localhost:8002/monitoring/stats/summary | jq
```

---

## 📱 Integrar no Frontend

Adicione um componente de monitoramento no Next.js:

```typescript
// components/MonitoringPanel.tsx
import useSWR from 'swr'

export function MonitoringPanel() {
  const { data: metrics } = useSWR('/monitoring/stats/summary', fetcher)

  return (
    <div className="monitoring-panel">
      <h3>Métricas do Sistema</h3>
      <div className="metrics-grid">
        <div className="metric-card">
          <span>Requests</span>
          <strong>{metrics?.total_requests || 0}</strong>
        </div>
        <div className="metric-card">
          <span>Taxa de Sucesso</span>
          <strong>{metrics?.success_rate_percent || 0}%</strong>
        </div>
        <div className="metric-card">
          <span>Tempo Médio</span>
          <strong>{metrics?.avg_response_time_ms || 0}ms</strong>
        </div>
        <div className="metric-card">
          <span>Similaridade RAG</span>
          <strong>{metrics?.rag_avg_similarity || 0}</strong>
        </div>
      </div>
    </div>
  )
}
```

---

## 🎯 KPIs para Monitorar

### Saúde do Sistema
- ✅ **Error Rate**: < 5%
- ✅ **Success Rate**: > 95%
- ✅ **Avg Response Time**: < 1000ms

### Qualidade RAG
- ✅ **Avg Similarity**: > 0.60
- ✅ **RAG Success Rate**: > 90%
- ✅ **Cache Hit Rate**: > 30%

### Performance LLM
- ✅ **Avg Latency**: < 800ms (8B), < 1500ms (70B)
- ✅ **Tokens por Request**: < 1000
- ✅ **Model Distribution**: 8B (60%), 70B (30%), GLM-4 (10%)

---

**Monitoramento configurado!** 📊

Agora você pode acompanhar todas as métricas em tempo real.
