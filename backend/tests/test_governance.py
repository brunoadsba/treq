"""
Testes de Governança e Tracing.
"""

import os
from unittest.mock import patch
from app.core.governance import get_trace_config, get_langsmith_client


class TestGovernance:
    """Testes para o módulo de governança."""
    
    def test_trace_config_structure(self):
        """Valida estrutura do config de trace."""
        with patch.dict(os.environ, {"LANGCHAIN_PROJECT": "test-project"}):
            config = get_trace_config(user_id="user_123", thread_id="thread_abc")
            
            assert "metadata" in config
            assert config["metadata"]["user_id"] == "user_123"
            assert config["metadata"]["thread_id"] == "thread_abc"
            assert config["metadata"]["project"] == "test-project"
            
            assert "tags" in config
            assert "user:user_123" in config["tags"]
            assert "agent" in config["tags"]
    
    def test_langsmith_client_singleton(self):
        """Valida singleton do cliente."""
        client1 = get_langsmith_client()
        client2 = get_langsmith_client()
        
        assert client1 is client2
