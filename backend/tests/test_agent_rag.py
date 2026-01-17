import pytest
from unittest.mock import MagicMock, patch
from app.features.agent.tools.knowledge import search_knowledge_base
from app.features.agent.nodes.retriever import retriever_node

@pytest.fixture
def mock_vector_store():
    with patch("app.features.agent.tools.knowledge.get_vector_store") as mock:
        store = MagicMock()
        mock.return_value = store
        yield store

def test_search_knowledge_base_success(mock_vector_store):
    # Setup mock return
    doc_mock = MagicMock()
    doc_mock.page_content = "Conteúdo relevante sobre Treq"
    doc_mock.metadata = {"source": "manual.pdf", "page": 10}
    
    mock_vector_store.similarity_search_with_score.return_value = [(doc_mock, 0.9)]
    
    # Execute tool
    result = search_knowledge_base.invoke("O que é Treq?")
    
    # Assert
    assert "Conteúdo relevante" in result
    assert "manual.pdf" in result
    mock_vector_store.similarity_search_with_score.assert_called_once()

def test_search_knowledge_base_empty(mock_vector_store):
    mock_vector_store.similarity_search_with_score.return_value = []
    
    result = search_knowledge_base.invoke("Nada a ver")
    
    assert "Nenhuma informação relevante" in result

@pytest.mark.asyncio
async def test_retriever_node_integration(mock_vector_store):
    # Setup state
    state = {
        "messages": [MagicMock(content="Explain RAG")],
        "steps_taken": 0
    }
    
    doc_mock = MagicMock()
    doc_mock.page_content = "RAG is Retrieval Augmented Generation"
    doc_mock.metadata = {"source": "wiki", "page": 1}
    
    mock_vector_store.similarity_search_with_score.return_value = [(doc_mock, 0.9)]
    
    # Execute node
    output = await retriever_node(state)
    
    # Assert
    assert output["context"] is not None
    assert "RAG is Retrieval Augmented Generation" in output["context"][0]
    assert output["steps_taken"] == 1
