"""
BaseTool - Interface padronizada para ferramentas do agente.
"""

from typing import Dict, Any
from abc import ABC, abstractmethod


class BaseTool(ABC):
    """
    Interface base para todas as ferramentas do agente.
    
    Attributes:
        name: Identificador único da ferramenta
        description: Descrição para o LLM entender quando usar
    """
    
    def __init__(self, name: str, description: str):
        self.name = name
        self.description = description
    
    @abstractmethod
    async def execute(self, **kwargs) -> Dict[str, Any]:
        """
        Executa a ferramenta com os parâmetros fornecidos.
        
        Returns:
            Dict com status e resultado da execução
        """
        pass
    
    def to_schema(self) -> Dict[str, Any]:
        """
        Retorna schema JSON para function calling.
        
        Override nas subclasses para parâmetros específicos.
        """
        return {
            "name": self.name,
            "description": self.description,
            "parameters": {"type": "object", "properties": {}}
        }
