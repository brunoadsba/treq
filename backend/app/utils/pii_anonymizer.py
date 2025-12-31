"""
Anonimização básica de PII (Dados Pessoais Identificáveis).
Versão simplificada para MVP.
"""
import re
from typing import Tuple
from loguru import logger

# Padrões de detecção (regex simples)
CPF_PATTERN = r'\b\d{3}\.?\d{3}\.?\d{3}-?\d{2}\b'
EMAIL_PATTERN = r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b'
PHONE_PATTERN = r'\b(\(?\d{2}\)?\s?)?(\d{4,5})-?(\d{4})\b'


def detect_pii(text: str) -> dict:
    """
    Detecta PII no texto (versão básica).
    
    Args:
        text: Texto a analisar
        
    Returns:
        Dict com tipos de PII encontrados e contagem
    """
    if not text:
        return {}
    
    detections = {
        "cpf": len(re.findall(CPF_PATTERN, text)),
        "email": len(re.findall(EMAIL_PATTERN, text, re.IGNORECASE)),
        "phone": len(re.findall(PHONE_PATTERN, text)),
    }
    
    # Remover tipos com 0 detecções
    return {k: v for k, v in detections.items() if v > 0}


def anonymize_pii(
    text: str,
    mask_email: bool = True,
    mask_cpf: bool = True,
    mask_phone: bool = True
) -> Tuple[str, dict]:
    """
    Anonimiza PII no texto substituindo por placeholders.
    Versão básica para MVP.
    
    Args:
        text: Texto contendo possivelmente PII
        mask_email: Se True, mascara emails
        mask_cpf: Se True, mascara CPFs
        mask_phone: Se True, mascara telefones
        
    Returns:
        Tuple[texto anonimizado, dict com estatísticas de anonimização]
    """
    if not text:
        return text, {}
    
    anonymized = text
    stats = {"replaced": 0, "types": {}}
    
    # Anonimizar CPF
    if mask_cpf:
        cpf_count = len(re.findall(CPF_PATTERN, anonymized))
        if cpf_count > 0:
            anonymized = re.sub(CPF_PATTERN, '[CPF]', anonymized)
            stats["replaced"] += cpf_count
            stats["types"]["cpf"] = cpf_count
            logger.debug(f"PII detectado: {cpf_count} CPF(s) anonimizado(s)")
    
    # Anonimizar Email
    if mask_email:
        email_count = len(re.findall(EMAIL_PATTERN, anonymized, re.IGNORECASE))
        if email_count > 0:
            anonymized = re.sub(
                EMAIL_PATTERN, '[EMAIL]', anonymized, flags=re.IGNORECASE
            )
            stats["replaced"] += email_count
            stats["types"]["email"] = email_count
            logger.debug(f"PII detectado: {email_count} email(s) anonimizado(s)")
    
    # Anonimizar Telefone
    if mask_phone:
        phone_count = len(re.findall(PHONE_PATTERN, anonymized))
        if phone_count > 0:
            anonymized = re.sub(PHONE_PATTERN, '[TELEFONE]', anonymized)
            stats["replaced"] += phone_count
            stats["types"]["phone"] = phone_count
            logger.debug(f"PII detectado: {phone_count} telefone(s) anonimizado(s)")
    
    if stats["replaced"] > 0:
        types_str = ', '.join(stats['types'].keys())
        logger.info(
            f"PII anonimizado: {stats['replaced']} ocorrência(s) de {types_str}"
        )
    
    return anonymized, stats


def sanitize_for_logs(text: str, max_length: int = 200) -> str:
    """
    Sanitiza texto para logs (trunca e anonimiza PII básico).
    
    Args:
        text: Texto a sanitizar
        max_length: Tamanho máximo para logs
        
    Returns:
        Texto sanitizado para logs
    """
    if not text:
        return ""
    
    # Anonimizar PII
    sanitized, _ = anonymize_pii(text)
    
    # Truncar se muito longo
    if len(sanitized) > max_length:
        sanitized = sanitized[:max_length] + "..."
    
    return sanitized
