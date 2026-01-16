# benchmark_runner.py - Executor principal das 12.500 simulações

import json
import time
import uuid
import os
from datetime import datetime
from typing import List, Dict, Any, Callable, Optional
from itertools import product

from config import MODELS, BENCHMARK_CONFIG, IO_FORMATS
from system_messages import get_all_system_messages
from prompts import get_all_prompts
from input_formatters import InputFormatter
from bedrock_client import BedrockClient
from greenhouse_simulator import GreenhouseSimulator
from orchestration_validator import OrchestrationValidator
from metrics import ExperimentMetrics, MetricsAggregator


class BenchmarkRunner:
    """Executor de benchmark para todos os modelos, system messages, prompts e formatos"""
    
    def __init__(self, output_dir: str = None):
        """
        Args:
            output_dir: Diretório para salvar resultados
        """
        self.client = BedrockClient()
        self.formatter = InputFormatter()
        self.simulator = GreenhouseSimulator(seed=42)
        self.validator = OrchestrationValidator()
        self.aggregator = MetricsAggregator()
        
        self.models = list(MODELS.keys())
        self.system_messages = get_all_system_messages()
        self.prompts = get_all_prompts()
        self.formats = IO_FORMATS
        self.runs_per_combination = BENCHMARK_CONFIG['runs_per_combination']
        
        self.output_dir = output_dir or BENCHMARK_CONFIG.get('output_dir', 'results')
        os.makedirs(self.output_dir, exist_ok=True)
    
    def calculate_total_experiments(self) -> int:
        """Calcula número total de experimentos"""
        return (
            len(self.models) * 
            len(self.system_messages) * 
            len(self.prompts) * 
            len(self.formats) * 
            self.runs_per_combination
        )
    
    def generate_combinations(self) -> List[Dict[str, Any]]:
        """Gera todas as combinações de teste"""
        combinations = []
        
        for model_key, sm, prompt, fmt in product(
            self.models,
            self.system_messages,
            self.prompts,
            self.formats
        ):
            for run_number in range(1, self.runs_per_combination + 1):
                combinations.append({
                    "model_key": model_key,
                    "model_config": MODELS[model_key],
                    "system_message": sm,
                    "prompt": prompt,
                    "format": fmt,
                    "run_number": run_number
                })
        
        return combinations
    
    def run_single_experiment(
        self, 
        model_key: str,
        model_config: dict,
        system_message: dict,
        prompt: dict,
        input_format: str,
        run_number: int
    ) -> ExperimentMetrics:
        """Executa um único experimento"""
        
        run_id = f"{model_key}_{system_message['id']}_{prompt['id']}_{input_format}_run{run_number}_{uuid.uuid4().hex[:8]}"
        
        context = self.simulator.generate_scenario_for_prompt(prompt)
        
        formatted_input = self.formatter.format(
            format_type=input_format,
            system_message=system_message["message"],
            prompt=prompt["text"],
            context=context
        )
        
        start_time = time.perf_counter()
        
        result = self.client.invoke_model(
            model_key=model_key,
            system_message=system_message["message"],
            user_message=formatted_input
        )
        
        end_time = time.perf_counter()
        end_to_end_latency_ms = (end_time - start_time) * 1000
        
        metrics = ExperimentMetrics(
            run_id=run_id,
            model_key=model_key,
            model_name=model_config["name"],
            model_parameters=model_config["parameters"],
            system_message_id=system_message["id"],
            prompt_id=prompt["id"],
            prompt_category=prompt["category"],
            input_format=input_format,
            run_number=run_number,
            end_to_end_latency_ms=end_to_end_latency_ms,
            expected_response=prompt.get("expected_response", {}),
            price_per_1k_input=model_config.get("price_per_1k_input", 0.0),
            price_per_1k_output=model_config.get("price_per_1k_output", 0.0)
        )
        
        if result["success"]:
            validation = self.validator.validate_response(
                response=result["response"],
                expected=prompt.get("expected_response", {}),
                prompt_is_valid=prompt["is_valid"],
                format_type=input_format
            )
            
            metrics.inference_latency_ms = result["inference_latency_ms"]
            metrics.input_tokens = result["input_tokens"]
            metrics.output_tokens = result["output_tokens"]
            metrics.total_tokens = result["total_tokens"]
            metrics.actual_response = result["response"]
            metrics.parsed_response = validation.parsed_response
            
            metrics.correctness = validation.correctness_score
            metrics.success = 1.0 if validation.success else 0.0
            metrics.syntax_error = 0.0 if validation.syntax_valid else 1.0
            metrics.constraint_violation = 0.0 if validation.constraints_respected else 1.0
            metrics.hallucinations = validation.hallucinations
            metrics.error_details = "; ".join(validation.errors) if validation.errors else None
            
            metrics.calculate_all_derived_metrics()
            
            metrics.status = "success"
        else:
            metrics.inference_latency_ms = result["inference_latency_ms"]
            metrics.correctness = 0.0
            metrics.success = 0.0
            metrics.syntax_error = 1.0
            metrics.constraint_violation = 0.0
            metrics.error_details = result.get("error", "Unknown error")
            metrics.status = "error"
            metrics.pep = 0.0
        
        return metrics
    
    def run_all_experiments(
        self,
        progress_callback: Callable[[int, int, str], None] = None,
        save_intermediate: bool = True,
        checkpoint_every: int = None,
        limit: int = None
    ) -> str:
        """
        Executa todos os experimentos.
        
        Args:
            progress_callback: Função callback(current, total, message)
            save_intermediate: Salvar checkpoints intermediários
            checkpoint_every: Frequência de salvamento (default: 100)
            limit: Limitar número de experimentos (para testes)
        
        Returns:
            Caminho do arquivo JSON com resultados
        """
        combinations = self.generate_combinations()
        
        if limit:
            combinations = combinations[:limit]
        
        total = len(combinations)
        checkpoint_every = checkpoint_every or BENCHMARK_CONFIG.get('checkpoint_every', 100)
        
        print(f"\n{'='*70}")
        print(f"INICIANDO BENCHMARK - {total} EXPERIMENTOS")
        print(f"{'='*70}")
        print(f"Modelos: {len(self.models)}")
        print(f"System Messages: {len(self.system_messages)}")
        print(f"Prompts: {len(self.prompts)}")
        print(f"Formatos: {len(self.formats)}")
        print(f"Runs por combinação: {self.runs_per_combination}")
        print(f"{'='*70}\n")
        
        start_time = datetime.now()
        
        for i, combo in enumerate(combinations):
            current = i + 1
            
            status_msg = f"{combo['model_key']} | {combo['system_message']['id']} | {combo['prompt']['id']} | {combo['format']} | Run {combo['run_number']}"
            
            if progress_callback:
                progress_callback(current, total, status_msg)
            else:
                print(f"[{current}/{total}] {status_msg}")
            
            metrics = self.run_single_experiment(
                model_key=combo["model_key"],
                model_config=combo["model_config"],
                system_message=combo["system_message"],
                prompt=combo["prompt"],
                input_format=combo["format"],
                run_number=combo["run_number"]
            )
            
            self.aggregator.add_result(metrics)
            
            if save_intermediate and current % checkpoint_every == 0:
                checkpoint_file = os.path.join(
                    self.output_dir, 
                    f"checkpoint_{current}.json"
                )
                self.aggregator.export_to_json(checkpoint_file)
                print(f"  Checkpoint salvo: {checkpoint_file}")
        
        end_time = datetime.now()
        duration = end_time - start_time
        
        print(f"\n{'='*70}")
        print(f"BENCHMARK COMPLETO")
        print(f"Duração total: {duration}")
        print(f"{'='*70}\n")
        
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        output_file = os.path.join(
            self.output_dir,
            f"greenhouse_benchmark_results_{timestamp}.json"
        )
        self.aggregator.export_to_json(output_file)
        
        print(f"Resultados salvos em: {output_file}")
        
        self._print_summary()
        
        return output_file
    
    def _print_summary(self):
        """Imprime resumo dos resultados"""
        metrics = self.aggregator.calculate_aggregate_metrics()
        
        print(f"\n{'='*70}")
        print("RESUMO DOS RESULTADOS")
        print(f"{'='*70}")
        print(f"Total de Experimentos: {metrics.get('total_experiments', 0)}")
        print(f"\nMÉTRICAS PRINCIPAIS:")
        print(f"  1. PEP Médio: {metrics.get('avg_pep', 0):.4f}")
        print(f"  2. Corretude Média: {metrics.get('avg_correctness', 0):.2%}")
        print(f"  3. Taxa de Sucesso: {metrics.get('success_rate', 0):.2%}")
        print(f"  4. Latência Fim-a-Fim Média: {metrics.get('avg_end_to_end_latency_ms', 0):.2f}ms")
        print(f"  5. Latência de Inferência Média: {metrics.get('avg_inference_latency_ms', 0):.2f}ms")
        print(f"  6. Tokens Médios (Input/Output): {metrics.get('avg_input_tokens', 0):.0f} / {metrics.get('avg_output_tokens', 0):.0f}")
        print(f"  7. Taxa de Violação de Restrições: {metrics.get('constraint_violation_rate', 0):.2%}")
        print(f"  8. Taxa de Erro de Sintaxe: {metrics.get('syntax_error_rate', 0):.2%}")
        print(f"  9. Custo Médio por Tarefa (C_task): ${metrics.get('avg_cost_per_task', 0):.6f}")
        print(f"  10. PVO Médio (Viabilidade Operacional): {metrics.get('avg_pvo', 0):.4f}")
        print(f"\nCUSTO TOTAL ESTIMADO: ${metrics.get('total_cost', 0):.4f}")
        print(f"{'='*70}\n")
        
        by_model = self.aggregator.group_by_model()
        print("RESULTADOS POR MODELO:")
        for model_key, data in by_model.items():
            m = data["metrics"]
            print(f"\n  {data['model_name']}:")
            print(f"    PEP: {m['avg_pep']:.4f} | Corretude: {m['avg_correctness']:.2%} | Sucesso: {m['success_rate']:.2%}")
            print(f"    Custo: ${m['total_cost']:.4f} | PVO: {m['avg_pvo']:.4f}")
        
        by_format = self.aggregator.group_by_format()
        print("\nRESULTADOS POR FORMATO:")
        for fmt, data in by_format.items():
            m = data["metrics"]
            print(f"  {fmt.upper()}: Corretude {m['avg_correctness']:.2%} | Erro Sintaxe {m['syntax_error_rate']:.2%}")


def run_benchmark_cli():
    """Interface CLI para executar benchmark"""
    import argparse
    
    parser = argparse.ArgumentParser(description='Benchmark LLM para Orquestração IoT de Estufas')
    parser.add_argument('--limit', type=int, help='Limitar número de experimentos')
    parser.add_argument('--output', type=str, help='Diretório de saída')
    parser.add_argument('--checkpoint', type=int, default=100, help='Frequência de checkpoint')
    parser.add_argument('--no-intermediate', action='store_true', help='Não salvar checkpoints')
    
    args = parser.parse_args()
    
    runner = BenchmarkRunner(
        output_dir=args.output
    )
    
    total = runner.calculate_total_experiments()
    if args.limit:
        total = min(total, args.limit)
    
    print(f"\nBenchmark de Orquestração IoT para Estufas")
    print(f"Total de experimentos a executar: {total}")
    
    output_file = runner.run_all_experiments(
        save_intermediate=not args.no_intermediate,
        checkpoint_every=args.checkpoint,
        limit=args.limit
    )
    
    print(f"\nBenchmark completo! Resultados em: {output_file}")


if __name__ == "__main__":
    run_benchmark_cli()
