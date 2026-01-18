"""
Rotas da API para upload e gerenciamento de documentos.
Endpoint para upload de PDF/DOCX/PPTX/Excel e indexação automática no RAG.
"""
from fastapi import APIRouter, HTTPException, Depends, UploadFile, File, Form
from pydantic import BaseModel
from pathlib import Path
from loguru import logger
from typing import Optional, TYPE_CHECKING

if TYPE_CHECKING:
    from app.services.document_converter import DocumentConverterService
    from app.core.chunking_service import ChunkingService
    from app.core.rag_service import RAGService
from app.api.routes.documents_helpers import (
    prepare_document_metadata,
    index_document_chunks
)
from app.core.dependencies import get_current_user
from app.core.audit import log_mutation, log_security_event

router = APIRouter(prefix="/documents", tags=["documents"])

# Instâncias singleton dos serviços
_converter_service: Optional['DocumentConverterService'] = None
_chunking_service: Optional['ChunkingService'] = None
_rag_service: Optional['RAGService'] = None


def get_converter_service() -> 'DocumentConverterService':
    """Retorna instância singleton do DocumentConverterService."""
    global _converter_service
    if _converter_service is None:
        from app.services.document_converter import DocumentConverterService
        # Habilitar OCR por padrão para suportar PDFs escaneados e imagens
        _converter_service = DocumentConverterService(enable_ocr=True)
    return _converter_service


def get_chunking_service() -> 'ChunkingService':
    """Retorna instância singleton do ChunkingService."""
    global _chunking_service
    if _chunking_service is None:
        from app.core.chunking_service import ChunkingService
        # Fase 2: Aumentado de 500 para 1200 para preservar mais contexto
        _chunking_service = ChunkingService(chunk_size=1200, chunk_overlap=250)
    return _chunking_service


def get_rag_service() -> 'RAGService':
    """Retorna instância singleton do RAGService."""
    global _rag_service
    if _rag_service is None:
        from app.core.rag_service import RAGService
        _rag_service = RAGService()
    return _rag_service


class DocumentUploadResponse(BaseModel):
    """Model de resposta para upload de documento."""
    success: bool
    chunks_indexed: int
    message: str


# Formatos suportados
SUPPORTED_EXTENSIONS = {'.pdf', '.docx', '.pptx', '.xlsx', '.xls', '.jpg', '.jpeg', '.png', '.gif', '.bmp', '.tiff', '.webp', '.md', '.txt', '.csv'}
MAX_FILE_SIZE = 25 * 1024 * 1024  # 25MB (aumentado de 10MB para permitir documentos maiores)


def validate_file(file: UploadFile) -> None:
    """
    Valida formato e tamanho do arquivo.
    
    Raises:
        HTTPException: Se arquivo inválido
    """
    if not file.filename:
        raise HTTPException(status_code=400, detail="Nome do arquivo não fornecido")
    
    # Validar extensão
    file_extension = Path(file.filename).suffix.lower()
    if file_extension not in SUPPORTED_EXTENSIONS:
        raise HTTPException(
            status_code=400,
            detail=f"Formato não suportado: {file_extension}. "
                   f"Formatos aceitos: {', '.join(SUPPORTED_EXTENSIONS)}"
        )
    
    # Validar nome do arquivo (prevenir path traversal)
    if '..' in file.filename or '/' in file.filename or '\\' in file.filename:
        raise HTTPException(
            status_code=400,
            detail="Nome do arquivo inválido (contém caracteres não permitidos)"
        )


@router.post("/upload", response_model=DocumentUploadResponse)
async def upload_document(
    file: UploadFile = File(...),
    document_type: Optional[str] = Form(None),
    user_message: Optional[str] = Form(None),
    current_user_id: str = Depends(get_current_user),
    converter: 'DocumentConverterService' = Depends(get_converter_service),
    chunking: 'ChunkingService' = Depends(get_chunking_service),
    rag: 'RAGService' = Depends(get_rag_service)
):
    """
    Endpoint para upload e indexação automática de documentos.
    
    Aceita PDF, DOCX, PPTX, Excel (.xlsx, .xls) e imagens (JPEG, PNG, GIF, BMP, TIFF, WEBP).
    O documento é convertido para Markdown, dividido em chunks
    e indexado automaticamente no RAG.
    
    Args:
        file: Arquivo a ser enviado
        document_type: Tipo do documento (opcional, ex: "manual", "procedimento", "planilha")
        user_message: Mensagem do usuário explicando o que fazer com o arquivo (opcional)
        
    Returns:
        DocumentUploadResponse: Estatísticas da indexação
    """
    try:
        logger.info(f"📄 Upload recebido: {file.filename} (tipo: {document_type or 'unknown'})")
        if user_message:
            logger.info(f"💬 Mensagem do usuário: {user_message[:100]}...")
        
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
        
        # Extrair extensão do arquivo para validações adicionais
        file_extension = Path(file.filename).suffix.lower()
        
        # Validação básica de segurança: verificar conteúdo suspeito
        # (apenas para arquivos de texto, não binários)
        if file_extension in ['.docx', '.pptx']:
            # Verificar se não é um arquivo malicioso disfarçado
            # DOCX/PPTX são ZIPs, então verificamos o magic number
            if file_content[:2] != b'PK':  # ZIP magic number
                raise HTTPException(
                    status_code=400,
                    detail="Arquivo inválido: formato não corresponde à extensão"
                )
        
        # Validação de imagens: verificar magic numbers
        if file_extension in ['.jpg', '.jpeg', '.png', '.gif', '.bmp', '.tiff', '.tif', '.webp']:
            # Verificar magic numbers comuns de imagens
            image_magic_numbers = {
                '.jpg': [b'\xff\xd8\xff'],  # JPEG
                '.jpeg': [b'\xff\xd8\xff'],  # JPEG
                '.png': [b'\x89PNG\r\n\x1a\n'],  # PNG
                '.gif': [b'GIF87a', b'GIF89a'],  # GIF
                '.bmp': [b'BM'],  # BMP
                '.tiff': [b'II*\x00', b'MM\x00*'],  # TIFF (little-endian e big-endian)
                '.tif': [b'II*\x00', b'MM\x00*'],  # TIFF
                '.webp': [b'RIFF'],  # WEBP (precisa verificar mais adiante)
            }
            
            magic_numbers = image_magic_numbers.get(file_extension, [])
            is_valid = False
            
            if magic_numbers:
                for magic in magic_numbers:
                    if file_content.startswith(magic):
                        is_valid = True
                        break
                    # WEBP precisa verificar após RIFF
                    if file_extension == '.webp' and file_content.startswith(b'RIFF'):
                        if len(file_content) > 8 and file_content[8:12] == b'WEBP':
                            is_valid = True
                            break
                
                if not is_valid:
                    raise HTTPException(
                        status_code=400,
                        detail=f"Arquivo inválido: {file_extension} não corresponde ao conteúdo real da imagem"
                    )
        
        logger.info(f"Arquivo lido: {file_size} bytes")
        
        # Converter para Markdown
        logger.info("Convertendo documento para Markdown...")
        markdown_content = await converter.convert_bytes(file_content, file.filename)
        
        if not markdown_content:
            if file_extension in ['.jpg', '.jpeg', '.png', '.gif', '.bmp', '.tiff', '.tif', '.webp']:
                raise HTTPException(
                    status_code=400,
                    detail="Não foi possível extrair texto ou descrever o conteúdo desta imagem. Tente uma imagem mais nítida ou aguarde um minuto caso o limite de uso tenha sido atingido."
                )
            raise HTTPException(
                status_code=400,
                detail="O documento parece estar vazio ou não contém texto extraível."
            )
        
        logger.info(f"Documento convertido: {len(markdown_content)} caracteres")
        
        # Preparar metadata base
        base_metadata = prepare_document_metadata(
            file.filename,
            document_type,
            file_size,
            user_id=current_user_id
        )
        
        # Fazer chunking semântico
        logger.info("Dividindo documento em chunks...")
        chunks = chunking.chunk_markdown(
            content=markdown_content,
            source=file.filename,
            metadata=base_metadata
        )
        
        logger.info(f"Documento dividido em {len(chunks)} chunks")
        
        # Prevenção: Limpar versões anteriores do mesmo arquivo antes de indexar a nova
        # Isso evita redundância (mesmo documento indexado n vezes)
        logger.info(f"Limpando chunks antigos para prevenir redundância: {file.filename}")
        deleted_count = rag.delete_by_source(file.filename)
        if deleted_count > 0:
            logger.info(f"Substituindo versão anterior: {deleted_count} chunks removidos")
            log_mutation(
                user_id=current_user_id,
                action="DELETE_PREVIOUS_VERSION",
                resource="DOCUMENT_CHUNKS",
                resource_id=file.filename,
                metadata={"deleted_chunks": deleted_count}
            )
        
        # Indexar chunks no RAG
        indexed_count, failed_count = await index_document_chunks(
            chunks,
            base_metadata,
            rag
        )
        
        # Limpar cache de busca RAG para garantir que novas queries vejam os novos dados
        rag.clear_cache()
        
        # Resposta
        if indexed_count == 0:
            raise HTTPException(
                status_code=500,
                detail="Nenhum chunk foi indexado. Verifique os logs para mais detalhes."
            )
        
        message = f"Documento indexado com sucesso: {indexed_count} chunks"
        if failed_count > 0:
            message += f" ({failed_count} falhas)"
        
        log_mutation(
            user_id=current_user_id,
            action="UPLOAD_DOCUMENT",
            resource="DOCUMENT",
            resource_id=file.filename,
            metadata={
                "chunks": indexed_count,
                "size": file_size,
                "type": document_type
            }
        )
        
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


@router.get("/stats")
async def get_documents_stats(
    current_user_id: str = Depends(get_current_user),
    rag: 'RAGService' = Depends(get_rag_service)
):
    """
    Retorna estatísticas da base de conhecimento.
    
    Returns:
        Dict com estatísticas da base indexada
    """
    try:
        from app.services.supabase_service import get_supabase_client
        from collections import Counter
        
        supabase = get_supabase_client()
        
        # Buscar apenas documentos do usuário (RLS enforced if using authenticated client)
        # Por enquanto, filtro explícito para garantir isolation
        result = supabase.table('knowledge_base').select('*').eq('metadata->>user_id', current_user_id).execute()
        all_documents = result.data
        
        if not all_documents:
            return {
                "total_chunks": 0,
                "total_unique_documents": 0,
                "empty": True
            }
        
        # Calcular estatísticas
        total_chunks = len(all_documents)
        
        # Agrupar por documento original (source)
        sources = Counter(
            doc.get('metadata', {}).get('source', 'unknown')
            for doc in all_documents
        )
        
        # Agrupar por tipo
        types = Counter(
            doc.get('metadata', {}).get('document_type', 'unknown')
            for doc in all_documents
        )
        
        # Tamanhos dos chunks
        sizes = [len(doc.get('content', '')) for doc in all_documents]
        avg_size = sum(sizes) / len(sizes) if sizes else 0
        
        # Chunks problemáticos
        small_chunks = sum(1 for s in sizes if s < 100)
        large_chunks = sum(1 for s in sizes if s > 2000)
        empty_chunks = sum(1 for doc in all_documents if not doc.get('content', '').strip())
        
        # Metadata
        missing_source = sum(
            1 for doc in all_documents 
            if not doc.get('metadata', {}).get('source')
        )
        
        return {
            "total_chunks": total_chunks,
            "total_unique_documents": len(sources),
            "avg_chunk_size": round(avg_size, 0),
            "min_chunk_size": min(sizes) if sizes else 0,
            "max_chunk_size": max(sizes) if sizes else 0,
            "small_chunks_count": small_chunks,
            "large_chunks_count": large_chunks,
            "empty_chunks_count": empty_chunks,
            "missing_source_count": missing_source,
            "documents_by_source": dict(sources.most_common(10)),
            "chunks_by_type": dict(types),
            "empty": False
        }
        
    except Exception as e:
        logger.error(f"Erro ao buscar estatísticas: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"Erro ao buscar estatísticas: {str(e)}"
        )

