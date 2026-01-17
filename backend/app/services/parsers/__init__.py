from typing import Dict, Type, Optional
from pathlib import Path
from loguru import logger

from .base_parser import BaseParser
from .pdf_parser import PDFParser
from .excel_parser import ExcelParser
from .text_parser import TextParser

class IngestionService:
    """
    Serviço central de ingestão que roteia arquivos para o parser correto.
    """
    
    def __init__(self):
        self._parsers: Dict[str, Type[BaseParser]] = {
            ".pdf": PDFParser,
            ".xlsx": ExcelParser,
            ".xls": ExcelParser,
            ".csv": ExcelParser,
            ".txt": TextParser,
            ".md": TextParser,
            ".markdown": TextParser
        }
    
    def get_parser_for_file(self, filename: str) -> Optional[BaseParser]:
        ext = Path(filename).suffix.lower()
        parser_cls = self._parsers.get(ext)
        
        if parser_cls:
            return parser_cls()
        return None
        
    def ingest_file(self, content: bytes, filename: str) -> Dict[str, Any]:
        """
        Ponto de entrada principal para ingestão de arquivos.
        """
        parser = self.get_parser_for_file(filename)
        
        if not parser:
            logger.warning(f"Nenhum parser encontrado para extensão do arquivo: {filename}")
            raise ValueError(f"Formato de arquivo não suportado: {Path(filename).suffix}")
            
        try:
            return parser.parse(content, filename)
        except Exception as e:
            logger.error(f"Falha fatal na ingestão do arquivo {filename}: {e}")
            raise e

# Instância Singleton
_ingestion_service = IngestionService()

def ingest_file(content: bytes, filename: str) -> Dict[str, Any]:
    return _ingestion_service.ingest_file(content, filename)
