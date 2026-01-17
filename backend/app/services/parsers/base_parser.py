from abc import ABC, abstractmethod
from typing import Dict, Any, Optional

class BaseParser(ABC):
    """
    Interface base para todos os parsers de documentos.
    Define o contrato para processamento e normalização.
    """
    
    @abstractmethod
    def parse(self, file_content: bytes, file_name: str) -> Dict[str, Any]:
        """
        Processa o conteúdo do arquivo e retorna um objeto padronizado.
        
        Args:
            file_content: Bytes do arquivo a ser processado
            file_name: Nome do arquivo (útil para logs e metadados)
            
        Returns:
            Dict contendo:
            - content: str (Texto extraído em Markdown/Texto limpo)
            - metadata: Dict (Informações sobre o arquivo)
        """
        pass
    
    def _create_result(self, content: str, metadata: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """Helper para criar o objeto de retorno padronizado."""
        return {
            "content": content,
            "metadata": metadata or {}
        }
