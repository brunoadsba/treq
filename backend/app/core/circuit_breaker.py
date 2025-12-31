"""
Circuit Breakers para serviços externos.
Previne cascata de falhas quando serviços externos estão indisponíveis.
"""
from typing import Callable, Any, Optional
from loguru import logger

try:
    import pybreaker
    PYBREAKER_AVAILABLE = True
except ImportError:
    PYBREAKER_AVAILABLE = False
    logger.warning("pybreaker não instalado - circuit breakers desabilitados")


class CircuitBreakerError(Exception):
    """Exceção lançada quando circuit breaker está aberto."""
    pass


# Definir CircuitBreakerLogger apenas se pybreaker estiver disponível
if PYBREAKER_AVAILABLE:
    class CircuitBreakerLogger(pybreaker.CircuitBreakerListener):
        """Listener customizado para logging de eventos do circuit breaker."""
        
        def __init__(self, name: str):
            self.name = name
            super().__init__()
        
        def state_change(self, cb, old_state, new_state):
            """Chamado quando o estado do circuit breaker muda."""
            state_name = str(new_state).split('.')[-1]  # Pega apenas o nome do estado
            if state_name == 'OPEN':
                logger.error(f"🔴 Circuit breaker '{self.name}' ABERTO - {cb.fail_counter} falhas")
            elif state_name == 'CLOSED':
                logger.info(f"🟢 Circuit breaker '{self.name}' FECHADO - recuperado")
            elif state_name == 'HALF_OPEN':
                logger.warning(f"🟡 Circuit breaker '{self.name}' HALF-OPEN - tentando recuperar")
else:
    # Stub para quando pybreaker não está disponível
    class CircuitBreakerLogger:
        """Stub quando pybreaker não está disponível."""
        def __init__(self, name: str):
            self.name = name


def create_circuit_breaker(
    name: str,
    failure_threshold: int = 5,
    success_threshold: int = 2,
    timeout: float = 60.0
) -> Optional[Any]:
    """
    Cria um circuit breaker configurado.
    
    Args:
        name: Nome do circuit breaker (para logging)
        failure_threshold: Número de falhas antes de abrir o circuito
        success_threshold: Número de sucessos antes de fechar o circuito
        timeout: Tempo (segundos) antes de tentar fechar o circuito novamente
        
    Returns:
        CircuitBreaker instance ou None se pybreaker não estiver disponível
    """
    if not PYBREAKER_AVAILABLE:
        logger.warning(f"Circuit breaker '{name}' desabilitado - pybreaker não instalado")
        return None
    
    listener = CircuitBreakerLogger(name)
    
    breaker = pybreaker.CircuitBreaker(
        fail_max=failure_threshold,
        reset_timeout=timeout,
        success_threshold=success_threshold,
        listeners=[listener]
    )
    
    logger.info(
        f"Circuit breaker '{name}' criado: "
        f"abrir após {failure_threshold} falhas, "
        f"fechar após {success_threshold} sucessos, "
        f"timeout {timeout}s"
    )
    
    return breaker


# Circuit breakers globais
_groq_breaker: Optional[Any] = None
_zhipu_breaker: Optional[Any] = None
_supabase_breaker: Optional[Any] = None


def get_groq_breaker() -> Optional[Any]:
    """Retorna circuit breaker para Groq API."""
    global _groq_breaker
    if _groq_breaker is None and PYBREAKER_AVAILABLE:
        _groq_breaker = create_circuit_breaker(
            name="Groq_API",
            failure_threshold=5,
            success_threshold=2,
            timeout=60.0
        )
    return _groq_breaker


def get_zhipu_breaker() -> Optional[Any]:
    """Retorna circuit breaker para Zhipu AI."""
    global _zhipu_breaker
    if _zhipu_breaker is None and PYBREAKER_AVAILABLE:
        _zhipu_breaker = create_circuit_breaker(
            name="Zhipu_AI",
            failure_threshold=5,
            success_threshold=2,
            timeout=60.0
        )
    return _zhipu_breaker


def get_supabase_breaker() -> Optional[Any]:
    """Retorna circuit breaker para Supabase."""
    global _supabase_breaker
    if _supabase_breaker is None and PYBREAKER_AVAILABLE:
        _supabase_breaker = create_circuit_breaker(
            name="Supabase",
            failure_threshold=5,
            success_threshold=2,
            timeout=60.0
        )
    return _supabase_breaker


def call_with_circuit_breaker(
    breaker: Optional[Any],
    func: Callable,
    *args,
    **kwargs
) -> Any:
    """
    Executa função protegida por circuit breaker.
    
    Args:
        breaker: Circuit breaker instance (ou None para bypass)
        func: Função a executar
        *args: Argumentos posicionais
        **kwargs: Argumentos nomeados
        
    Returns:
        Resultado da função
        
    Raises:
        CircuitBreakerError: Se circuit breaker estiver aberto
        Exception: Outras exceções da função
    """
    if breaker is None:
        # Sem circuit breaker, executa diretamente
        return func(*args, **kwargs)
    
    if not PYBREAKER_AVAILABLE:
        # Se pybreaker não está disponível, executar diretamente
        return func(*args, **kwargs)
    
    try:
        return breaker.call(func, *args, **kwargs)
    except pybreaker.CircuitBreakerError as e:
        raise CircuitBreakerError(f"Circuit breaker aberto: {e}") from e
