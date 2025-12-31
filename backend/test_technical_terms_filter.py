"""
Teste automatizado para validação do filtro de termos técnicos.
Valida todos os casos mencionados no documento erros-chat-procedimentos.md
"""
from app.utils.technical_term_filter import filter_technical_terms

# Casos de teste conforme especificação
test_cases = [
    ("com SLA mensal", "com prazo mensal"),
    ("SLA de 24h", "prazo de 24h"),
    ("SLA:", "prazo:"),
    ("SLAs", "prazos"),
    ("SLA's", "prazos"),
    ("SLazo mensal", "prazo mensal"),
    ("responsável e SLA", "responsável e prazo"),
    ("Procedimentos com SLA de resposta", "Procedimentos com prazo de resposta"),
    ("O threshold foi excedido", "O limite foi excedido"),
    ("O KPI está fora do sigma", "O indicador de performance está fora do desvio padrão"),
]

def test_filter():
    """Executa todos os casos de teste"""
    print("=== TESTE DE FILTRO DE TERMOS TÉCNICOS ===\n")
    
    all_passed = True
    failed_tests = []
    
    for input_text, expected in test_cases:
        result = filter_technical_terms(input_text)
        passed = result == expected
        
        status = "PASS" if passed else "FAIL"
        print(f"{status}: '{input_text:45}' → '{result:50}' (esperado: '{expected}')")
        
        if not passed:
            all_passed = False
            failed_tests.append((input_text, expected, result))
    
    print(f"\n{'='*80}")
    if all_passed:
        print("RESULTADO: Todos os testes passaram!")
    else:
        print(f"RESULTADO: {len(failed_tests)} teste(s) falharam:")
        for inp, exp, res in failed_tests:
            print(f"  - '{inp}' → '{res}' (esperado: '{exp}')")
    
    return all_passed

if __name__ == "__main__":
    success = test_filter()
    exit(0 if success else 1)
