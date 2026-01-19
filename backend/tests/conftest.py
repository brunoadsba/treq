"""
Configuração do pytest para testes do Treq Backend.

Este arquivo configura:
- Fixtures compartilhados
- Configuração de ambiente para testes
- Mocks para serviços externos
"""
import sys
from pathlib import Path
import pytest

import os

# Configurar variáveis de ambiente MOCK antes de importar qualquer módulo da aplicação
os.environ.setdefault("SECRET_KEY", "mock_secret_key_for_testing_only_unsafe")
os.environ.setdefault("JWT_SECRET_KEY", "mock_jwt_secret_key_for_testing_only_unsafe")
os.environ.setdefault("SUPABASE_URL", "https://mock.supabase.co")
os.environ.setdefault("SUPABASE_SERVICE_KEY", "mock_supabase_service_key")
os.environ.setdefault("SUPABASE_ANON_KEY", "mock_supabase_anon_key")
os.environ.setdefault("GROQ_API_KEY", "mock_groq_key")
os.environ["LANGCHAIN_TRACING_V2"] = "false"
os.environ["LANGSMITH_API_KEY"] = ""

# Adicionar o diretório raiz ao path para imports
backend_dir = Path(__file__).parent.parent
sys.path.insert(0, str(backend_dir))


@pytest.fixture
def mock_settings():
    """
    Fixture para fornecer configurações mockadas.
    Útil para testes que não devem acessar serviços reais.
    """
    from unittest.mock import MagicMock
    
    settings = MagicMock()
    settings.supabase_url = "https://example.supabase.co"
    settings.supabase_key = "mock_key"
    settings.groq_api_key = "mock_groq_key"
    settings.gemini_api_key = "mock_gemini_key"
    settings.embedding_model = "sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2"
    settings.embedding_dimension = 384
    settings.llm_model = "llama-3.1-8b-instant"
    settings.llm_temperature = 0.4
    settings.llm_max_tokens = 1200
    settings.log_level = "DEBUG"
    
    return settings


@pytest.fixture
def sample_query():
    """Fixture com query de exemplo para testes."""
    return "Qual o procedimento para manutenção preventiva?"


@pytest.fixture
def sample_context():
    """Fixture com contexto de exemplo para testes RAG."""
    return [
        "Procedimento de Manutenção Preventiva:\n1. Verificar nível de óleo\n2. Checar filtros\n3. Inspecionar correias",
        "Manual de Operação - Seção 5.2: A manutenção preventiva deve ser realizada mensalmente.",
    ]


@pytest.fixture
def sample_chat_message():
    """Fixture com mensagem de chat para testes."""
    return {
        "role": "user",
        "content": "Me explique sobre os alertas ativos"
    }


# Configuração para testes assíncronos
pytest_plugins = ["pytest_asyncio"]
