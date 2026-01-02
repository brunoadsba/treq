"""
Decorators e utilitários para tracing com LangSmith.

Fornece wrappers para rastrear chamadas LLM e pipeline RAG.
"""
import time
import uuid
from typing import Any, Callable, Dict, Optional
from functools import wraps
from contextlib import contextmanager
from loguru import logger

from app.core.langsmith_config import is_langsmith_enabled, get_langsmith_client


def _get_tracer():
    """Retorna o tracer se LangSmith estiver habilitado."""
    if not is_langsmith_enabled():
        return None
    
    try:
        from langsmith import traceable
        return traceable
    except ImportError:
        return None


def trace_llm_call(
    name: str = "llm_call",
    run_type: str = "llm",
    metadata: Optional[Dict[str, Any]] = None
):
    """
    Decorator para tracing de chamadas LLM.
    
    Args:
        name: Nome do span
        run_type: Tipo do run (llm, chain, tool)
        metadata: Metadados adicionais
        
    Example:
        @trace_llm_call(name="generate_response")
        def generate_response(prompt: str) -> str:
            ...
    """
    def decorator(func: Callable) -> Callable:
        @wraps(func)
        def wrapper(*args, **kwargs):
            if not is_langsmith_enabled():
                return func(*args, **kwargs)
            
            try:
                from langsmith import traceable
                
                # Criar função traceable
                traced_func = traceable(
                    name=name,
                    run_type=run_type,
                    metadata=metadata or {}
                )(func)
                
                return traced_func(*args, **kwargs)
            except ImportError:
                return func(*args, **kwargs)
            except Exception as e:
                logger.debug(f"Erro no tracing: {e}")
                return func(*args, **kwargs)
        
        return wrapper
    return decorator


def trace_rag_pipeline(
    name: str = "rag_pipeline",
    metadata: Optional[Dict[str, Any]] = None
):
    """
    Decorator para tracing de pipeline RAG.
    
    Args:
        name: Nome do span
        metadata: Metadados adicionais
        
    Example:
        @trace_rag_pipeline(name="search_documents")
        def search(query: str) -> List[Dict]:
            ...
    """
    def decorator(func: Callable) -> Callable:
        @wraps(func)
        def wrapper(*args, **kwargs):
            if not is_langsmith_enabled():
                return func(*args, **kwargs)
            
            try:
                from langsmith import traceable
                
                traced_func = traceable(
                    name=name,
                    run_type="retriever",
                    metadata=metadata or {}
                )(func)
                
                return traced_func(*args, **kwargs)
            except ImportError:
                return func(*args, **kwargs)
            except Exception as e:
                logger.debug(f"Erro no tracing RAG: {e}")
                return func(*args, **kwargs)
        
        return wrapper
    return decorator


@contextmanager
def trace_span(
    name: str,
    run_type: str = "chain",
    inputs: Optional[Dict[str, Any]] = None,
    metadata: Optional[Dict[str, Any]] = None
):
    """
    Context manager para criar spans customizados.
    
    Args:
        name: Nome do span
        run_type: Tipo do run
        inputs: Inputs do span
        metadata: Metadados adicionais
        
    Example:
        with trace_span("process_query", inputs={"query": query}):
            result = process(query)
    """
    if not is_langsmith_enabled():
        yield None
        return
    
    start_time = time.time()
    run_id = str(uuid.uuid4())
    
    try:
        from langsmith import trace
        
        with trace(
            name=name,
            run_type=run_type,
            inputs=inputs or {},
            metadata=metadata or {}
        ) as run:
            yield run
            
    except ImportError:
        yield None
    except Exception as e:
        logger.debug(f"Erro no trace_span: {e}")
        yield None
    finally:
        elapsed = time.time() - start_time
        logger.debug(f"[TRACE] {name} concluído em {elapsed:.2f}s")


class TracingMetrics:
    """
    Coletor de métricas para logging local (quando LangSmith não disponível).
    """
    
    def __init__(self):
        self.metrics = []
    
    def log_llm_call(
        self,
        model: str,
        prompt_tokens: int,
        completion_tokens: int,
        latency_ms: float,
        success: bool,
        error: Optional[str] = None
    ):
        """Loga métricas de chamada LLM."""
        metric = {
            "type": "llm_call",
            "model": model,
            "prompt_tokens": prompt_tokens,
            "completion_tokens": completion_tokens,
            "total_tokens": prompt_tokens + completion_tokens,
            "latency_ms": latency_ms,
            "success": success,
            "error": error,
            "timestamp": time.time()
        }
        self.metrics.append(metric)
        
        # Log estruturado
        if success:
            logger.info(
                f"[LLM_METRICS] {model} | "
                f"Tokens: {prompt_tokens}+{completion_tokens}={prompt_tokens + completion_tokens} | "
                f"Latência: {latency_ms:.0f}ms"
            )
        else:
            logger.warning(
                f"[LLM_METRICS] {model} | ERRO: {error} | Latência: {latency_ms:.0f}ms"
            )
    
    def log_rag_search(
        self,
        query: str,
        num_results: int,
        top_similarity: float,
        latency_ms: float,
        search_type: str = "vector"
    ):
        """Loga métricas de busca RAG."""
        metric = {
            "type": "rag_search",
            "query_length": len(query),
            "num_results": num_results,
            "top_similarity": top_similarity,
            "latency_ms": latency_ms,
            "search_type": search_type,
            "timestamp": time.time()
        }
        self.metrics.append(metric)
        
        logger.info(
            f"[RAG_METRICS] {search_type} | "
            f"Resultados: {num_results} | "
            f"Top sim: {top_similarity:.3f} | "
            f"Latência: {latency_ms:.0f}ms"
        )
    
    def get_summary(self) -> Dict[str, Any]:
        """Retorna resumo das métricas coletadas."""
        if not self.metrics:
            return {}
        
        llm_calls = [m for m in self.metrics if m["type"] == "llm_call"]
        rag_searches = [m for m in self.metrics if m["type"] == "rag_search"]
        
        return {
            "total_llm_calls": len(llm_calls),
            "total_rag_searches": len(rag_searches),
            "avg_llm_latency_ms": sum(m["latency_ms"] for m in llm_calls) / len(llm_calls) if llm_calls else 0,
            "avg_rag_latency_ms": sum(m["latency_ms"] for m in rag_searches) / len(rag_searches) if rag_searches else 0,
            "total_tokens": sum(m.get("total_tokens", 0) for m in llm_calls),
            "llm_success_rate": sum(1 for m in llm_calls if m["success"]) / len(llm_calls) if llm_calls else 1.0
        }


# Instância global para métricas locais
tracing_metrics = TracingMetrics()
