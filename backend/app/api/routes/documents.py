"""
Rotas da API para upload e gerenciamento de documentos.
Endpoint para upload de PDF/DOCX/PPTX/Excel e indexação automática no RAG.
"""
from fastapi import APIRouter, HTTPException, Depends, UploadFile, File, Form
from pydantic import BaseModel
from typing import Optional
from pathlib import Path
from loguru import logger
from datetime import datetime

from app.services.document_converter import DocumentConverterService
from app.core.chunking_service import ChunkingService
from app.core.rag_service import RAGService

router = APIRouter(prefix="/documents", tags=["documents"])

# Instâncias singleton dos serviços
_converter_service: Optional[DocumentConverterService] = None
_chunking_service: Optional[ChunkingService] = None
_rag_service: Optional[RAGService] = None


def get_converter_service() -> DocumentConverterService:
    """Retorna instância singleton do DocumentConverterService."""
    global _converter_service
    if _converter_service is None:
        _converter_service = DocumentConverterService()
    return _converter_service


def get_chunking_service() -> ChunkingService:
    """Retorna instância singleton do ChunkingService."""
    global _chunking_service
    if _chunking_service is None:
        _chunking_service = ChunkingService(chunk_size=500, chunk_overlap=100)
    return _chunking_service


def get_rag_service() -> RAGService:
    """Retorna instância singleton do RAGService."""
    global _rag_service
    if _rag_service is None:
        _rag_service = RAGService()
    return _rag_service


class DocumentUploadResponse(BaseModel):
    """Model de resposta para upload de documento."""
    success: bool
    chunks_indexed: int
    message: str


# Formatos suportados
SUPPORTED_EXTENSIONS = {'.pdf', '.docx', '.pptx', '.xlsx', '.xls'}
MAX_FILE_SIZE = 10 * 1024 * 1024  # 10MB


def validate_file(file: UploadFile) -> None:
    """
    Valida formato e tamanho do arquivo.
    
    Raises:
        HTTPException: Se arquivo inválido
    """
    # Validar extensão
    file_extension = Path(file.filename).suffix.lower()
    if file_extension not in SUPPORTED_EXTENSIONS:
        raise HTTPException(
            status_code=400,
            detail=f"Formato não suportado: {file_extension}. "
                   f"Formatos aceitos: {', '.join(SUPPORTED_EXTENSIONS)}"
        )


@router.post("/upload", response_model=DocumentUploadResponse)
async def upload_document(
    file: UploadFile = File(...),
    document_type: Optional[str] = Form(None),
    converter: DocumentConverterService = Depends(get_converter_service),
    chunking: ChunkingService = Depends(get_chunking_service),
    rag: RAGService = Depends(get_rag_service)
):
    """
    Endpoint para upload e indexação automática de documentos.
    
    Aceita PDF, DOCX, PPTX e Excel (.xlsx, .xls).
    O documento é convertido para Markdown, dividido em chunks
    e indexado automaticamente no RAG.
    
    Args:
        file: Arquivo a ser enviado
        document_type: Tipo do documento (opcional, ex: "manual", "procedimento", "planilha")
        
    Returns:
        DocumentUploadResponse: Estatísticas da indexação
    """
    try:
        logger.info(f"📄 Upload recebido: {file.filename} (tipo: {document_type or 'unknown'})")
        
        # Validar arquivo
        validate_file(file)
        
        # Ler conteúdo do arquivo
        file_content = await file.read()
        file_size = len(file_content)
        
        # Validar tamanho
        if file_size > MAX_FILE_SIZE:
            raise HTTPException(
                status_code=400,
                detail=f"Arquivo muito grande: {file_size / 1024 / 1024:.2f}MB. "
                       f"Tamanho máximo: {MAX_FILE_SIZE / 1024 / 1024}MB"
            )
        
        if file_size == 0:
            raise HTTPException(status_code=400, detail="Arquivo vazio")
        
        logger.info(f"Arquivo lido: {file_size} bytes")
        
        # Converter para Markdown
        logger.info("Convertendo documento para Markdown...")
        markdown_content = converter.convert_bytes(file_content, file.filename)
        
        if not markdown_content:
            raise HTTPException(
                status_code=500,
                detail="Erro ao converter documento. Verifique se o arquivo é válido."
            )
        
        logger.info(f"Documento convertido: {len(markdown_content)} caracteres")
        
        # Preparar metadata base
        base_metadata = {
            'document_type': document_type or 'unknown',
            'filename': file.filename,
            'file_size': file_size,
            'original_filename': file.filename,
            'file_format': Path(file.filename).suffix.lower(),
            'uploaded_at': datetime.now().isoformat(),
        }
        
        # Fazer chunking semântico
        logger.info("Dividindo documento em chunks...")
        chunks = chunking.chunk_markdown(
            content=markdown_content,
            source=file.filename,
            metadata=base_metadata
        )
        
        logger.info(f"Documento dividido em {len(chunks)} chunks")
        
        # Indexar cada chunk no RAG
        indexed_count = 0
        failed_count = 0
        
        for i, chunk in enumerate(chunks, 1):
            try:
                # Combinar metadata base com metadata do chunk
                chunk_metadata = {
                    **base_metadata,
                    **chunk['metadata'],  # Metadata do chunking (section, hierarchy, etc.)
                    'chunk_index': i,
                    'total_chunks': len(chunks)
                }
                
                doc_id = rag.index_document(
                    content=chunk['content'],
                    metadata=chunk_metadata
                )
                
                if doc_id:
                    indexed_count += 1
                    logger.debug(f"✅ Chunk {i}/{len(chunks)} indexado: {doc_id[:8]}...")
                else:
                    failed_count += 1
                    logger.warning(f"⚠️ Falha ao indexar chunk {i}/{len(chunks)}")
                    
            except Exception as e:
                failed_count += 1
                logger.error(f"Erro ao indexar chunk {i}/{len(chunks)}: {e}")
                import traceback
                logger.error(traceback.format_exc())
        
        # Resposta
        if indexed_count == 0:
            raise HTTPException(
                status_code=500,
                detail="Nenhum chunk foi indexado. Verifique os logs para mais detalhes."
            )
        
        message = f"Documento indexado com sucesso: {indexed_count} chunks"
        if failed_count > 0:
            message += f" ({failed_count} falhas)"
        
        logger.info(f"✅ Upload concluído: {file.filename} - {indexed_count} chunks indexados")
        
        return DocumentUploadResponse(
            success=True,
            chunks_indexed=indexed_count,
            message=message
        )
        
    except HTTPException:
        # Re-raise HTTP exceptions
        raise
    except Exception as e:
        logger.error(f"Erro ao processar upload: {e}")
        import traceback
        logger.error(traceback.format_exc())
        raise HTTPException(
            status_code=500,
            detail=f"Erro interno ao processar documento: {str(e)}"
        )


@router.get("/health")
async def health_check():
    """Health check do endpoint de documentos."""
    return {
        "status": "ok",
        "supported_formats": list(SUPPORTED_EXTENSIONS),
        "max_file_size_mb": MAX_FILE_SIZE / 1024 / 1024
    }

