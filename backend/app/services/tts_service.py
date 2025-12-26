"""
Serviço de Text-to-Speech (TTS) usando Gemini API.
"""
import base64
import mimetypes
import re
import struct
from typing import Optional
from loguru import logger
from google import genai
from google.genai import types
from app.config import get_settings

settings = get_settings()


class TTSService:
    """Serviço de síntese de voz (texto para áudio) usando Gemini TTS."""
    
    def __init__(self):
        if not settings.gemini_api_key:
            raise ValueError("GEMINI_API_KEY não configurada no .env")
        self.client = genai.Client(api_key=settings.gemini_api_key)
        self.model = "gemini-2.5-flash-preview-tts"  # Modelo otimizado para custo e latência
        logger.info("✅ TTSService inicializado (Gemini TTS - Flash Preview)")
    
    async def synthesize_speech(
        self,
        text: str,
        language: Optional[str] = "pt-BR",
        voice: Optional[str] = "Charon"
    ) -> Optional[bytes]:
        """
        Converte texto em áudio usando Gemini TTS API.
        
        Args:
            text: Texto a ser convertido em áudio
            language: Código de idioma (padrão: "pt-BR")
            voice: Nome da voz predefinida (padrão: "Charon")
            
        Returns:
            bytes: Dados de áudio em formato WAV ou None se erro
        """
        try:
            if not text or len(text.strip()) == 0:
                logger.warning("Texto vazio para síntese de voz")
                return None
            
            logger.info(f"Sintetizando áudio: {len(text)} caracteres, voz: {voice}")
            
            contents = [
                types.Content(
                    role="user",
                    parts=[
                        types.Part.from_text(text=text),
                    ],
                ),
            ]
            
            generate_content_config = types.GenerateContentConfig(
                temperature=1,
                response_modalities=["audio"],
                speech_config=types.SpeechConfig(
                    voice_config=types.VoiceConfig(
                        prebuilt_voice_config=types.PrebuiltVoiceConfig(
                            voice_name=voice
                        )
                    )
                ),
            )
            
            # Coletar chunks de áudio
            audio_chunks = []
            for chunk in self.client.models.generate_content_stream(
                model=self.model,
                contents=contents,
                config=generate_content_config,
            ):
                if (
                    chunk.candidates is None
                    or chunk.candidates[0].content is None
                    or chunk.candidates[0].content.parts is None
                ):
                    continue
                
                part = chunk.candidates[0].content.parts[0]
                
                # Se há dados de áudio inline
                if part.inline_data and part.inline_data.data:
                    inline_data = part.inline_data
                    audio_data = inline_data.data
                    mime_type = inline_data.mime_type
                    
                    # Converter para WAV se necessário
                    if mime_type and not mime_type.endswith("/wav"):
                        wav_data = self._convert_to_wav(audio_data, mime_type)
                        audio_chunks.append(wav_data)
                    else:
                        audio_chunks.append(audio_data)
                elif hasattr(part, 'text') and part.text:
                    # Log de texto se houver (normalmente não há para TTS)
                    logger.debug(f"Chunk de texto recebido: {part.text[:50]}...")
            
            if not audio_chunks:
                logger.warning("Nenhum chunk de áudio recebido da API")
                return None
            
            # Combinar todos os chunks em um único áudio
            combined_audio = b''.join(audio_chunks)
            logger.info(f"✅ Áudio sintetizado: {len(combined_audio)} bytes")
            return combined_audio
            
        except Exception as e:
            error_msg = str(e)
            
            # Verificar se é erro de quota excedida (429)
            if "429" in error_msg or "RESOURCE_EXHAUSTED" in error_msg or "quota" in error_msg.lower():
                logger.warning(
                    "⚠️ Gemini TTS quota excedida ou não disponível no free tier. "
                    "Usando fallback para Web Speech API no frontend."
                )
                # Retornar None para ativar fallback no frontend
                return None
            
            logger.error(f"Erro ao sintetizar fala: {e}")
            import traceback
            logger.error(traceback.format_exc())
            return None
    
    def _convert_to_wav(self, audio_data: bytes, mime_type: str) -> bytes:
        """
        Converte dados de áudio para formato WAV.
        
        Args:
            audio_data: Dados de áudio brutos
            mime_type: Tipo MIME do áudio (ex: "audio/L16;rate=24000")
            
        Returns:
            bytes: Dados de áudio em formato WAV completo
        """
        parameters = self._parse_audio_mime_type(mime_type)
        bits_per_sample = parameters["bits_per_sample"]
        sample_rate = parameters["rate"]
        num_channels = 1
        data_size = len(audio_data)
        bytes_per_sample = bits_per_sample // 8
        block_align = num_channels * bytes_per_sample
        byte_rate = sample_rate * block_align
        chunk_size = 36 + data_size
        
        # Estrutura do header WAV (http://soundfile.sapp.org/doc/WaveFormat/)
        header = struct.pack(
            "<4sI4s4sIHHIIHH4sI",
            b"RIFF",          # ChunkID
            chunk_size,       # ChunkSize
            b"WAVE",          # Format
            b"fmt ",          # Subchunk1ID
            16,               # Subchunk1Size (16 for PCM)
            1,                # AudioFormat (1 for PCM)
            num_channels,     # NumChannels
            sample_rate,      # SampleRate
            byte_rate,        # ByteRate
            block_align,      # BlockAlign
            bits_per_sample,  # BitsPerSample
            b"data",          # Subchunk2ID
            data_size         # Subchunk2Size
        )
        
        return header + audio_data
    
    def _parse_audio_mime_type(self, mime_type: str) -> dict:
        """
        Extrai parâmetros de áudio do tipo MIME.
        
        Args:
            mime_type: Tipo MIME (ex: "audio/L16;rate=24000")
            
        Returns:
            dict: {"bits_per_sample": int, "rate": int}
        """
        bits_per_sample = 16  # Padrão
        rate = 24000  # Padrão
        
        parts = mime_type.split(";")
        for param in parts:
            param = param.strip()
            if param.lower().startswith("rate="):
                try:
                    rate_str = param.split("=", 1)[1]
                    rate = int(rate_str)
                except (ValueError, IndexError):
                    pass
            elif param.startswith("audio/L"):
                try:
                    bits_per_sample = int(param.split("L", 1)[1])
                except (ValueError, IndexError):
                    pass
        
        return {"bits_per_sample": bits_per_sample, "rate": rate}

