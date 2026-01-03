"""
Serviço de Text-to-Speech (TTS) usando Google Gemini (Novo SDK google-genai) com Fallback para Edge TTS.
"""
from typing import Optional, Any
from loguru import logger
import time
from app.config import get_settings
from app.utils.text_utils import truncate_for_tts

settings = get_settings()

class TTSService:
    """Serviço de síntese de voz usando Gemini 2.0+ (Primário) e Edge TTS (Fallback)."""
    
    def __init__(self):
        self.api_key = settings.gemini_api_key
        self._client: Optional[Any] = None
        logger.info("✅ TTSService pronto para inicialização (Lazy Loading + Multi-Provider)")
        
    def _get_client(self) -> Any:
        """Lazy loading do cliente Google GenAI."""
        if self._client is None:
            if not self.api_key:
                logger.error("GEMINI_API_KEY não configurada no .env")
                raise ValueError("GEMINI_API_KEY não configurada")
            try:
                from google import genai
                self._client = genai.Client(api_key=self.api_key)
                logger.info("✨ Cliente Google GenAI inicializado")
            except Exception as e:
                logger.error(f"Erro ao inicializar cliente Google GenAI: {e}")
                raise
        return self._client
    
    async def _synthesize_with_edge_tts(self, text: str, voice: str) -> bytes:
        """Fallback: Sintetiza usando Edge TTS gratuito (Microsoft Azure Neural Voices)."""
        import edge_tts
        
        voice_map = {
            "Charon": "pt-BR-AntonioNeural",
            "Kore": "pt-BR-FranciscaNeural",
            "Fenrir": "pt-BR-FabioNeural",
            "Puck": "pt-BR-ThalitaNeural",
            "Aoede": "pt-BR-FranciscaNeural"
        }
        edge_voice = voice_map.get(voice, "pt-BR-AntonioNeural")
        
        try:
            logger.info(f"🔄 Iniciando Fallback TTS (Edge) com voz {edge_voice}")
            communicate = edge_tts.Communicate(text, edge_voice)
            audio_data = b""
            async for chunk in communicate.stream():
                if chunk["type"] == "audio":
                    audio_data += chunk["data"]
            
            if audio_data:
                logger.info(f"✅ Fallback TTS (Edge) concluído: {len(audio_data)} bytes")
                return audio_data
        except Exception as e:
            logger.error(f"❌ Falha crítica no Fallback TTS (Edge): {e}")
        
        raise ValueError("Todos os provedores de TTS (Gemini & Edge) falharam.")

    async def synthesize_speech(
        self,
        text: str,
        voice: str = "Charon",
        language: str = "pt-BR"
    ) -> bytes:
        """
        Sintetiza texto em áudio usando Gemini 2.0 (Premium).
        Fallback automático para Edge TTS em caso de erro ou cota esgotada.
        """
        voice_map = {
            "default": "Charon", "charon": "Charon", "puck": "Puck", 
            "kore": "Kore", "fenrir": "Fenrir", "aoede": "Aoede"
        }
        target_voice = voice_map.get(voice.lower(), "Charon")
        clean_text = truncate_for_tts(text)
        start_time = time.time()

        try:
            client = self._get_client()
            logger.info(f"🎙️ Tentando Gemini TTS (Voz: {target_voice})")
            
            response = client.models.generate_content(
                model="gemini-2.0-flash",
                contents=clean_text,
                config={
                    "speech_config": {
                        "voice_config": {
                            "prebuilt_voice_config": {
                                "voice_name": target_voice 
                            }
                        }
                    }
                }
            )
            
            audio_bytes = None
            if hasattr(response, 'audio') and response.audio:
                audio_bytes = response.audio.data
            elif response.candidates and len(response.candidates) > 0:
                for part in response.candidates[0].content.parts:
                    if hasattr(part, 'inline_data') and part.inline_data:
                        if 'audio' in part.inline_data.mime_type:
                            audio_bytes = part.inline_data.data
                            break
            
            if audio_bytes:
                elapsed = time.time() - start_time
                logger.info(f"✅ Gemini TTS concluído em {elapsed:.2f}s")
                return audio_bytes
                
            raise ValueError("Resposta Gemini sem áudio.")

        except Exception as e:
            if "429" in str(e) or "RESOURCE_EXHAUSTED" in str(e):
                logger.warning("⚠️ Cota Gemini esgotada. Usando Edge TTS...")
            else:
                logger.error(f"❌ Gemini TTS falhou ({e}). Usando Edge TTS...")
            
            return await self._synthesize_with_edge_tts(clean_text, target_voice)
