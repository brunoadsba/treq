import sys
import os
import json
import asyncio
# Adicionar root ao path
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))

from app.features.agent.nodes.planner import planner_node
from langchain_core.messages import HumanMessage

async def run_quality_check():
    print("🧪 Iniciando Validação de Qualidade (Intent Classification)...\n")
    
    with open('backend/scripts/golden_dataset.json', 'r') as f:
        dataset = json.load(f)
        
    passed = 0
    total = len(dataset)
    
    for case in dataset:
        print(f"🔸 Testando: '{case['query']}' ...")
        
        # Simula estado
        state = {
            "messages": [HumanMessage(content=case['query'])],
            "steps_taken": 0,
            "context": []
        }
        
        # Executa Planner
        result = await planner_node(state)
        action = result.get("next_action")
        
        # Verifica se ação corresponde ao esperado (mapeamento simples)
        expected = case['expected_action']
        
        if action == expected:
            print(f"   ✅ Passou (Ação: {action})")
            passed += 1
        else:
            print(f"   ❌ Falhou. Esperado: {expected}, Recebido: {action}")
            
    print(f"\n📊 Resultado Final: {passed}/{total} passaram.")

if __name__ == "__main__":
    asyncio.run(run_quality_check())
