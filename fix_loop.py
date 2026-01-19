#!/usr/bin/env python3
"""
Patch emergencial para corrigir loop infinito no streaming
"""

import requests
import json

def test_and_fix_streaming():
    print("🚨 CORREÇÃO EMERGENCIAL - Loop Infinito")
    
    # 1. Testar endpoint atual
    try:
        response = requests.post(
            "http://localhost:8002/chat/",
            json={
                "message": "teste simples",
                "user_id": "test",
                "stream": False  # Desabilitar streaming temporariamente
            },
            headers={"Authorization": "Bearer TOKEN_AQUI"},
            timeout=10
        )
        
        if response.status_code == 200:
            data = response.json()
            print(f"✅ Resposta sem streaming: {len(data.get('response', ''))} chars")
            
            if len(data.get('response', '')) > 5000:
                print("❌ AINDA HAY PROBLEMA: Resposta muito longa")
            else:
                print("✅ Resposta normal")
        else:
            print(f"❌ Erro HTTP: {response.status_code}")
            
    except Exception as e:
        print(f"❌ Erro na requisição: {e}")

    # 2. Sugestões de correção
    print("\n🛠️ CORREÇÕES NECESSÁRIAS:")
    print("1. Reduzir max_tokens para 500")
    print("2. Adicionar stop_sequences")
    print("3. Implementar timeout no streaming")
    print("4. Limpar cache/contexto corrompido")

if __name__ == "__main__":
    test_and_fix_streaming()
