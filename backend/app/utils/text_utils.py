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


def safe_json_parse(text: str) -> dict:
    """
    Extrai e faz o parse do primeiro bloco JSON encontrado no texto.
    Útil quando o LLM inclui preâmbulos ou explicações fora do bloco JSON.
    
    Trata casos comuns:
    - JSON puro
    - Blocos markdown com ` ```json ... ``` `
    - Blocos markdown com identificadores variados (` ```formato de dados ... ``` `)
    - JSON precedido por texto explicativo
    
    Args:
        text: Texto bruto retornado pelo LLM
        
    Returns:
        dict: Objeto JSON parseado
        
    Raises:
        ValueError: Se nenhum JSON válido for encontrado
    """
    import json
    
    if not text or not text.strip():
        raise ValueError("Texto vazio recebido para parsing JSON.")
    
    # 1. Tentar parse direto (caso ideal)
    try:
        return json.loads(text.strip())
    except json.JSONDecodeError:
        pass
    
    # 2. Remover blocos de código markdown com identificadores variados
    # Trata: ```json, ```formato de dados, ```JSON, ```output, etc.
    clean_text = re.sub(r'```[\w\s]*\n?([\s\S]*?)\n?```', r'\1', text, flags=re.IGNORECASE)
    try:
        return json.loads(clean_text.strip())
    except json.JSONDecodeError:
        pass
    
    # 3. Tentar encontrar primeiro objeto JSON { ... }
    match = re.search(r'(\{[\s\S]*\})', clean_text, re.DOTALL)
    if match:
        try:
            return json.loads(match.group(1))
        except json.JSONDecodeError:
            # Tentar encontrar o menor objeto válido (evita capturar JSON aninhado incompleto)
            # Busca do início do { até o último } balanceado
            json_str = match.group(1)
            brace_count = 0
            end_idx = 0
            for i, char in enumerate(json_str):
                if char == '{':
                    brace_count += 1
                elif char == '}':
                    brace_count -= 1
                    if brace_count == 0:
                        end_idx = i + 1
                        break
            if end_idx > 0:
                try:
                    return json.loads(json_str[:end_idx])
                except json.JSONDecodeError:
                    pass
    
    # 4. Fallback: tentar array JSON [ ... ]
    match = re.search(r'(\[[\s\S]*\])', clean_text, re.DOTALL)
    if match:
        try:
            return json.loads(match.group(1))
        except json.JSONDecodeError:
            pass
        
    raise ValueError("Não foi possível encontrar ou parsear um bloco JSON válido na resposta do LLM.")

