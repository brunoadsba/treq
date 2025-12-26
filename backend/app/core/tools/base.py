"""
Classe base para Tools.

Tools são ferramentas que consultam sistemas externos ou bancos de dados
para obter informações atualizadas em tempo real.
"""
from abc import ABC, abstractmethod
from typing import Dict, Any, Optional
from dataclasses import dataclass
from loguru import logger


@dataclass
class ToolResult:
    """Resultado de execução de uma Tool."""
    success: bool
    data: Optional[Any] = None
    message: Optional[str] = None
    error: Optional[str] = None
    
    def __bool__(self) -> bool:
        """Permite usar ToolResult como boolean."""
        return self.success


class Tool(ABC):
    """
    Classe base abstrata para todas as Tools.
    
    Cada Tool implementa métodos para buscar dados específicos
    de sistemas externos ou bancos de dados.
    """
    
    def __init__(self, name: str, description: str):
        """
        Inicializa a Tool.
        
        Args:
            name: Nome da tool (ex: "metrics", "orders")
            description: Descrição do que a tool faz
        """
        self.name = name
        self.description = description
        logger.debug(f"Tool '{name}' inicializada: {description}")
    
    @abstractmethod
    async def execute(self, **kwargs) -> ToolResult:
        """
        Executa a tool com os parâmetros fornecidos.
        
        Args:
            **kwargs: Parâmetros específicos da tool
            
        Returns:
            ToolResult: Resultado da execução
        """
        pass
    
    def validate_params(self, required_params: list, **kwargs) -> tuple[bool, Optional[str]]:
        """
        Valida se todos os parâmetros obrigatórios foram fornecidos.
        
        Args:
            required_params: Lista de parâmetros obrigatórios
            **kwargs: Parâmetros fornecidos
            
        Returns:
            tuple: (is_valid, error_message)
        """
        missing = [param for param in required_params if param not in kwargs or kwargs[param] is None]
        if missing:
            return False, f"Parâmetros obrigatórios faltando: {', '.join(missing)}"
        return True, None
    
    def __repr__(self) -> str:
        """Representação da tool."""
        return f"<Tool: {self.name}>"

