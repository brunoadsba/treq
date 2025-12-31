"""
Seleção de modelo LLM baseado no tipo de query e tarefa.
Otimizado com pré-compilação de padrões regex para performance.
"""
from typing import Optional, Tuple, List
from loguru import logger
import re

# Pré-compilar padrões regex para otimização (executado uma vez no import)
_HEAVY_PATTERNS_COMPILED: List[re.Pattern] = []
_SOTREQ_PATTERNS_COMPILED: List[re.Pattern] = []

def _compile_patterns():
    """Pré-compila todos os padrões regex uma vez no startup."""
    global _HEAVY_PATTERNS_COMPILED, _SOTREQ_PATTERNS_COMPILED
    
    if _HEAVY_PATTERNS_COMPILED:  # Já compilado
        return
    
    # Padrões de tarefas pesadas
    heavy_patterns = {
        "analise_multi": [
            "compare", "comparar", "relacione", "relacionar", "correlação", "correlacionar",
            "padrão", "padrões", "tendência", "tendências", "análise de", "análise dos",
            "síntese", "comparação", "relação entre", "correlação entre"
        ],
        "calculo_complexo": [
            "calcule", "calcular", "equação", "equações", "porcentagem", "percentual",
            "projeção", "projete", "se então", "impacto de", "impacto se",
            "redução de", "aumento de", "crescimento de", "diminuição de",
            "quanto será", "qual será", "se reduzirmos", "se aumentarmos"
        ],
        "sintese_executiva": [
            "resumo executivo", "visão geral", "dashboard", "múltiplos documentos",
            "consolidação", "consolidado", "panorama", "visão consolidada",
            "resumo geral", "visão estratégica", "análise consolidada"
        ],
        "raciocínio_profundo": [
            "por que múltiplos", "causa raiz de múltiplos", "análise profunda",
            "investigação", "investigar", "raiz do problema", "origem do problema",
            "por que vários", "motivos múltiplos", "fatores múltiplos"
        ]
    }
    
    # Compilar padrões simples (strings) em regex case-insensitive
    for category, patterns in heavy_patterns.items():
        for pattern in patterns:
            # Escapar caracteres especiais e criar regex
            escaped_pattern = re.escape(pattern)
            _HEAVY_PATTERNS_COMPILED.append(re.compile(escaped_pattern, re.IGNORECASE))
    
    # Padrões específicos Sotreq (já são regex)
    sotreq_specific_patterns = [
        r"compare.*unidades", r"comparar.*unidades", r"todas as unidades",
        r"todas unidades", r"múltiplas unidades", r"várias unidades",
        r"análise.*múltiplas", r"síntese.*operacional", r"visão geral.*operações",
        r"calcule.*impacto", r"projeção.*performance", r"tendência.*operacional",
        r"consolida.*unidades", r"dashboard.*operações", r"panorama.*operacional",
        r"análise.*consolidada", r"resumo.*todas.*unidades", r"performance.*todas",
        r"problemas.*múltiplas", r"alertas.*todas", r"status.*todas.*unidades"
    ]
    
    for pattern in sotreq_specific_patterns:
        _SOTREQ_PATTERNS_COMPILED.append(re.compile(pattern, re.IGNORECASE))
    
    logger.debug(f"✅ Padrões regex pré-compilados: {len(_HEAVY_PATTERNS_COMPILED)} padrões simples + {len(_SOTREQ_PATTERNS_COMPILED)} padrões Sotreq")

# Compilar padrões no import
_compile_patterns()


def is_heavy_task(
    query_text: Optional[str],
    query_type: Optional[str],
    use_3_level: bool,
    zhipu_available: bool
) -> bool:
    """
    Detecta se query requer GLM 4 (tarefa pesada).
    
    Tarefas pesadas:
    - Consultoria (sempre usa GLM 4)
    - Análise multi-dimensional (compare, relacione, correlação)
    - Cálculos complexos (calcule, equação, porcentagem, projeção)
    - Síntese executiva (resumo executivo, visão geral, dashboard)
    - Raciocínio profundo (por que múltiplos, causa raiz de múltiplos)
    
    Args:
        query_text: Texto da query do usuário
        query_type: Tipo da query classificada
        use_3_level: Se roteamento em 3 níveis está habilitado
        zhipu_available: Se cliente Zhipu está disponível
        
    Returns:
        bool: True se é tarefa pesada
    """
    if not query_text:
        logger.debug("is_heavy_task: query_text vazio")
        return False
    
    if not use_3_level:
        logger.debug("is_heavy_task: roteamento em 3 níveis desabilitado")
        return False
    
    if not zhipu_available:
        logger.debug("is_heavy_task: Zhipu AI não disponível (GLM 4 desabilitado)")
        return False
    
    # Consultoria sempre usa GLM 4
    if query_type == "consultoria":
        return True
    
    query_lower = query_text.lower()
    
    # Verificar padrões pré-compilados (otimizado - O(n) em vez de O(n*m))
    # Padrões simples
    for pattern in _HEAVY_PATTERNS_COMPILED:
        if pattern.search(query_lower):
            logger.info(f"🔷 Tarefa pesada detectada (padrão simples: {pattern.pattern}) para query: '{query_text[:50]}...'")
            return True
    
    # Padrões específicos Sotreq (regex)
    for pattern in _SOTREQ_PATTERNS_COMPILED:
        if pattern.search(query_lower):
            logger.info(f"🔷 Tarefa pesada detectada (padrão Sotreq: {pattern.pattern}) para query: '{query_text[:50]}...'")
            return True
    
    logger.debug(f"Query '{query_text[:50]}...' não detectada como tarefa pesada")
    return False


def select_model(
    query_type: Optional[str],
    query_text: Optional[str],
    model_8b: str,
    model_70b: str,
    glm_model: str,
    use_dynamic: bool,
    use_3_level: bool,
    zhipu_available: bool
) -> Tuple[str, str]:
    """
    Seleção em 3 níveis:
    - Nível 1 (8B): Queries simples
    - Nível 2 (70B): Queries complexas padrão
    - Nível 3 (GLM 4): Tarefas pesadas
    
    Args:
        query_type: Tipo da query (detalhamento, causa, procedimento, etc.)
        query_text: Texto da query (para detecção de tarefas pesadas)
        model_8b: Nome do modelo 8B
        model_70b: Nome do modelo 70B
        glm_model: Nome do modelo GLM 4
        use_dynamic: Se roteamento dinâmico está habilitado
        use_3_level: Se roteamento em 3 níveis está habilitado
        zhipu_available: Se cliente Zhipu está disponível
        
    Returns:
        tuple: (model_name, provider) - provider: "groq" ou "zhipu"
    """
    if not use_dynamic:
        return (model_8b, "groq")
    
    # Nível 3: Detectar tarefas pesadas (GLM 4)
    if is_heavy_task(query_text, query_type, use_3_level, zhipu_available):
        logger.info(f"🔷 Usando GLM 4 para tarefa pesada")
        return (glm_model, "zhipu")
    
    # Nível 2: Complexas padrão (Llama 70B)
    complex_queries = ["detalhamento", "causa", "procedimento"]
    if query_type in complex_queries:
        logger.debug(f"Usando modelo 70B para query complexa: {query_type}")
        return (model_70b, "groq")
    
    # Nível 1: Simples (Llama 8B)
    return (model_8b, "groq")
