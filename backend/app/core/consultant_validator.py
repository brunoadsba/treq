"""
Validador de tom conversacional para respostas do consultor.
Garante que respostas sigam diretrizes de linguagem natural e profissional.
"""
import re
import statistics
from typing import Dict, Any, List
from loguru import logger


def validate_consultant_response(response: str) -> Dict[str, Any]:
    """
    Valida se resposta do consultor segue diretrizes de tom conversacional.
    
    Verifica:
    - Ausência de estruturas rígidas proibidas (ex: "PROBLEMA IDENTIFICADO:")
    - Comprimento médio de frases (máximo 25 palavras)
    - Presença de expressões de empatia em respostas longas
    - Ausência de jargões técnicos não explicados
    
    Args:
        response: Texto da resposta do consultor
        
    Returns:
        Dicionário com resultados da validação:
        - valid: bool - Se a resposta é válida
        - issues: List[str] - Lista de problemas encontrados
        - warnings: List[str] - Lista de avisos (não bloqueantes)
        - avg_sentence_length: float - Comprimento médio das frases
        - sentence_count: int - Número de frases
        - has_empathy: bool - Se contém expressões de empatia
        - technical_terms_found: List[str] - Termos técnicos encontrados
    """
    if not response or not isinstance(response, str):
        return {"valid": False, "issues": ["Texto vazio ou inválido"]}
    
    issues = []
    warnings = []
    
    # Verifica estruturas proibidas
    forbidden_patterns = [
        (r'PROBLEMA\s+IDENTIFICADO[:\s]', "Use linguagem mais natural em vez de 'PROBLEMA IDENTIFICADO'"),
        (r'SOLUÇÃO\s+PROPOSTA[:\s]', "Use linguagem mais natural em vez de 'SOLUÇÃO PROPOSTA'"),
        (r'RECOMENDAÇÃO[:\s]', "Evite cabeçalhos formais como 'RECOMENDAÇÃO'"),
        (r'CONCLUSÃO[:\s]', "Evite cabeçalhos formais como 'CONCLUSÃO'"),
        (r'^\d+\.\s', "Evite listas numeradas no início da resposta"),
        (r'^\s*[-*•]\s', "Evite listas com marcadores no início da resposta"),
    ]
    
    for pattern, message in forbidden_patterns:
        if re.search(pattern, response, re.IGNORECASE | re.MULTILINE):
            issues.append(message)
    
    # Verifica comprimento médio das frases
    sentences = [s.strip() for s in re.split(r'[.!?]', response) if s.strip()]
    avg_sentence_length = 0
    
    if sentences:
        sentence_lengths = [len(s.split()) for s in sentences]
        avg_sentence_length = statistics.mean(sentence_lengths)
        
        if avg_sentence_length > 25:
            issues.append(f"Frases muito longas (média: {avg_sentence_length:.1f} palavras). Mantenha frases curtas (máximo 25 palavras).")
        elif avg_sentence_length < 8:
            warnings.append(f"Frases muito curtas (média: {avg_sentence_length:.1f} palavras). Pode parecer truncado.")
    
    # Verifica falta de empatia
    empathy_keywords = ['entendo', 'compreendo', 'imagino', 'sei que', 'reconheço', 'frustrante', 'desafiador', 'difícil', 'importante']
    has_empathy = any(keyword in response.lower() for keyword in empathy_keywords)
    
    if not has_empathy and len(response) > 50:
        warnings.append("Resposta longa sem expressões de empatia. Considere adicionar reconhecimento do problema do usuário.")
    
    # Verifica jargões técnicos (usando o filtro do Problema 2 como referência)
    technical_terms = ['threshold', 'sigma', 'σ', 'sla', 'kpi', 'api', 'json', 'etl', 'query', 'algoritmo']
    found_technical = [term for term in technical_terms if re.search(r'\b' + re.escape(term) + r'\b', response, re.IGNORECASE)]
    
    if found_technical:
        issues.append(f"Contém termos técnicos não explicados: {', '.join(found_technical)}")
    
    valid = len(issues) == 0
    
    return {
        "valid": valid,
        "issues": issues,
        "warnings": warnings,
        "avg_sentence_length": avg_sentence_length,
        "sentence_count": len(sentences),
        "has_empathy": has_empathy,
        "technical_terms_found": found_technical
    }


def assess_response_quality(response: str) -> str:
    """
    Avaliação básica da qualidade da resposta para logging.
    
    Args:
        response: Texto da resposta
        
    Returns:
        String com classificação da qualidade:
        - "too_short": Resposta muito curta (< 50 caracteres)
        - "fallback_generic": Resposta genérica de fallback
        - "too_structured": Resposta com estrutura rígida proibida
        - "clarifying_question": Pergunta clarificadora
        - "adequate": Resposta adequada
    """
    response_lower = response.lower()
    
    # Verificar fallback genérico primeiro (mesmo em respostas curtas)
    if any(phrase in response_lower for phrase in ["não tenho informações", "não posso responder", "não sei"]):
        return "fallback_generic"
    
    if len(response) < 50:
        return "too_short"
    if re.search(r'PROBLEMA IDENTIFICADO:|SOLUÇÃO PROPOSTA:', response):
        return "too_structured"
    if "?" in response and len(response) < 100:
        return "clarifying_question"
    
    return "adequate"
