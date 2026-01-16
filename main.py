# main.py - Ponto de entrada principal do sistema de benchmark

import argparse
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from config import MODELS, IO_FORMATS, BENCHMARK_CONFIG
from system_messages import get_all_system_messages
from prompts import get_all_prompts, get_simple_prompts, get_complex_prompts, get_hallucination_prompts
from benchmark_runner import BenchmarkRunner
from results_analyzer import ResultsAnalyzer


def print_config():
    """Mostra configuração atual do experimento"""
    print("\n" + "=" * 70)
    print("CONFIGURAÇÃO DO EXPERIMENTO DE ORQUESTRAÇÃO IoT PARA ESTUFAS")
    print("=" * 70)
    
    print("\nMODELOS LLM:")
    for key, model in MODELS.items():
        print(f"  - {model['name']} ({model['parameters']:,} params)")
        print(f"    Model ID: {model['model_id']}")
    
    print(f"\nSYSTEM MESSAGES: {len(get_all_system_messages())}")
    for sm in get_all_system_messages():
        print(f"  - {sm['id']}: {sm['name']}")
    
    print(f"\nPROMPTS: {len(get_all_prompts())}")
    print(f"  - Simples: {len(get_simple_prompts())}")
    print(f"  - Complexos: {len(get_complex_prompts())}")
    print(f"  - Alucinação: {len(get_hallucination_prompts())}")
    
    print(f"\nFORMATOS I/O: {len(IO_FORMATS)}")
    for fmt in IO_FORMATS:
        print(f"  - {fmt.upper()}")
    
    print(f"\nRUNS POR COMBINAÇÃO: {BENCHMARK_CONFIG['runs_per_combination']}")
    
    total = (
        len(MODELS) * 
        len(get_all_system_messages()) * 
        len(get_all_prompts()) * 
        len(IO_FORMATS) * 
        BENCHMARK_CONFIG['runs_per_combination']
    )
    print(f"\nTOTAL DE EXPERIMENTOS: {total:,}")
    print(f"   ({len(MODELS)} modelos × {len(get_all_system_messages())} SMs × "
          f"{len(get_all_prompts())} prompts × {len(IO_FORMATS)} formatos × "
          f"{BENCHMARK_CONFIG['runs_per_combination']} runs)")
    
    print("=" * 70 + "\n")


def run_benchmark(args):
    """Executa o benchmark completo"""
    runner = BenchmarkRunner(
        output_dir=args.output
    )
    
    output_file = runner.run_all_experiments(
        save_intermediate=not args.no_checkpoint,
        checkpoint_every=args.checkpoint,
        limit=args.limit
    )
    
    return output_file


def analyze_results(args):
    """Analisa resultados existentes"""
    if not os.path.exists(args.file):
        print(f"Arquivo não encontrado: {args.file}")
        return
    
    analyzer = ResultsAnalyzer(args.file)
    
    if args.latex:
        analyzer.export_for_latex(args.latex)
    
    if args.report:
        analyzer.generate_text_report(args.report)
    else:
        print(analyzer.generate_text_report())


def main():
    parser = argparse.ArgumentParser(
        description='Sistema de Benchmark de LLMs para Orquestração IoT de Estufas',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Exemplos de uso:
  python main.py config                    # Mostra configuração
  python main.py run                       # Executa benchmark real (AWS)
  python main.py analyze results.json      # Analisa resultados
  python main.py analyze results.json --latex tables.tex  # Gera LaTeX
        """
    )
    
    subparsers = parser.add_subparsers(dest='command', help='Comandos disponíveis')
    
    config_parser = subparsers.add_parser('config', help='Mostra configuração do experimento')
    
    run_parser = subparsers.add_parser('run', help='Executa o benchmark')

    run_parser.add_argument('--limit', type=int, 
                           help='Limitar número de experimentos')
    run_parser.add_argument('--output', '-o', type=str, default='results',
                           help='Diretório de saída')
    run_parser.add_argument('--checkpoint', type=int, default=100,
                           help='Frequência de checkpoint')
    run_parser.add_argument('--no-checkpoint', action='store_true',
                           help='Não salvar checkpoints intermediários')
    
    analyze_parser = subparsers.add_parser('analyze', help='Analisa resultados')
    analyze_parser.add_argument('file', help='Arquivo JSON de resultados')
    analyze_parser.add_argument('--report', '-r', help='Salvar relatório em arquivo')
    analyze_parser.add_argument('--latex', '-l', help='Gerar tabelas LaTeX')
    
    args = parser.parse_args()
    
    if args.command == 'config':
        print_config()
    
    elif args.command == 'run':
        print_config()
        
        output_file = run_benchmark(args)
        print(f"\nBenchmark completo!")
        print(f"   Resultados salvos em: {output_file}")
    
    elif args.command == 'analyze':
        analyze_results(args)
    
    else:
        parser.print_help()


if __name__ == "__main__":
    main()
