"""
Rotas para a feature de visão computacional avançada.
Localizado em src/features/vision/backend/routes.py seguindo a arquitetura modular.
"""
from fastapi import APIRouter, UploadFile, File, HTTPException, BackgroundTasks
from typing import Optional, Dict, Any
from loguru import logger
import uuid

from .multimodal_service import multimodal_service
from app.api.routes.chat_modules.models import ChatResponse
from app.core.rag_service import RAGService

router = APIRouter(prefix="/vision", tags=["vision"])

@router.post("/upload-multimodal")
async def upload_multimodal(
    file: UploadFile = File(...),
    prompt: Optional[str] = None,
    extract_type: Optional[str] = None # 'table', 'chart', 'form'
):
    """
    Recebe imagem/documento, processa via Gemini Vision e retorna análise ou extração.
    """
    try:
        content = await file.read()
        filename = file.filename
        
        logger.info(f"📸 Recebido arquivo multimodal: {filename} (size: {len(content)} bytes)")
        
        # 1. Se extract_type for fornecido, foca na extração estruturada
        if extract_type:
            data = await multimodal_service.extract_structured_data(content, extract_type)
            return {
                "success": True,
                "type": extract_type,
                "data": data,
                "filename": filename
            }
        
        # 2. Caso contrário, faz descrição e análise analítica
        analysis = await multimodal_service.analyze_document_page(content)
        description = await multimodal_service.describe_image(content, prompt)
        
        # 3. Preparar para indexação no RAG (opcional, dependendo do fluxo)
        # return analysis enriquecido
        return {
            "success": True,
            "filename": filename,
            "description": description,
            "analysis": analysis
        }
        
    except Exception as e:
        logger.error(f"Erro no upload multimodal: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/analyze-webcam")
async def analyze_webcam(
    base64_image: Dict[str, str], # Recebe { "image": "data:image/jpeg;base64,..." }
    prompt: Optional[str] = None
):
    """
    Recebe captura de webcam/câmera direta para análise rápida.
    """
    try:
        import base64
        import io
        
        img_data = base64_image.get("image", "")
        if "base64," in img_data:
            img_data = img_data.split("base64,")[1]
            
        content = base64.b64decode(img_data)
        
        logger.info(f"📸 Recebida captura de webcam/câmera (size: {len(content)} bytes)")
        
        analysis = await multimodal_service.analyze_document_page(content)
        description = await multimodal_service.describe_image(content, prompt)
        
        return {
            "success": True,
            "description": description,
            "analysis": analysis
        }
    except Exception as e:
        logger.error(f"Erro ao analisar webcam: {e}")
        raise HTTPException(status_code=500, detail=str(e))
