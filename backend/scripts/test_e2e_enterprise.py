"""
Teste End-to-End (E2E) para Treq Enterprise v2.0.

Valida o fluxo completo contra o servidor rodando localmente.
Requer que o servidor esteja rodando em localhost:8002.
"""

import requests
import json
import time

BASE_URL = "http://localhost:8002"
API_KEY = "treq-dev-key-2024"  # Chave de dev hardcoded no auth middleware
HEADERS = {
    "X-API-Key": API_KEY,
    "Content-Type": "application/json",
    "X-User-ID": "e2e-tester"
}

def log(msg, type="INFO"):
    colors = {
        "INFO": "\033[94m",
        "SUCCESS": "\033[92m",
        "ERROR": "\033[91m",
        "WARN": "\033[93m",
        "RESET": "\033[0m"
    }
    print(f"{colors.get(type, '')}[{type}] {msg}{colors['RESET']}")

def test_health():
    log("Testando Health Check...", "INFO")
    try:
        resp = requests.get(f"{BASE_URL}/agent/health", timeout=5)
        if resp.status_code == 200:
            log(f"Health OK: {resp.json()}", "SUCCESS")
        else:
            log(f"Health Falhou: {resp.status_code}", "ERROR")
            exit(1)
    except Exception as e:
        log(f"Erro de conexão: {e}", "ERROR")
        log("Certifique-se que o uvicorn está rodando na porta 8002", "WARN")
        exit(1)

def test_connectors_status():
    log("\nTestando Status Conectores...", "INFO")
    resp = requests.get(f"{BASE_URL}/connectors/status", headers=HEADERS)
    data = resp.json()
    log(f"Status: {json.dumps(data, indent=2)}", "INFO")
    
    # Verificar se Slack está desconectado inicialmente (ou conectado de testes anteriores)
    return data

def test_agent_rag_flow():
    log("\nTestando Fluxo RAG (Perguntas)...", "INFO")
    payload = {
        "query": "Qual o procedimento para vazamento de óleo?",
        "user_id": "e2e-tester"
    }
    
    start = time.time()
    resp = requests.post(f"{BASE_URL}/agent/chat", json=payload, headers=HEADERS)
    duration = time.time() - start
    
    if resp.status_code == 200:
        data = resp.json()
        log(f"Resposta ({duration:.2f}s):", "SUCCESS")
        print(f"  Fluxo: {data.get('flow')}")
        print(f"  Tools: {data.get('tools_used')}")
        print(f"  Contexto: {data.get('context_count')} docs")
        print(f"  Resposta AI: {data.get('response')[:100]}...")
        
        if "retriever" not in data.get("flow", []):
            log("Alerta: Esperava-se uso do retriever", "WARN")
    else:
        log(f"Erro RAG: {resp.text}", "ERROR")

def test_agent_tool_flow():
    log("\nTestando Fluxo Tool (Slack)...", "INFO")
    
    # 1. Garantir conexão
    requests.post(f"{BASE_URL}/connectors/slack/connect", headers=HEADERS)
    
    # 2. Pedir ação
    payload = {
        "query": "Avise a equipe no canal #geral que o sistema foi atualizado com sucesso.",
        "user_id": "e2e-tester"
    }
    
    start = time.time()
    resp = requests.post(f"{BASE_URL}/agent/chat", json=payload, headers=HEADERS)
    duration = time.time() - start
    
    if resp.status_code == 200:
        data = resp.json()
        log(f"Resposta ({duration:.2f}s):", "SUCCESS")
        print(f"  Fluxo: {data.get('flow')}")
        print(f"  Tools: {data.get('tools_used')}")
        print(f"  Resposta AI: {data.get('response')}")
        
        # Validações
        if "executor" in data.get("flow", []) and "slack_notify" in data.get("tools_used", []):
            log("Fluxo correto: Planner -> Executor -> SlackTool -> Responder", "SUCCESS")
        else:
            log(f"Fluxo inesperado: {data.get('flow')}", "ERROR")
    else:
        log(f"Erro Tool: {resp.text}", "ERROR")

def main():
    log("=== INICIANDO TESTE E2E TREQ ENTERPRISE ===", "INFO")
    test_health()
    test_connectors_status()
    test_agent_rag_flow()
    test_agent_tool_flow()
    log("\n=== TESTE E2E CONCLUÍDO ===", "SUCCESS")

if __name__ == "__main__":
    main()
