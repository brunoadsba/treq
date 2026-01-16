"""
Registro Central de Ferramentas e Intenções.

Implementa 'Single Source of Truth' para o despacho de ferramentas.
Mapeia palavras-chave e intenções para as classes de ferramentas correspondentes.
"""

from typing import Type, List, Optional, Dict
from .base import BaseTool
from .jira import JiraCreateTicketTool
from .slack import SlackSendMessageTool

class ToolRegistry:
    """Registro estático de ferramentas."""
    
    # Mapa: Nome da Tool -> Classe da Tool
    _TOOLS: Dict[str, Type[BaseTool]] = {
        "jira_create_ticket": JiraCreateTicketTool,
        "slack_notify": SlackSendMessageTool
    }
    
    # Mapa: Keywords -> Nome da Tool
    # Isso permite que múltiplas keywords apontem para a mesma ferramenta
    _INTENTS: Dict[str, List[str]] = {
        "jira_create_ticket": [
            "ticket", "jira", "criar ticket", "abrir chamado", "reportar problema", 
            "bug", "erro"
        ],
        "slack_notify": [
            "notificar", "slack", "avisar", "avise", "avisa", "enviar mensagem", 
            "mandar mensagem", "comunicar"
        ]
    }

    @classmethod
    def get_tool_by_name(cls, name: str) -> Optional[BaseTool]:
        """Instancia uma ferramenta pelo seu nome interno."""
        tool_cls = cls._TOOLS.get(name)
        return tool_cls() if tool_cls else None

    @classmethod
    def detect_tool(cls, query: str) -> Optional[str]:
        """
        Detecta qual ferramenta deve ser usada baseada na query.
        Retorna o nome da ferramenta ou None.
        """
        query_lower = query.lower()
        
        for tool_name, keywords in cls._INTENTS.items():
            if any(kw in query_lower for kw in keywords):
                return tool_name
                
        return None

    @classmethod
    def get_all_tool_names(cls) -> List[str]:
        """Retorna lista de todas as ferramentas registradas."""
        return list(cls._TOOLS.keys())
