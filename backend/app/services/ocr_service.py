"""
Serviço de OCR para processamento de PDFs escaneados.
Suporte básico usando pytesseract (requer Tesseract instalado no sistema).

LIMITAÇÕES:
- Requer Tesseract OCR instalado no sistema
- Processamento mais lento que PDFs nativos
- Qualidade depende da qualidade da imagem escaneada

INSTALAÇÃO:
- Ubuntu/Debian: sudo apt-get install tesseract-ocr tesseract-ocr-por
- macOS: brew install tesseract tesseract-lang
- Windows: Baixar instalador de https://github.com/UB-Mannheim/tesseract/wiki
"""
from typing import Optional
from loguru import logger
import re
from io import BytesIO

# Verificar disponibilidade de bibliotecas OCR
try:
    import pytesseract
    PYTESSERACT_AVAILABLE = True
except ImportError:
    PYTESSERACT_AVAILABLE = False
    logger.warning("pytesseract não instalado. OCR não será suportado.")

try:
    from pdf2image import convert_from_bytes
    PDF2IMAGE_AVAILABLE = True
except ImportError:
    PDF2IMAGE_AVAILABLE = False
    logger.warning("pdf2image não instalado. OCR não será suportado.")

try:
    from PIL import Image
    import numpy as np
    PIL_AVAILABLE = True
except ImportError:
    PIL_AVAILABLE = False
    logger.warning("PIL/Pillow não instalado. OCR não será suportado.")


class OCRService:
    """Serviço de OCR para processamento de PDFs escaneados."""
    
    def __init__(self, confidence_threshold: float = 70.0):
        """
        Inicializa o serviço de OCR.
        
        Args:
            confidence_threshold: Limite mínimo de confiança OCR (0-100)
        """
        self.confidence_threshold = confidence_threshold
        self.is_available = PYTESSERACT_AVAILABLE and PDF2IMAGE_AVAILABLE and PIL_AVAILABLE
        
        if self.is_available:
            logger.info("✅ OCRService inicializado (pytesseract + pdf2image)")
        else:
            missing = []
            if not PYTESSERACT_AVAILABLE:
                missing.append("pytesseract")
            if not PDF2IMAGE_AVAILABLE:
                missing.append("pdf2image")
            if not PIL_AVAILABLE:
                missing.append("PIL/Pillow")
            logger.warning(f"OCRService não disponível - faltando: {', '.join(missing)}")
    
    def is_ocr_available(self) -> bool:
        """Verifica se OCR está disponível."""
        return self.is_available
    
    def process_image(self, image_bytes: bytes, filename: str = "image.jpg") -> Optional[str]:
        """
        Processa imagem diretamente com OCR e retorna Markdown.
        
        Args:
            image_bytes: Conteúdo da imagem em bytes
            filename: Nome do arquivo (para logging e detecção de formato)
            
        Returns:
            str: Texto extraído em formato Markdown ou None se erro
        """
        if not self.is_available:
            logger.error("OCR não disponível - bibliotecas não instaladas")
            return None
        
        try:
            logger.info(f"Iniciando OCR para imagem: {filename}")
            
            # Abrir imagem usando PIL
            try:
                image = Image.open(BytesIO(image_bytes))
                # Converter para RGB se necessário (PNG pode ter RGBA, GIF pode ter P)
                if image.mode not in ('RGB', 'L'):
                    image = image.convert('RGB')
            except Exception as e:
                logger.error(f"Erro ao abrir imagem: {e}")
                return None
            
            if not image:
                logger.warning(f"Imagem não pôde ser aberta: {filename}")
                return None
            
            logger.info(f"Imagem aberta: {image.size[0]}x{image.size[1]} pixels")
            
            # Pré-processamento da imagem (melhora qualidade OCR)
            processed_image = self._preprocess_image(image)
            
            # OCR com configuração otimizada para português
            text = pytesseract.image_to_string(
                processed_image,
                lang='por+eng',  # Português + Inglês
                config='--psm 1 --oem 3 -c preserve_interword_spaces=1'
            )
            
            if not text.strip():
                logger.warning(f"Nenhum texto extraído da imagem: {filename}")
                return None
            
            # Pós-processamento do texto
            cleaned_text = self._postprocess_ocr_text(text)
            
            if not cleaned_text:
                logger.warning(f"Texto extraído mas vazio após processamento: {filename}")
                return None
            
            # Formatar como Markdown
            result = f"# Texto extraído de {filename}\n\n{cleaned_text}"
            
            logger.info(f"OCR concluído: {filename} - {len(cleaned_text)} caracteres extraídos")
            
            return result
            
        except Exception as e:
            logger.error(f"Erro no processamento OCR da imagem: {e}")
            import traceback
            logger.error(traceback.format_exc())
            return None
    
    def process_scanned_pdf(self, pdf_bytes: bytes, filename: str = "document.pdf") -> Optional[str]:
        """
        Processa PDF escaneado com OCR e retorna Markdown.
        
        Args:
            pdf_bytes: Conteúdo do PDF em bytes
            filename: Nome do arquivo (para logging)
            
        Returns:
            str: Texto extraído em formato Markdown ou None se erro
        """
        if not self.is_available:
            logger.error("OCR não disponível - bibliotecas não instaladas")
            return None
        
        try:
            logger.info(f"Iniciando OCR para PDF escaneado: {filename}")
            
            # Converter PDF para imagens
            try:
                images = convert_from_bytes(pdf_bytes, dpi=300)
            except Exception as e:
                logger.error(f"Erro ao converter PDF para imagens: {e}")
                return None
            
            if not images:
                logger.warning(f"Nenhuma imagem extraída do PDF: {filename}")
                return None
            
            logger.info(f"PDF convertido em {len(images)} imagens")
            
            extracted_text = []
            
            for i, image in enumerate(images, 1):
                try:
                    # Pré-processamento da imagem (melhora qualidade OCR)
                    processed_image = self._preprocess_image(image)
                    
                    # OCR com configuração otimizada para português
                    text = pytesseract.image_to_string(
                        processed_image,
                        lang='por+eng',  # Português + Inglês
                        config='--psm 1 --oem 3 -c preserve_interword_spaces=1'
                    )
                    
                    if text.strip():
                        # Pós-processamento do texto
                        cleaned_text = self._postprocess_ocr_text(text)
                        
                        if cleaned_text:
                            extracted_text.append(f"## Página {i}\n")
                            extracted_text.append(cleaned_text)
                            extracted_text.append("\n")
                            logger.debug(f"Página {i} processada: {len(cleaned_text)} caracteres")
                    else:
                        logger.warning(f"Página {i} não retornou texto (pode estar vazia ou com baixa qualidade)")
                        
                except Exception as page_error:
                    logger.error(f"Erro ao processar página {i}: {page_error}")
                    continue
            
            if not extracted_text:
                logger.warning(f"Nenhum texto extraído do PDF escaneado: {filename}")
                return None
            
            result = "\n".join(extracted_text).strip()
            logger.info(f"OCR concluído: {filename} - {len(result)} caracteres extraídos de {len(images)} páginas")
            
            return result
            
        except Exception as e:
            logger.error(f"Erro no processamento OCR: {e}")
            import traceback
            logger.error(traceback.format_exc())
            return None
    
    def _preprocess_image(self, image: Image.Image) -> Image.Image:
        """
        Pré-processamento da imagem para melhorar qualidade OCR.
        
        Args:
            image: Imagem PIL
            
        Returns:
            Image.Image: Imagem processada
        """
        try:
            # Converter para escala de cinza
            gray = image.convert('L')
            
            # Converter para numpy array para processamento
            np_image = np.array(gray)
            
            # Normalizar contraste
            if np_image.max() > np_image.min():
                np_image = ((np_image - np_image.min()) / (np_image.max() - np_image.min()) * 255).astype(np.uint8)
            
            # Aplicar threshold adaptativo simples
            threshold = 128
            binary = Image.fromarray((np_image > threshold).astype(np.uint8) * 255)
            
            return binary
            
        except Exception as e:
            logger.warning(f"Erro no pré-processamento de imagem: {e}, usando imagem original")
            return image.convert('L')
    
    def _postprocess_ocr_text(self, text: str) -> str:
        """
        Pós-processamento do texto OCR para melhorar qualidade.
        
        Args:
            text: Texto bruto do OCR
            
        Returns:
            str: Texto processado
        """
        if not text:
            return ""
        
        # Remover caracteres estranhos (manter apenas letras, números, pontuação e espaços)
        text = re.sub(r'[^\w\s.,;:!?()"\'\-áéíóúàèìòùãõâêîôûçÁÉÍÓÚÀÈÌÒÙÃÕÂÊÎÔÛÇ\n]', '', text)
        
        # Corrigir quebras de linha múltiplas
        text = re.sub(r'\n{3,}', '\n\n', text)
        
        # Corrigir espaços múltiplos
        text = re.sub(r' {2,}', ' ', text)
        
        # Remover espaços no início/fim de linhas
        lines = [line.strip() for line in text.split('\n')]
        text = '\n'.join(lines)
        
        # Remover linhas vazias excessivas
        text = re.sub(r'\n\n\n+', '\n\n', text)
        
        return text.strip()
    
    def get_ocr_confidence(self, text: str) -> float:
        """
        Estima confiança do OCR baseado em características do texto.
        (Simplificado - OCR real retorna confiança por palavra)
        
        Args:
            text: Texto extraído
            
        Returns:
            float: Confiança estimada (0-100)
        """
        if not text or len(text.strip()) < 10:
            return 0.0
        
        # Heurística simples: verificar proporção de caracteres válidos
        valid_chars = sum(1 for c in text if c.isalnum() or c in ' .,;:!?()"\'-')
        total_chars = len(text)
        
        if total_chars == 0:
            return 0.0
        
        confidence = (valid_chars / total_chars) * 100
        
        # Penalizar textos muito curtos ou com muitos caracteres estranhos
        if len(text.strip()) < 50:
            confidence *= 0.8
        
        return min(confidence, 100.0)
