#!/usr/bin/env python3
"""
Script de Validação Pós-Auditoria
Verifica se as correções críticas foram aplicadas corretamente.
"""

import requests
import json
from datetime import datetime

def test_security_fixes():
    """Testa se as correções de segurança RLS foram aplicadas."""
    print("🔐 TESTANDO CORREÇÕES DE SEGURANÇA...")
    
    # Obter token
    login_response = requests.post(
        "http://localhost:8002/auth/login",
        headers={"Content-Type": "application/x-www-form-urlencoded"},
        data="username=admin&password=admin123"
    )
    
    if login_response.status_code != 200:
        print("❌ Falha no login")
        return False
    
    token = login_response.json()["access_token"]
    
    # Testar busca RAG
    rag_response = requests.post(
        "http://localhost:8002/chat/",
        headers={
            "Content-Type": "application/json",
            "Authorization": f"Bearer {token}"
        },
        json={
            "message": "teste segurança rag",
            "user_id": "test_user",
            "stream": False
        }
    )
    
    if rag_response.status_code != 200:
        print("❌ Falha na busca RAG")
        return False
    
    data = rag_response.json()
    sources = data.get("sources", [])
    
    print(f"✅ RAG funcionando - {len(sources)} fontes encontradas")
    
    # Verificar metadados de segurança
    security_issues = []
    for source in sources:
        metadata = source.get("metadata", {})
        classification = metadata.get("classification")
        allowed_users = metadata.get("allowed_users", [])
        
        # VALIDAÇÃO CRÍTICA: Confidencial + público
        if classification in ["confidential", "restricted"] and "*" in allowed_users:
            security_issues.append(f"VAZAMENTO: {metadata.get('filename')} é {classification} mas público")
        
        # VALIDAÇÃO: allowed_users não vazio
        if not allowed_users:
            security_issues.append(f"RLS FALHO: {metadata.get('filename')} sem allowed_users")
    
    if security_issues:
        print("❌ PROBLEMAS DE SEGURANÇA DETECTADOS:")
        for issue in security_issues:
            print(f"   - {issue}")
        return False
    
    print("✅ Validação de segurança RLS: APROVADA")
    return True

def test_chunking_optimization():
    """Testa se a otimização de chunking foi aplicada."""
    print("\n📏 TESTANDO OTIMIZAÇÃO DE CHUNKING...")
    
    # Verificar se chunks estão dentro do novo limite (1200 chars)
    token = requests.post(
        "http://localhost:8002/auth/login",
        headers={"Content-Type": "application/x-www-form-urlencoded"},
        data="username=admin&password=admin123"
    ).json()["access_token"]
    
    response = requests.post(
        "http://localhost:8002/chat/",
        headers={
            "Content-Type": "application/json",
            "Authorization": f"Bearer {token}"
        },
        json={
            "message": "teste chunking",
            "user_id": "test",
            "stream": False
        }
    )
    
    sources = response.json().get("sources", [])
    chunk_sizes = []
    
    for source in sources:
        content = source.get("content", "")
        chunk_sizes.append(len(content))
    
    if chunk_sizes:
        avg_size = sum(chunk_sizes) / len(chunk_sizes)
        max_size = max(chunk_sizes)
        
        print(f"✅ Tamanho médio dos chunks: {avg_size:.0f} chars")
        print(f"✅ Tamanho máximo: {max_size} chars")
        
        if max_size > 1200:
            print(f"⚠️ Chunk muito grande detectado: {max_size} chars")
            return False
    
    print("✅ Otimização de chunking: APROVADA")
    return True

def test_noise_cleaning():
    """Testa se a limpeza de ruído foi aplicada."""
    print("\n🧹 TESTANDO LIMPEZA DE RUÍDO...")
    
    token = requests.post(
        "http://localhost:8002/auth/login",
        headers={"Content-Type": "application/x-www-form-urlencoded"},
        data="username=admin&password=admin123"
    ).json()["access_token"]
    
    response = requests.post(
        "http://localhost:8002/chat/",
        headers={
            "Content-Type": "application/json",
            "Authorization": f"Bearer {token}"
        },
        json={
            "message": "teste limpeza",
            "user_id": "test",
            "stream": False
        }
    )
    
    sources = response.json().get("sources", [])
    noise_detected = []
    
    for source in sources:
        content = source.get("content", "")
        
        # Verificar padrões de ruído
        if "[Fonte:" in content:
            noise_detected.append("Prefixo de fonte não removido")
        if "- [ ]" in content:
            noise_detected.append("Checkbox vazio não removido")
    
    if noise_detected:
        print("❌ RUÍDO DETECTADO:")
        for noise in noise_detected:
            print(f"   - {noise}")
        return False
    
    print("✅ Limpeza de ruído: APROVADA")
    return True

def main():
    """Executa todos os testes de validação."""
    print("🔍 VALIDAÇÃO PÓS-AUDITORIA TREQ RAG")
    print("=" * 50)
    
    results = []
    
    try:
        results.append(("Segurança RLS", test_security_fixes()))
        results.append(("Chunking", test_chunking_optimization()))
        results.append(("Limpeza", test_noise_cleaning()))
    except Exception as e:
        print(f"❌ Erro durante validação: {e}")
        return
    
    print("\n" + "=" * 50)
    print("📊 RESUMO DA VALIDAÇÃO:")
    
    passed = 0
    for test_name, result in results:
        status = "✅ PASSOU" if result else "❌ FALHOU"
        print(f"   {test_name}: {status}")
        if result:
            passed += 1
    
    score = (passed / len(results)) * 10
    print(f"\n🎯 SCORE FINAL: {score:.1f}/10")
    
    if score >= 9.0:
        print("🎉 BASE DE CONHECIMENTO APROVADA PARA PRODUÇÃO!")
    elif score >= 7.0:
        print("⚠️ Melhorias necessárias antes da produção")
    else:
        print("🚨 CORREÇÕES CRÍTICAS NECESSÁRIAS")

if __name__ == "__main__":
    main()
