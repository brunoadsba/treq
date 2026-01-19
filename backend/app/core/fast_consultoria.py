"""
Otimização de Performance para Consultoria
Implementa cache e respostas diretas para consultas comuns
"""
from typing import Dict, Optional
import re
from loguru import logger

# Cache de respostas comuns sobre consultoria
CONSULTORIA_RESPONSES = {
    "definicao": (
        "Sim, a Consultoria é responsável por:\n\n"
        "• **Treinamento:** Treinar os responsáveis por nível de escalação\n"
        "• **Validação:** Validar o entendimento dos prazos estabelecidos\n"
        "• **Testes:** Testar o fluxo de escalação através de simulações\n\n"
        "A Consultoria garante que todos os envolvidos compreendam seus papéis "
        "e responsabilidades no processo operacional."
    ),
    "responsabilidades": (
        "A Consultoria tem três responsabilidades principais:\n\n"
        "1. **Treinar responsáveis** por nível de escalação\n"
        "2. **Validar entendimento** dos prazos estabelecidos\n"
        "3. **Testar fluxo de escalação** através de simulações\n\n"
        "Essas atividades garantem que o processo operacional funcione corretamente."
    ),
    "treinamento": (
        "O treinamento da Consultoria foca em:\n\n"
        "• Capacitar responsáveis por cada nível de escalação\n"
        "• Garantir compreensão dos prazos de resposta\n"
        "• Validar conhecimento através de simulações práticas\n\n"
        "O objetivo é preparar a equipe para responder adequadamente aos alertas."
    )
}

def detect_fast_consultoria_response(message: str) -> Optional[str]:
    """
    Detecta consultas sobre consultoria que podem ter resposta imediata.
    
    Args:
        message: Mensagem do usuário
        
    Returns:
        Resposta direta se detectada, None caso contrário
    """
    if not message.lower().startswith("consultoria:"):
        return None
    
    content = message.lower().replace("consultoria:", "").strip()
    
    # Padrões para resposta rápida
    patterns = {
        "definicao": [
            r"você quer saber sobre a consultoria",
            r"o que é consultoria",
            r"consultoria é responsável",
            r"consultoria.*responsável.*treinar.*validar.*testar"
        ],
        "responsabilidades": [
            r"quais.*responsabilidades.*consultoria",
            r"o que.*consultoria.*faz",
            r"funções.*consultoria"
        ],
        "treinamento": [
            r"consultoria.*treina",
            r"treinamento.*consultoria",
            r"como.*consultoria.*treina"
        ]
    }
    
    # Verificar padrões
    for response_type, pattern_list in patterns.items():
        for pattern in pattern_list:
            if re.search(pattern, content):
                logger.info(f"Consultoria rápida detectada: {response_type}")
                return CONSULTORIA_RESPONSES[response_type]
    
    # Fallback para consultas longas sobre consultoria (>15 palavras)
    if len(content.split()) > 15 and any(word in content for word in ["consultoria", "responsável", "treinar", "validar", "testar"]):
        logger.info("Consultoria longa detectada - usando resposta padrão")
        return CONSULTORIA_RESPONSES["definicao"]
    
    return None
