"""
Serviço LLM usando Groq API (Llama 3.1 8B Instant) e Zhipu AI (GLM 4).
Roteamento em 3 níveis: 8B (simples) → 70B (complexas) → GLM 4 (tarefas pesadas).
Suporta streaming de respostas para melhor UX.
"""
from typing import List, Dict, Optional, Any, Tuple, Generator, Union
from loguru import logger
import time
import re
from groq import Groq
from app.config import get_settings
from app.services.prompts import SYSTEM_PROMPTS, DEFAULT_PROMPT

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
        # Ajustes conforme análise consolidada: temperatura 0.4, max_tokens 800
        self.temperature = 0.3  # Reduzido para respostas mais determinísticas
        self.max_tokens = 400  # Reduzido para respostas executivas concisas (gestores)
    
    def _is_heavy_task(self, query_text: Optional[str], query_type: Optional[str]) -> bool:
        """
        Detecta se query requer GLM 4 (tarefa pesada).
        
        Tarefas pesadas:
        - Análise multi-dimensional (compare, relacione, correlação)
        - Cálculos complexos (calcule, equação, porcentagem, projeção)
        - Síntese executiva (resumo executivo, visão geral, dashboard)
        - Raciocínio profundo (por que múltiplos, causa raiz de múltiplos)
        
        Args:
            query_text: Texto da query do usuário
            query_type: Tipo da query classificada
            
        Returns:
            bool: True se é tarefa pesada
        """
        if not query_text or not self.use_3_level or not self.zhipu_client:
            return False
        
        query_lower = query_text.lower()
        
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
        
        # Padrões específicos do domínio Sotreq (operacional/logística)
        sotreq_specific_patterns = [
            r"compare.*unidades", r"comparar.*unidades", r"todas as unidades",
            r"todas unidades", r"múltiplas unidades", r"várias unidades",
            r"análise.*múltiplas", r"síntese.*operacional", r"visão geral.*operações",
            r"calcule.*impacto", r"projeção.*performance", r"tendência.*operacional",
            r"consolida.*unidades", r"dashboard.*operações", r"panorama.*operacional",
            r"análise.*consolidada", r"resumo.*todas.*unidades", r"performance.*todas",
            r"problemas.*múltiplas", r"alertas.*todas", r"status.*todas.*unidades"
        ]
        
        # Verificar padrões gerais
        for category, patterns in heavy_patterns.items():
            if any(pattern in query_lower for pattern in patterns):
                logger.info(f"🔷 Tarefa pesada detectada (categoria: {category})")
                return True
        
        # Verificar padrões específicos Sotreq usando regex
        for pattern in sotreq_specific_patterns:
            if re.search(pattern, query_lower, re.IGNORECASE):
                logger.info(f"🔷 Tarefa pesada detectada (padrão Sotreq: {pattern})")
                return True
        
        return False
    
    def _select_model(self, query_type: Optional[str], query_text: Optional[str] = None) -> Tuple[str, str]:
        """
        Seleção em 3 níveis:
        - Nível 1 (8B): Queries simples
        - Nível 2 (70B): Queries complexas padrão
        - Nível 3 (GLM 4): Tarefas pesadas
        
        Args:
            query_type: Tipo da query (detalhamento, causa, procedimento, etc.)
            query_text: Texto da query (para detecção de tarefas pesadas)
            
        Returns:
            tuple: (model_name, provider) - provider: "groq" ou "zhipu"
        """
        if not self.use_dynamic:
            return (self.model_8b, "groq")
        
        # Nível 3: Detectar tarefas pesadas (GLM 4)
        if self._is_heavy_task(query_text, query_type):
            logger.info(f"🔷 Usando GLM 4 para tarefa pesada")
            return (self.glm_model, "zhipu")
        
        # Nível 2: Complexas padrão (Llama 70B)
        complex_queries = ["detalhamento", "causa", "procedimento"]
        if query_type in complex_queries:
            logger.debug(f"Usando modelo 70B para query complexa: {query_type}")
            return (self.model_70b, "groq")
        
        # Nível 1: Simples (Llama 8B)
        return (self.model_8b, "groq")
    
    def _call_glm4(
        self,
        messages: List[Dict[str, str]],
        temperature: Optional[float] = None,
        max_tokens: Optional[int] = None
    ) -> str:
        """
        Chama GLM 4 via Zhipu AI SDK.
        
        Args:
            messages: Lista de mensagens no formato OpenAI
            temperature: Temperatura (padrão 0.3 para precisão)
            max_tokens: Máximo de tokens (padrão 1500 para análises longas)
        
        Returns:
            str: Resposta do GLM 4
        """
        if not self.zhipu_client:
            raise ValueError("Cliente GLM 4 não configurado")
        
        try:
            start_time = time.time()
            response = self.zhipu_client.chat.completions.create(
                model=self.glm_model,
                messages=messages,
                temperature=temperature or 0.3,  # Menor temperatura para precisão
                max_tokens=max_tokens or 1500  # Mais tokens para análises longas
            )
            
            elapsed = time.time() - start_time
            content = response.choices[0].message.content
            logger.info(f"✅ GLM 4 resposta gerada: {len(content)} caracteres (tempo: {elapsed:.2f}s)")
            return content
            
        except Exception as e:
            logger.error(f"Erro ao chamar GLM 4: {e}")
            import traceback
            logger.error(traceback.format_exc())
            raise
    
    def _stream_groq(
        self,
        model: str,
        messages: List[Dict[str, str]],
        temperature: float,
        max_tokens: int
    ) -> Generator[str, None, None]:
        """
        Stream de respostas do Groq.
        
        Args:
            model: Nome do modelo (8B ou 70B)
            messages: Lista de mensagens
            temperature: Temperatura
            max_tokens: Máximo de tokens
            
        Yields:
            str: Chunks de texto conforme são gerados
        """
        try:
            logger.debug(f"📡 Iniciando stream Groq: {model}")
            stream = self.client.chat.completions.create(
                model=model,
                messages=messages,
                temperature=temperature,
                max_tokens=max_tokens,
                stream=True
            )
            
            for chunk in stream:
                if chunk.choices[0].delta.content:
                    yield chunk.choices[0].delta.content
            
            logger.debug("✅ Stream Groq concluído")
            
        except Exception as e:
            logger.error(f"Erro no stream Groq: {e}")
            raise
    
    def _stream_glm4(
        self,
        messages: List[Dict[str, str]],
        temperature: Optional[float],
        max_tokens: Optional[int]
    ) -> Generator[str, None, None]:
        """
        Stream de respostas do GLM 4 (Zhipu AI).
        
        Args:
            messages: Lista de mensagens
            temperature: Temperatura
            max_tokens: Máximo de tokens
            
        Yields:
            str: Chunks de texto conforme são gerados
        """
        if not self.zhipu_client:
            raise ValueError("Cliente GLM 4 não configurado")
        
        try:
            logger.debug("📡 Iniciando stream GLM 4")
            # Zhipu AI SDK suporta streaming via stream=True
            stream = self.zhipu_client.chat.completions.create(
                model=self.glm_model,
                messages=messages,
                temperature=temperature or 0.3,
                max_tokens=max_tokens or 1500,
                stream=True
            )
            
            for chunk in stream:
                if hasattr(chunk, 'choices') and chunk.choices:
                    delta = chunk.choices[0].delta
                    if hasattr(delta, 'content') and delta.content:
                        yield delta.content
            
            logger.debug("✅ Stream GLM 4 concluído")
            
        except Exception as e:
            logger.error(f"Erro no stream GLM 4: {e}")
            # Fallback para Groq 70B em modo streaming
            logger.warning("Fallback para Groq 70B em modo streaming")
            yield from self._stream_groq(
                model=self.model_70b,
                messages=messages,
                temperature=temperature or 0.3,
                max_tokens=max_tokens or 1500
            )
    
    def _fallback_to_groq(
        self,
        messages: List[Dict[str, str]],
        model: str,
        temperature: Optional[float],
        max_tokens: Optional[int]
    ) -> str:
        """Fallback para Groq se GLM 4 falhar."""
        try:
            logger.info(f"🔄 Executando fallback para Groq {model}")
            response = self.client.chat.completions.create(
                model=model,
                messages=messages,
                temperature=temperature or self.temperature,
                max_tokens=max_tokens or self.max_tokens
            )
            logger.info(f"✅ Fallback Groq executado com sucesso")
            return response.choices[0].message.content
        except Exception as e:
            logger.error(f"Erro no fallback Groq: {e}")
            raise
    
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
                content = self._call_glm4(messages, temperature, max_tokens)
            else:
                # Groq (8B ou 70B)
                response = self.client.chat.completions.create(
                    model=selected_model,
                    messages=messages,
                    temperature=temperature or self.temperature,
                    max_tokens=max_tokens or self.max_tokens,
                    stream=False
                )
                content = response.choices[0].message.content
                elapsed = time.time() - start_time
                logger.debug(f"Resposta LLM gerada: {len(content)} caracteres (tempo: {elapsed:.2f}s)")
            
            return content
            
        except Exception as e:
            # Fallback: tentar com Groq 70B se GLM 4 falhar
            if provider == "zhipu":
                logger.warning(f"GLM 4 falhou, tentando fallback com Groq 70B: {e}")
                try:
                    return self._fallback_to_groq(messages, self.model_70b, temperature, max_tokens)
                except Exception as fallback_error:
                    logger.error(f"Fallback também falhou: {fallback_error}")
                    # Tentar último fallback com 8B
                    logger.warning("Tentando último fallback com Groq 8B")
                    return self._fallback_to_groq(messages, self.model_8b, temperature, max_tokens)
            
            logger.error(f"Erro ao gerar resposta do LLM: {e}")
            import traceback
            logger.error(traceback.format_exc())
            raise
    
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
            if provider == "zhipu":
                yield from self._stream_glm4(messages, temperature, max_tokens)
            else:
                # Groq (8B ou 70B)
                yield from self._stream_groq(
                    model=selected_model,
                    messages=messages,
                    temperature=temperature or self.temperature,
                    max_tokens=max_tokens or self.max_tokens
                )
        except Exception as e:
            logger.error(f"Erro no streaming: {e}")
            # Fallback para Groq em modo não-streaming (converter para stream)
            logger.warning("Fallback para Groq 70B (modo não-streaming convertido)")
            try:
                fallback_result = self._fallback_to_groq(messages, self.model_70b, temperature, max_tokens)
                # Enviar resultado completo como único chunk
                yield fallback_result
            except Exception as fallback_error:
                logger.error(f"Fallback falhou: {fallback_error}")
                yield f"Erro ao gerar resposta: {str(e)}"
    
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
            selected_model, provider = self._select_model(query_type, query_text)
            
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
                return self._generate_response_stream(
                    messages, selected_model, provider, temperature, max_tokens
                )
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
        # Status: respostas executivas concisas (gestores)
        max_tokens_override = None
        if query_type == "status":
            max_tokens_override = 250  # Reduzido para forçar agregação e evitar redundâncias
        
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

