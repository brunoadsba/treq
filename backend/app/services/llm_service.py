"""
Serviço LLM usando Groq API (Llama 3.1 8B Instant) e Zhipu AI (GLM 4).
Roteamento em 3 níveis: 8B (simples) → 70B (complexas) → GLM 4 (tarefas pesadas).
Suporta streaming de respostas para melhor UX.
"""
import time
from typing import List, Dict, Optional, Generator, Union
from loguru import logger
from groq import Groq
from app.config import get_settings
from app.services.prompts import SYSTEM_PROMPTS, DEFAULT_PROMPT
from app.services.llm_model_selector import select_model
from app.services.llm_clients import (
    call_glm4,
    call_groq,
    stream_groq,
    stream_glm4,
    fallback_to_groq
)
from app.utils.debug import trace_generator
from app.utils.technical_term_filter import filter_technical_terms
from app.core.tracing import tracing_metrics, trace_llm_call

# Importar Zhipu AI SDK (pode não estar instalado inicialmente)
try:
    from zai import ZhipuAiClient
    ZHIPU_AVAILABLE = True
except ImportError:
    ZHIPU_AVAILABLE = False
    logger.warning("zai-sdk não instalado. GLM 4 desabilitado. Instale com: pip install zai-sdk")

settings = get_settings()


class LLMService:
    """Serviço para interagir com LLM via Groq API e Zhipu AI (GLM 4)."""
    
    # Prompts específicos por tipo de query (importados de prompts.py)
    SYSTEM_PROMPTS = SYSTEM_PROMPTS
    DEFAULT_PROMPT = DEFAULT_PROMPT
    
    def __init__(self):
        """Inicializa os clientes Groq e Zhipu AI."""
        if not settings.groq_api_key:
            raise ValueError("GROQ_API_KEY não configurada no .env")
        
        # Cliente Groq (atual)
        self.client = Groq(api_key=settings.groq_api_key)
        self.model_8b = settings.llm_model
        self.model_70b = settings.llm_model_complex
        self.use_dynamic = settings.use_dynamic_model
        
        # Cliente GLM 4 (novo)
        self.use_3_level = settings.use_3_level_routing
        if settings.zhipu_api_key and ZHIPU_AVAILABLE:
            try:
                self.zhipu_client = ZhipuAiClient(api_key=settings.zhipu_api_key)
                self.glm_model = settings.glm_model
                logger.info("✅ Cliente GLM 4 (Zhipu AI) inicializado com sucesso")
            except Exception as e:
                logger.warning(f"Erro ao inicializar cliente GLM 4: {e}. GLM 4 desabilitado.")
                self.zhipu_client = None
                self.glm_model = None
        else:
            self.zhipu_client = None
            self.glm_model = None
            if not settings.zhipu_api_key:
                logger.warning("ZHIPU_API_KEY não configurada - GLM 4 desabilitado")
            elif not ZHIPU_AVAILABLE:
                logger.warning("zai-sdk não disponível - GLM 4 desabilitado")
        
        self.model = settings.llm_model  # Fallback padrão
        # Usar valores do config para garantir respostas completas
        self.temperature = settings.llm_temperature  # Usar temperatura do config (0.4)
        self.max_tokens = settings.llm_max_tokens  # Usar max_tokens do config (800) para respostas completas
    
    @trace_llm_call(name="llm_generate_non_stream")
    def _generate_response_non_stream(
        self,
        messages: List[Dict[str, str]],
        selected_model: str,
        provider: str,
        temperature: Optional[float],
        max_tokens: Optional[int]
    ) -> str:
        """
        Gera resposta não-streaming (sempre retorna string).
        Método privado separado para evitar conflito com generator.
        """
        start_time = time.time()
        
        try:
            if provider == "zhipu":
                try:
                    content = call_glm4(
                        self.zhipu_client,
                        self.glm_model,
                        messages,
                        temperature,
                        max_tokens
                    )
                    # Verificar novamente se conteúdo não está vazio após retorno
                    if not content or not content.strip():
                        raise ValueError("GLM 4 retornou conteúdo vazio após validação")
                    
                    # Aplicar filtro de termos técnicos (pós-processamento obrigatório)
                    content = filter_technical_terms(content)
                    
                    return content
                except (ValueError, Exception) as glm_error:
                    # Fallback automático para Groq 70B se GLM 4 falhar ou retornar vazio
                    logger.warning(f"🔄 GLM 4 falhou ou retornou vazio: {glm_error}")
                    logger.info("🔄 Tentando fallback automático com Groq 70B...")
                    try:
                        fallback_content = fallback_to_groq(
                            self.client,
                            self.model_70b,
                            messages,
                            temperature,
                            max_tokens,
                            self.temperature,
                            self.max_tokens
                        )
                        if not fallback_content or not fallback_content.strip():
                            raise ValueError("Fallback Groq 70B também retornou vazio")
                        
                        # Aplicar filtro de termos técnicos
                        fallback_content = filter_technical_terms(fallback_content)
                        
                        logger.info("✅ Fallback Groq 70B bem-sucedido")
                        return fallback_content
                    except Exception as fallback_error:
                        logger.warning(f"⚠️ Fallback Groq 70B falhou: {fallback_error}")
                        # Último fallback com 8B
                        logger.info("🔄 Tentando último fallback com Groq 8B...")
                        try:
                            final_content = fallback_to_groq(
                                self.client,
                                self.model_8b,
                                messages,
                                temperature,
                                max_tokens,
                                self.temperature,
                                self.max_tokens
                            )
                            if not final_content or not final_content.strip():
                                raise ValueError("Fallback Groq 8B também retornou vazio")
                            
                            # Aplicar filtro de termos técnicos
                            final_content = filter_technical_terms(final_content)
                            
                            logger.info("✅ Fallback Groq 8B bem-sucedido")
                            return final_content
                        except Exception as final_error:
                            logger.error(f"❌ Todos os fallbacks falharam. Último erro: {final_error}")
                            raise ValueError(f"Falha em GLM 4 e todos os fallbacks: {final_error}")
            else:
                # Groq (8B ou 70B) - protegido por circuit breaker
                content = call_groq(
                    self.client,
                    selected_model,
                    messages,
                    temperature,
                    max_tokens,
                    self.temperature,
                    self.max_tokens
                )
                
                # Aplicar filtro de termos técnicos (pós-processamento obrigatório)
                content = filter_technical_terms(content)
                
                elapsed = time.time() - start_time
                elapsed_ms = elapsed * 1000
                
                # Registrar métricas para observabilidade
                tracing_metrics.log_llm_call(
                    model=selected_model,
                    prompt_tokens=len(str(messages)) // 4,  # Estimativa aproximada
                    completion_tokens=len(content) // 4,
                    latency_ms=elapsed_ms,
                    success=True
                )
                
                logger.debug(f"Resposta LLM gerada: {len(content)} caracteres (tempo: {elapsed:.2f}s)")
                return content
            
        except Exception as e:
            logger.error(f"Erro ao gerar resposta do LLM: {e}")
            import traceback
            logger.error(traceback.format_exc())
            raise
    
    @trace_llm_call(name="llm_generate_stream")
    @trace_generator("Response_Stream")
    def _generate_response_stream(
        self,
        messages: List[Dict[str, str]],
        selected_model: str,
        provider: str,
        temperature: Optional[float],
        max_tokens: Optional[int]
    ) -> Generator[str, None, None]:
        """
        Gera resposta streaming (sempre retorna generator).
        Método privado separado para streaming.
        """
        try:
            logger.debug(f"🔄 _generate_response_stream chamado (provider: {provider})")
            if provider == "zhipu":
                logger.debug("🔄 Delegando para stream_glm4")
                # Preparar fallback stream para GLM4
                fallback_gen = stream_groq(
                    self.client,
                    self.model_70b,
                    messages,
                    temperature or self.temperature,
                    max_tokens or self.max_tokens
                )
                yield from stream_glm4(
                    self.zhipu_client,
                    self.glm_model,
                    messages,
                    temperature,
                    max_tokens,
                    fallback_gen
                )
                logger.debug("✅ stream_glm4 concluído (todos os chunks yieldados)")
            else:
                # Groq (8B ou 70B)
                logger.debug(f"🔄 Delegando para stream_groq (model: {selected_model})")
                yield from stream_groq(
                    self.client,
                    selected_model,
                    messages,
                    temperature or self.temperature,
                    max_tokens or self.max_tokens
                )
        except Exception as e:
            logger.error(f"❌ Erro no streaming: {e}")
            import traceback
            logger.error(traceback.format_exc())
            # Fallback para Groq em modo não-streaming (converter para stream)
            logger.warning("🔄 Fallback para Groq 70B (modo não-streaming convertido)")
            try:
                fallback_result = fallback_to_groq(
                    self.client,
                    self.model_70b,
                    messages,
                    temperature,
                    max_tokens,
                    self.temperature,
                    self.max_tokens
                )
                # Enviar resultado completo como único chunk
                yield fallback_result
            except Exception as fallback_error:
                logger.error(f"❌ Fallback falhou: {fallback_error}")
                yield f"Erro ao gerar resposta: {str(e)}"
    
    @trace_llm_call(name="llm_service_main", run_type="chain")
    def generate_response(
        self,
        messages: List[Dict[str, str]],
        temperature: Optional[float] = None,
        max_tokens: Optional[int] = None,
        stream: bool = False,
        query_type: Optional[str] = None,
        query_text: Optional[str] = None
    ) -> Union[Generator[str, None, None], str]:
        """
        Gera resposta do LLM com roteamento automático em 3 níveis.
        
        Args:
            messages: Lista de mensagens no formato [{"role": "user", "content": "..."}]
            temperature: Temperatura para geração (usa padrão se None)
            max_tokens: Máximo de tokens (usa padrão se None)
            stream: Se True, retorna generator; se False, retorna string
            query_type: Tipo da query (opcional, usado para seleção dinâmica de modelo)
            query_text: Texto da query (opcional, usado para detecção de tarefas pesadas)
            
        Returns:
            str ou Generator[str, None, None]: Resposta do LLM (string ou generator de chunks)
        """
        provider = "groq"  # Default
        selected_model = self.model_8b
        
        try:
            # Selecionar modelo e provider dinamicamente
            selected_model, provider = select_model(
                query_type,
                query_text,
                self.model_8b,
                self.model_70b,
                self.glm_model,
                self.use_dynamic,
                self.use_3_level,
                self.zhipu_client is not None
            )
            
            # Determinar nível para logging
            if provider == "zhipu":
                level = "Nível 3 (GLM 4)"
            elif selected_model == self.model_70b:
                level = "Nível 2 (Llama 70B)"
            else:
                level = "Nível 1 (Llama 8B)"
            
            logger.info(f"🔷 Modelo selecionado: {selected_model} (Provider: {provider}, {level})")
            
            # Chamar método apropriado baseado em stream
            if stream:
                logger.debug(f"🔄 generate_response: retornando generator para streaming (provider: {provider})")
                generator = self._generate_response_stream(
                    messages, selected_model, provider, temperature, max_tokens
                )
                logger.debug(f"🔄 generate_response: generator criado, retornando")
                return generator
            else:
                return self._generate_response_non_stream(
                    messages, selected_model, provider, temperature, max_tokens
                )
            
        except Exception as e:
            logger.error(f"Erro ao gerar resposta do LLM: {e}")
            import traceback
            logger.error(traceback.format_exc())
            raise
    
    def generate_with_context(
        self,
        user_query: str,
        context: List[str],
        query_type: str = "geral",
        system_prompt: Optional[str] = None,
        conversation_history: Optional[List[Dict[str, str]]] = None
    ) -> str:
        """
        Gera resposta do LLM com contexto RAG e histórico de conversa.
        
        Args:
            user_query: Consulta do usuário
            context: Lista de textos de contexto (do RAG)
            query_type: Tipo da query (alerta, procedimento, metrica, causa, status, geral)
            system_prompt: Prompt do sistema (opcional, sobrescreve query_type se fornecido)
            conversation_history: Histórico de mensagens anteriores (opcional, para follow-up)
            
        Returns:
            str: Resposta do LLM
        """
        # Construir prompt com contexto
        context_text = "\n\n---\n\n".join([
            f"Documento {i+1}:\n{ctx}"
            for i, ctx in enumerate(context)
        ])
        
        # Selecionar prompt específico por tipo ou usar fornecido
        if system_prompt:
            system_content = system_prompt
        elif query_type in self.SYSTEM_PROMPTS:
            system_content = self.SYSTEM_PROMPTS[query_type]
        else:
            system_content = self.DEFAULT_PROMPT
        
        logger.debug(f"Usando prompt do tipo: {query_type} (histórico: {len(conversation_history) if conversation_history else 0} mensagens)")
        
        # Ajustar max_tokens por tipo de query
        # Usar None para respeitar o valor definido no .env (LLM_MAX_TOKENS)
        # Overrides hardcoded anteriores (1500/2000) estavam cortando respostas longas.
        max_tokens_override = None
        
        # if query_type == "status":
        #     max_tokens_override = 600
        # elif query_type == "consultoria":
        #     max_tokens_override = 2000
        # elif query_type in ["procedimento", "metrica_temporal"]:
        #     max_tokens_override = 1500
        
        # Construir mensagens com formato melhorado
        messages = [
            {"role": "system", "content": system_content}
        ]
        
        # Adicionar histórico da conversa se fornecido (para follow-up questions)
        if conversation_history:
            messages.extend(conversation_history)
            logger.debug(f"Histórico da conversa incluído: {len(conversation_history)} mensagens")
        
        # Adicionar mensagem do usuário atual com contexto RAG
        user_content = f"""CONTEXTO DOS DOCUMENTOS:
{context_text}

---

PERGUNTA DO USUÁRIO:
{user_query}

Responda usando APENAS as informações do contexto acima."""
        
        # Se há histórico, adicionar instrução para usar contexto conversacional
        if conversation_history:
            user_content = f"""CONTEXTO DOS DOCUMENTOS:
{context_text}

---

HISTÓRICO DA CONVERSA:
[As mensagens anteriores estão acima]

PERGUNTA DO USUÁRIO (FOLLOW-UP):
{user_query}

Responda usando as informações do contexto dos documentos E do histórico da conversa acima. 
Se o usuário pedir detalhes sobre algo mencionado anteriormente, use o contexto da conversa para fornecer informações detalhadas."""
        
        messages.append({
            "role": "user",
            "content": user_content
        })
        
        # generate_response agora pode retornar Generator | str
        result = self.generate_response(
            messages, 
            max_tokens=max_tokens_override, 
            query_type=query_type,
            query_text=user_query,  # Novo: passar texto da query para detecção de tarefas pesadas
            stream=False  # generate_with_context sempre usa stream=False (endpoint não-streaming)
        )
        return result

