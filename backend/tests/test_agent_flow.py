import pytest
from unittest.mock import AsyncMock, patch
from app.features.agent.graph import create_agent_graph
from langchain_core.messages import HumanMessage, AIMessage

@pytest.mark.asyncio
async def test_agent_flow_planner_to_responder():
    """Testa o fluxo direto: Planner -> Responder (sem ferramentas)."""
    with patch("app.features.agent.graph.planner_node", new_callable=AsyncMock) as mock_planner, \
         patch("app.features.agent.graph.responder_node", new_callable=AsyncMock) as mock_responder:
        
        # Mock Planner: decide responder diretamente
        mock_planner.return_value = {"next_action": "respond"}
        
        # Mock Responder: gera a resposta final
        mock_responder.return_value = {
            "messages": [AIMessage(content="Olá! Como posso ajudar?")],
            "next_action": "end"
        }
        
        app = create_agent_graph()
        
        inputs = {
            "messages": [HumanMessage(content="oi")],
            "user_id": "test_user",
            "context": [],
            "next_action": "",
            "tool_outputs": [],
            "metadata": {}
        }
        
        config = {"configurable": {"thread_id": "test_thread"}}
        result = await app.ainvoke(inputs, config=config)
        
        assert "messages" in result
        assert result["messages"][-1].content == "Olá! Como posso ajudar?"
        assert mock_planner.called
        assert mock_responder.called

@pytest.mark.asyncio
async def test_agent_flow_with_retriever():
    """Testa o fluxo: Planner -> Retriever -> Planner -> Responder."""
    with patch("app.features.agent.graph.planner_node", new_callable=AsyncMock) as mock_planner, \
         patch("app.features.agent.graph.retriever_node", new_callable=AsyncMock) as mock_retriever, \
         patch("app.features.agent.graph.responder_node", new_callable=AsyncMock) as mock_responder:
        
        # Sequência do Planner: 1o chama RAG, 2o responde
        mock_planner.side_effect = [
            {"next_action": "call_rag"},
            {"next_action": "respond"}
        ]
        
        # Mock Retriever: simula busca
        mock_retriever.return_value = {
            "tool_outputs": [{"tool": "knowledge", "result": "Informação encontrada"}]
        }
        
        # Mock Responder
        mock_responder.return_value = {
            "messages": [AIMessage(content="Aqui está a informação")],
            "next_action": "end"
        }
        
        app = create_agent_graph()
        
        inputs = {
            "messages": [HumanMessage(content="Qual o procedimento X?")],
            "user_id": "test_user",
            "context": [],
            "next_action": "",
            "tool_outputs": [],
            "metadata": {}
        }
        
        result = await app.ainvoke(inputs, config={"configurable": {"thread_id": "test_thread"}})
        
        assert result["messages"][-1].content == "Aqui está a informação"
        assert mock_planner.call_count == 1
        assert mock_retriever.called
        assert mock_responder.called
