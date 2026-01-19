#!/usr/bin/env python3
"""
Script de correção emergencial para dados já indexados
"""
import requests
import json

def fix_existing_data():
    print("🔧 CORRIGINDO DADOS EXISTENTES...")
    
    # Este seria um script para atualizar dados no Supabase
    # Por segurança, apenas logamos o que deveria ser feito
    
    print("⚠️ AÇÃO MANUAL NECESSÁRIA:")
    print("1. Conectar ao Supabase")
    print("2. UPDATE langchain_pg_embedding SET metadata = jsonb_set(metadata, '{allowed_users}', '[\"admin\"]') WHERE metadata->>'classification' = 'confidential' AND metadata->>'allowed_users' = '[\"*\"]';")
    print("3. Reindexar documentos com nova lógica de segurança")

if __name__ == "__main__":
    fix_existing_data()
