
import requests
import json
import base64

BASE_URL = "http://localhost:8002/chat/"

def test_chat(message, image_url=None, stream=False):
    payload = {
        "message": message,
        "user_id": "test_user_123",
        "conversation_id": "test_conv_123",
        "stream": stream,
        "image_url": image_url
    }
    
    print(f"\n--- Testando: '{message}' {'(com imagem)' if image_url else ''} ---")
    try:
        response = requests.post(BASE_URL, json=payload, timeout=30)
        if response.status_code == 200:
            if stream:
                print("Resposta (Stream chunks):")
                for line in response.iter_lines():
                    if line:
                        print(line.decode('utf-8'))
            else:
                data = response.json()
                print(f"Tipo: {data.get('type', 'N/A')}")
                print(f"Estratégia: {data.get('strategy', 'N/A')}")
                print(f"Resposta: {data.get('response')[:200]}...")
                if 'special_response' in data:
                    print(f"Special Response: {data.get('special_response')}")
        else:
            print(f"Erro {response.status_code}: {response.text}")
    except Exception as e:
        print(f"Falha na requisição: {e}")

if __name__ == "__main__":
    # Teste 1: Pergunta de capacidade pura (Deve retornar resposta estática)
    test_chat("você consegue ler arquivos PDF?")
    
    # Teste 2: Comando de análise direto (Deve ir para RAG/LLM, não resposta estática)
    test_chat("analise o arquivo")
    
    # Teste 3: Pergunta de capacidade com "imagem" simulada (Deve ignorar resposta estática e ir para Vision)
    # Nota: Vai falhar no Gemini se o base64 for inválido, mas o objetivo é ver se o CHAT_HANDLER ignora o special_response
    fake_image = "data:image/jpeg;base64,VEVTVA==" # "TEST" em base64
    test_chat("consegue ler esta imagem?", image_url=fake_image)
    
    # Teste 4: Saudação social
    test_chat("olá, tudo bem?")
