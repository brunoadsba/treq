"""
Gerenciador de contexto para rastrear estado da conversa.
Rastreia unidade atual, período, tipo de consulta, etc.
"""
from typing import Dict, Optional, Any, List
from datetime import datetime
from loguru import logger
from app.core.query_classifier import classify_query as classify_query_type


class ContextManager:
    """Gerencia contexto da conversa e slots explícitos."""
    
    def __init__(self, user_id: str):
        """
        Inicializa o gerenciador de contexto.
        
        Args:
            user_id: ID do usuário
        """
        self.user_id = user_id
        
        # Slots de contexto explícitos
        self.current_unit: Optional[str] = None  # BA-Salvador, PE-Recife, etc.
        self.current_period: Optional[Dict[str, int]] = None  # {"month": 12, "year": 2024}
        self.query_type: Optional[str] = None  # "alerta", "procedimento", "métrica", "geral"
        
        # Histórico de mensagens
        self.message_history: List[Dict[str, Any]] = []
        
        # Metadata adicional
        self.metadata: Dict[str, Any] = {}
    
    def update_unit(self, unit: str) -> bool:
        """
        Atualiza unidade atual (apenas se mudou explicitamente).
        
        Args:
            unit: Código da unidade (ex: "BA-Salvador")
            
        Returns:
            bool: True se atualizou, False se já estava igual
        """
        if self.current_unit != unit:
            old_unit = self.current_unit
            self.current_unit = unit
            logger.info(f"Unidade atualizada: {old_unit} -> {unit}")
            return True
        return False
    
    def update_period(self, month: int, year: int) -> bool:
        """
        Atualiza período atual (apenas se mudou explicitamente).
        
        Args:
            month: Mês (1-12)
            year: Ano
            
        Returns:
            bool: True se atualizou, False se já estava igual
        """
        new_period = {"month": month, "year": year}
        if self.current_period != new_period:
            old_period = self.current_period
            self.current_period = new_period
            logger.info(f"Período atualizado: {old_period} -> {new_period}")
            return True
        return False
    
    def classify_query(self, query: str) -> str:
        """
        Classifica o tipo de consulta usando o classificador dedicado.
        
        Args:
            query: Texto da consulta
            
        Returns:
            str: Tipo da consulta ("alerta", "procedimento", "métrica", "status", "detalhamento", "geral")
        """
        # Usar classificador dedicado
        query_type = classify_query_type(query, self.message_history)
        self.query_type = query_type
        return query_type
    
    def extract_entities(self, query: str) -> Dict[str, Any]:
        """
        Extrai entidades da query (unidades, períodos, etc.).
        
        Args:
            query: Texto da consulta
            
        Returns:
            Dict: Entidades extraídas {"unit": "...", "period": {...}}
        """
        query_lower = query.lower()
        entities: Dict[str, Any] = {}
        
        # Unidades conhecidas
        units = {
            "salvador": "BA-Salvador",
            "recife": "PE-Recife",
            "bahia": "BA-Salvador",
            "pernambuco": "PE-Recife",
            "ba": "BA-Salvador",
            "pe": "PE-Recife",
        }
        
        for keyword, unit_code in units.items():
            if keyword in query_lower:
                entities["unit"] = unit_code
                logger.debug(f"Entidade extraída: unidade = {unit_code}")
                break
        
        # Períodos (meses)
        months = {
            "janeiro": 1, "fevereiro": 2, "março": 3, "abril": 4,
            "maio": 5, "junho": 6, "julho": 7, "agosto": 8,
            "setembro": 9, "outubro": 10, "novembro": 11, "dezembro": 12
        }
        
        current_year = datetime.now().year
        for month_name, month_num in months.items():
            if month_name in query_lower:
                entities["period"] = {"month": month_num, "year": current_year}
                logger.debug(f"Entidade extraída: período = {month_num}/{current_year}")
                break
        
        # Anos (2024, 2025, etc.)
        import re
        year_match = re.search(r'\b(20\d{2})\b', query)
        if year_match:
            year = int(year_match.group(1))
            if "period" not in entities:
                entities["period"] = {"month": datetime.now().month, "year": year}
            else:
                entities["period"]["year"] = year
            logger.debug(f"Entidade extraída: ano = {year}")
        
        return entities
    
    def add_message(self, role: str, content: str, metadata: Optional[Dict[str, Any]] = None):
        """
        Adiciona mensagem ao histórico.
        
        Args:
            role: "user" ou "assistant"
            content: Conteúdo da mensagem
            metadata: Metadata adicional
        """
        message = {
            "role": role,
            "content": content,
            "timestamp": datetime.now().isoformat(),
            "metadata": metadata or {}
        }
        
        self.message_history.append(message)
        
        # Manter apenas últimas 20 mensagens (evitar contexto muito longo)
        if len(self.message_history) > 20:
            self.message_history = self.message_history[-20:]
    
    def get_context_summary(self) -> str:
        """
        Retorna resumo do contexto atual.
        
        Returns:
            str: Resumo formatado do contexto
        """
        parts = []
        
        if self.current_unit:
            parts.append(f"Unidade: {self.current_unit}")
        
        if self.current_period:
            parts.append(f"Período: {self.current_period['month']}/{self.current_period['year']}")
        
        if self.query_type:
            parts.append(f"Tipo de consulta: {self.query_type}")
        
        return " | ".join(parts) if parts else "Sem contexto específico"
    
    def get_recent_messages(self, n: int = 5) -> List[Dict[str, str]]:
        """
        Retorna últimas N mensagens formatadas para o LLM.
        
        Args:
            n: Número de mensagens a retornar
            
        Returns:
            List[Dict]: Lista de mensagens no formato {"role": "...", "content": "..."}
        """
        recent = self.message_history[-n:] if len(self.message_history) > n else self.message_history
        return [
            {"role": msg["role"], "content": msg["content"]}
            for msg in recent
        ]

