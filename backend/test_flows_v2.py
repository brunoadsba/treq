
import requests
import json
import base64

BASE_URL = "http://localhost:8002/chat/"

def test_chat(message, image_url=None, stream=False, label=""):
    payload = {
        "message": message,
        "user_id": "test_user_v2",
        "conversation_id": "test_conv_v2",
        "stream": stream,
        "image_url": image_url
    }
    
    print(f"\n--- TESTE: {label} ---")
    print(f"Query: '{message}'")
    try:
        response = requests.post(BASE_URL, json=payload, timeout=60)
        if response.status_code == 200:
            data = response.json()
            print(f"Tipo: {data.get('type', 'N/A')}")
            print(f"Fontes/Documentos usados: {len(data.get('sources', []))}")
            for i, src in enumerate(data.get('sources', [])):
                print(f"  [{i+1}] {src.get('metadata', {}).get('source', 'Desconhecido')}")
            
            resp_text = data.get('response', '')
            print(f"Resposta (resumo): {resp_text[:300]}...")
            
            # Verificação do Clean-RAG no teste do Bruno
            if "Bruno Almeida" in resp_text and "procedimentos" in message.lower():
                 print("⚠️ ALERTA: Ainda está citando Bruno no contexto operacional!")
            elif "Bruno Almeida" not in resp_text and "procedimentos" in message.lower():
                 print("✅ SUCESSO: Filtro Clean-RAG removeu ruído do currículo.")

        else:
            print(f"Erro {response.status_code}: {response.text}")
    except Exception as e:
        print(f"Falha na requisição: {e}")

if __name__ == "__main__":
    # Teste 1: Clean-RAG - Pergunta operacional que antes trazia o currículo do Bruno
    test_chat("Quais são os procedimentos operacionais?", label="Clean-RAG (Filtro de Currículos)")
    
    # Teste 2: Pergunta pessoal - Deve TRAZER o currículo do Bruno
    test_chat("Quem é Bruno Almeida?", label="Persistência Biográfica (Pergunta Pessoal)")
    
    # Teste 3: Visão com Base64 corrompido (para disparar MultimodalError mas não alucinar descrição de erro)
    corrupted_image = "data:image/png;base64,CORRUPTED_DATA_HERE"
    test_chat("O que você está vendo?", image_url=corrupted_image, label="Robustez de Visão (Erro de Base64)")
    
    # Teste 4: Saudação simples
    test_chat("Olá!", label="Interação Social")
