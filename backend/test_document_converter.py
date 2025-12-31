#!/usr/bin/env python3
"""
Script de teste para DocumentConverterService via terminal.

Este script testa a conversão de documentos (PDF, Excel, DOCX, PPTX)
mostrando logs detalhados e validando a conversão.

Uso:
    python test_document_converter.py
    python test_document_converter.py --format docx
    python test_document_converter.py --format pptx --file caminho/arquivo.pptx
"""

import sys
import argparse
from pathlib import Path
from typing import Optional
from io import BytesIO

# Adicionar o diretório raiz ao path para imports
backend_dir = Path(__file__).parent
sys.path.insert(0, str(backend_dir))

from app.services.document_converter import DocumentConverterService
from loguru import logger

# Configurar logger
logger.remove()
logger.add(
    sys.stderr,
    format="<green>{time:HH:mm:ss}</green> | <level>{level: <8}</level> | <level>{message}</level>",
    level="INFO",
    colorize=True
)


def print_section(title: str):
    """Imprime um separador visual."""
    print("\n" + "=" * 80)
    print(f"  {title}")
    print("=" * 80 + "\n")


def test_converter_initialization():
    """Testa inicialização do conversor."""
    print_section("TESTE 1: INICIALIZAÇÃO DO CONVERSOR")
    
    try:
        converter = DocumentConverterService()
        print("✅ DocumentConverterService inicializado com sucesso")
        
        # Verificar formatos disponíveis
        if hasattr(converter, 'enable_ocr'):
            print(f"   OCR habilitado: {converter.enable_ocr}")
        
        return True, converter
    except Exception as e:
        print(f"❌ Erro ao inicializar: {e}")
        import traceback
        traceback.print_exc()
        return False, None


def test_format_support(converter: DocumentConverterService):
    """Testa suporte a formatos."""
    print_section("TESTE 2: SUPORTE A FORMATOS")
    
    formats = {
        '.pdf': 'PDF',
        '.xlsx': 'Excel',
        '.xls': 'Excel',
        '.docx': 'DOCX',
        '.pptx': 'PPTX'
    }
    
    print("Formatos suportados:")
    results = {}
    for ext, name in formats.items():
        # Verificar disponibilidade baseado em imports
        available = False
        if ext == '.pdf':
            try:
                import PyPDF2
                available = True
            except ImportError:
                pass
        elif ext in ['.xlsx', '.xls']:
            try:
                import pandas
                available = True
            except ImportError:
                pass
        elif ext == '.docx':
            try:
                from docx import Document
                available = True
            except ImportError:
                pass
        elif ext == '.pptx':
            try:
                from pptx import Presentation
                available = True
            except ImportError:
                pass
        
        status = "✅" if available else "❌"
        results[ext] = available
        print(f"   {status} {name} ({ext})")
    
    return results


def test_conversion_from_bytes(converter: DocumentConverterService, file_path: Path, expected_format: str):
    """Testa conversão a partir de bytes."""
    print_section(f"TESTE 3: CONVERSÃO DE {expected_format.upper()}")
    
    if not file_path.exists():
        print(f"❌ Arquivo não encontrado: {file_path}")
        return False
    
    try:
        # Ler arquivo
        file_content = file_path.read_bytes()
        file_size = len(file_content)
        print(f"📄 Arquivo: {file_path.name}")
        print(f"   Tamanho: {file_size / 1024:.2f} KB")
        
        # Converter
        print(f"🔄 Convertendo {expected_format} para Markdown...")
        markdown_content = converter.convert_bytes(file_content, file_path.name)
        
        if markdown_content:
            content_length = len(markdown_content)
            lines = markdown_content.count('\n')
            
            print(f"✅ Conversão bem-sucedida!")
            print(f"   Tamanho do Markdown: {content_length} caracteres")
            print(f"   Linhas: {lines}")
            
            # Mostrar preview
            preview = markdown_content[:500].replace('\n', ' ')
            print(f"\n📝 Preview (primeiros 500 caracteres):")
            print(f"   {preview}...")
            
            # Verificar estrutura básica
            has_headers = '#' in markdown_content
            has_content = len(markdown_content.strip()) > 100
            
            print(f"\n🔍 Validação:")
            print(f"   {'✅' if has_headers else '⚠️'} Contém cabeçalhos Markdown")
            print(f"   {'✅' if has_content else '❌'} Tem conteúdo suficiente")
            
            return True
        else:
            print("❌ Conversão retornou None (erro ou formato não suportado)")
            return False
            
    except Exception as e:
        print(f"❌ Erro durante conversão: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_invalid_file(converter: DocumentConverterService):
    """Testa tratamento de arquivo inválido."""
    print_section("TESTE 4: TRATAMENTO DE ERROS")
    
    try:
        # Teste com arquivo inexistente
        result = converter.convert_bytes(b"invalid content", "test.xyz")
        if result is None:
            print("✅ Arquivo inválido tratado corretamente (retornou None)")
            return True
        else:
            print("⚠️ Arquivo inválido não foi rejeitado")
            return False
    except Exception as e:
        print(f"✅ Erro tratado corretamente: {type(e).__name__}")
        return True


def test_ocr_service():
    """Testa disponibilidade do OCR Service."""
    print_section("TESTE 5: SERVIÇO OCR (OPCIONAL)")
    
    try:
        from app.services.ocr_service import OCRService
        
        ocr_service = OCRService()
        is_available = ocr_service.is_ocr_available()
        
        if is_available:
            print("✅ OCR Service disponível e funcional")
            print("   PDFs escaneados podem ser processados")
        else:
            print("⚠️ OCR Service não disponível")
            print("   Bibliotecas faltando: pytesseract, pdf2image ou Pillow")
            print("   Ou Tesseract OCR não instalado no sistema")
        
        return True
    except ImportError:
        print("⚠️ OCR Service não importável (módulo não encontrado)")
        return True  # Não é erro crítico


def main():
    """Função principal."""
    parser = argparse.ArgumentParser(description="Teste de conversão de documentos")
    parser.add_argument(
        '--format',
        choices=['pdf', 'xlsx', 'docx', 'pptx', 'all'],
        default='all',
        help='Formato específico para testar'
    )
    parser.add_argument(
        '--file',
        type=str,
        help='Caminho para arquivo específico para testar'
    )
    
    args = parser.parse_args()
    
    print_section("TESTE DE CONVERSÃO DE DOCUMENTOS - Treq")
    print(f"Formato: {args.format}")
    if args.file:
        print(f"Arquivo: {args.file}")
    
    # Teste 1: Inicialização
    success, converter = test_converter_initialization()
    if not success:
        print("\n❌ Falha na inicialização. Abortando testes.")
        sys.exit(1)
    
    # Teste 2: Suporte a formatos
    format_results = test_format_support(converter)
    
    # Teste 3: Conversão (se arquivo fornecido)
    conversion_success = None
    if args.file:
        file_path = Path(args.file)
        if file_path.exists():
            ext = file_path.suffix.lower()
            format_map = {
                '.pdf': 'PDF',
                '.xlsx': 'Excel',
                '.xls': 'Excel',
                '.docx': 'DOCX',
                '.pptx': 'PPTX'
            }
            expected_format = format_map.get(ext, 'Desconhecido')
            conversion_success = test_conversion_from_bytes(converter, file_path, expected_format)
        else:
            print(f"\n❌ Arquivo não encontrado: {args.file}")
    
    # Teste 4: Tratamento de erros
    error_handling_success = test_invalid_file(converter)
    
    # Teste 5: OCR Service
    ocr_test_success = test_ocr_service()
    
    # Resumo final
    print_section("RESUMO DOS TESTES")
    
    print("✅ Inicialização: OK")
    print(f"✅ Suporte a formatos: Verificado ({sum(format_results.values())}/{len(format_results)} disponíveis)")
    if conversion_success is not None:
        print(f"{'✅' if conversion_success else '❌'} Conversão: {'OK' if conversion_success else 'FALHOU'}")
    else:
        print("⚠️ Conversão: Não testado (use --file para testar)")
    print(f"{'✅' if error_handling_success else '❌'} Tratamento de erros: {'OK' if error_handling_success else 'FALHOU'}")
    print(f"{'✅' if ocr_test_success else '⚠️'} OCR Service: {'OK' if ocr_test_success else 'Não disponível (opcional)'}")
    
    print("\n💡 Dica: Use --file para testar conversão de um arquivo específico")
    print("   Exemplo: python test_document_converter.py --file documento.docx")


if __name__ == "__main__":
    main()
