from typing import Dict, Any
from .base_parser import BaseParser
from loguru import logger
import chardet

class TextParser(BaseParser):
    """Parser para arquivos de texto simples e Markdown (.txt, .md)."""
    
    def parse(self, file_content: bytes, file_name: str) -> Dict[str, Any]:
        logger.info(f"Iniciando parse de Texto: {file_name}")
        try:
            # Detectar encoding
            encoding_result = chardet.detect(file_content)
            encoding = encoding_result.get('encoding') or 'utf-8'
            
            text = file_content.decode(encoding)
            
            metadata = {
                "encoding": encoding,
                "char_count": len(text)
            }
            
            return self._create_result(text, metadata)
            
        except Exception as e:
            logger.error(f"Erro ao parsear arquivo de texto {file_name}: {str(e)}")
            raise ValueError(f"Falha ao processar arquivo de texto: {str(e)}")
