#!/usr/bin/env python3
"""
Script de teste para VisualizationService via terminal.

Este script testa a geração de gráficos diretamente,
mostrando logs detalhados e validando a estrutura de dados.

Uso:
    python test_visualization.py
    python test_visualization.py --action alertas
    python test_visualization.py --action status-recife --unit PE-Recife
"""

import asyncio
import json
import sys
import argparse
from pathlib import Path
from typing import Optional

# Adicionar o diretório raiz ao path para imports
backend_dir = Path(__file__).parent
sys.path.insert(0, str(backend_dir))

from app.services.visualization_service import VisualizationService
from loguru import logger

# Configurar logger para output colorido e detalhado
logger.remove()  # Remover handler padrão
logger.add(
    sys.stderr,
    format="<green>{time:YYYY-MM-DD HH:mm:ss}</green> | <level>{level: <8}</level> | <cyan>{name}</cyan>:<cyan>{function}</cyan>:<cyan>{line}</cyan> - <level>{message}</level>",
    level="DEBUG",
    colorize=True
)


def print_section(title: str):
    """Imprime um separador visual."""
    print("\n" + "=" * 80)
    print(f"  {title}")
    print("=" * 80 + "\n")


def print_result(action_id: str, result: Optional[dict], success: bool):
    """Imprime resultado formatado."""
    print_section(f"RESULTADO: {action_id.upper()}")
    
    if not success:
        print("❌ FALHA: Não foi possível gerar gráfico")
        return
    
    if result is None:
        print("❌ FALHA: Resultado é None")
        return
    
    # Informações básicas
    print(f"✅ Tipo: {result.get('type', 'N/A')}")
    print(f"📊 Título: {result.get('title', 'N/A')}")
    print(f"📝 Subtítulo: {result.get('subtitle', 'N/A')}")
    
    # Metadata
    metadata = result.get('metadata', {})
    print(f"\n📋 Metadata:")
    print(f"   - Período: {metadata.get('period', 'N/A')}")
    print(f"   - Unidade: {metadata.get('unit', 'N/A')}")
    print(f"   - Vazio: {metadata.get('empty', False)}")
    print(f"   - Última atualização: {metadata.get('last_updated', 'N/A')}")
    
    if metadata.get('empty'):
        print(f"\n⚠️  AVISO: Gráfico está vazio!")
        print(f"   Mensagem: {metadata.get('message', 'N/A')}")
        
        failed_metrics = metadata.get('failed_metrics', [])
        if failed_metrics:
            print(f"\n   Métricas com falha ({len(failed_metrics)}):")
            for fm in failed_metrics[:5]:
                print(f"     - {fm.get('metric', 'N/A')}: {fm.get('error', 'N/A')}")
    
    # Dados do gráfico
    data = result.get('data', {})
    labels = data.get('labels', [])
    datasets = data.get('datasets', [])
    
    print(f"\n📈 Dados do Gráfico:")
    print(f"   - Labels: {len(labels)}")
    if labels:
        print(f"     {labels}")
    
    print(f"   - Datasets: {len(datasets)}")
    for i, dataset in enumerate(datasets):
        print(f"     Dataset {i+1}: {dataset.get('label', 'N/A')}")
        print(f"       - Valores: {dataset.get('data', [])}")
        print(f"       - Tipo: {dataset.get('type', 'bar')}")
    
    # Métricas encontradas (se disponível)
    if 'metrics_found' in metadata:
        print(f"\n📊 Métricas:")
        print(f"   - Encontradas: {metadata.get('metrics_found', 0)}/{metadata.get('metrics_total', 0)}")
    
    # Flag de dados mockados
    if metadata.get('is_mock_data'):
        print(f"\n⚠️  AVISO: Dados MOCKADOS (não são dados reais)")


async def test_alertas(service: VisualizationService):
    """Testa geração de gráfico de alertas."""
    print_section("TESTE: Gráfico de Alertas")
    
    try:
        result = await service.generate_chart_data(
            action_id="alertas",
            period="today"
        )
        
        print_result("alertas", result, result is not None)
        return result is not None
        
    except Exception as e:
        logger.error(f"Erro ao testar alertas: {e}")
        import traceback
        traceback.print_exc()
        return False


async def test_status(service: VisualizationService, unit: str, action_id: str):
    """Testa geração de gráfico de status operacional."""
    print_section(f"TESTE: Status Operacional - {unit}")
    
    try:
        result = await service.generate_chart_data(
            action_id=action_id,
            period="today",
            unit=unit
        )
        
        print_result(action_id, result, result is not None)
        return result is not None
        
    except Exception as e:
        logger.error(f"Erro ao testar status {unit}: {e}")
        import traceback
        traceback.print_exc()
        return False


async def test_all(service: VisualizationService):
    """Testa todos os gráficos."""
    print_section("TESTE COMPLETO: Todos os Gráficos")
    
    results = {
        "alertas": False,
        "status-recife": False,
        "status-salvador": False,
    }
    
    # Testar alertas
    results["alertas"] = await test_alertas(service)
    
    # Testar status Recife
    results["status-recife"] = await test_status(
        service, 
        unit="PE-Recife", 
        action_id="status-recife"
    )
    
    # Testar status Salvador
    results["status-salvador"] = await test_status(
        service, 
        unit="BA-Salvador", 
        action_id="status-salvador"
    )
    
    # Resumo final
    print_section("RESUMO DOS TESTES")
    
    total = len(results)
    passed = sum(1 for v in results.values() if v)
    
    print(f"✅ Passou: {passed}/{total}")
    print(f"❌ Falhou: {total - passed}/{total}")
    
    print("\nDetalhes:")
    for action_id, success in results.items():
        status = "✅" if success else "❌"
        print(f"  {status} {action_id}")
    
    return all(results.values())


async def main():
    """Função principal."""
    parser = argparse.ArgumentParser(
        description="Testa VisualizationService via terminal"
    )
    parser.add_argument(
        "--action",
        choices=["alertas", "status-recife", "status-salvador", "all"],
        default="all",
        help="Ação a testar (padrão: all)"
    )
    parser.add_argument(
        "--unit",
        help="Unidade específica (ex: PE-Recife, BA-Salvador)"
    )
    parser.add_argument(
        "--period",
        default="today",
        choices=["today", "this_week", "this_month", "this_year"],
        help="Período para buscar dados (padrão: today)"
    )
    parser.add_argument(
        "--json",
        action="store_true",
        help="Saída em formato JSON"
    )
    
    args = parser.parse_args()
    
    print_section("INICIALIZANDO TESTES")
    print(f"Ação: {args.action}")
    print(f"Período: {args.period}")
    if args.unit:
        print(f"Unidade: {args.unit}")
    
    # Criar serviço
    try:
        service = VisualizationService()
        print("✅ VisualizationService inicializado\n")
    except Exception as e:
        logger.error(f"Erro ao inicializar VisualizationService: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
    
    # Executar testes
    try:
        if args.action == "all":
            success = await test_all(service)
        elif args.action == "alertas":
            result = await service.generate_chart_data(
                action_id="alertas",
                period=args.period
            )
            if args.json:
                print(json.dumps(result, indent=2, ensure_ascii=False))
            else:
                print_result("alertas", result, result is not None)
            success = result is not None
        elif args.action in ["status-recife", "status-salvador"]:
            unit = args.unit or ("PE-Recife" if args.action == "status-recife" else "BA-Salvador")
            result = await service.generate_chart_data(
                action_id=args.action,
                period=args.period,
                unit=unit
            )
            if args.json:
                print(json.dumps(result, indent=2, ensure_ascii=False))
            else:
                print_result(args.action, result, result is not None)
            success = result is not None
        else:
            print(f"❌ Ação desconhecida: {args.action}")
            success = False
        
        # Exit code
        sys.exit(0 if success else 1)
        
    except KeyboardInterrupt:
        print("\n\n⚠️  Teste interrompido pelo usuário")
        sys.exit(130)
    except Exception as e:
        logger.error(f"Erro durante execução dos testes: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    asyncio.run(main())
