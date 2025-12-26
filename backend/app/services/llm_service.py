"""
Serviço LLM usando Groq API (Llama 3.1 8B Instant).
"""
from typing import List, Dict, Optional, Any
from loguru import logger
from groq import Groq
from app.config import get_settings
from app.services.prompts import SYSTEM_PROMPTS, DEFAULT_PROMPT

settings = get_settings()


class LLMService:
    """Serviço para interagir com LLM via Groq API."""
    
    # Prompts específicos por tipo de query (importados de prompts.py)
    SYSTEM_PROMPTS = SYSTEM_PROMPTS
    DEFAULT_PROMPT = DEFAULT_PROMPT
    
    def __init__(self):
        """Inicializa o cliente Groq."""
        if not settings.groq_api_key:
            raise ValueError("GROQ_API_KEY não configurada no .env")
        
        self.client = Groq(api_key=settings.groq_api_key)
        self.model = settings.llm_model
        # Ajustes conforme análise consolidada: temperatura 0.4, max_tokens 800
        self.temperature = 0.3  # Reduzido para respostas mais determinísticas
        self.max_tokens = 400  # Reduzido para respostas executivas concisas (gestores)
    
    def generate_response(
        self,
        messages: List[Dict[str, str]],
        temperature: Optional[float] = None,
        max_tokens: Optional[int] = None,
        stream: bool = False
    ) -> str:
        """
        Gera resposta do LLM.
        
        Args:
            messages: Lista de mensagens no formato [{"role": "user", "content": "..."}]
            temperature: Temperatura para geração (usa padrão se None)
            max_tokens: Máximo de tokens (usa padrão se None)
            stream: Se True, retorna generator (não implementado ainda)
            
        Returns:
            str: Resposta do LLM
        """
        try:
            response = self.client.chat.completions.create(
                model=self.model,
                messages=messages,
                temperature=temperature or self.temperature,
                max_tokens=max_tokens or self.max_tokens,
                stream=stream
            )
            
            if stream:
                # TODO: Implementar streaming
                raise NotImplementedError("Streaming não implementado ainda")
            
            content = response.choices[0].message.content
            logger.debug(f"Resposta LLM gerada: {len(content)} caracteres")
            return content
            
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
        
        return self.generate_response(messages, max_tokens=max_tokens_override)

