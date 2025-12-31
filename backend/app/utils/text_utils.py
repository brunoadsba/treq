"""
Utilitários para processamento de texto.
"""
import re

MAX_TTS_CHARS = 500  # Limite otimizado para UX rápida de síntese de voz

def truncate_for_tts(text: str, max_chars: int = MAX_TTS_CHARS) -> str:
    """
    Trunca texto para TTS respeitando pontuação e sentenças completas.
    Mantém coerência do texto ao cortar apenas em pontos de pontuação válidos.
    
    IMPORTANTE: Remove tags HTML/XML sempre, não apenas quando truncar.
    
    Args:
        text: Texto original
        max_chars: Número máximo de caracteres (padrão: 500)
        
    Returns:
        Texto truncado mantendo coerência
    """
    if not text:
        return text
    
    # Remove tags HTML/XML sempre, não apenas quando truncar
    clean_text = re.sub(r'<[^>]+>', '', text)
    
    if len(clean_text) <= max_chars:
        return clean_text
    
    # Trunca no limite
    truncated = clean_text[:max_chars]
    
    # Tenta encontrar último final de sentença (., !, ?)
    last_sentence_end = max(
        truncated.rfind('.'),
        truncated.rfind('!'),
        truncated.rfind('?')
    )
    
    # Se encontrou final de sentença em posição razoável (últimos 40%)
    if last_sentence_end > max_chars * 0.6:
        return truncated[:last_sentence_end + 1]
    
    # Fallback: última vírgula
    last_comma = truncated.rfind(',')
    if last_comma > max_chars * 0.8:
        return truncated[:last_comma] + '...'
    
    # Último recurso: último espaço
    last_space = truncated.rfind(' ')
    if last_space > max_chars * 0.9:
        return truncated[:last_space] + '...'
    
    return truncated + '...'
