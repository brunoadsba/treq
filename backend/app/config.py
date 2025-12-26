"""
Configurações da aplicação usando Pydantic Settings.
"""
from pydantic_settings import BaseSettings
from functools import lru_cache


class Settings(BaseSettings):
    """Configurações da aplicação."""
    
    # Aplicação
    app_name: str = "Treq Assistente Operacional"
    environment: str = "development"
    debug: bool = True
    secret_key: str = "change-this-in-production"  # Valor padrão para desenvolvimento
    
    # Backend
    host: str = "0.0.0.0"
    port: int = 8000
    
    # Supabase
    supabase_url: str = ""
    supabase_key: str = ""  # Service role key
    supabase_anon_key: str = ""
    database_password: str = ""  # Database password (backup local, não usada no código inicialmente)
    
    # APIs
    groq_api_key: str = ""
    gemini_api_key: str = ""
    
    # Audio
    audio_max_duration_seconds: int = 60  # Máximo 60 segundos de áudio
    audio_supported_formats: list = ["webm", "wav", "mp3", "ogg"]
    
    # Embeddings
    embedding_model: str = "sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2"
    embedding_dimension: int = 384
    
    # LLM
    llm_model: str = "llama-3.1-8b-instant"
    llm_temperature: float = 0.4  # Aumentado de 0.3 para menos conservador (análise consolidada)
    llm_max_tokens: int = 800  # Aumentado de 500 para respostas mais completas (análise consolidada)
    
    # Rate Limiting
    rate_limit_per_minute: int = 60
    
    # Logging
    log_level: str = "INFO"
    
    class Config:
        env_file = ".env"
        case_sensitive = False


@lru_cache()
def get_settings() -> Settings:
    """Retorna instância singleton das configurações."""
    return Settings()

