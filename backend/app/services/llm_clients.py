"""
Clientes LLM: wrappers para chamadas Groq e Zhipu AI.
"""
from typing import List, Dict, Optional, Generator, Any
from loguru import logger
import time
import json
from tenacity import retry, stop_after_attempt, wait_exponential, retry_if_exception_type

from app.utils.debug import trace_generator
from app.middleware.request_id import get_request_id
from app.core.circuit_breaker import (
    get_groq_breaker,
    get_zhipu_breaker,
    call_with_circuit_breaker,
    CircuitBreakerError
)
from app.core.tracing import trace_llm_call


@retry(
    wait=wait_exponential(multiplier=1, min=2, max=10),
    stop=stop_after_attempt(3),
    reraise=True
)
@trace_llm_call(name="call_glm4", run_type="llm")
def call_glm4(
    zhipu_client: Any,
    glm_model: str,
    messages: List[Dict[str, str]],
    temperature: Optional[float] = None,
    max_tokens: Optional[int] = None
) -> str:
    """
    Chama GLM 4 via Zhipu AI SDK (protegido por circuit breaker).
    
    Args:
        zhipu_client: Cliente Zhipu AI
        glm_model: Nome do modelo GLM
        messages: Lista de mensagens no formato OpenAI
        temperature: Temperatura (padrão 0.3 para precisão)
        max_tokens: Máximo de tokens (padrão 1500 para análises longas)
    
    Returns:
        str: Resposta do GLM 4
        
    Raises:
        CircuitBreakerError: Se circuit breaker estiver aberto
        ValueError: Se resposta estiver vazia ou None
        Exception: Outros erros da API
    """
    if not zhipu_client:
        raise ValueError("Cliente GLM 4 não configurado")
    
    def _call_glm4_internal():
        start_time = time.time()
        response = zhipu_client.chat.completions.create(
            model=glm_model,
            messages=messages,
            temperature=temperature or 0.3,
            max_tokens=max_tokens or 1500
        )
        
        elapsed = time.time() - start_time
        
        # Verificar se resposta existe e tem conteúdo
        if not response or not response.choices:
            raise ValueError("GLM 4 retornou resposta vazia (sem choices)")
        
        content = response.choices[0].message.content
        
        # Verificar se conteúdo está vazio ou None
        if not content or not content.strip():
            logger.warning(f"⚠️ GLM 4 retornou conteúdo vazio (tempo: {elapsed:.2f}s)")
            raise ValueError("GLM 4 retornou conteúdo vazio")
        
        logger.info(f"✅ GLM 4 resposta gerada: {len(content)} caracteres (tempo: {elapsed:.2f}s)")
        return content.strip()
    
    # Executar com circuit breaker
    breaker = get_zhipu_breaker()
    try:
        return call_with_circuit_breaker(breaker, _call_glm4_internal)
    except CircuitBreakerError as e:
        logger.error(f"Circuit breaker Zhipu AI aberto: {e}")
        raise
    except (ValueError, Exception) as e:
        logger.error(f"Erro ao chamar GLM 4: {e}")
        import traceback
        logger.error(traceback.format_exc())
        raise


@trace_llm_call(name="stream_groq", run_type="llm")
@trace_generator("Groq_Stream")
def stream_groq(
    groq_client: Any,
    model: str,
    messages: List[Dict[str, str]],
    temperature: float,
    max_tokens: int
) -> Generator[str, None, None]:
    """
    Stream de respostas do Groq.
    
    Args:
        groq_client: Cliente Groq
        model: Nome do modelo (8B ou 70B)
        messages: Lista de mensagens
        temperature: Temperatura
        max_tokens: Máximo de tokens
        
    Yields:
        str: Chunks de texto conforme são gerados
    """
    try:
        logger.debug(f"📡 Iniciando stream Groq: {model}")
        stream = groq_client.chat.completions.create(
            model=model,
            messages=messages,
            temperature=temperature,
            max_tokens=max_tokens,
            stream=True
        )
        
        chunk_count = 0
        yielded_count = 0
        
        for chunk in stream:
            chunk_count += 1
            
            # Verificar se há choices e delta
            if not (chunk.choices and len(chunk.choices) > 0):
                continue
            
            choice = chunk.choices[0]
            
            # Verificar finish_reason (chunks de controle/finalização)
            # IMPORTANTE: Capturar conteúdo ANTES de verificar finish_reason
            # pois o último chunk pode ter tanto conteúdo quanto finish_reason
            has_content = False
            if hasattr(choice, 'delta') and choice.delta:
                if hasattr(choice.delta, 'content') and choice.delta.content:
                    has_content = True
                    content = choice.delta.content
                    yielded_count += 1
                    yield content
            
            # Verificar finish_reason após capturar conteúdo
            if hasattr(choice, 'finish_reason') and choice.finish_reason:
                logger.debug(f"🏁 Stream Groq finalizado (chunk #{chunk_count}, finish_reason={choice.finish_reason}, chunks yieldados={yielded_count})")
                # Não fazer break aqui - continuar para garantir que todos os chunks sejam processados
        
        logger.debug(f"✅ Stream Groq concluído ({chunk_count} chunks recebidos, {yielded_count} chunks yieldados)")
        
    except Exception as e:
        logger.error(f"Erro no stream Groq: {e}")
        raise


@trace_llm_call(name="stream_glm4", run_type="llm")
@trace_generator("GLM4_Stream")
def stream_glm4(
    zhipu_client: Any,
    glm_model: str,
    messages: List[Dict[str, str]],
    temperature: Optional[float],
    max_tokens: Optional[int],
    fallback_stream: Optional[Generator] = None
) -> Generator[str, None, None]:
    """
    Stream de respostas do GLM 4 (Zhipu AI).
    
    Args:
        zhipu_client: Cliente Zhipu AI
        glm_model: Nome do modelo GLM
        messages: Lista de mensagens
        temperature: Temperatura
        max_tokens: Máximo de tokens
        fallback_stream: Generator para fallback (opcional)
        
    Yields:
        str: Chunks de texto conforme são gerados
    """
    if not zhipu_client:
        raise ValueError("Cliente GLM 4 não configurado")
    
    try:
        request_id = get_request_id()
        logger.info(f"[{request_id}] 📡 Iniciando stream GLM 4")
        stream = zhipu_client.chat.completions.create(
            model=glm_model,
            messages=messages,
            temperature=temperature or 0.3,
            max_tokens=max_tokens or 1500,
            stream=True
        )
        
        logger.info(f"[{request_id}] 📡 Stream GLM 4 criado, aguardando chunks...")
        chunk_count = 0
        yielded_count = 0
        empty_chunks = 0
        control_chunks = 0
        
        # Flag para diagnóstico detalhado dos primeiros chunks (apenas para debug)
        DIAGNOSTIC_MODE = False  # Pode ser ativado via env var se necessário
        
        for chunk in stream:
            chunk_count += 1
            try:
                # Verificar estrutura básica
                if not (hasattr(chunk, 'choices') and chunk.choices and len(chunk.choices) > 0):
                    empty_chunks += 1
                    if empty_chunks <= 3:
                        logger.debug(f"[{request_id}] ⚠️ Chunk GLM 4 sem choices (chunk #{chunk_count}, chunk type: {type(chunk)})")
                    continue
                
                choice = chunk.choices[0]
                
                # CORREÇÃO 1: Verificar finish_reason (chunks de controle/finalização)
                if hasattr(choice, 'finish_reason') and choice.finish_reason:
                    control_chunks += 1
                    if control_chunks <= 5:
                        logger.debug(f"[{request_id}] 🏁 Chunk GLM 4 de controle (chunk #{chunk_count}, finish_reason={choice.finish_reason})")
                    continue
                
                # Extrair delta
                if not hasattr(choice, 'delta'):
                    empty_chunks += 1
                    if empty_chunks <= 3:
                        logger.debug(f"[{request_id}] ⚠️ Chunk GLM 4 sem delta (chunk #{chunk_count})")
                    continue
                
                delta = choice.delta
                
                # DIAGNÓSTICO: Log detalhado dos primeiros 3 chunks (apenas se diagnostic mode ativo)
                if DIAGNOSTIC_MODE and chunk_count <= 3:
                    diagnostic_info = {
                        'chunk_number': chunk_count,
                        'chunk_type': str(type(chunk)),
                        'delta_type': str(type(delta)),
                        'delta_attrs': [a for a in dir(delta) if not a.startswith('_')] if hasattr(delta, '__dir__') else None,
                    }
                    if hasattr(delta, '__dict__'):
                        diagnostic_info['delta_dict'] = delta.__dict__
                    elif isinstance(delta, dict):
                        diagnostic_info['delta_dict'] = delta
                    logger.info(f"[{request_id}] 🔍 DIAGNÓSTICO CHUNK {chunk_count}: {json.dumps(diagnostic_info, default=str, ensure_ascii=False)}")
                
                # CORREÇÃO 2: Tentar obter content de diferentes formas (compatibilidade com diferentes versões do SDK)
                content = None
                
                # Tentativa 1: Atributo direto 'content' (Padrão SDK)
                if hasattr(delta, 'content') and delta.content:
                    content = delta.content
                
                # Tentativa 2: Objeto 'message' dentro de delta (Comum em atualizações de SDK)
                elif hasattr(delta, 'message') and delta.message:
                    if hasattr(delta.message, 'content') and delta.message.content:
                        content = delta.message.content
                
                # Tentativa 3: Acesso como dicionário
                elif isinstance(delta, dict):
                    content = delta.get('content') or delta.get('text')
                
                # Tentativa 4: Acesso via __getitem__ (para objetos dict-like)
                elif hasattr(delta, '__getitem__'):
                    try:
                        # Verifica chaves comuns
                        for key in ['content', 'text']:
                            try:
                                val = delta[key]
                                if val:
                                    # Se val for um objeto com 'content', desce um nível
                                    if hasattr(val, 'content'):
                                        content = val.content
                                    else:
                                        content = val
                                    break
                            except (KeyError, TypeError):
                                continue
                    except Exception:
                        pass
                
                # Validação e yield
                if content and str(content).strip():
                    yielded_count += 1
                    if yielded_count == 1:
                        logger.info(f"[{request_id}] ✅ Primeiro chunk GLM 4 yieldado: '{str(content)[:50]}...'")
                    yield str(content)
                    if yielded_count % 100 == 0:
                        logger.debug(f"[{request_id}] 📡 {yielded_count} chunks yieldados do GLM 4")
                else:
                    empty_chunks += 1
                    if empty_chunks <= 3:  # Log apenas os primeiros 3 para não poluir
                        delta_info = f"type={type(delta)}"
                        if hasattr(delta, '__dict__'):
                            delta_info += f", attrs={list(delta.__dict__.keys())}"
                        elif isinstance(delta, dict):
                            delta_info += f", keys={list(delta.keys())}"
                        logger.debug(f"[{request_id}] ⚠️ Chunk GLM 4 sem conteúdo (chunk #{chunk_count}, {delta_info})")
                    
            except Exception as chunk_error:
                logger.warning(f"[{request_id}] ⚠️ Erro ao processar chunk GLM 4 #{chunk_count}: {chunk_error}")
                empty_chunks += 1
        
        logger.info(f"[{request_id}] ✅ Stream GLM 4 concluído ({chunk_count} chunks do stream, {yielded_count} chunks yieldados, {empty_chunks} chunks vazios, {control_chunks} chunks de controle)")
        
        # Se nenhum chunk foi yieldado, isso é um problema crítico
        if yielded_count == 0 and chunk_count > 0:
            error_msg = (
                f"Stream GLM 4 não produziu chunks válidos. "
                f"Recebidos: {chunk_count} chunks, "
                f"Vazios: {empty_chunks}, "
                f"Controle: {control_chunks}, "
                f"Yieldados: 0."
            )
            logger.error(f"[{request_id}] ❌ CRÍTICO: {error_msg}")
            raise ValueError(error_msg)
        
    except Exception as e:
        request_id = get_request_id()
        logger.error(f"[{request_id}] ❌ Erro no stream GLM 4: {e}")
        import traceback
        logger.error(traceback.format_exc())
        # Fallback se fornecido
        if fallback_stream:
            logger.warning(f"[{request_id}] 🔄 Fallback para Groq 70B em modo streaming")
            yield from fallback_stream


@retry(
    wait=wait_exponential(multiplier=1, min=2, max=10),
    stop=stop_after_attempt(3),
    reraise=True
)
@trace_llm_call(name="call_groq", run_type="llm")
def call_groq(
    groq_client: Any,
    model: str,
    messages: List[Dict[str, str]],
    temperature: Optional[float],
    max_tokens: Optional[int],
    default_temperature: float,
    default_max_tokens: int
) -> str:
    """
    Chama Groq API (protegido por circuit breaker).
    
    Args:
        groq_client: Cliente Groq
        model: Nome do modelo
        messages: Lista de mensagens
        temperature: Temperatura
        max_tokens: Máximo de tokens
        default_temperature: Temperatura padrão
        default_max_tokens: Max tokens padrão
        
    Returns:
        str: Resposta do Groq
        
    Raises:
        CircuitBreakerError: Se circuit breaker estiver aberto
        Exception: Outros erros da API
    """
    def _call_groq_internal():
        temp = temperature if temperature is not None else default_temperature
        tokens = max_tokens if max_tokens is not None else default_max_tokens
        
        msg_count = len(messages)
        content_len = sum(len(m.get('content', '')) for m in messages)
        logger.info(f"📡 Chamando Groq {model} (temp={temp}, tokens={tokens}, msgs={msg_count}, chars={content_len})")
        start_time = time.time()
        
        response = groq_client.chat.completions.create(
            model=model,
            messages=messages,
            temperature=temp,
            max_tokens=tokens,
            stream=False
        )
        content = response.choices[0].message.content
        elapsed = time.time() - start_time
        
        if not content or not content.strip():
            raise ValueError(f"Groq {model} retornou conteúdo vazio")
        
        logger.info(f"✅ Groq {model} resposta pronta em {elapsed:.2f}s")
        return content.strip()
    
    breaker = get_groq_breaker()
    try:
        return call_with_circuit_breaker(breaker, _call_groq_internal)
    except CircuitBreakerError as e:
        logger.error(f"Circuit breaker Groq aberto: {e}")
        raise
    except Exception as e:
        logger.error(f"Erro ao chamar Groq: {e}")
        raise


def fallback_to_groq(
    groq_client: Any,
    model: str,
    messages: List[Dict[str, str]],
    temperature: Optional[float],
    max_tokens: Optional[int],
    default_temperature: float,
    default_max_tokens: int
) -> str:
    """
    Fallback para Groq se GLM 4 falhar (protegido por circuit breaker).
    
    Args:
        groq_client: Cliente Groq
        model: Nome do modelo Groq
        messages: Lista de mensagens
        temperature: Temperatura
        max_tokens: Máximo de tokens
        default_temperature: Temperatura padrão
        default_max_tokens: Max tokens padrão
        
    Returns:
        str: Resposta do Groq
        
    Raises:
        CircuitBreakerError: Se circuit breaker estiver aberto
        Exception: Outros erros da API
    """
    def _call_groq_internal():
        temp = temperature if temperature is not None else default_temperature
        tokens = max_tokens if max_tokens is not None else default_max_tokens
        
        logger.info(f"📡 Chamando Groq Fallback {model} (temp={temp}, tokens={tokens})")
        start_time = time.time()
        
        response = groq_client.chat.completions.create(
            model=model,
            messages=messages,
            temperature=temp,
            max_tokens=tokens
        )
        elapsed = time.time() - start_time
        logger.info(f"✅ Groq Fallback {model} resposta pronta em {elapsed:.2f}s")
        return response.choices[0].message.content
    
    breaker = get_groq_breaker()
    try:
        logger.info(f"🔄 Executando fallback para Groq {model}")
        result = call_with_circuit_breaker(breaker, _call_groq_internal)
        logger.info(f"✅ Fallback Groq executado com sucesso")
        return result
    except CircuitBreakerError as e:
        logger.error(f"Circuit breaker Groq aberto durante fallback: {e}")
        raise
    except Exception as e:
        logger.error(f"Erro no fallback Groq: {e}")
        raise
