#!/usr/bin/env python3
"""
Script para verificar o schema da tabela operational_data no Supabase.

Este script consulta o Supabase para descobrir:
1. Quais colunas existem na tabela operational_data
2. Qual é o nome correto da coluna de unidade
3. Estrutura completa da tabela
"""

import sys
from pathlib import Path

# Adicionar o diretório raiz ao path para imports
backend_dir = Path(__file__).parent
sys.path.insert(0, str(backend_dir))

from app.services.supabase_service import get_supabase_client
from loguru import logger

# Configurar logger
logger.remove()
logger.add(
    sys.stderr,
    format="<green>{time:HH:mm:ss}</green> | <level>{level: <8}</level> | <level>{message}</level>",
    level="INFO",
    colorize=True
)


def check_table_schema():
    """Verifica o schema da tabela operational_data."""
    print("\n" + "=" * 80)
    print("  VERIFICANDO SCHEMA DA TABELA operational_data")
    print("=" * 80 + "\n")
    
    try:
        supabase = get_supabase_client()
        logger.info("✅ Cliente Supabase conectado")
        
        # Método 1: Tentar buscar um registro para ver as colunas disponíveis
        print("📋 Método 1: Buscando um registro de exemplo...")
        try:
            result = supabase.table("operational_data").select("*").limit(1).execute()
            
            if result.data and len(result.data) > 0:
                print("✅ Registro encontrado!")
                print("\n📊 Colunas disponíveis no registro:")
                print("-" * 80)
                for key in result.data[0].keys():
                    value = result.data[0][key]
                    value_type = type(value).__name__
                    value_preview = str(value)[:50] if value is not None else "NULL"
                    print(f"  • {key:30} | Tipo: {value_type:15} | Valor exemplo: {value_preview}")
                
                print("\n🔍 Procurando coluna de unidade...")
                unit_candidates = []
                for key in result.data[0].keys():
                    key_lower = key.lower()
                    if any(term in key_lower for term in ['unidade', 'unit', 'filial', 'codigo']):
                        unit_candidates.append(key)
                
                if unit_candidates:
                    print(f"✅ Possíveis colunas de unidade encontradas: {unit_candidates}")
                else:
                    print("⚠️  Nenhuma coluna óbvia de unidade encontrada")
                    print("   Verifique manualmente as colunas acima")
                
                print("\n📄 Registro completo (primeiro registro):")
                print("-" * 80)
                import json
                print(json.dumps(result.data[0], indent=2, ensure_ascii=False, default=str))
                
            else:
                print("⚠️  Nenhum registro encontrado na tabela")
                print("   A tabela pode estar vazia ou não existir")
                
        except Exception as e:
            logger.error(f"Erro ao buscar registro: {e}")
            print(f"\n❌ Erro: {e}")
        
        # Método 2: Tentar consultar informações do schema via SQL (se possível)
        print("\n" + "-" * 80)
        print("📋 Método 2: Tentando consultar schema via SQL...")
        print("-" * 80)
        
        # Nota: Supabase PostgREST não suporta queries SQL diretas via Python client
        # Mas podemos tentar descobrir através de tentativas de filtro
        print("⚠️  Consulta SQL direta não disponível via PostgREST")
        print("   Use o Supabase Dashboard → SQL Editor para executar:")
        print("\n   SELECT column_name, data_type, is_nullable")
        print("   FROM information_schema.columns")
        print("   WHERE table_name = 'operational_data';")
        
        # Método 3: Tentar diferentes nomes de coluna comuns
        print("\n" + "-" * 80)
        print("📋 Método 3: Testando nomes comuns de coluna de unidade...")
        print("-" * 80)
        
        common_unit_names = [
            "unidade",
            "unidade_codigo",
            "unidade_id",
            "codigo_unidade",
            "unit",
            "unit_code",
            "unit_id",
            "filial",
            "filial_codigo",
            "codigo_filial",
        ]
        
        test_unit_value = "PE-Recife"  # Valor de teste
        
        for col_name in common_unit_names:
            try:
                # Tentar filtrar por esta coluna
                test_result = supabase.table("operational_data").select("*").eq(col_name, test_unit_value).limit(1).execute()
                
                if test_result.data:
                    print(f"✅ COLUNA ENCONTRADA: '{col_name}'")
                    print(f"   Filtro funcionou com valor '{test_unit_value}'")
                    print(f"   Registros encontrados: {len(test_result.data)}")
                    return col_name
                else:
                    print(f"   ❌ '{col_name}' - Não encontrada ou sem dados")
            except Exception as e:
                error_msg = str(e)
                if "does not exist" in error_msg or "42703" in error_msg:
                    print(f"   ❌ '{col_name}' - Coluna não existe")
                else:
                    print(f"   ⚠️  '{col_name}' - Erro: {error_msg[:60]}")
        
        print("\n" + "=" * 80)
        print("  RESUMO")
        print("=" * 80)
        print("\n⚠️  Nenhuma coluna de unidade encontrada automaticamente.")
        print("\n📝 Próximos passos:")
        print("   1. Acesse o Supabase Dashboard")
        print("   2. Vá em Table Editor → operational_data")
        print("   3. Verifique manualmente as colunas disponíveis")
        print("   4. Identifique qual coluna armazena a unidade (ex: PE-Recife, BA-Salvador)")
        print("   5. Informe o nome correto da coluna para correção do código")
        
        return None
        
    except Exception as e:
        logger.error(f"Erro ao conectar ao Supabase: {e}")
        import traceback
        traceback.print_exc()
        return None


if __name__ == "__main__":
    result = check_table_schema()
    sys.exit(0 if result else 1)
