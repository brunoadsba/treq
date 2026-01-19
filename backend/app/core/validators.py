from pydantic import BaseModel, Field, validator
from typing import Optional, List
import re

class MessageSanitizer:
    """Sanitizador de mensagens com whitelisting agressivo"""
    
    # Caracteres permitidos: alfanuméricos, acentuação básica, pontuação comum e espaços
    # Bloqueia tags HTML (<, >), colchetes de script, etc.
    SAFE_PATTERN = re.compile(r'[^a-zA-Z0-9áéíóúàèìòùâêîôûãõçÁÉÍÓÚÀÈÌÒÙÂÊÎÔÛÃÕÇ\s\.,!\?\(\)\-\:\;\/]')

    @classmethod
    def sanitize(cls, text: str) -> str:
        if not text:
            return ""
        # Remove caracteres que não estão no whitelist
        return cls.SAFE_PATTERN.sub('', text).strip()

class ChatMessageRequest(BaseModel):
    message: str = Field(..., min_length=1, max_length=10000)
    user_id: Optional[str] = Field(None, pattern=r'^[a-f0-9-]{36}$')

    @validator('message')
    def sanitize_content(cls, v):
        return MessageSanitizer.sanitize(v)

class FileUploadRequest(BaseModel):
    filename: str = Field(..., max_length=255)
    content_type: str = Field(..., pattern=r'^(application/pdf|text/plain|text/markdown|image/jpeg|image/png)$')
    
    @validator('filename')
    def validate_filename(cls, v):
        # Prevenir Path Traversal e nomes maliciosos
        if '..' in v or '/' in v or '\\' in v:
            raise ValueError("Nome de arquivo inválido")
        return v

class DocumentQueryRequest(BaseModel):
    query: str = Field(..., min_length=2, max_length=500)
    limit: int = Field(5, ge=1, le=20)

    @validator('query')
    def sanitize_query(cls, v):
        return MessageSanitizer.sanitize(v)
