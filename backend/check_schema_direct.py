#!/usr/bin/env python3
"""
Script para verificar o schema usando query SQL direta no Supabase.

Este script usa a API REST do Supabase para executar uma query SQL
que retorna informações do schema da tabela.
"""

import sys
import os
import requests
from pathlib import Path

# Adicionar o diretório raiz ao path para imports
backend_dir = Path(__file__).parent
sys.path.insert(0, str(backend_dir))

from app.config import get_settings

settings = get_settings()


def check_schema_via_sql():
    """Verifica schema usando query SQL via REST API do Supabase."""
    print("\n" + "=" * 80)
    print("  VERIFICANDO SCHEMA VIA SQL DIRETO")
    print("=" * 80 + "\n")
    
    supabase_url = str(settings.supabase_url).rstrip('/')
    supabase_key = settings.supabase_key or settings.supabase_anon_key
    
    if not supabase_key:
        print("❌ Erro: SUPABASE_KEY ou SUPABASE_ANON_KEY não configurada")
        return None
    
    # Query SQL para obter informações do schema
    sql_query = """
    SELECT 
        column_name,
        data_type,
        is_nullable,
        column_default
    FROM information_schema.columns
    WHERE table_schema = 'public' 
      AND table_name = 'operational_data'
    ORDER BY ordinal_position;
    """
    
    # Endpoint do Supabase para executar SQL via REST
    # Nota: Isso requer permissões adequadas
    endpoint = f"{supabase_url}/rest/v1/rpc/exec_sql"
    
    print(f"🔗 Conectando ao Supabase: {supabase_url}")
    print(f"📝 Executando query SQL...\n")
    
    try:
        # Tentar método alternativo: usar PostgREST para descobrir colunas
        # Fazendo uma query SELECT limitada para ver estrutura
        headers = {
            "apikey": supabase_key,
            "Authorization": f"Bearer {supabase_key}",
            "Content-Type": "application/json",
            "Prefer": "return=representation"
        }
        
        # Tentar buscar qualquer registro (mesmo que vazio) para ver estrutura
        table_url = f"{supabase_url}/rest/v1/operational_data"
        
        print("📋 Tentando descobrir estrutura da tabela...")
        response = requests.get(
            table_url,
            headers=headers,
            params={"limit": "0", "select": "*"}  # Limit 0 para não buscar dados, só estrutura
        )
        
        if response.status_code == 200:
            print("✅ Tabela existe!")
            # Se a tabela existe mas está vazia, não conseguimos ver colunas assim
            print("⚠️  Tabela existe mas pode estar vazia")
        elif response.status_code == 404:
            print("❌ Tabela 'operational_data' não encontrada")
            print("   Verifique se o nome da tabela está correto")
            return None
        else:
            print(f"⚠️  Status: {response.status_code}")
            print(f"   Resposta: {response.text[:200]}")
        
        # Método alternativo: tentar inserir um registro de teste (e depois deletar)
        # para descobrir quais colunas são obrigatórias
        print("\n" + "-" * 80)
        print("📋 Tentando descobrir colunas através de análise de erro...")
        print("-" * 80)
        
        # Tentar diferentes combinações de colunas comuns
        test_records = [
            {"data": "2025-01-01", "valor": 100, "indicador": "test"},
            {"data": "2025-01-01", "value": 100, "metric": "test"},
            {"data": "2025-01-01", "valor": 100, "unidade": "PE-Recife"},
            {"data": "2025-01-01", "valor": 100, "unit": "PE-Recife"},
            {"data": "2025-01-01", "valor": 100, "area": "Vendas"},
        ]
        
        for i, test_record in enumerate(test_records, 1):
            print(f"\n🧪 Teste {i}: Tentando inserir com colunas: {list(test_record.keys())}")
            try:
                insert_response = requests.post(
                    table_url,
                    headers=headers,
                    json=test_record
                )
                
                if insert_response.status_code == 201:
                    print(f"   ✅ Sucesso! Colunas aceitas: {list(test_record.keys())}")
                    # Deletar registro de teste
                    if insert_response.json():
                        record_id = insert_response.json()[0].get('id')
                        if record_id:
                            requests.delete(f"{table_url}?id=eq.{record_id}", headers=headers)
                    return list(test_record.keys())
                else:
                    error_msg = insert_response.text
                    if "column" in error_msg.lower() and "does not exist" in error_msg.lower():
                        print(f"   ❌ Alguma coluna não existe")
                    elif "null value" in error_msg.lower() or "violates" in error_msg.lower():
                        print(f"   ⚠️  Erro de validação (pode indicar estrutura correta)")
                        print(f"   Mensagem: {error_msg[:100]}")
                    else:
                        print(f"   ⚠️  Status {insert_response.status_code}: {error_msg[:100]}")
            except Exception as e:
                print(f"   ❌ Erro: {e}")
        
        print("\n" + "=" * 80)
        print("  RECOMENDAÇÃO")
        print("=" * 80)
        print("\n📝 Para descobrir o schema completo:")
        print("   1. Acesse o Supabase Dashboard")
        print("   2. Vá em 'SQL Editor'")
        print("   3. Execute a query:")
        print("\n   SELECT column_name, data_type, is_nullable")
        print("   FROM information_schema.columns")
        print("   WHERE table_schema = 'public'")
        print("     AND table_name = 'operational_data';")
        print("\n   4. Ou vá em 'Table Editor' → 'operational_data'")
        print("      e verifique as colunas manualmente")
        
        return None
        
    except Exception as e:
        print(f"\n❌ Erro: {e}")
        import traceback
        traceback.print_exc()
        return None


if __name__ == "__main__":
    result = check_schema_via_sql()
    sys.exit(0 if result else 1)
