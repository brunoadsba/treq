"""
Validador de Grounding (Gatekeeper) - Anti-alucinação.

Verifica se a resposta gerada pelo LLM é estritamente suportada
pelo contexto fornecido. Se não for, rejeita a resposta e retorna
uma mensagem padrão de fallback.

Baseado no plano "Pragmatic Intelligence" (chat-inteligente.md).
"""
from typing import Dict, Any, Optional, Tuple
from loguru import logger
from app.core.tracing import trace_llm_call


class GroundingValidator:
    """
    Validador de Grounding para evitar alucinações.
    
    Usa o próprio LLM para verificar se a resposta é suportada
    pelo contexto fornecido.
    """
    
    VALIDATION_PROMPT = """Você é um verificador de fatos rigoroso. Sua tarefa é verificar se uma resposta é 100% suportada pelo contexto fornecido.

CONTEXTO ORIGINAL:
{context}

---

RESPOSTA GERADA:
{response}

---

TAREFA:
Analise se TODAS as afirmações na resposta são estritamente suportadas pelo contexto acima.

CRITÉRIOS DE VALIDAÇÃO:
1. Cada fato mencionado na resposta DEVE estar presente no contexto.
2. Números, datas e valores DEVEM corresponder exatamente.
3. Se a resposta infere algo que não está explícito no contexto, é uma alucinação.
4. Se a resposta menciona informações que não aparecem no contexto, é uma alucinação.

RESPONDA APENAS no seguinte formato JSON:
{{"valido": true/false, "confianca": 0.0-1.0, "motivo": "explicação breve"}}

Se válido = true, a resposta pode ser entregue ao usuário.
Se válido = false, a resposta contém informações não suportadas e deve ser rejeitada."""

    FALLBACK_MESSAGE = (
        "Não tenho certeza sobre essa informação nos meus registros atuais. "
        "Por favor, consulte o manual oficial ou um supervisor para confirmação."
    )
    
    FALLBACK_MESSAGE_WITH_CONTEXT = (
        "Encontrei algumas informações relacionadas, mas não consigo confirmar "
        "todos os detalhes da sua pergunta. Recomendo consultar o manual oficial "
        "ou um supervisor para uma resposta completa."
    )
    
    def __init__(self, confidence_threshold: float = 0.7):
        """
        Inicializa o validador.
        
        Args:
            confidence_threshold: Limite mínimo de confiança para aceitar resposta (0-1)
        """
        self.confidence_threshold = confidence_threshold
    
    @trace_llm_call(name="validate_grounding", run_type="chain")
    async def validate(
        self,
        response: str,
        context: str,
        llm_service: Any
    ) -> Tuple[bool, float, str]:
        """
        Valida se a resposta é suportada pelo contexto.
        
        Args:
            response: Resposta gerada pelo LLM
            context: Contexto usado para gerar a resposta
            llm_service: Serviço LLM para executar a validação
            
        Returns:
            Tuple[is_valid, confidence, reason]
        """
        # Se não houver contexto, não há como validar
        if not context or not context.strip():
            logger.warning("Validação de grounding pulada: contexto vazio")
            return True, 0.5, "Sem contexto para validar"
        
        # Se a resposta for muito curta, provavelmente é uma resposta de fallback
        if len(response.strip()) < 50:
            logger.debug("Resposta curta, pulando validação de grounding")
            return True, 0.8, "Resposta curta aceita"
        
        try:
            # Preparar prompt de validação
            validation_prompt = self.VALIDATION_PROMPT.format(
                context=context[:4000],  # Limitar contexto para evitar tokens excessivos
                response=response[:2000]  # Limitar resposta
            )
            
            # Chamar LLM para validação (usar modelo rápido)
            messages = [
                {"role": "system", "content": "Você é um verificador de fatos técnico e preciso."},
                {"role": "user", "content": validation_prompt}
            ]
            
            # Usar geração síncrona sem streaming para validação
            validation_response = llm_service._generate_response_non_stream(
                messages=messages,
                selected_model="llama-3.1-8b-instant",  # Modelo rápido para validação
                provider="groq",
                temperature=0.1,  # Baixa temperatura para respostas consistentes
                max_tokens=200
            )
            
            # Parsear resposta JSON
            return self._parse_validation_response(validation_response)
            
        except Exception as e:
            logger.error(f"Erro na validação de grounding: {e}")
            # Em caso de erro, aceitar resposta (fail-open)
            return True, 0.5, f"Erro na validação: {e}"
    
    def _parse_validation_response(self, response: str) -> Tuple[bool, float, str]:
        """
        Parseia a resposta JSON do validador.
        
        Args:
            response: Resposta do LLM validador
            
        Returns:
            Tuple[is_valid, confidence, reason]
        """
        import json
        import re
        
        try:
            # Tentar extrair JSON da resposta
            json_match = re.search(r'\{[^}]+\}', response)
            if json_match:
                data = json.loads(json_match.group())
                is_valid = data.get("valido", True)
                confidence = float(data.get("confianca", 0.5))
                reason = data.get("motivo", "Sem motivo especificado")
                
                # Aplicar threshold de confiança
                if confidence < self.confidence_threshold:
                    is_valid = False
                    reason = f"Confiança baixa ({confidence:.2f} < {self.confidence_threshold}): {reason}"
                
                return is_valid, confidence, reason
            else:
                # Se não encontrar JSON, verificar por palavras-chave
                response_lower = response.lower()
                if "true" in response_lower or "válido" in response_lower:
                    return True, 0.7, "Validação implícita positiva"
                elif "false" in response_lower or "alucinação" in response_lower:
                    return False, 0.3, "Validação implícita negativa"
                else:
                    # Fallback: aceitar se não houver indicação clara de problema
                    return True, 0.5, "Validação inconclusiva"
                    
        except json.JSONDecodeError as e:
            logger.warning(f"Falha ao parsear JSON de validação: {e}")
            return True, 0.5, "Erro de parsing"
    
    def get_fallback_response(self, has_context: bool = True) -> str:
        """
        Retorna mensagem de fallback quando a resposta é rejeitada.
        
        Args:
            has_context: Se havia contexto disponível
            
        Returns:
            str: Mensagem de fallback apropriada
        """
        if has_context:
            return self.FALLBACK_MESSAGE_WITH_CONTEXT
        return self.FALLBACK_MESSAGE


# Instância singleton
grounding_validator = GroundingValidator()
