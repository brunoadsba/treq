"""
Módulo de Limpeza de Conteúdo para Sistema RAG
Projeto: Treq - Assistente Operacional Treq

Remove ruído de formatação Markdown que polui embeddings vetoriais:
- Checkboxes (- [ ], - [x])
- Linhas de separação de tabelas
- Múltiplas quebras de linha
- Rodapés repetitivos
"""

import re
from typing import Optional


def clean_content(text: str) -> str:
    """
    Remove ruído de formatação Markdown.
    
    Args:
        text: Texto original com formatação Markdown
        
    Returns:
        Texto limpo sem ruído de formatação
    """
    if not text:
        return ""
    
    # Remover checkboxes markdown
    text = re.sub(r'- \[[ x]\] ', '', text)
    
    # Remover linhas de tabela vazias (separadores)
    text = re.sub(r'\|[-: ]+\|', '', text)
    
    # Remover múltiplas quebras de linha (mais de 2)
    text = re.sub(r'\n{3,}', '\n\n', text)
    
    # Remover headers repetitivos de rodapé
    text = re.sub(r'---\n*$', '', text)
    
    # Remover espaços em branco no início e fim
    text = text.strip()
    
    return text


def clean_content_advanced(text: str, preserve_tables: bool = True) -> str:
    """
    Limpeza avançada com opções adicionais.
    
    Args:
        text: Texto original
        preserve_tables: Se True, mantém estrutura básica de tabelas
        
    Returns:
        Texto limpo
    """
    if not text:
        return ""
    
    # Aplicar limpeza básica
    text = clean_content(text)
    
    # Remover comentários HTML
    text = re.sub(r'<!--.*?-->', '', text, flags=re.DOTALL)
    
    # Normalizar espaços múltiplos
    text = re.sub(r' {2,}', ' ', text)
    
    # Se não preservar tabelas, remover completamente
    if not preserve_tables:
        # Remover linhas que parecem ser de tabela
        lines = text.split('\n')
        cleaned_lines = [
            line for line in lines 
            if not (line.strip().startswith('|') and line.strip().endswith('|'))
        ]
        text = '\n'.join(cleaned_lines)
    
    # Remover linhas vazias consecutivas
    text = re.sub(r'\n\s*\n\s*\n', '\n\n', text)
    
    return text.strip()


def remove_markdown_formatting(text: str) -> str:
    """
    Remove toda formatação Markdown, deixando apenas texto puro.
    Útil para análise de conteúdo sem formatação.
    
    Args:
        text: Texto com formatação Markdown
        
    Returns:
        Texto puro sem formatação
    """
    if not text:
        return ""
    
    # Remover headers (###, ##, #)
    text = re.sub(r'^#{1,6}\s+', '', text, flags=re.MULTILINE)
    
    # Remover bold e itálico
    text = re.sub(r'\*\*(.+?)\*\*', r'\1', text)  # Bold
    text = re.sub(r'\*(.+?)\*', r'\1', text)      # Itálico
    text = re.sub(r'__(.+?)__', r'\1', text)      # Bold alternativo
    text = re.sub(r'_(.+?)_', r'\1', text)        # Itálico alternativo
    
    # Remover links [texto](url)
    text = re.sub(r'\[(.+?)\]\(.+?\)', r'\1', text)
    
    # Remover imagens ![alt](url)
    text = re.sub(r'!\[.*?\]\(.+?\)', '', text)
    
    # Remover código inline `code`
    text = re.sub(r'`(.+?)`', r'\1', text)
    
    # Remover blocos de código
    text = re.sub(r'```.*?```', '', text, flags=re.DOTALL)
    
    # Remover listas (-, *, +)
    text = re.sub(r'^[\-\*\+]\s+', '', text, flags=re.MULTILINE)
    
    # Remover listas numeradas
    text = re.sub(r'^\d+\.\s+', '', text, flags=re.MULTILINE)
    
    # Remover blockquotes
    text = re.sub(r'^>\s+', '', text, flags=re.MULTILINE)
    
    # Aplicar limpeza básica
    text = clean_content(text)
    
    return text.strip()


def normalize_whitespace(text: str) -> str:
    """
    Normaliza espaços em branco no texto.
    
    Args:
        text: Texto com espaços irregulares
        
    Returns:
        Texto com espaços normalizados
    """
    if not text:
        return ""
    
    # Remover espaços no início e fim de cada linha
    lines = [line.strip() for line in text.split('\n')]
    
    # Remover linhas completamente vazias duplicadas
    normalized_lines = []
    prev_empty = False
    
    for line in lines:
        if not line:
            if not prev_empty:
                normalized_lines.append(line)
            prev_empty = True
        else:
            normalized_lines.append(line)
            prev_empty = False
    
    return '\n'.join(normalized_lines).strip()


def clean_for_embedding(text: str) -> str:
    """
    Limpeza específica para otimizar embeddings vetoriais.
    Remove elementos que não contribuem para similaridade semântica.
    
    Args:
        text: Texto original
        
    Returns:
        Texto otimizado para embedding
    """
    # Aplicar limpeza avançada
    text = clean_content_advanced(text, preserve_tables=False)
    
    # Remover URLs
    text = re.sub(r'https?://\S+', '', text)
    
    # Remover emails
    text = re.sub(r'\S+@\S+\.\S+', '', text)
    
    # Remover números de telefone (formato brasileiro)
    text = re.sub(r'\(?\d{2}\)?\s?\d{4,5}-?\d{4}', '', text)
    
    # Remover caracteres especiais repetidos
    text = re.sub(r'([^\w\s])\1+', r'\1', text)
    
    # Normalizar espaços
    text = normalize_whitespace(text)
    
    return text


# Estatísticas de limpeza
def get_cleaning_stats(original: str, cleaned: str) -> dict:
    """
    Calcula estatísticas sobre a limpeza realizada.
    
    Args:
        original: Texto original
        cleaned: Texto limpo
        
    Returns:
        Dicionário com estatísticas
    """
    return {
        "original_length": len(original),
        "cleaned_length": len(cleaned),
        "chars_removed": len(original) - len(cleaned),
        "reduction_percent": round((1 - len(cleaned) / len(original)) * 100, 2) if original else 0,
        "original_lines": original.count('\n') + 1,
        "cleaned_lines": cleaned.count('\n') + 1
    }


# Exemplo de uso
if __name__ == "__main__":
    sample_text = """
# Checklist de Manutenção

## Itens Obrigatórios

- [x] Verificar nível de óleo
- [ ] Verificar pressão dos pneus
- [x] Testar freios


| Item | Status | Responsável |
|------|--------|-------------|
| Óleo | OK     | João        |
| Pneus| Pendente| Maria      |


---

Documento gerado automaticamente
---
"""
    
    print("=== Texto Original ===")
    print(sample_text)
    print(f"\nTamanho: {len(sample_text)} caracteres")
    
    cleaned = clean_content(sample_text)
    print("\n=== Texto Limpo (Básico) ===")
    print(cleaned)
    
    stats = get_cleaning_stats(sample_text, cleaned)
    print(f"\n=== Estatísticas ===")
    print(f"Caracteres removidos: {stats['chars_removed']}")
    print(f"Redução: {stats['reduction_percent']}%")
    
    embedding_optimized = clean_for_embedding(sample_text)
    print("\n=== Texto Otimizado para Embedding ===")
    print(embedding_optimized)
    
    stats_embedding = get_cleaning_stats(sample_text, embedding_optimized)
    print(f"\nRedução para embedding: {stats_embedding['reduction_percent']}%")
