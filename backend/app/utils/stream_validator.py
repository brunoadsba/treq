"""
StreamValidator - Wrapper para validação de generators sem consumir o iterator.

Resolve o problema de iterator exhaustion no pipeline de streaming GLM-4.
"""
import logging
from typing import Generator, Any, Optional

logger = logging.getLogger(__name__)


class StreamValidator:
    """
    Wrapper que valida um generator sem consumir o iterator principal.
    
    Problema resolvido:
    - Generators Python são single-pass iterators
    - Qualquer validação/peek consome o iterator
    - Isso causa "iterator exhaustion" antes do loop SSE
    
    Solução:
    - Armazena o primeiro chunk durante validação
    - Yield do chunk armazenado antes de delegar ao generator original
    - Mantém a integridade do iterator para o loop SSE
    """
    
    def __init__(self, generator: Generator[Any, None, None]):
        """
        Inicializa o wrapper.
        
        Args:
            generator: Generator original a ser validado
        """
        self._gen = generator
        self._validated = False
        self._first_chunk: Optional[Any] = None
        self._is_empty = False
    
    def __iter__(self):
        """Retorna o iterator (self)."""
        return self
    
    def __next__(self):
        """
        Implementa o protocolo de iterator.
        
        Returns:
            Próximo chunk do generator
            
        Raises:
            StopIteration: Quando o generator está exausto
        """
        # Primeira iteração: validar e armazenar primeiro chunk
        if not self._validated:
            try:
                self._first_chunk = next(self._gen)
                self._validated = True
                logger.info(f"✅ Stream validado - primeiro chunk: {str(self._first_chunk)[:50]}...")
            except StopIteration:
                self._is_empty = True
                self._validated = True
                logger.error("❌ Stream vazio - generator não produziu chunks")
                raise
        
        # Se estava vazio, propagar StopIteration
        if self._is_empty:
            raise StopIteration
        
        # Se temos o primeiro chunk armazenado, retorná-lo
        if self._first_chunk is not None:
            chunk = self._first_chunk
            self._first_chunk = None  # Limpar para não retornar novamente
            return chunk
        
        # Delegar para o generator original
        return next(self._gen)
    
    def validate(self) -> bool:
        """
        Valida explicitamente o generator sem consumir no loop.
        
        Returns:
            True se o generator tem chunks, False caso contrário
        """
        if not self._validated:
            try:
                self._first_chunk = next(self._gen)
                self._validated = True
                logger.info("✅ Validação explícita bem-sucedida")
                return True
            except StopIteration:
                self._is_empty = True
                self._validated = True
                logger.error("❌ Validação explícita falhou - stream vazio")
                return False
        
        return not self._is_empty
