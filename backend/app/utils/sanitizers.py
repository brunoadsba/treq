import re

def sanitize_response(text: str) -> str:
    """
    Filtro Pós-Recuperação: Remove artefatos internos e corrige branding.
    
    Aplica as seguintes regras:
    1. Remove menções a nomes de arquivos (xlsx, pdf, etc).
    2. Garante branding 'Treq' em vez de nomes legados.
    3. Remove caminhos de sistema (/app/...).
    """
    # 1. Remover menções a arquivos (ex: .xlsx, .pdf)
    text = re.sub(r'[\w\-\s]+\.(xlsx|xls|pdf|csv|json|txt)', '', text, flags=re.IGNORECASE)
    
    # 2. Forçar branding Treq (segurança de marca)
    text = re.sub(r'\bSotreq\b', 'Treq', text, flags=re.IGNORECASE)
    
    # 3. Remover caminhos de arquivo (ex: /app/data/...)
    text = re.sub(r'(/[a-zA-Z0-9_\-\.]+)+', '', text)
    
    return text.strip()
