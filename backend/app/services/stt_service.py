"""
Serviço de Speech-to-Text (STT) usando Groq Whisper via API HTTP.
"""
import io
from typing import Optional
from loguru import logger
import httpx
from tenacity import retry, wait_exponential, stop_after_attempt, retry_if_exception, before_sleep_log
from app.config import get_settings

settings = get_settings()


class STTService:
    """Serviço de transcrição de áudio para texto."""
    
    def __init__(self):
        if not settings.groq_api_key:
            raise ValueError("GROQ_API_KEY não configurada no .env")
        self.api_key = settings.groq_api_key
        self.base_url = "https://api.groq.com/openai/v1"
        logger.info("✅ STTService inicializado (Groq Whisper)")
    
    @retry(
        wait=wait_exponential(multiplier=1, min=2, max=10),
        stop=stop_after_attempt(3),
        retry=retry_if_exception(lambda e: "429" in str(e) or "rate limit" in str(e).lower() or isinstance(e, httpx.TimeoutException)),
        before_sleep=before_sleep_log(logger, "WARNING"),
        reraise=True
    )
    async def transcribe_audio(
        self,
        audio_data: bytes,
        language: Optional[str] = "pt"
    ) -> str:
        """
        Transcreve áudio para texto usando Groq Whisper API com retentativas.
        """
        try:
            # Criar arquivo temporário em memória
            audio_file = io.BytesIO(audio_data)
            audio_file.name = "audio.webm"  # Nome do arquivo para API
            
            # Preparar requisição para Groq Whisper API
            async with httpx.AsyncClient(timeout=30.0) as client:
                files = {
                    "file": ("audio.webm", audio_file, "audio/webm")
                }
                data = {
                    "model": "whisper-large-v3",
                    "language": language,
                    "response_format": "text"
                }
                headers = {
                    "Authorization": f"Bearer {self.api_key}"
                }
                
                response = await client.post(
                    f"{self.base_url}/audio/transcriptions",
                    files=files,
                    data=data,
                    headers=headers
                )
                
                if response.status_code == 429:
                    raise ValueError(f"Rate limit atingido na Groq (429): {response.text}")
                
                if response.status_code != 200:
                    error_msg = response.text
                    logger.error(f"Erro na API Groq: {response.status_code} - {error_msg}")
                    raise ValueError(f"Erro na API Groq: {error_msg}")
                
                transcript = response.text.strip()
                logger.info(f"✅ Áudio transcrito: {len(transcript)} caracteres")
                return transcript
                
        except httpx.TimeoutException:
            logger.error("Timeout ao transcrever áudio")
            raise ValueError("Timeout ao transcrever áudio. Tente novamente.")
        except Exception as e:
            logger.error(f"Erro ao transcrever áudio: {e}")
            import traceback
            logger.error(traceback.format_exc())
            raise ValueError(f"Erro ao transcrever áudio: {str(e)}")
