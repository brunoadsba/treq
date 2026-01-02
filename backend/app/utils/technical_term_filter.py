"""
Filtro de pós-processamento para remover ou traduzir termos técnicos.
Atua como camada obrigatória de limpeza após geração do LLM.
"""
import re
from typing import List, Tuple
from loguru import logger


def replace_sla(text: str) -> str:
    """
    Substitui "SLA" e variantes por "prazo(s)" de forma robusta.
    
    Args:
        text: Texto a ser processado
        
    Returns:
        Texto com SLA substituído por prazo/prazos
    """
    # Padrões específicos primeiro (mais específicos → mais genéricos)
    patterns = [
        # Correção de termos corrompidos (LLM às vezes gera texto truncado)
        (r'\bSLazo\b', 'Prazo'),  # SLA + prazo corrompido
        (r'\bSLazos\b', 'Prazos'),  # SLA + prazos corrompido
        (r'\b3to\b', 'desvio'),  # 3σ truncado
        (r'\b2to\b', 'desvio'),  # 2σ truncado
        # SLA com apóstrofe e número: "SLA's de 24h"
        (r"\bSLA'?s?\b\s+(de|da|do)\s+(\d+\w*)", r'prazo \1 \2'),
        # SLA com dois pontos: "SLA:"
        (r'\bSLA\b\s*:\s*', 'prazo: '),
        # SLA com preposição antes e adjetivo: "com SLA mensal"
        (r'\b(com|do|da|no|na|em|para|por)\s+SLA\b\s+([a-záàâãéêíóôõúç]+)', r'\1 prazo \2'),
        # SLA com preposição antes (sem adjetivo): "com SLA"
        (r'\b(com|do|da|no|na|em|para|por)\s+SLA\b', r'\1 prazo'),
        # SLA com preposição depois e número: "SLA de 24h"
        (r'\bSLA\b\s+(de|da|do)\s+(\d+\s*\w+)', r'prazo \1 \2'),
        # SLA com número sem preposição: "SLA 24h"
        (r'\bSLA\b\s+(\d+\s*\w+)', r'prazo de \1'),
        # SLA com adjetivo: "SLA mensal"
        (r'\bSLA\b\s+([a-záàâãéêíóôõúç]+(?:\s+[a-záàâãéêíóôõúç]+)?)', r'prazo \1'),
        # SLA (singular/plural)
        (r"\bSLA'?s?\b", 'prazo'),
    ]
    
    for pattern, replacement in patterns:
        text = re.sub(pattern, replacement, text, flags=re.IGNORECASE)
    
    return text


# Mapeamento centralizado e extensível de substituições
# IMPORTANTE: Ordem importa! Padrões mais específicos primeiro
TECHNICAL_TERMS_SUBSTITUTIONS: List[Tuple[re.Pattern, str]] = [
    # 1. Desvios padrão e Sigma
    (re.compile(r'\bdesvio\s*>\s*3\s*σ|\bdesvio\s*>\s*3\s*sigma\b', re.IGNORECASE), 'desvio muito acima do normal'),
    (re.compile(r'\bdesvio\s*>\s*2\s*σ|\bdesvio\s*>\s*2\s*sigma\b', re.IGNORECASE), 'desvio acima do normal'),
    (re.compile(r'>\s*3\s*σ|>\s*3\s*sigma\b', re.IGNORECASE), 'desvio muito acima do normal'),
    (re.compile(r'>\s*2\s*σ|>\s*2\s*sigma\b', re.IGNORECASE), 'desvio acima do normal'),
    (re.compile(r'\b3\s*σ\b|\b3\s*sigma\b', re.IGNORECASE), 'três desvios padrão'),
    (re.compile(r'\b2\s*σ\b|\b2\s*sigma\b', re.IGNORECASE), 'dois desvios padrão'),
    (re.compile(r'σ|sigma\b', re.IGNORECASE), 'desvio padrão'),
    
    # 2. Threshold e Limites
    (re.compile(r'\bThreshold\b:\s*', re.IGNORECASE), 
     'Limite: '),
    # Threshold no início da frase: manter maiúscula
    (re.compile(r'^Threshold\b', re.IGNORECASE | re.MULTILINE), 
     'Limite'),
    (re.compile(r'\bThreshold\b', re.IGNORECASE), 
     'limite'),
    
    # 3. SLA será processado pela função replace_sla() separadamente
    
    # 4. Outros termos técnicos comuns
    (re.compile(r'\bKPI\b|\bKPIs\b', re.IGNORECASE), 
     'indicador de performance'),
    (re.compile(r'\bAPI\b', re.IGNORECASE), 
     'interface de programação'),
    (re.compile(r'\bJSON\b', re.IGNORECASE), 
     'formato de dados'),
    (re.compile(r'\bETL\b', re.IGNORECASE), 
     'processo de integração de dados'),
    (re.compile(r'\bquery\b', re.IGNORECASE), 
     'consulta'),
    (re.compile(r'\bHardcoded\b', re.IGNORECASE), 
     'definido diretamente no código'),
    (re.compile(r'\bPII\b', re.IGNORECASE), 
     'dados pessoais'),
]


def filter_technical_terms(text: str, max_iterations: int = 3) -> str:
    """
    Remove ou traduz jargão técnico para linguagem de negócio.
    Atua como camada de pós-processamento obrigatória.
    
    Aplica filtro iterativamente até que não haja mais termos técnicos detectados
    ou até atingir o número máximo de iterações.
    
    Args:
        text: Texto gerado pelo LLM que pode conter termos técnicos
        max_iterations: Número máximo de iterações para garantir filtragem completa
        
    Returns:
        Texto com termos técnicos substituídos por explicações claras
    """
    if not text or not isinstance(text, str):
        return text
    
    original_text = text
    result = text
    iterations = 0
    
    try:
        # Aplicar filtro iterativamente até não detectar mais termos técnicos
        while iterations < max_iterations:
            previous_result = result
            
            # 1. Aplicar substituições de termos técnicos (exceto SLA)
            for pattern, replacement in TECHNICAL_TERMS_SUBSTITUTIONS:
                result = pattern.sub(replacement, result)
            
            # 2. Processar SLA separadamente com função dedicada
            result = replace_sla(result)
            
            # 3. Correção pós-processamento: manter maiúscula apenas quando Threshold está no início da frase
            # Exemplo: "Threshold:" -> "Limite:" mas "o threshold" -> "o limite"
            result = re.sub(r'^(\s*)limite\b', r'\1Limite', result, flags=re.MULTILINE)
            
            # Se não houve mudança nesta iteração, parar
            if result == previous_result:
                break
            
            iterations += 1
        
        # Validação pós-processamento: verificar se ainda há termos técnicos
        remaining_terms = _detect_remaining_technical_terms(result)
        if remaining_terms:
            logger.warning(
                f"⚠️ Termo técnico detectado após filtragem! Termos: {remaining_terms}. "
                f"Reaplicando filtro...",
                extra={"remaining_terms": remaining_terms, "text_preview": result[:200]}
            )
            # Reaplicar filtro uma última vez
            for pattern, replacement in TECHNICAL_TERMS_SUBSTITUTIONS:
                result = pattern.sub(replacement, result)
            result = replace_sla(result)
        
        # Log apenas se houve alteração (para monitoramento)
        if result != original_text:
            logger.debug(
                f"Filtro de termos técnicos aplicado ({iterations} iterações): "
                f"{len(original_text)} → {len(result)} chars"
            )
            
    except Exception as e:
        logger.error(f"Erro ao filtrar termos técnicos: {e}")
        # Fallback seguro: retornar original se falhar
        return original_text
    
    return result


def _detect_remaining_technical_terms(text: str) -> List[str]:
    """
    Detecta termos técnicos que ainda podem estar presentes no texto após filtragem.
    
    Args:
        text: Texto a ser verificado
        
    Returns:
        Lista de termos técnicos detectados
    """
    detected_terms = []
    
    # Padrões para detectar termos técnicos comuns
    technical_patterns = [
        (r'\bSLA\b', 'SLA'),
        (r'\bSLAs\b', 'SLAs'),
        (r'\bSLA\'s\b', "SLA's"),
        (r'\bSLazo\b', 'SLazo'),
        (r'\bSLazos\b', 'SLazos'),
        (r'\bThreshold\b', 'Threshold'),
        (r'\bKPI\b', 'KPI'),
        (r'\bKPIs\b', 'KPIs'),
    ]
    
    for pattern, term_name in technical_patterns:
        if re.search(pattern, text, re.IGNORECASE):
            detected_terms.append(term_name)
    
    return detected_terms


class StreamingTermFilter:
    """
    Filtro de termos técnicos para streaming.
    
    Estratégia simples: acumula chunks, processa quando tem tamanho suficiente,
    e retorna apenas o conteúdo novo para evitar duplicação.
    """
    def __init__(self, buffer_size: int = 15):
        """
        Args:
            buffer_size: Tamanho mínimo antes de processar (padrão: 15 caracteres)
        """
        self.buffer = ""
        self.buffer_size = buffer_size
        self.output_sent = 0  # Quantidade de caracteres já enviados para o cliente
    
    def filter_chunk(self, chunk: str) -> str:
        """
        Filtra um chunk de texto.
        
        Acumula no buffer, processa quando tem tamanho suficiente,
        e retorna apenas o conteúdo novo (não duplicado).
        
        Args:
            chunk: Chunk de texto a ser filtrado
            
        Returns:
            Chunk filtrado (pode ser string vazia se retido no buffer)
        """
        if not chunk:
            return ""
        
        # Acumular no buffer
        self.buffer += chunk
        
        # Se buffer ainda é pequeno, reter para evitar processar termos parciais
        if len(self.buffer) < self.buffer_size:
            return ""
        
        # Processar buffer inteiro com filtro de termos técnicos
        filtered = filter_technical_terms(self.buffer)
        
        # Calcular quanto já foi enviado vs quanto temos agora
        # Enviamos apenas o conteúdo novo (do ponto output_sent em diante)
        if self.output_sent >= len(filtered):
            # Já enviamos tudo que tem no filtered
            return ""
        
        # Conteúdo novo para enviar
        new_content = filtered[self.output_sent:]
        
        # Atualizar contador de enviados
        self.output_sent = len(filtered)
        
        return new_content
    
    def flush(self) -> str:
        """
        Processa e retorna qualquer conteúdo restante no buffer.
        
        Returns:
            Conteúdo filtrado restante
        """
        if not self.buffer:
            return ""
        
        # Processar buffer final
        filtered = filter_technical_terms(self.buffer)
        
        # Retornar apenas o que ainda não foi enviado
        if self.output_sent >= len(filtered):
            new_content = ""
        else:
            new_content = filtered[self.output_sent:]
        
        # Limpar estado
        self.buffer = ""
        self.output_sent = 0
        
        return new_content


# Exemplo de uso para testes
if __name__ == "__main__":
    sample_text = "O valor está > 3σ da média com Threshold: > 50 e o SLA de 24h foi comprometido."
    cleaned_text = filter_technical_terms(sample_text)
    print(f"Original: {sample_text}")
    print(f"Filtrado: {cleaned_text}")
