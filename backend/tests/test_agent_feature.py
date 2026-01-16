"""
Testes unitários para a feature Agent (LangGraph).

Cenários:
1. AgentState valido
2. Planner decide corretamente
3. Tools mock funcionam
4. Graph compila sem erro
"""

import pytest
from unittest.mock import AsyncMock, patch


class TestAgentState:
    """Testes para AgentState."""
    
    def test_agent_state_structure(self):
        """AgentState tem todos os campos necessários."""
        from app.features.agent.state import AgentState
        from langchain_core.messages import HumanMessage
        
        state: AgentState = {
            "messages": [HumanMessage(content="teste")],
            "user_id": "user_123",
            "context": [],
            "next_action": "",
            "tool_outputs": [],
            "metadata": None
        }
        
        assert state["user_id"] == "user_123"
        assert len(state["messages"]) == 1


class TestPlannerNode:
    """Testes para planner_node."""
    
    @pytest.mark.asyncio
    async def test_planner_decides_rag_for_question(self):
        """Planner escolhe RAG para perguntas normais."""
        from app.features.agent.nodes.planner import planner_node
        from langchain_core.messages import HumanMessage
        
        state = {
            "messages": [HumanMessage(content="Como fazer manutenção?")],
            "user_id": "user_1",
            "context": [],
            "next_action": "",
            "tool_outputs": [],
            "metadata": None
        }
        
        result = await planner_node(state)
        assert result["next_action"] == "call_rag"
    
    @pytest.mark.asyncio
    async def test_planner_decides_tool_for_jira(self):
        """Planner escolhe Tool para criar ticket."""
        from app.features.agent.nodes.planner import planner_node
        from langchain_core.messages import HumanMessage
        
        state = {
            "messages": [HumanMessage(content="Criar ticket no Jira")],
            "user_id": "user_1",
            "context": [],
            "next_action": "",
            "tool_outputs": [],
            "metadata": None
        }
        
        result = await planner_node(state)
        assert result["next_action"] == "call_tool"


class TestToolsMock:
    """Testes para ferramentas mock."""
    
    @pytest.mark.asyncio
    async def test_jira_tool_returns_ticket_id(self):
        """JiraCreateTicketTool retorna ticket ID."""
        from app.features.agent.tools import JiraCreateTicketTool
        
        tool = JiraCreateTicketTool()
        result = await tool.execute(summary="Teste", description="Descrição")
        
        assert result["status"] == "success"
        assert "ticket_id" in result
        assert result["ticket_id"] == "TREQ-123"
    
    @pytest.mark.asyncio
    async def test_slack_tool_returns_success(self):
        """SlackSendMessageTool retorna sucesso."""
        from app.features.agent.tools import SlackSendMessageTool
        
        tool = SlackSendMessageTool()
        result = await tool.execute(channel="#geral", message="Teste")
        
        assert result["status"] == "success"
        assert result["channel"] == "#geral"


class TestAgentGraph:
    """Testes para compilação do grafo."""
    
    def test_graph_compiles_successfully(self):
        """Grafo compila sem erros."""
        from app.features.agent.graph import create_agent_graph, LANGGRAPH_AVAILABLE
        
        if not LANGGRAPH_AVAILABLE:
            pytest.skip("langgraph não instalado")
        
        graph = create_agent_graph()
        assert graph is not None
