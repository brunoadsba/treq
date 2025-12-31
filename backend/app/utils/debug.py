"""
Debug utilities - Decorators para observabilidade de generators.

Fornece trace_generator para rastreamento do ciclo de vida de generators.
"""
import functools
import logging

logger = logging.getLogger(__name__)


def trace_generator(generator_name: str):
    """
    Decorator para rastrear criação, yield e fechamento de generators.
    
    Args:
        generator_name: Nome identificador do generator para logs
    
    Usage:
        @trace_generator("GLM4_Stream")
        def _stream_glm4(...):
            # código do generator
    """
    def decorator(func):
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            logger.info(f"🟢 [{generator_name}] CRIADO")
            
            # Cria o generator original
            gen = func(*args, **kwargs)
            
            # Cria um generator proxy para monitorar o loop
            def traced_generator():
                chunk_count = 0
                try:
                    for value in gen:
                        chunk_count += 1
                        if chunk_count == 1:
                            logger.info(f"🟡 [{generator_name}] PRIMEIRO CHUNK YIELDADO")
                        yield value
                except GeneratorExit:
                    logger.warning(f"🔴 [{generator_name}] FECHADO PELO CLIENTE (GeneratorExit) após {chunk_count} chunks")
                    raise
                except Exception as e:
                    logger.error(f"💥 [{generator_name}] ERRO NO LOOP: {str(e)}")
                    raise
                finally:
                    logger.info(f"⚫ [{generator_name}] FINALIZADO (Total: {chunk_count} chunks)")
            
            return traced_generator()
        return wrapper
    return decorator
