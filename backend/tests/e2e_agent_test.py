import asyncio
import os
import sys

# Adicionar o diretório /app ao sys.path para garantir que os imports funcionem no docker
sys.path.append("/app")

from app.features.agent.graph import create_agent_graph
from app.features.agent.state import AgentState
from langchain_core.messages import HumanMessage

async def test_agent_graph_e2e():
    print("🚀 Iniciando Teste E2E do Grafo Cognitivo...")
    
    app = create_agent_graph()
    
    # Estado inicial completo
    inputs: AgentState = {
        "messages": [HumanMessage(content="Crie um ticket no Jira sobre erro no login")],
        "user_id": "test-user-123",
        "context": [],
        "next_action": "",
        "tool_outputs": [],
        "metadata": {},
        "current_decision": None,
        "execution_trace": [],
        "retry_count": 0,
        "max_retries": 3,
        "steps_taken": 0,
        "documents_retrieved": [],
        "response_mode": "text"
    }
    
    config = {"configurable": {"thread_id": "test-thread-e2e-1"}}
    
    try:
        # Executar o grafo
        print("🧠 Agente está processando...")
        result = await app.ainvoke(inputs, config=config)
        
        print("\n--- RESULTADOS DO TESTE ---")
        
        decision = result.get("current_decision")
        if decision:
            print(f"✅ Intent Detectada: {decision.intent}")
            print(f"✅ Thought Field: {decision.thought[:100]}...")
        else:
            print("❌ Erro: current_decision não encontrado no estado final.")
            
        tool_outputs = result.get("tool_outputs", [])
        if tool_outputs:
            print(f"✅ Tool Outputs ({len(tool_outputs)}):")
            for out in tool_outputs:
                print(f"   - Ferramenta: {out.get('tool')}")
                if "prefill" in out:
                    print(f"   - Prefill: {out['prefill']}")
                else:
                    print("   - ❌ Prefill ausente!")
        else:
            print("⚠️ Nenhuma ferramenta foi executada (Pode ser normal dependendo da intenção).")

        trace = result.get("execution_trace", [])
        if trace:
            print(f"✅ Execution Trace ({len(trace)} passos):")
            for i, step in enumerate(trace):
                step_name = step.get('step', 'unknown')
                print(f"   [{i}] Passo: {step_name}")
                if "prefill" in step:
                    print(f"       ✅ Prefill presente")
                if "thought" in step:
                    print(f"       ✅ Thought presente")
        else:
            print("⚠️ Execution Trace vazio.")

        print("\n✨ Teste concluído com sucesso!")
        
    except Exception as e:
        print(f"\n❌ Falha no teste: {str(e)}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(test_agent_graph_e2e())
