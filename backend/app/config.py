"""
Configurações da aplicação usando Pydantic Settings.
"""
from pydantic_settings import BaseSettings
from pydantic import HttpUrl, Field
from functools import lru_cache


class Settings(BaseSettings):
    """Configurações da aplicação."""
    
    # Aplicação
    app_name: str = "Treq Assistente Operacional"
    environment: str = "development"
    debug: bool = True
    secret_key: str = Field(..., env="SECRET_KEY", description="Secret key obrigatória para segurança")
    
    # Backend
    host: str = "0.0.0.0"
    port: int = 8000
    
    # Supabase
    supabase_url: HttpUrl = Field(..., description="URL do Supabase (deve ser HTTPS)")
    supabase_key: str = ""  # Service role key
    supabase_anon_key: str = ""
    database_password: str = ""  # Database password (backup local, não usada no código inicialmente)
    
    # APIs
    groq_api_key: str = ""
    gemini_api_key: str = ""
    zhipu_api_key: str = ""  # API Key para Zhipu AI (GLM 4)
    
    # Audio
    audio_max_duration_seconds: int = 60  # Máximo 60 segundos de áudio
    audio_supported_formats: list = ["webm", "wav", "mp3", "ogg"]
    
    # Embeddings
    embedding_model: str = "sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2"
    embedding_dimension: int = 384
    
    # LLM
    llm_model: str = "llama-3.1-8b-instant"  # Nível 1: Modelo padrão (rápido)
    llm_model_complex: str = "llama-3.3-70b-versatile"  # Nível 2: Modelo para queries complexas
    glm_model: str = "glm-4.7"  # Nível 3: Modelo GLM 4 para tarefas pesadas
    use_dynamic_model: bool = True  # Ativar seleção dinâmica
    use_3_level_routing: bool = True  # Ativar roteamento em 3 níveis (8B → 70B → GLM 4)
    llm_temperature: float = 0.4  # Aumentado de 0.3 para menos conservador (análise consolidada)
    llm_max_tokens: int = 1200  # Aumentado de 800 para 1200 para garantir respostas completas (pode ser sobrescrito por .env)
    
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

