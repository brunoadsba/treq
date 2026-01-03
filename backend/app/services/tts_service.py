"""
Serviço de Text-to-Speech (TTS) usando Google Gemini (Novo SDK google-genai).
"""
from typing import Optional, Any
from loguru import logger
import time
from app.config import get_settings
from app.utils.text_utils import truncate_for_tts

settings = get_settings()

class TTSService:
    """Serviço de síntese de voz usando Gemini 2.0+."""
    
    def __init__(self):
        self.api_key = settings.gemini_api_key
        self._client: Optional[Any] = None
        logger.info("✅ TTSService pronto para inicialização (Lazy Loading)")
        
    def _get_client(self) -> Any:
        """
        Lazy loading do cliente Google GenAI.
        Evita carregar o SDK pesado e validar credenciais durante o boot do Render.
        """
        if self._client is None:
            if not self.api_key:
                logger.error("GEMINI_API_KEY não configurada no .env")
                raise ValueError("GEMINI_API_KEY não configurada")
                
            try:
                # O import 'from google import genai' agora funciona sem conflito
                # após a remoção do google-generativeai legado.
                from google import genai
                self._client = genai.Client(api_key=self.api_key)
                logger.info("✨ Cliente Google GenAI (SDK Novo) inicializado com sucesso")
            except ImportError:
                logger.error("SDK google-genai não encontrado. Verifique o requirements.txt")
                raise
            except Exception as e:
                logger.error(f"Erro ao inicializar cliente Google GenAI: {e}")
                raise
                
        return self._client
    
    async def synthesize_speech(
        self,
        text: str,
        voice: str = "Charon",
        language: str = "pt-BR"
    ) -> bytes:
        """
        Sintetiza texto em áudio usando os modelos multimodais do Gemini.
        """
        try:
            # 1. Mapear voz padrão se vier como "default"
            voice_map = {
                "default": "Charon",
                "charon": "Charon",
                "puck": "Puck",
                "kore": "Kore",
                "fenrir": "Fenrir",
                "aoede": "Aoede"
            }
            target_voice = voice_map.get(voice.lower(), "Charon")
            
            # 2. Truncar texto para UX (500 chars max)
            clean_text = truncate_for_tts(text)
            
            client = self._get_client()
            start_time = time.time()
            
            logger.info(f"🎙️ Iniciando síntese TTS para {len(clean_text)} caracteres (Voz: {target_voice})")
            
            # 3. Chamada ao modelo Gemini para geração de áudio
            # Usando gemini-2.0-flash (GA) ou flash-exp conforme disponibilidade
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
            
            # 4. Extrair áudio da resposta 
            # O áudio vem no corpo da resposta multimodal
            if not response.audio:
                # Fallback para extração manual das partes se o atributo .audio estiver vazio
                # mas o dado estiver presente em parts
                try:
                    audio_bytes = response.candidates[0].content.parts[0].inline_data.data
                except:
                    logger.error("Gemini não retornou dados de áudio.")
                    raise ValueError("Falha na síntese de áudio (Sem dados)")
            else:
                audio_bytes = response.audio.data
            
            elapsed = time.time() - start_time
            logger.info(f"✅ TTS concluído com sucesso: {len(audio_bytes)} bytes em {elapsed:.2f}s")
            
            return audio_bytes
            
        except Exception as e:
            logger.error(f"❌ Erro crítico no TTSService: {e}")
            raise ValueError(f"Erro na síntese de voz: {str(e)}")
