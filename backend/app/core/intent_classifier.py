"""
Classificador de intenção e gerador de perguntas clarificadoras.
Ajuda a identificar quando uma consulta precisa de mais contexto.
"""
import re
from typing import Dict, Any, List
from loguru import logger


# Padrões de intenção para classificação
INTENT_PATTERNS = {
    "capability_inquiry": [
        r'você\s+(é|está|pode|consegue|faz|realiza|analisa|extrai|lê|le)',
        r'(você|vc)\s+(pode|consegue|faz|realiza|analisa|extrai|lê|le)',
        r'que\s+tipo\s+(de\s+)?(arquivo|documento|formato)',
        r'quais\s+(tipos|formatos)\s+(de\s+)?(arquivo|documento)',
        r'você\s+(aceita|suporta|trabalha\s+com)',
        r'(é|está)\s+capaz\s+(de|de\s+extrair|de\s+ler|de\s+analisar)',
        r'capaz\s+(de|de\s+extrair|de\s+ler|de\s+analisar)',
        r'que\s+(você|vc)\s+(pode|consegue|faz)',
        r'o\s+que\s+(você|vc)\s+(pode|consegue|faz)',
        r'quais\s+(são\s+)?(suas\s+)?(capacidades|funcionalidades|recursos)',
    ],
    "performance_issues": [
        r'atraso|atrasos|atrasada|atrasadas',
        r'desempenho|performance|produtividade',
        r'problema|problemas|dificuldade|dificuldades',
        r'métrica|métricas|indicador|indicadores',
        r'por que|porquê|motivo|causa'
    ],
    "process_improvement": [
        r'melhorar|melhoria|otimizar|otimização',
        r'como fazer|como fazer para|estratégia|estratégias',
        r'sugestão|sugestões|dica|dicas',
        r'melhor prática|melhores práticas',
        r'eficiência|eficiências'
    ],
    "troubleshooting": [
        r'como resolver|solucionar|corrigir',
        r'o que fazer quando|em caso de',
        r'erro|erros|falha|falhas',
        r'não está funcionando|parou de funcionar',
        r'ajuda|socorro|urgente'
    ],
    "strategic_planning": [
        r'planejamento|planejar|estratégia|estratégico',
        r'futuro|próximo|próximos',
        r'expansão|crescimento|escalar',
        r'investimento|recursos|orçamento',
        r'longo prazo|médio prazo'
    ]
}


def classify_intent(query: str) -> Dict[str, Any]:
    """
    Classifica a intenção da consulta do usuário para melhor direcionar o contexto.
    
    Args:
        query: Texto da consulta do usuário
        
    Returns:
        Dicionário com:
        - primary_intent: str - Intenção principal detectada
        - all_intents: List[str] - Todas as intenções detectadas
        - confidence_scores: Dict[str, float] - Pontuações de confiança por intenção
        - requires_clarification: bool - Se precisa de clarificação
    """
    query_lower = query.lower()
    
    detected_intents = []
    confidence_scores = {}
    
    for intent, patterns in INTENT_PATTERNS.items():
        score = 0
        matches = 0
        for pattern in patterns:
            if re.search(pattern, query_lower):
                matches += 1
                score += 0.3  # Peso por padrão encontrado
        
        if score > 0:
            detected_intents.append(intent)
            # Aumentar confiança se múltiplos padrões foram encontrados
            if matches >= 2:
                score = min(score * 1.2, 1.0)  # Bônus de 20% para múltiplos padrões
            confidence_scores[intent] = min(score, 1.0)  # Cap em 1.0
    
    # Retornar a intenção com maior confiança ou "general" se nenhuma for clara
    primary_intent = max(confidence_scores.items(), key=lambda x: x[1])[0] if confidence_scores else "general"
    
    # Ajustar lógica de clarificação: considerar comprimento da query e termos técnicos específicos
    max_confidence = max(confidence_scores.values()) if confidence_scores else 0
    query_length = len(query.split())
    
    # Verificar se menciona termos técnicos específicos que indicam contexto suficiente
    technical_indicators = ['threshold', 'limite', 'desvio', 'desvios', 'sigma', 'sla', 'prazo', 
                           'entregas', 'entrega', 'motoristas', 'frota', 'equipe', 'produtividade',
                           'aceitáveis', 'aceitável']
    has_technical_context = any(term in query_lower for term in technical_indicators)
    
    # Queries muito curtas (< 3 palavras) SEMPRE precisam clarificação, mesmo que detecte padrões
    if query_length < 3:
        requires_clarification = True
    # Queries com 6+ palavras e termos técnicos/contexto específico SEMPRE têm contexto suficiente
    elif query_length >= 6 and has_technical_context:
        requires_clarification = False
    # Outras condições para contexto suficiente
    else:
        has_sufficient_context = (
            (query_length >= 5 and len(detected_intents) > 0 and max_confidence >= 0.3) or
            (max_confidence >= 0.3 and len(detected_intents) >= 2) or
            max_confidence >= 0.5
        )
        requires_clarification = not has_sufficient_context
    
    return {
        "primary_intent": primary_intent,
        "all_intents": detected_intents,
        "confidence_scores": confidence_scores,
        "requires_clarification": requires_clarification
    }


def generate_clarifying_question(original_query: str) -> str:
    """
    Gera uma pergunta clarificadora específica baseada na query original.
    
    Args:
        original_query: Query original do usuário
        
    Returns:
        String com pergunta clarificadora
    """
    query_lower = original_query.lower()
    
    # Padrões comuns e suas perguntas clarificadoras
    clarification_patterns = [
        (r'como melhorar|como otimizar|melhorar|otimizar', 
         "Você poderia especificar qual área específica você quer melhorar? Por exemplo: produtividade da equipe, tempo de entrega, ou custos operacionais?"),
        
        (r'problema|dificuldade|desafio', 
         "Poderia descrever com mais detalhes qual é o problema específico que você está enfrentando? Por exemplo: atrasos frequentes, erros recorrentes, ou falta de recursos?"),
        
        (r'prazo|tempo|deadline', 
         "Você está se referindo ao prazo de entregas, tempo de processamento de pedidos, ou algum outro tipo de prazo operacional?"),
        
        (r'custo|gasto|despesa', 
         "Estamos falando de custos com frota, mão de obra, armazenagem, ou qual tipo específico de custo?"),
        
        (r'relatorio|dashboard|indicador', 
         "Qual indicador específico você gostaria de entender melhor? Por exemplo: taxa de entrega no prazo, custo por entrega, ou satisfação do cliente?")
    ]
    
    for pattern, question in clarification_patterns:
        if re.search(pattern, query_lower):
            return question
    
    # Pergunta genérica se nenhuma padrão for encontrado
    return "Para que eu possa te ajudar da melhor forma, poderia especificar um pouco mais o que você precisa? Por exemplo: qual área operacional, qual tipo de problema ou qual objetivo você quer alcançar?"
