
import sys
from pathlib import Path

# Adicionar o diretório raiz ao path para imports
backend_dir = Path(__file__).parent.parent
sys.path.insert(0, str(backend_dir))

from app.core.query_classifier import classify_query
from app.core.follow_up_detector import detect_follow_up

def test_metrics_classification():
    print("=== TESTE DE CLASSIFICAÇÃO DE MÉTRICAS ===")
    metric_queries = [
        "quais as métricas de cancelamento",
        "qual o valor de indicadores",
        "performance de recife",
        "kpi de atrasos",
        "quantos pedidos cancelados"
    ]
    
    for q in metric_queries:
        res = classify_query(q)
        print(f"Query: '{q}' -> Class: '{res}'")
        assert res in ["metrica", "metrica_temporal"], f"Erro na query {q}"

def test_follow_up_style():
    print("\n=== TESTE DE DETECÇÃO DE ESTILO EM FOLLOW-UP ===")
    
    # Mock simples do context_manager
    class MockContextManager:
        def __init__(self):
            # Precisa ter histórico para ser considerado follow-up
            self.message_history = [{"content": "Olá", "role": "user"}]
            
    ctx = MockContextManager()
    
    style_queries = [
        "seja direto",
        "resuma",
        "simplifique",
        "mais curto",
        "seja objetivo"
    ]
    
    for q in style_queries:
        res = detect_follow_up(q, ctx)
        print(f"Query: '{q}' -> Follow-up: {res}")
        assert res is True, f"Erro na query {q}"

if __name__ == "__main__":
    try:
        test_metrics_classification()
        test_follow_up_style()
        print("\n✅ Todos os novos testes de lógica passaram!")
    except Exception as e:
        print(f"\n❌ Falha nos testes: {e}")
        sys.exit(1)
