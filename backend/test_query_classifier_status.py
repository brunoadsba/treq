"""
Teste automatizado para validação da classificação de queries de status.
Valida que "Status de todas as unidades" e variações são classificadas corretamente.
"""
from app.core.query_classifier import classify_query

# Casos de teste conforme especificação
test_cases = [
    ("Status de todas as unidades", "status"),
    ("Status operacional", "status"),
    ("Status das unidades", "status"),
    ("Status de todas", "status"),
    ("Status geral", "status"),
    ("Status das operações", "status"),
    ("Qual o status de todas as unidades", "status"),
    ("Mostre o status operacional", "status"),
]

def test_classification():
    """Executa todos os casos de teste"""
    print("=== TESTE DE CLASSIFICAÇÃO DE QUERIES DE STATUS ===\n")
    
    all_passed = True
    failed_tests = []
    
    for query, expected_type in test_cases:
        result = classify_query(query)
        passed = result == expected_type
        
        status = "PASS" if passed else "FAIL"
        print(f"{status}: '{query:45}' → '{result:20}' (esperado: '{expected_type}')")
        
        if not passed:
            all_passed = False
            failed_tests.append((query, expected_type, result))
    
    print(f"\n{'='*80}")
    if all_passed:
        print("RESULTADO: Todos os testes passaram!")
    else:
        print(f"RESULTADO: {len(failed_tests)} teste(s) falharam:")
        for query, exp, res in failed_tests:
            print(f"  - '{query}' → '{res}' (esperado: '{exp}')")
    
    return all_passed

if __name__ == "__main__":
    success = test_classification()
    exit(0 if success else 1)
