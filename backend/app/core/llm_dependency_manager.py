"""
Gerenciador de dependências LLM - Verificação proativa de disponibilidade.
"""
import importlib.util
import sys
from typing import Dict, Optional
from loguru import logger
from app.config import get_settings


class LLMDependencyManager:
    """Gerencia dependências e disponibilidade de modelos LLM."""
    
    _providers_cache: Optional[Dict[str, bool]] = None
    
    @staticmethod
    def get_available_providers() -> Dict[str, bool]:
        """
        Verifica quais providers LLM estão disponíveis.
        
        Returns:
            Dict com status de cada provider:
            {
                "groq": True/False,
                "zhipu": True/False
            }
        """
        # Usar cache para evitar verificações repetidas
        if LLMDependencyManager._providers_cache is not None:
            return LLMDependencyManager._providers_cache
        
        providers = {"groq": False, "zhipu": False}
        settings = get_settings()
        
        # Verificar Groq (obrigatório)
        if settings.groq_api_key:
            try:
                import groq
                providers["groq"] = True
                logger.debug("✅ Provider Groq disponível")
            except ImportError:
                logger.warning("⚠️ groq não instalado - Groq desabilitado")
        else:
            logger.warning("⚠️ GROQ_API_KEY não configurada - Groq desabilitado")
        
        # Verificar Zhipu AI (opcional)
        zhipu_available = False
        try:
            # Verificar se módulo está instalado
            if "zai" in sys.modules:
                zhipu_available = True
            elif importlib.util.find_spec("zai") is not None:
                zhipu_available = True
            
            # Se módulo disponível, verificar API key
            if zhipu_available:
                if settings.zhipu_api_key:
                    try:
                        from zai import ZhipuAiClient
                        # Tentar criar cliente para validar
                        test_client = ZhipuAiClient(api_key=settings.zhipu_api_key)
                        providers["zhipu"] = True
                        logger.debug("✅ Provider Zhipu AI disponível")
                    except Exception as e:
                        logger.warning(f"⚠️ Zhipu AI SDK instalado mas API key inválida: {e}")
                        providers["zhipu"] = False
                else:
                    logger.debug("⚠️ zai-sdk instalado mas ZHIPU_API_KEY não configurada")
                    providers["zhipu"] = False
            else:
                logger.debug("⚠️ zai-sdk não instalado - Zhipu AI desabilitado")
                providers["zhipu"] = False
        except Exception as e:
            logger.warning(f"⚠️ Erro ao verificar Zhipu AI: {e}")
            providers["zhipu"] = False
        
        # Cachear resultado
        LLMDependencyManager._providers_cache = providers
        return providers
    
    @staticmethod
    def clear_cache():
        """Limpa cache de providers (útil para testes)."""
        LLMDependencyManager._providers_cache = None
    
    @staticmethod
    def get_provider_status(provider: str) -> Dict[str, any]:
        """
        Retorna status detalhado de um provider específico.
        
        Args:
            provider: Nome do provider ("groq" ou "zhipu")
            
        Returns:
            Dict com informações detalhadas do provider
        """
        providers = LLMDependencyManager.get_available_providers()
        settings = get_settings()
        
        if provider == "groq":
            return {
                "available": providers["groq"],
                "api_key_configured": bool(settings.groq_api_key),
                "sdk_installed": "groq" in sys.modules or importlib.util.find_spec("groq") is not None,
                "reason": None if providers["groq"] else (
                    "GROQ_API_KEY não configurada" if not settings.groq_api_key 
                    else "groq SDK não instalado"
                )
            }
        elif provider == "zhipu":
            return {
                "available": providers["zhipu"],
                "api_key_configured": bool(settings.zhipu_api_key),
                "sdk_installed": "zai" in sys.modules or importlib.util.find_spec("zai") is not None,
                "reason": None if providers["zhipu"] else (
                    "ZHIPU_API_KEY não configurada" if not settings.zhipu_api_key
                    else "zai-sdk não instalado"
                )
            }
        else:
            return {
                "available": False,
                "reason": f"Provider desconhecido: {provider}"
            }
