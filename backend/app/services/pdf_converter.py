"""
Conversor de PDF para Markdown.
"""
from typing import Optional
import io
from loguru import logger


try:
    import pdfplumber
    PDFPLUMBER_AVAILABLE = True
except ImportError:
    PDFPLUMBER_AVAILABLE = False


def convert_pdf_to_markdown(file_content: bytes, filename: str) -> Optional[str]:
    """
    Converte PDF para Markdown usando pdfplumber (preferido) ou PyPDF2 (fallback).
    
    Args:
        file_content: Conteúdo do arquivo em bytes
        filename: Nome do arquivo (para logging)
        
    Returns:
        str: Conteúdo Markdown ou None se erro
    """
    if not PDFPLUMBER_AVAILABLE:
        logger.error("PDF não suportado - pdfplumber não instalado")
        return None
    
    try:
        return _convert_with_pdfplumber(file_content, filename)
    except Exception as e:
        logger.error(f"Erro ao converter PDF '{filename}': {e}")
        import traceback
        logger.error(traceback.format_exc())
        return None


def _convert_with_pdfplumber(file_content: bytes, filename: str) -> str:
    """Converte PDF usando pdfplumber (melhor para tabelas)."""
    pdf_file = io.BytesIO(file_content)
    markdown_parts = [f"# {filename}\n\n"]
    
    with pdfplumber.open(pdf_file) as pdf:
        for page_num, page in enumerate(pdf.pages, start=1):
            markdown_parts.append(f"## Página {page_num}\n\n")
            
            # Extrair texto
            text = page.extract_text()
            if text:
                markdown_parts.append(f"{text}\n\n")
            
            # Extrair tabelas
            tables = page.extract_tables()
            for table in tables:
                if table:
                    markdown_parts.append(_table_to_markdown(table))
                    markdown_parts.append("\n\n")
    
    return "".join(markdown_parts)




def _table_to_markdown(table: list) -> str:
    """
    Converte tabela (lista de listas) para Markdown.
    
    Args:
        table: Lista de listas representando a tabela
        
    Returns:
        str: Tabela em formato Markdown
    """
    if not table or not table[0]:
        return ""
    
    markdown_lines = []
    
    # Cabeçalho (primeira linha)
    header = [str(cell) if cell is not None else "" for cell in table[0]]
    markdown_lines.append("| " + " | ".join(header) + " |")
    markdown_lines.append("| " + " | ".join(["---"] * len(header)) + " |")
    
    # Linhas de dados
    for row in table[1:]:
        cells = [str(cell) if cell is not None else "" for cell in row]
        # Garantir que tem o mesmo número de colunas do cabeçalho
        while len(cells) < len(header):
            cells.append("")
        markdown_lines.append("| " + " | ".join(cells) + " |")
    
    return "\n".join(markdown_lines)
