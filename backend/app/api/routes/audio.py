"""
Rotas da API para processamento de áudio (STT e TTS).
"""
from fastapi import APIRouter, HTTPException, Depends, UploadFile, File, Query
from pydantic import BaseModel, Field
from typing import Optional
from loguru import logger

from app.services.stt_service import STTService
from app.services.tts_service import TTSService

router = APIRouter(prefix="/audio", tags=["audio"])

# Instâncias singleton dos serviços
_stt_service: Optional[STTService] = None
_tts_service: Optional[TTSService] = None


def get_stt_service() -> STTService:
    """Retorna instância singleton do STT Service."""
    global _stt_service
    if _stt_service is None:
        _stt_service = STTService()
    return _stt_service


def get_tts_service() -> TTSService:
    """Retorna instância singleton do TTS Service."""
    global _tts_service
    if _tts_service is None:
        _tts_service = TTSService()
    return _tts_service


class AudioTranscribeRequest(BaseModel):
    """Request para transcrição de áudio."""
    user_id: str = Field(..., description="ID do usuário")
    conversation_id: Optional[str] = Field(None, description="ID da conversa")
    language: Optional[str] = Field("pt", description="Código de idioma")


class AudioTranscribeResponse(BaseModel):
    """Response da transcrição de áudio."""
    text: str = Field(..., description="Texto transcrito")
    language: str = Field(..., description="Idioma detectado")


class AudioSynthesizeRequest(BaseModel):
    """Request para síntese de áudio."""
    text: str = Field(..., description="Texto a ser convertido em áudio")
    language: Optional[str] = Field("pt-BR", description="Código de idioma")
    voice: Optional[str] = Field("default", description="Voz a ser usada")


class AudioSynthesizeResponse(BaseModel):
    """Response da síntese de áudio."""
    audio_url: Optional[str] = Field(None, description="Data URI do áudio gerado (formato: data:audio/wav;base64,...)")
    use_web_speech: bool = Field(False, description="Se deve usar Web Speech API no frontend (fallback)")
    text: str = Field(..., description="Texto para síntese")


@router.post("/transcribe", response_model=AudioTranscribeResponse)
async def transcribe_audio(
    audio_file: UploadFile = File(...),
    user_id: Optional[str] = Query(None),
    conversation_id: Optional[str] = Query(None),
    language: Optional[str] = Query("pt"),
    stt_service: STTService = Depends(get_stt_service)
):
    """
    Transcreve áudio para texto usando Groq Whisper.
    
    Processo:
    1. Recebe arquivo de áudio
    2. Transcreve usando STT Service
    3. Retorna texto transcrito
    """
    try:
        # Validar formato de áudio
        if audio_file.content_type and not any(
            fmt in audio_file.content_type for fmt in ["audio", "video"]
        ):
            raise HTTPException(
                status_code=400,
                detail="Arquivo deve ser de áudio (webm, wav, mp3, etc.)"
            )
        
        # Ler dados de áudio
        audio_data = await audio_file.read()
        
        if len(audio_data) == 0:
            raise HTTPException(status_code=400, detail="Arquivo de áudio vazio")
        
        logger.info(
            f"Transcrevendo áudio: {len(audio_data)} bytes, "
            f"tipo: {audio_file.content_type}"
        )
        
        # Transcrever
        transcript = await stt_service.transcribe_audio(
            audio_data=audio_data,
            language=language
        )
        
        return AudioTranscribeResponse(
            text=transcript,
            language=language
        )
        
    except ValueError as e:
        logger.error(f"Erro de validação na transcrição: {e}")
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        logger.error(f"Erro ao transcrever áudio: {e}")
        import traceback
        logger.error(traceback.format_exc())
        raise HTTPException(status_code=500, detail=f"Erro ao transcrever áudio: {str(e)}")


@router.post("/synthesize", response_model=AudioSynthesizeResponse)
async def synthesize_audio(
    request: AudioSynthesizeRequest,
    tts_service: TTSService = Depends(get_tts_service)
):
    """
    Converte texto em áudio usando Gemini TTS.
    
    Nota: Se TTS não disponível, retorna flag para usar Web Speech API no frontend.
    """
    import time
    
    try:
        if not request.text or len(request.text.strip()) == 0:
            raise HTTPException(status_code=400, detail="Texto não pode estar vazio")
        
        start_time = time.time()
        logger.info(f"Sintetizando áudio para texto: {len(request.text)} caracteres")
        
        # Sintetizar áudio usando Gemini TTS
        audio_data = await tts_service.synthesize_speech(
            text=request.text,
            language=request.language,
            voice=request.voice
        )
        
        elapsed_time = time.time() - start_time
        logger.info(f"⏱️ TTS gerado em {elapsed_time:.2f}s ({len(request.text)} caracteres)")
        
        # Se TTS não retornou áudio, fallback para Web Speech API
        if audio_data is None:
            logger.warning("TTS retornou None - usando fallback Web Speech API")
            return AudioSynthesizeResponse(
                use_web_speech=True,
                text=request.text
            )
        
        # Converter áudio para base64 para retornar via JSON
        import base64
        audio_base64 = base64.b64encode(audio_data).decode('utf-8')
        
        # Retornar áudio gerado (frontend precisa decodificar base64)
        return AudioSynthesizeResponse(
            audio_url=f"data:audio/wav;base64,{audio_base64}",
            use_web_speech=False,
            text=request.text
        )
        
    except Exception as e:
        logger.error(f"Erro ao sintetizar áudio: {e}")
        import traceback
        logger.error(traceback.format_exc())
        # Fallback: retornar texto para Web Speech API
        return AudioSynthesizeResponse(
            use_web_speech=True,
            text=request.text
        )


@router.post("/chat")
async def chat_with_audio(
    audio_file: UploadFile = File(...),
    user_id: Optional[str] = None,
    conversation_id: Optional[str] = None,
    stt_service: STTService = Depends(get_stt_service)
):
    """
    Endpoint combinado: transcreve áudio e processa como chat normal.
    
    Processo:
    1. Transcreve áudio para texto
    2. Processa texto como mensagem normal de chat
    3. Retorna resposta (opcionalmente com áudio)
    """
    try:
        # Transcrever áudio
        audio_data = await audio_file.read()
        transcript = await stt_service.transcribe_audio(audio_data)
        
        logger.info(f"Áudio transcrito: '{transcript}'")
        
        # Criar request de chat com texto transcrito
        chat_request = ChatRequest(
            message=transcript,
            user_id=user_id or "anonymous",
            conversation_id=conversation_id
        )
        
        # Processar como chat normal (reutilizar endpoint existente)
        # Nota: Precisa injetar serviços do chat
        # Por enquanto, retornar transcrição para frontend processar
        
        return {
            "transcript": transcript,
            "message": "Use o endpoint /chat com o texto transcrito"
        }
        
    except Exception as e:
        logger.error(f"Erro no chat com áudio: {e}")
        import traceback
        logger.error(traceback.format_exc())
        raise HTTPException(status_code=500, detail=f"Erro ao processar áudio: {str(e)}")


@router.get("/health")
async def health_check():
    """Health check do endpoint de áudio."""
    return {"status": "ok", "service": "audio"}

