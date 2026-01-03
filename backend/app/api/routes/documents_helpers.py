"""
Funções auxiliares para rotas de documentos.
"""
from typing import Dict, Any, List, TYPE_CHECKING
from datetime import datetime
from pathlib import Path
from loguru import logger

if TYPE_CHECKING:
    from app.core.chunking_service import ChunkingService
    from app.core.rag_service import RAGService


def prepare_document_metadata(
    filename: str,
    document_type: str,
    file_size: int
) -> Dict[str, Any]:
    """
    Prepara metadata base para documento.
    
    Args:
        filename: Nome do arquivo
        document_type: Tipo do documento
        file_size: Tamanho do arquivo em bytes
        
    Returns:
        Dict com metadata do documento
    """
    return {
        'document_type': document_type or 'unknown',
        'filename': filename,
        'file_size': file_size,
        'original_filename': filename,
        'file_format': Path(filename).suffix.lower(),
        'uploaded_at': datetime.now().isoformat(),
    }


def index_document_chunks(
    chunks: List[Dict[str, Any]],
    base_metadata: Dict[str, Any],
    rag_service: 'RAGService'
) -> tuple[int, int]:
    """
    Indexa chunks do documento no RAG.
    
    Args:
        chunks: Lista de chunks do documento
        base_metadata: Metadata base do documento
        rag_service: Serviço RAG para indexação
        
    Returns:
        tuple: (indexed_count, failed_count)
    """
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
            
            doc_id = rag_service.index_document(
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
    
    return indexed_count, failed_count
