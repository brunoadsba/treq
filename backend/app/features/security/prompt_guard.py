import re
from typing import List, Tuple, Optional
from loguru import logger

class PromptInjectionGuard:
    """Proteção avançada contra ataques de Prompt Injection e Jailbreak"""
    
    # Padrões críticos com pesos de ameaça (0.0 a 1.0)
    CRITICAL_PATTERNS: List[Tuple[str, float]] = [
        (r'ignore\s+all\s+previous\s+instructions', 0.95),
        (r'disregard\s+everything\s+above', 0.90),
        (r'repeat\s+your\s+system\s+prompt', 0.98),
        (r'output\s+your\s+original\s+instructions', 0.98),
        (r'you\s+are\s+now\s+a\s+(hacker|attacker|jailbroken)', 0.85),
        (r'DAN\s+mode', 0.99),
        (r'System\s+Override', 0.95),
        (r'Forget\s+your\s+objectives', 0.90),
        (r'reveal\s+hidden\s+system\s+information', 0.97),
        (r'base64\s*\(', 0.70), # Encoding bypass attempt
    ]

    @classmethod
    def analyze_threat(cls, text: str) -> Tuple[bool, float, List[str]]:
        """
        Analisa o texto em busca de ameaças de injeção.
        Retorna (is_threat, score, matched_patterns)
        """
        if not text:
            return False, 0.0, []
        
        matches = []
        total_score = 0.0
        
        for pattern, score in cls.CRITICAL_PATTERNS:
            if re.search(pattern, text, re.IGNORECASE):
                matches.append(pattern)
                total_score = max(total_score, score) # Pega o maior score individual
        
        is_threat = total_score >= 0.80
        return is_threat, total_score, matches

    @classmethod
    def wrap_data(cls, data: str) -> str:
        """
        Segregação de dados usando delimitadores XML rígidos.
        Isola o input do usuário das instruções do sistema.
        """
        # Escapar delimitadores existentes para evitar breakout
        safe_data = data.replace("<user_input>", "&lt;user_input&gt;").replace("</user_input>", "&lt;/user_input&gt;")
        return f"\n<user_input>\n{safe_data}\n</user_input>\n"

class PromptGuardMiddleware:
    """Middleware para detecção precoce de injeções (opcionalmente usado via router)"""
    
    @staticmethod
    async def validate_input(text: str):
        is_threat, score, matches = PromptInjectionGuard.analyze_threat(text)
        if is_threat:
            logger.warning(f"🚨 TENTATIVA DE PROMPT INJECTION BLOQUEADA: Score={score}, Patterns={matches}")
            return False, "Sua mensagem contém padrões não permitidos por questões de segurança."
        return True, None
