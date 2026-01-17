import pymupdf
from typing import Dict, Any
from .base_parser import BaseParser
from loguru import logger

class PDFParser(BaseParser):
    def parse(self, file_content: bytes, file_name: str) -> Dict[str, Any]:
        logger.info(f"Iniciando parse de PDF: {file_name}")
        try:
            doc = pymupdf.open(stream=file_content, filetype="pdf")
            full_text = []
            
            for page_num, page in enumerate(doc):
                text = page.get_text()
                full_text.append(f"## Página {page_num + 1}\n{text}")
            
            content = "\n\n".join(full_text)
            
            metadata = {
                "page_count": len(doc),
                "author": doc.metadata.get("author", ""),
                "title": doc.metadata.get("title", "")
            }
            
            # TODO: Se content for muito curto, poderia ativar um fallback de OCR
            
            return self._create_result(content, metadata)
            
        except Exception as e:
            logger.error(f"Erro ao parsear PDF {file_name}: {str(e)}")
            raise ValueError(f"Falha ao processar PDF: {str(e)}")
