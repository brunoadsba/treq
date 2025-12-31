"""
Health check endpoints para monitoramento de serviços LLM.
"""
from fastapi import APIRouter, Depends
from loguru import logger
from app.core.llm_dependency_manager import LLMDependencyManager
from app.services.llm_service import LLMService
from app.api.routes.chat import get_llm_service

router = APIRouter(prefix="/health", tags=["health"])


@router.get("/llm")
async def llm_health_check(
    llm_service: LLMService = Depends(get_llm_service)
):
    """
    Health check específico para serviços LLM.
    
    Retorna status detalhado de cada modelo LLM:
    - Groq 8B: Status, latência, disponibilidade
    - Groq 70B: Status, latência, disponibilidade
    - GLM 4: Status, disponibilidade, motivo se desabilitado
    """
    providers = LLMDependencyManager.get_available_providers()
    
    # Status base
    status = {
        "groq_8b": {
            "status": "active" if providers["groq"] else "disabled",
            "model": "llama-3.1-8b-instant",
            "provider": "groq",
            "latency_ms": None,
            "reason": None if providers["groq"] else LLMDependencyManager.get_provider_status("groq")["reason"]
        },
        "groq_70b": {
            "status": "active" if providers["groq"] else "disabled",
            "model": "llama-3.3-70b-versatile",
            "provider": "groq",
            "latency_ms": None,
            "reason": None if providers["groq"] else LLMDependencyManager.get_provider_status("groq")["reason"]
        },
        "glm_4": {
            "status": "active" if providers["zhipu"] else "disabled",
            "model": "glm-4.7",
            "provider": "zhipu",
            "latency_ms": None,
            "reason": None if providers["zhipu"] else LLMDependencyManager.get_provider_status("zhipu")["reason"]
        }
    }
    
    # Teste de latência para modelos ativos (opcional, pode ser pesado)
    # Por padrão, não fazemos teste real para não sobrecarregar
    # Mas podemos fazer um teste simples se necessário
    
    # Adicionar informações detalhadas de cada provider
    groq_status = LLMDependencyManager.get_provider_status("groq")
    zhipu_status = LLMDependencyManager.get_provider_status("zhipu")
    
    status["groq_8b"]["details"] = groq_status
    status["groq_70b"]["details"] = groq_status  # Compartilha mesmo provider
    status["glm_4"]["details"] = zhipu_status
    
    # Informações gerais
    status["summary"] = {
        "total_providers": 2,
        "active_providers": sum([providers["groq"], providers["zhipu"]]),
        "routing_enabled": llm_service.use_dynamic,
        "three_level_routing": llm_service.use_3_level
    }
    
    return status


@router.get("/llm/providers")
async def llm_providers_check():
    """
    Retorna apenas status dos providers (mais leve que /llm).
    """
    providers = LLMDependencyManager.get_available_providers()
    
    return {
        "providers": providers,
        "groq": LLMDependencyManager.get_provider_status("groq"),
        "zhipu": LLMDependencyManager.get_provider_status("zhipu")
    }
