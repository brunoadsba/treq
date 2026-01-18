#!/usr/bin/env python3
"""
Script de Auditoria Crítica - Treq Enterprise
Valida pré-requisitos antes de iniciar roadmap de segurança
"""
import os
import sys
import subprocess
from pathlib import Path
from typing import Dict, List, Tuple
import re
import json

class Color:
    RED = '\033[91m'
    GREEN = '\033[92m'
    YELLOW = '\033[93m'
    BLUE = '\033[94m'
    RESET = '\033[0m'
    BOLD = '\033[1m'

def print_header(text: str):
    print(f"\n{Color.BOLD}{Color.BLUE}{'='*60}{Color.RESET}")
    print(f"{Color.BOLD}{Color.BLUE}{text.center(60)}{Color.RESET}")
    print(f"{Color.BOLD}{Color.BLUE}{'='*60}{Color.RESET}\n")

def print_check(name: str, passed: bool, details: str = ""):
    status = f"{Color.GREEN}✓ PASS{Color.RESET}" if passed else f"{Color.RED}✗ FAIL{Color.RESET}"
    print(f"{status} | {name}")
    if details:
        print(f"      {Color.YELLOW}{details}{Color.RESET}")

def check_wsl2_environment() -> Tuple[bool, str]:
    """Verifica se está rodando no WSL2 e identifica problemas"""
    try:
        with open('/proc/version', 'r') as f:
            version = f.read().lower()
        
        is_wsl = 'microsoft' in version or 'wsl' in version
        
        if is_wsl:
            # Testar imports problemáticos
            problems = []
            
            try:
                import psycopg
            except Exception as e:
                problems.append(f"psycopg3: {str(e)[:50]}")
            
            try:
                import sentence_transformers
            except Exception as e:
                problems.append(f"sentence-transformers: {str(e)[:50]}")
            
            if problems:
                return False, f"WSL2 detectado com problemas: {'; '.join(problems)}"
            return True, "WSL2 detectado mas bibliotecas funcionando"
        
        return True, "Ambiente Linux nativo"
    except FileNotFoundError:
        return True, "Ambiente Windows/Mac (não WSL)"

def check_rls_configuration() -> Tuple[bool, str]:
    """Verifica se RLS está configurado corretamente"""
    backend_path = Path("backend")
    
    # Procurar uso de service_role key (inseguro)
    service_role_uses = []
    
    for py_file in backend_path.rglob("*.py"):
        try:
            content = py_file.read_text()
            if "SUPABASE_SERVICE_KEY" in content or "service_role" in content.lower():
                service_role_uses.append(str(py_file))
        except:
            continue
    
    if service_role_uses:
        return False, f"service_role key encontrado em {len(service_role_uses)} arquivos (bypassa RLS)"
    
    # Verificar se há implementação de get_user_client
    has_user_client = False
    for py_file in backend_path.rglob("*.py"):
        try:
            content = py_file.read_text()
            if "get_user_supabase" in content or "user_client" in content:
                has_user_client = True
                break
        except:
            continue
    
    if not has_user_client:
        return False, "Nenhuma implementação de client por usuário encontrada"
    
    return True, "RLS configurado com client por usuário"

def check_ssot_configuration() -> Tuple[bool, str]:
    """Verifica se configurações estão centralizadas"""
    backend_path = Path("backend/app")
    
    # Contar usos de os.getenv espalhados
    getenv_count = 0
    getenv_files = []
    
    for py_file in backend_path.rglob("*.py"):
        if "config.py" in str(py_file):
            continue
        
        try:
            content = py_file.read_text()
            matches = len(re.findall(r'os\.getenv|os\.environ', content))
            if matches > 0:
                getenv_count += matches
                getenv_files.append(f"{py_file.name} ({matches}x)")
        except:
            continue
    
    # Verificar se existe config.py centralizado
    config_file = backend_path / "config.py"
    has_central_config = config_file.exists()
    
    if getenv_count > 15:  # Threshold arbitrário
        return False, f"{getenv_count} usos de getenv espalhados ({len(getenv_files)} arquivos)"
    
    if not has_central_config:
        return False, "Nenhum config.py centralizado encontrado"
    
    return True, f"Config centralizado, apenas {getenv_count} getenv em features"

def check_mock_implementations() -> Tuple[bool, str]:
    """Identifica implementações mock em produção"""
    backend_path = Path("backend/app/features")
    
    mock_files = []
    
    for py_file in backend_path.rglob("*.py"):
        try:
            content = py_file.read_text()
            # Procurar por padrões de mock
            if any(pattern in content.lower() for pattern in ['mock', 'fake', 'dummy', 'return [{"title": "mock']):
                # Verificar se NÃO é arquivo de teste
                if "test_" not in py_file.name and "tests/" not in str(py_file):
                    mock_files.append(str(py_file.relative_to(backend_path)))
        except:
            continue
    
    if mock_files:
        return False, f"{len(mock_files)} arquivos com mocks: {', '.join(mock_files[:3])}"
    
    return True, "Nenhum mock detectado em código de produção"

def check_secrets_in_repo() -> Tuple[bool, str]:
    """Verifica se há secrets commitados"""
    dangerous_patterns = [
        (r'GROQ_API_KEY\s*=\s*["\']sk-', "Groq API key hardcoded"),
        (r'GEMINI_API_KEY\s*=\s*["\']AI', "Gemini API key hardcoded"),
        (r'SUPABASE_KEY\s*=\s*["\']eyJ', "Supabase key hardcoded"),
        (r'password\s*=\s*["\'][^"\']{8,}', "Password hardcoded"),
    ]
    
    violations = []
    
    for py_file in Path("backend").rglob("*.py"):
        try:
            content = py_file.read_text()
            for pattern, desc in dangerous_patterns:
                if re.search(pattern, content, re.IGNORECASE):
                    violations.append(f"{py_file.name}: {desc}")
        except:
            continue
    
    if violations:
        return False, f"{len(violations)} secrets hardcoded: {violations[0]}"
    
    return True, "Nenhum secret hardcoded detectado"

def check_ci_cd_setup() -> Tuple[bool, str]:
    """Verifica se CI/CD está configurado"""
    github_workflows = Path(".github/workflows")
    
    if not github_workflows.exists():
        return False, "Nenhuma pasta .github/workflows encontrada"
    
    workflow_files = list(github_workflows.glob("*.yml")) + list(github_workflows.glob("*.yaml"))
    
    if not workflow_files:
        return False, "Nenhum workflow do GitHub Actions configurado"
    
    # Verificar se há testes automatizados
    has_tests = False
    for wf in workflow_files:
        try:
            content = wf.read_text()
            if 'pytest' in content or 'npm test' in content:
                has_tests = True
                break
        except:
            continue
    
    if not has_tests:
        return False, f"{len(workflow_files)} workflows mas sem testes automatizados"
    
    return True, f"{len(workflow_files)} workflows com testes configurados"

def check_auth_implementation() -> Tuple[bool, str]:
    """Verifica se autenticação está implementada"""
    backend_path = Path("backend/app")
    
    # Procurar por implementação de auth
    auth_indicators = []
    
    auth_dir = backend_path / "auth"
    if auth_dir.exists():
        auth_indicators.append("Pasta auth/ existe")
        
        jwt_file = auth_dir / "jwt.py"
        if jwt_file.exists():
            auth_indicators.append("jwt.py implementado")
    
    # Procurar por OAuth2
    for py_file in backend_path.rglob("*.py"):
        try:
            content = py_file.read_text()
            if "OAuth2PasswordBearer" in content or "get_current_user" in content:
                auth_indicators.append(f"OAuth2 em {py_file.name}")
                break
        except:
            continue
    
    if len(auth_indicators) < 2:
        return False, f"Autenticação incompleta: {', '.join(auth_indicators) if auth_indicators else 'Nenhuma implementação'}"
    
    return True, f"Autenticação implementada: {', '.join(auth_indicators)}"

def check_docker_setup() -> Tuple[bool, str]:
    """Verifica se Docker está configurado"""
    docker_compose = Path("docker-compose.yml")
    dockerfile = Path("Dockerfile")
    
    if docker_compose.exists() and dockerfile.exists():
        return True, "Docker Compose e Dockerfile configurados"
    
    if docker_compose.exists() or dockerfile.exists():
        return False, "Docker parcialmente configurado (falta compose ou Dockerfile)"
    
    return False, "Nenhuma configuração Docker encontrada"

def generate_report(results: Dict[str, Tuple[bool, str]]) -> Dict:
    """Gera relatório JSON estruturado"""
    total = len(results)
    passed = sum(1 for p, _ in results.values() if p)
    failed = total - passed
    
    return {
        "summary": {
            "total_checks": total,
            "passed": passed,
            "failed": failed,
            "score": round((passed / total) * 100, 2)
        },
        "checks": {
            name: {
                "passed": passed,
                "details": details
            }
            for name, (passed, details) in results.items()
        },
        "recommendation": get_recommendation(passed, total)
    }

def get_recommendation(passed: int, total: int) -> str:
    """Retorna recomendação baseada no score"""
    score = (passed / total) * 100
    
    if score >= 90:
        return "✅ APROVADO: Sistema pronto para iniciar roadmap de segurança"
    elif score >= 70:
        return "⚠️ ATENÇÃO: Resolver falhas críticas antes de prosseguir"
    elif score >= 50:
        return "❌ REPROVADO: Múltiplos problemas críticos identificados"
    else:
        return "🔴 CRÍTICO: Sistema não está pronto para produção enterprise"

def main():
    print_header("AUDITORIA TÉCNICA CRÍTICA - TREQ ENTERPRISE")
    
    # Verificar se está na raiz do projeto
    if not Path("backend").exists():
        print(f"{Color.RED}ERRO: Execute este script da raiz do projeto Treq{Color.RESET}")
        sys.exit(1)
    
    checks = {
        "1. Ambiente WSL2/Linux": check_wsl2_environment,
        "2. RLS Supabase": check_rls_configuration,
        "3. SSOT Configuração": check_ssot_configuration,
        "4. Mocks em Produção": check_mock_implementations,
        "5. Secrets Hardcoded": check_secrets_in_repo,
        "6. CI/CD GitHub Actions": check_ci_cd_setup,
        "7. Autenticação OAuth2": check_auth_implementation,
        "8. Docker Setup": check_docker_setup,
    }
    
    results = {}
    
    for name, check_func in checks.items():
        try:
            passed, details = check_func()
            results[name] = (passed, details)
            print_check(name, passed, details)
        except Exception as e:
            results[name] = (False, f"Erro ao executar check: {str(e)}")
            print_check(name, False, f"Erro: {str(e)}")
    
    # Gerar relatório
    report = generate_report(results)
    
    print_header("RELATÓRIO FINAL")
    print(f"Score: {Color.BOLD}{report['summary']['score']}%{Color.RESET}")
    print(f"Aprovados: {Color.GREEN}{report['summary']['passed']}{Color.RESET}/{report['summary']['total']}")
    print(f"Reprovados: {Color.RED}{report['summary']['failed']}{Color.RESET}/{report['summary']['total']}")
    print(f"\n{report['recommendation']}\n")
    
    # Salvar relatório JSON
    report_file = Path("audit_report.json")
    with open(report_file, 'w') as f:
        json.dump(report, f, indent=2)
    
    print(f"Relatório completo salvo em: {Color.BLUE}{report_file}{Color.RESET}\n")
    
    # Exit code baseado no score
    sys.exit(0 if report['summary']['score'] >= 70 else 1)

if __name__ == "__main__":
    main()