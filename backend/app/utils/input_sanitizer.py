"""
Sanitização e validação de input do usuário.
Proteção básica contra prompt injection e inputs maliciosos.
"""
import re
from typing import Tuple, Optional, Dict, Any
from loguru import logger

# Constantes
MAX_INPUT_LENGTH = 5000
MIN_INPUT_LENGTH = 1

# Padrões de jailbreak/prompt injection (deny-list)
JAILBREAK_PATTERNS = [
    # Padrões em inglês
    r"ignore\s+(previous|all|the)\s+(instructions?|rules?|guidelines?)",
    r"forget\s+(previous|all|the)\s+(instructions?|rules?|guidelines?)",
    r"disregard\s+(previous|all|the)\s+(instructions?|rules?|guidelines?)",
    r"translate\s+(everything|all|the)\s+(above|before|previous)",
    r"developer\s+mode",
    r"system\s+prompt",
    r"show\s+(me|the)\s+(system\s+)?(prompt|instructions?)",
    r"what\s+(are|were)\s+(your|the)\s+(initial|original|system)\s+(instructions?|prompts?)",
    r"repeat\s+(back|to me)\s+(your|the)\s+(instructions?|prompt)",
    r"new\s+instructions?",
    r"override\s+(previous|the)\s+(instructions?|rules?)",
    r"act\s+as\s+(if|though)",
    r"pretend\s+(you\s+are|to be)",
    r"you\s+are\s+now",
    r"from\s+now\s+on",
    
    # Padrões em português
    r"ignore\s+(as|todas|todas as)\s+(instruções|regras|diretrizes)\s+(anteriores|prévias)",
    r"esqueça\s+(as|todas|todas as)\s+(instruções|regras|diretrizes)\s+(anteriores|prévias)",
    r"desconsidere\s+(as|todas|todas as)\s+(instruções|regras|diretrizes)\s+(anteriores|prévias)",
    r"traduzir\s+(tudo|todas|todos)\s+(acima|anterior|prévio)",
    r"modo\s+desenvolvedor",
    r"prompt\s+do\s+sistema",
    r"mostre\s+(me|as)\s+(instruções|prompt)\s+(do\s+)?(sistema|inicial)",
    r"quais\s+(são|eram)\s+(suas|as)\s+(instruções|regras|prompt)\s+(iniciais|originais)",
    r"repita\s+(para\s+)?mim\s+(suas|as)\s+(instruções|regras)",
    r"novas\s+instruções",
    r"sobrescrever\s+(as|todas as)\s+(instruções|regras)\s+(anteriores)",
    r"finja\s+(que|ser)",
    r"você\s+é\s+agora",
    r"a\s+partir\s+de\s+agora",
]

# Compilar patterns uma vez para melhor performance
COMPILED_PATTERNS = [re.compile(pattern, re.IGNORECASE) for pattern in JAILBREAK_PATTERNS]


def detect_jailbreak_attempt(text: str) -> bool:
    """
    Detecta tentativas de jailbreak/prompt injection no texto.
    
    Args:
        text: Texto a verificar
        
    Returns:
        bool: True se detectar padrão suspeito de jailbreak
    """
    if not text or not isinstance(text, str):
        return False
    
    text_lower = text.lower()
    
    for pattern in COMPILED_PATTERNS:
        if pattern.search(text_lower):
            logger.warning(
                f"Tentativa de jailbreak detectada. Pattern: {pattern.pattern[:50]}... "
                f"Input (primeiros 100 chars): {text[:100]}"
            )
            return True
    
    return False


def sanitize_user_input(text: str) -> Tuple[str, bool]:
    """
    Sanitiza input do usuário removendo caracteres perigosos e validando tamanho.
    Também detecta tentativas de prompt injection.
    
    Args:
        text: Texto de input do usuário
        
    Returns:
        Tuple[str, bool]: (texto sanitizado, sucesso)
        - Se False, o texto está inválido e deve ser rejeitado
        
    Nota: Validação de tamanho máximo deve ser feita ANTES de chamar esta função
    para evitar que Pydantic valide primeiro (retornaria 422 em vez de 400).
    """
    if not text or not isinstance(text, str):
        logger.warning("Input vazio ou não-string recebido")
        return "", False
    
    # Detectar tentativas de jailbreak ANTES de sanitizar
    if detect_jailbreak_attempt(text):
        logger.warning("Input rejeitado: padrão de jailbreak detectado")
        return "", False
    
    # Remover espaços em branco no início e fim
    sanitized = text.strip()
    
    # Validar tamanho mínimo
    if len(sanitized) < MIN_INPUT_LENGTH:
        logger.warning(f"Input muito curto: {len(sanitized)} caracteres")
        return "", False
    
    # Validar tamanho máximo (REJEITAR em vez de truncar)
    if len(sanitized) > MAX_INPUT_LENGTH:
        logger.warning(f"Input muito longo: {len(sanitized)} caracteres (máx: {MAX_INPUT_LENGTH}) - REJEITADO")
        # REJEITAR explicitamente - não truncar silenciosamente
        return "", False
    
    # Remover caracteres de controle perigosos (exceto \n e \t que são úteis)
    # Remove: \x00-\x08, \x0B-\x0C, \x0E-\x1F, \x7F
    sanitized = re.sub(r'[\x00-\x08\x0B-\x0C\x0E-\x1F\x7F]', '', sanitized)
    
    # Remover sequências de escape perigosas (exceto \n e \t)
    # Remove: \r (carriage return isolado)
    sanitized = sanitized.replace('\r', '')
    
    # Normalizar múltiplas quebras de linha consecutivas (máx 2)
    sanitized = re.sub(r'\n{3,}', '\n\n', sanitized)
    
    # Normalizar múltiplos espaços consecutivos (máx 2)
    sanitized = re.sub(r' {3,}', '  ', sanitized)
    
    return sanitized, True


def validate_input_length(text: str) -> Tuple[bool, str]:
    """
    Valida apenas o tamanho do input.
    
    Args:
        text: Texto a validar
        
    Returns:
        Tuple[bool, str]: (válido, mensagem de erro)
    """
    if not text:
        return False, "Input não pode estar vazio"
    
    if len(text) < MIN_INPUT_LENGTH:
        return False, f"Input muito curto (mínimo: {MIN_INPUT_LENGTH} caracteres)"
    
    if len(text) > MAX_INPUT_LENGTH:
        return False, f"Input muito longo (máximo: {MAX_INPUT_LENGTH} caracteres)"
    
    return True, ""


def get_max_input_length() -> int:
    """Retorna o tamanho máximo permitido para input."""
    return MAX_INPUT_LENGTH


def get_min_input_length() -> int:
    """Retorna o tamanho mínimo permitido para input."""
    return MIN_INPUT_LENGTH


def sanitize_context_dict(context: Optional[Dict[str, Any]]) -> Dict[str, Any]:
    """
    Sanitiza dicionário de contexto recebido do frontend.
    Remove valores potencialmente perigosos e valida estrutura.
    
    Args:
        context: Dicionário de contexto (pode ser None)
        
    Returns:
        Dict sanitizado e seguro para uso no prompt
    """
    if not context or not isinstance(context, dict):
        return {}
    
    sanitized = {}
    
    # Campos permitidos e seus tipos esperados
    ALLOWED_KEYS = {
        'unidade': str,
        'periodo': str,
        'data_inicio': str,
        'data_fim': str,
        'filtros': dict,
        'parametros': dict,
    }
    
    for key, value in context.items():
        # Ignorar chaves não permitidas
        if key not in ALLOWED_KEYS:
            logger.warning(f"Chave não permitida no contexto ignorada: {key}")
            continue
        
        # Validar tipo esperado
        expected_type = ALLOWED_KEYS[key]
        if not isinstance(value, expected_type):
            logger.warning(f"Tipo inválido para contexto['{key}']: esperado {expected_type.__name__}, recebido {type(value).__name__}")
            continue
        
        # Sanitizar strings
        if isinstance(value, str):
            # Limitar tamanho e remover caracteres perigosos
            sanitized_value = value.strip()[:200]  # Limitar tamanho
            sanitized_value = re.sub(r'[\x00-\x08\x0B-\x0C\x0E-\x1F\x7F]', '', sanitized_value)  # Remover control chars
            
            # Verificar padrões de jailbreak em strings
            if detect_jailbreak_attempt(sanitized_value):
                logger.warning(f"Tentativa de jailbreak detectada no contexto['{key}'], valor ignorado")
                continue
            
            sanitized[key] = sanitized_value
        
        # Para dicts aninhados, sanitizar recursivamente (limitado a 2 níveis)
        elif isinstance(value, dict):
            nested_sanitized = {}
            for nested_key, nested_value in value.items():
                if isinstance(nested_key, str) and len(nested_key) <= 50:
                    if isinstance(nested_value, (str, int, float, bool)):
                        if isinstance(nested_value, str):
                            nested_value = nested_value.strip()[:200]
                            nested_value = re.sub(r'[\x00-\x08\x0B-\x0C\x0E-\x1F\x7F]', '', nested_value)
                            if detect_jailbreak_attempt(nested_value):
                                continue
                        nested_sanitized[nested_key] = nested_value
            if nested_sanitized:
                sanitized[key] = nested_sanitized
        else:
            sanitized[key] = value
    
    return sanitized
