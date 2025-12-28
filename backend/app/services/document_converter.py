"""
Serviço para converter documentos (PDF simples/Excel) para Markdown.
MVP 100% FREE: Usa apenas soluções leves e gratuitas.

- PDF (texto nativo): PyPDF2/pdfplumber - Extrai texto de PDFs com texto nativo
- Excel: pandas/openpyxl - Conversão completa de planilhas
- PDF (escaneado/OCR): Não suportado no MVP (TODO futuro)

LIMITAÇÕES MVP:
- PDFs escaneados não funcionam (sem OCR)
- PDFs com imagens não extraem texto das imagens
- DOCX/PPTX não são suportados

FUTURO:
- OCR para PDFs escaneados: Google Document AI (1k páginas/mês free) ou solução paga
- DOCX/PPTX: python-docx/python-pptx ou conversão via API
"""
from typing import Optional
from pathlib import Path
import io
from loguru import logger

# Importar bibliotecas PDF (leves, gratuitas)
try:
    import PyPDF2
    PYPDF2_AVAILABLE = True
except ImportError:
    PYPDF2_AVAILABLE = False
    logger.warning("PyPDF2 não instalado. PDF não será suportado.")

try:
    import pdfplumber
    PDFPLUMBER_AVAILABLE = True
except ImportError:
    PDFPLUMBER_AVAILABLE = False
    logger.debug("pdfplumber não instalado. Usando apenas PyPDF2.")

# Importar bibliotecas Excel (podem não estar instaladas)
try:
    import pandas as pd
    from openpyxl import load_workbook
    EXCEL_AVAILABLE = True
except ImportError:
    EXCEL_AVAILABLE = False
    logger.warning("pandas/openpyxl não instalados. Excel não será suportado.")


class DocumentConverterService:
    """Serviço para converter documentos para Markdown (MVP 100% FREE)."""
    
    def __init__(self):
        """Inicializa o conversor de documentos."""
        if not PYPDF2_AVAILABLE:
            logger.warning("PDF não disponível - PyPDF2 não instalado")
        
        if PDFPLUMBER_AVAILABLE:
            logger.info("✅ DocumentConverterService inicializado (PDF: pdfplumber, Excel: pandas/openpyxl)")
        elif PYPDF2_AVAILABLE:
            logger.info("✅ DocumentConverterService inicializado (PDF: PyPDF2, Excel: pandas/openpyxl)")
        else:
            logger.warning("DocumentConverterService inicializado (sem suporte a PDF)")
        
        if not EXCEL_AVAILABLE:
            logger.warning("Excel não disponível - pandas/openpyxl não instalados")
    
    def convert_file(self, file_path: str) -> Optional[str]:
        """
        Converte arquivo do sistema de arquivos para Markdown.
        
        Args:
            file_path: Caminho do arquivo a converter
            
        Returns:
            str: Conteúdo Markdown ou None se erro
        """
        path = Path(file_path)
        
        if not path.exists():
            logger.error(f"Arquivo não encontrado: {file_path}")
            return None
        
        suffix = path.suffix.lower()
        
        # Verificar se é Excel
        if suffix in ['.xlsx', '.xls']:
            if not EXCEL_AVAILABLE:
                logger.error("Excel não suportado - pandas/openpyxl não instalados")
                return None
            return self._convert_excel_to_markdown(path.read_bytes(), path.name)
        
        # Verificar se é PDF
        if suffix == '.pdf':
            if not PYPDF2_AVAILABLE:
                logger.error("PDF não suportado - PyPDF2 não instalado")
                return None
            return self._convert_pdf_to_markdown(path.read_bytes(), path.name)
        
        # Formatos não suportados
        logger.warning(f"Formato {suffix} não suportado no MVP (apenas PDF texto nativo e Excel)")
        return None
    
    def convert_bytes(self, file_content: bytes, filename: str) -> Optional[str]:
        """
        Converte arquivo a partir de bytes (para upload) para Markdown.
        
        Args:
            file_content: Conteúdo do arquivo em bytes
            filename: Nome do arquivo (para detectar formato)
            
        Returns:
            str: Conteúdo Markdown ou None se erro
        """
        suffix = Path(filename).suffix.lower()
        
        # Roteamento: Excel usa conversão manual
        if suffix in ['.xlsx', '.xls']:
            if not EXCEL_AVAILABLE:
                logger.error("Excel não suportado - pandas/openpyxl não instalados")
                return None
            return self._convert_excel_to_markdown(file_content, filename)
        
        # PDF
        if suffix == '.pdf':
            if not PYPDF2_AVAILABLE:
                logger.error("PDF não suportado - PyPDF2 não instalado")
                return None
            return self._convert_pdf_to_markdown(file_content, filename)
        
        # Formatos não suportados
        logger.warning(f"Formato {suffix} não suportado no MVP (apenas PDF texto nativo e Excel)")
        return None
    
    def _convert_pdf_to_markdown(
        self,
        file_content: bytes,
        filename: str
    ) -> Optional[str]:
        """
        Converte PDF para Markdown usando PyPDF2/pdfplumber.
        
        IMPORTANTE: Apenas extrai texto nativo. PDFs escaneados (imagens) não funcionam.
        
        Args:
            file_content: Conteúdo do arquivo PDF em bytes
            filename: Nome do arquivo
            
        Returns:
            str: Markdown ou None se erro
        """
        try:
            pdf_io = io.BytesIO(file_content)
            text_parts = []
            
            # Tentar pdfplumber primeiro (melhor extração de tabelas)
            if PDFPLUMBER_AVAILABLE:
                try:
                    with pdfplumber.open(pdf_io) as pdf:
                        for i, page in enumerate(pdf.pages, 1):
                            # Extrair texto
                            page_text = page.extract_text()
                            if page_text:
                                text_parts.append(f"## Página {i}\n\n{page_text}\n\n")
                            
                            # Tentar extrair tabelas
                            tables = page.extract_tables()
                            if tables:
                                for j, table in enumerate(tables, 1):
                                    if table:
                                        # Converter tabela para Markdown
                                        markdown_table = self._table_to_markdown(table)
                                        text_parts.append(f"### Tabela {j} (Página {i})\n\n{markdown_table}\n\n")
                    
                    if text_parts:
                        markdown = "".join(text_parts)
                        # Calcular tamanho do texto real (removendo cabeçalhos e estrutura markdown)
                        text_content = markdown
                        # Remover cabeçalhos de página e tabelas (linhas que começam com #)
                        lines = text_content.split('\n')
                        content_lines = [line for line in lines if not line.strip().startswith('## Página') and not line.strip().startswith('### Tabela')]
                        text_content_clean = '\n'.join(content_lines)
                        text_length = len(text_content_clean.replace('#', '').replace('|', '').replace('-', '').strip())
                        
                        if text_length < 50:
                            logger.warning(
                                f"PDF {filename} retornou pouco texto ({text_length} caracteres). "
                                "Pode ser um PDF escaneado (imagem). OCR não está disponível no MVP. "
                                "Para PDFs escaneados, use uma solução com OCR (futuro)."
                            )
                        
                        logger.info(f"✅ PDF convertido: {filename} ({text_length} caracteres, {len(pdf.pages)} páginas)")
                        return markdown
                except Exception as e:
                    logger.debug(f"pdfplumber falhou, tentando PyPDF2: {e}")
                    pdf_io.seek(0)  # Resetar
            
            # Fallback para PyPDF2
            if PYPDF2_AVAILABLE:
                pdf_reader = PyPDF2.PdfReader(pdf_io)
                
                for i, page in enumerate(pdf_reader.pages, 1):
                    page_text = page.extract_text()
                    if page_text:
                        text_parts.append(f"## Página {i}\n\n{page_text}\n\n")
                
                if text_parts:
                    markdown = "".join(text_parts)
                    # Calcular tamanho do texto real (removendo cabeçalhos e estrutura markdown)
                    text_content = markdown
                    # Remover cabeçalhos de página
                    lines = text_content.split('\n')
                    content_lines = [line for line in lines if not line.strip().startswith('## Página')]
                    text_content_clean = '\n'.join(content_lines)
                    text_length = len(text_content_clean.replace('#', '').strip())
                    
                    if text_length < 50:
                        logger.warning(
                            f"PDF {filename} retornou pouco texto ({text_length} caracteres). "
                            "Pode ser um PDF escaneado (imagem). OCR não está disponível no MVP."
                        )
                    
                    logger.info(f"✅ PDF convertido: {filename} ({text_length} caracteres, {len(pdf_reader.pages)} páginas)")
                    return markdown
            
            # Se chegou aqui, não conseguiu extrair texto
            logger.error(
                f"Não foi possível extrair texto do PDF {filename}. "
                "O PDF pode estar escaneado (imagem) ou corrompido. "
                "OCR não está disponível no MVP (100% FREE)."
            )
            return None
            
        except Exception as e:
            logger.error(f"Erro ao converter PDF {filename}: {e}")
            import traceback
            logger.error(traceback.format_exc())
            return None
    
    def _table_to_markdown(self, table: list) -> str:
        """
        Converte tabela (lista de listas) para Markdown.
        
        Args:
            table: Lista de linhas, cada linha é uma lista de células
            
        Returns:
            str: Tabela em formato Markdown
        """
        if not table:
            return ""
        
        lines = []
        
        # Cabeçalho (primeira linha)
        if table:
            header = "| " + " | ".join([str(cell) if cell else "" for cell in table[0]]) + " |"
            lines.append(header)
            # Separador
            lines.append("| " + " | ".join(["---"] * len(table[0])) + " |")
        
        # Corpo (resto das linhas)
        for row in table[1:]:
            if row:  # Ignorar linhas vazias
                row_str = "| " + " | ".join([str(cell) if cell else "" for cell in row]) + " |"
                lines.append(row_str)
        
        return "\n".join(lines)
    
    def _convert_excel_to_markdown(
        self,
        file_content: bytes,
        filename: str
    ) -> Optional[str]:
        """
        Converte Excel para Markdown manualmente.
        Preserva tabelas, múltiplas abas e estrutura básica.
        
        Args:
            file_content: Conteúdo do arquivo Excel em bytes
            filename: Nome do arquivo
            
        Returns:
            str: Markdown ou None se erro
        """
        if not EXCEL_AVAILABLE:
            logger.error("pandas/openpyxl não disponíveis")
            return None
        
        try:
            excel_file = io.BytesIO(file_content)
            
            # Carregar workbook
            workbook = load_workbook(excel_file, data_only=True, read_only=True)
            
            markdown_sections = []
            
            # Processar cada planilha
            for sheet_name in workbook.sheetnames:
                try:
                    # Ler sheet como DataFrame
                    excel_file.seek(0)  # Resetar para ler novamente
                    df = pd.read_excel(
                        excel_file,
                        sheet_name=sheet_name,
                        engine='openpyxl'
                    )
                    
                    # Remover linhas completamente vazias
                    df = df.dropna(how='all').reset_index(drop=True)
                    
                    # Remover colunas completamente vazias
                    df = df.dropna(axis=1, how='all')
                    
                    # Pular se DataFrame vazio
                    if df.empty:
                        logger.debug(f"Planilha {sheet_name} está vazia, pulando...")
                        continue
                    
                    # Adicionar seção
                    markdown_sections.append(f"## {sheet_name}\n\n")
                    
                    # Converter DataFrame para Markdown table
                    # Usar tabulate para melhor formatação (se disponível)
                    try:
                        from tabulate import tabulate
                        markdown_table = tabulate(
                            df,
                            headers='keys',
                            tablefmt='pipe',
                            showindex=False
                        )
                    except ImportError:
                        # Fallback: usar método básico do pandas
                        markdown_table = df.to_markdown(index=False, tablefmt='pipe')
                    
                    markdown_sections.append(markdown_table)
                    markdown_sections.append("\n\n")
                    
                except Exception as e:
                    logger.warning(f"Erro ao processar planilha {sheet_name}: {e}")
                    continue
            
            workbook.close()
            
            if not markdown_sections:
                logger.warning(f"Nenhum conteúdo encontrado no Excel: {filename}")
                return None
            
            markdown = "".join(markdown_sections)
            logger.info(f"✅ Excel convertido: {filename} ({len(workbook.sheetnames)} planilhas)")
            return markdown
            
        except Exception as e:
            logger.error(f"Erro ao converter Excel {filename}: {e}")
            import traceback
            logger.error(traceback.format_exc())
            return None
