
import requests
import json
import time

BASE_URL = "http://localhost:8002/chat/"

def test_chat(message, image_url=None, label=""):
    payload = {
        "message": message,
        "user_id": "test_user_v3",
        "conversation_id": "test_conv_v3",
        "stream": False,
        "image_url": image_url
    }
    
    print(f"\n--- TESTE: {label} ---")
    print(f"Query: '{message}'")
    try:
        start_time = time.time()
        response = requests.post(BASE_URL, json=payload, timeout=90)
        elapsed = time.time() - start_time
        
        if response.status_code == 200:
            data = response.json()
            print(f"Tipo: {data.get('type', 'N/A')}")
            print(f"Fontes: {len(data.get('sources', []))}")
            resp_text = data.get('response', '')
            print(f"Resposta: {resp_text[:150]}...")
            print(f"Tempo: {elapsed:.2f}s")
            
            if "Bruno Almeida" in resp_text and "procedimentos" in message.lower():
                 print("❌ FALHA: Citou Bruno.")
            elif "procedimentos" in message.lower():
                 print("✅ SUCESSO: Filtro Clean-RAG ok.")
        else:
            print(f"Erro {response.status_code}: {response.text}")
    except Exception as e:
        print(f"Falha: {e}")

if __name__ == "__main__":
    # Sequencial para não sobrecarregar
    test_chat("Quais são os procedimentos operacionais?", label="1. Operacional (Clean-RAG)")
    test_chat("Quem é Bruno Almeida?", label="2. Pessoal (RAG normal)")
    test_chat("Diga 'Olá'", label="3. Social")
