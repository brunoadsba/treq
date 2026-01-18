#!/usr/bin/env python3
"""
Script de Validação de RLS (Row Level Security) - Supabase
Testa se as políticas de segurança estão REALMENTE ativas
"""
import os
import sys
from pathlib import Path
from typing import Dict, List
import asyncio
from supabase import create_client, Client

# Adicionar path do backend
sys.path.insert(0, str(Path(__file__).parent.parent))

class Color:
    RED = '\033[91m'
    GREEN = '\033[92m'
    YELLOW = '\033[93m'
    BLUE = '\033[94m'
    RESET = '\033[0m'
    BOLD = '\033[1m'

def print_test(name: str, passed: bool, details: str = ""):
    status = f"{Color.GREEN}✓ PASS{Color.RESET}" if passed else f"{Color.RED}✗ FAIL{Color.RESET}"
    print(f"{status} | {name}")
    if details:
        print(f"      {Color.YELLOW}{details}{Color.RESET}")

class RLSTester:
    def __init__(self):
        self.supabase_url = os.getenv("SUPABASE_URL")
        self.anon_key = os.getenv("SUPABASE_ANON_KEY")
        self.service_key = os.getenv("SUPABASE_SERVICE_KEY")
        
        if not all([self.supabase_url, self.anon_key, self.service_key]):
            print(f"{Color.RED}ERRO: Variáveis SUPABASE não configuradas{Color.RESET}")
            sys.exit(1)
        
        # Cliente com service_role (BYPASSA RLS)
        self.service_client = create_client(self.supabase_url, self.service_key)
        
        # Cliente com anon key (RESPEITA RLS)
        self.anon_client = create_client(self.supabase_url, self.anon_key)
    
    def test_service_key_detection(self) -> bool:
        """Verifica se código está usando service_role em produção"""
        backend_path = Path(__file__).parent.parent / "app"
        
        violations = []
        for py_file in backend_path.rglob("*.py"):
            try:
                content = py_file.read_text()
                if "SUPABASE_SERVICE_KEY" in content:
                    # Permitido apenas em scripts ou testes
                    if "scripts/" not in str(py_file) and "tests/" not in str(py_file):
                        violations.append(str(py_file.relative_to(backend_path)))
            except:
                continue
        
        if violations:
            print_test(
                "Service Key Detection",
                False,
                f"service_role key usado em {len(violations)} arquivos de produção: {violations[0]}"
            )
            return False
        
        print_test("Service Key Detection", True, "Nenhum uso de service_role em código de produção")
        return True
    
    def test_rls_policies_exist(self) -> bool:
        """Verifica se políticas RLS existem nas tabelas"""
        try:
            # Testar tabela 'documents'
            result = self.service_client.rpc('get_rls_policies', {'table_name': 'documents'}).execute()
            
            if not result.data:
                print_test("RLS Policies Exist", False, "Nenhuma política RLS encontrada na tabela 'documents'")
                return False
            
            print_test("RLS Policies Exist", True, f"{len(result.data)} políticas RLS ativas")
            return True
        except Exception as e:
            print_test("RLS Policies Exist", False, f"Erro ao verificar políticas: {str(e)[:100]}")
            return False
    
    def test_cross_user_access(self) -> bool:
        """Testa se usuário A consegue ver dados do usuário B (NÃO DEVE)"""
        try:
            # Criar documento de teste com service_client (user_id fake)
            test_doc = {
                "user_id": "test-user-a",
                "content": "Documento secreto do User A",
                "document_type": "test"
            }
            
            insert_result = self.service_client.table("documents").insert(test_doc).execute()
            doc_id = insert_result.data[0]['id']
            
            # Tentar acessar com cliente anônimo (simulando user B)
            # Se RLS estiver correto, não deve retornar nada
            access_result = self.anon_client.table("documents").select("*").eq("id", doc_id).execute()
            
            # Limpar teste
            self.service_client.table("documents").delete().eq("id", doc_id).execute()
            
            if access_result.data:
                print_test(
                    "Cross-User Access Prevention",
                    False,
                    "CRÍTICO: Usuário anônimo conseguiu acessar dados de outro usuário!"
                )
                return False
            
            print_test("Cross-User Access Prevention", True, "RLS bloqueou acesso cross-user corretamente")
            return True
            
        except Exception as e:
            print_test("Cross-User Access Prevention", False, f"Erro no teste: {str(e)[:100]}")
            return False
    
    def test_authenticated_client_implementation(self) -> bool:
        """Verifica se existe implementação de client autenticado por usuário"""
        backend_path = Path(__file__).parent.parent / "app"
        
        has_implementation = False
        for py_file in backend_path.rglob("*.py"):
            try:
                content = py_file.read_text()
                # Procurar por padrões de autenticação de client
                if any(pattern in content for pattern in [
                    "get_user_supabase_client",
                    "get_authenticated_client",
                    "create_client.*headers.*Authorization"
                ]):
                    has_implementation = True
                    print_test(
                        "Authenticated Client Implementation",
                        True,
                        f"Implementação encontrada em {py_file.name}"
                    )
                    return True
            except:
                continue
        
        if not has_implementation:
            print_test(
                "Authenticated Client Implementation",
                False,
                "CRÍTICO: Nenhuma implementação de client autenticado encontrada"
            )
            return False
        
        return True
    
    def test_jwt_generation_for_rls(self) -> bool:
        """Verifica se JWT está sendo gerado para passar ao Supabase"""
        backend_path = Path(__file__).parent.parent / "app"
        
        has_jwt_gen = False
        for py_file in backend_path.rglob("*.py"):
            try:
                content = py_file.read_text()
                if "generate_supabase_jwt" in content or "supabase.*jwt" in content.lower():
                    has_jwt_gen = True
                    break
            except:
                continue
        
        print_test(
            "JWT Generation for RLS",
            has_jwt_gen,
            "JWT sendo gerado para Supabase" if has_jwt_gen else "JWT NÃO está sendo gerado"
        )
        return has_jwt_gen
    
    def run_all_tests(self) -> Dict[str, bool]:
        """Executa todos os testes de RLS"""
        print(f"\n{Color.BOLD}{Color.BLUE}{'='*60}{Color.RESET}")
        print(f"{Color.BOLD}{Color.BLUE}TESTE DE RLS SUPABASE{Color.RESET}".center(70))
        print(f"{Color.BOLD}{Color.BLUE}{'='*60}{Color.RESET}\n")
        
        results = {
            "Service Key Detection": self.test_service_key_detection(),
            "RLS Policies Exist": self.test_rls_policies_exist(),
            "Cross-User Access Prevention": self.test_cross_user_access(),
            "Authenticated Client Implementation": self.test_authenticated_client_implementation(),
            "JWT Generation for RLS": self.test_jwt_generation_for_rls(),
        }
        
        # Resumo
        total = len(results)
        passed = sum(results.values())
        
        print(f"\n{Color.BOLD}{'='*60}{Color.RESET}")
        print(f"{Color.BOLD}RESULTADO FINAL:{Color.RESET}")
        print(f"Aprovados: {Color.GREEN}{passed}{Color.RESET}/{total}")
        print(f"Reprovados: {Color.RED}{total - passed}{Color.RESET}/{total}")
        
        if passed == total:
            print(f"\n{Color.GREEN}✅ RLS CONFIGURADO CORRETAMENTE{Color.RESET}")
            print(f"{Color.GREEN}Sistema pronto para produção multi-tenant{Color.RESET}\n")
            return results
        elif passed >= 3:
            print(f"\n{Color.YELLOW}⚠️ RLS PARCIALMENTE CONFIGURADO{Color.RESET}")
            print(f"{Color.YELLOW}Corrigir falhas antes de produção{Color.RESET}\n")
        else:
            print(f"\n{Color.RED}❌ RLS NÃO CONFIGURADO{Color.RESET}")
            print(f"{Color.RED}CRÍTICO: Sistema vulnerável a acesso cross-user{Color.RESET}\n")
        
        return results

def main():
    tester = RLSTester()
    results = tester.run_all_tests()
    
    # Exit code baseado nos resultados
    critical_tests = [
        "Cross-User Access Prevention",
        "Service Key Detection"
    ]
    
    critical_passed = all(results.get(test, False) for test in critical_tests)
    
    if not critical_passed:
        print(f"{Color.RED}BLOQUEADOR: Testes críticos falharam. Não prosseguir com roadmap.{Color.RESET}")
        sys.exit(1)
    
    all_passed = all(results.values())
    sys.exit(0 if all_passed else 1)

if __name__ == "__main__":
    main()