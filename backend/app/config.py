"""
Configurações da aplicação usando Pydantic Settings.
"""
from pydantic_settings import BaseSettings
from pydantic import HttpUrl, Field, AliasChoices
from functools import lru_cache
import os
from dotenv import load_dotenv

# Carregar variáveis do .env IMEDIATAMENTE para garantir que o LangSmith as veja
load_dotenv()

# Forçar injeção no ambiente para bibliotecas que leem direto do os.environ
if os.getenv("LANGCHAIN_TRACING_V2", "").lower() == "true":
    os.environ["LANGCHAIN_TRACING_V2"] = "true"
    # Tenta LANGSMITH_API_KEY, se não houver, tenta LANGCHAIN_API_KEY
    ls_key = os.getenv("LANGSMITH_API_KEY") or os.getenv("LANGCHAIN_API_KEY", "")
    os.environ["LANGSMITH_API_KEY"] = ls_key
    os.environ["LANGCHAIN_PROJECT"] = os.getenv("LANGCHAIN_PROJECT", "treq-assistente")

class Settings(BaseSettings):
    """Configurações centralizadas (SSOT) para Treq Enterprise."""
    
    # Aplicação
    app_name: str = "Treq Enterprise"
    version: str = "2026.1.0"
    environment: str = "production"
    debug: bool = False
    secret_key: str = Field(..., env="SECRET_KEY")
    cors_origins: str = "*"
    
    # Segurança & Auth (Enterprise Hardening)
    jwt_secret_key: str = Field(..., env="JWT_SECRET_KEY")
    jwt_algorithm: str = "HS256"
    access_token_expire_minutes: int = 60 * 24  # 24 horas
    
    # Backend
    host: str = "0.0.0.0"
    port: int = 8002
    
    # Supabase (RLS Mandatory)
    supabase_url: HttpUrl = Field(..., env="SUPABASE_URL")
    supabase_service_key: str = Field(..., validation_alias=AliasChoices("supabase_service_key", "SUPABASE_SERVICE_KEY"))
    supabase_anon_key: str = Field(..., validation_alias=AliasChoices("supabase_anon_key", "SUPABASE_ANON_KEY"))
    database_url: str = Field("", env="DATABASE_URL")
    redis_url: str = Field("redis://redis:6379/0", env="REDIS_URL")
    
    # Rate Limiting
    rate_limit_per_minute: int = 60
    
    # Logging
    log_level: str = "INFO"
    
    # LLM Routing
    use_dynamic_model: bool = True
    use_3_level_routing: bool = True
    
    # Alias para compatibilidade legada
    @property
    def supabase_key(self) -> str:
        return self.supabase_service_key

    # APIs
    groq_api_key: str = Field("", env="GROQ_API_KEY")
    gemini_api_key: str = Field("", env="GEMINI_API_KEY")
    zhipu_api_key: str = Field("", env="ZHIPU_API_KEY")
    
    # Audio & TTS
    audio_max_duration_seconds: int = 60
    audio_supported_formats: list = ["webm", "wav", "mp3", "ogg"]
    
    # Embeddings
    embedding_model: str = "sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2"
    embedding_dimension: int = 768 # Gemini default to avoid mismatch
    
    # Timeouts & Retries
    default_timeout: float = 30.0
    long_timeout: float = 60.0
    max_retries: int = 3

    # LLM & RAG
    llm_model: str = "llama-3.1-8b-instant"
    llm_model_complex: str = "llama-3.3-70b-versatile"
    glm_model: str = "glm-4.7"
    llm_temperature: float = 0.4
    llm_max_tokens: int = 1200
    
    # Observabilidade
    langsmith_api_key: str = Field("", env="LANGSMITH_API_KEY")
    langchain_tracing_v2: bool = False
    langchain_project: str = "treq-enterprise"
    
    # Billing (Placeholder for Stage 5)
    stripe_api_key: str = ""
    stripe_webhook_secret: str = ""

    class Config:
        env_file = ".env"
        case_sensitive = False
        extra = "ignore"  # Ignorar variáveis extras no .env


@lru_cache()
def get_settings() -> Settings:
    """Singleton pattern para configurações."""
    return Settings()

