# results_analyzer.py - Analisador de resultados e geração de relatórios

import json
import os
import statistics
from datetime import datetime
from typing import Dict, List, Any, Optional

from metrics import MetricsAggregator, ExperimentMetrics


class ResultsAnalyzer:
    """Analisador de resultados do benchmark"""
    
    def __init__(self, results_file: str):
        """
        Args:
            results_file: Caminho para o arquivo JSON de resultados
        """
        with open(results_file, 'r', encoding='utf-8') as f:
            self.data = json.load(f)
        
        self.metadata = self.data.get('metadata', {})
        self.aggregate_metrics = self.data.get('aggregate_metrics', {})
        self.by_model = self.data.get('by_model', {})
        self.by_format = self.data.get('by_format', {})
        self.by_system_message = self.data.get('by_system_message', {})
        self.by_prompt_category = self.data.get('by_prompt_category', {})
        self.detailed_results = self.data.get('detailed_results', [])
    
    def get_overall_summary(self) -> dict:
        """Retorna resumo geral do benchmark"""
        return {
            "total_experiments": self.metadata.get('total_experiments', 0),
            "export_timestamp": self.metadata.get('export_timestamp', ''),
            **self.aggregate_metrics
        }
    
    def get_model_ranking(self, metric: str = "avg_correctness") -> List[dict]:
        """Retorna ranking dos modelos por uma métrica específica"""
        ranking = []
        for model_key, data in self.by_model.items():
            ranking.append({
                "model_key": model_key,
                "model_name": data.get("model_name", model_key),
                "model_parameters": data.get("model_parameters", 0),
                "value": data.get("metrics", {}).get(metric, 0),
                "all_metrics": data.get("metrics", {})
            })
        
        ranking.sort(key=lambda x: x["value"], reverse=True)
        return ranking
    
    def get_format_ranking(self, metric: str = "avg_correctness") -> List[dict]:
        """Retorna ranking dos formatos por uma métrica específica"""
        ranking = []
        for fmt, data in self.by_format.items():
            ranking.append({
                "format": fmt,
                "value": data.get("metrics", {}).get(metric, 0),
                "all_metrics": data.get("metrics", {})
            })
        
        ranking.sort(key=lambda x: x["value"], reverse=True)
        return ranking
    
    def get_system_message_ranking(self, metric: str = "avg_correctness") -> List[dict]:
        """Retorna ranking dos system messages por uma métrica específica"""
        ranking = []
        for sm_id, data in self.by_system_message.items():
            ranking.append({
                "system_message_id": sm_id,
                "value": data.get("metrics", {}).get(metric, 0),
                "all_metrics": data.get("metrics", {})
            })
        
        ranking.sort(key=lambda x: x["value"], reverse=True)
        return ranking
    
    def get_best_combinations(self, top_n: int = 10) -> List[dict]:
        """Retorna as melhores combinações de parâmetros"""
        combinations = {}
        
        for result in self.detailed_results:
            key = f"{result['model_key']}_{result['system_message_id']}_{result['input_format']}"
            if key not in combinations:
                combinations[key] = {
                    "model_key": result['model_key'],
                    "model_name": result['model_name'],
                    "system_message_id": result['system_message_id'],
                    "input_format": result['input_format'],
                    "correctness_values": [],
                    "pep_values": [],
                    "success_values": []
                }
            
            combinations[key]["correctness_values"].append(result.get('correctness', 0))
            combinations[key]["pep_values"].append(result.get('pep', 0))
            combinations[key]["success_values"].append(result.get('success', 0))
        
        results = []
        for key, data in combinations.items():
            results.append({
                "combination": key,
                "model_key": data["model_key"],
                "model_name": data["model_name"],
                "system_message_id": data["system_message_id"],
                "input_format": data["input_format"],
                "avg_correctness": statistics.mean(data["correctness_values"]),
                "avg_pep": statistics.mean(data["pep_values"]),
                "success_rate": statistics.mean(data["success_values"]),
                "sample_count": len(data["correctness_values"])
            })
        
        results.sort(key=lambda x: x["avg_correctness"], reverse=True)
        return results[:top_n]
    
    def get_prompt_category_analysis(self) -> dict:
        """Análise detalhada por categoria de prompt"""
        analysis = {}
        
        for cat, data in self.by_prompt_category.items():
            metrics = data.get("metrics", {})
            analysis[cat] = {
                "count": metrics.get("count", 0),
                "avg_correctness": metrics.get("avg_correctness", 0),
                "success_rate": metrics.get("success_rate", 0),
                "hallucination_detection_rate": metrics.get("hallucination_detection_rate")
            }
        
        return analysis
    
    def get_pep_analysis(self) -> dict:
        """Análise específica do PEP (Parameter Efficiency Score)"""
        pep_by_model = {}
        
        for model_key, data in self.by_model.items():
            pep_by_model[model_key] = {
                "model_name": data.get("model_name", model_key),
                "parameters": data.get("model_parameters", 0),
                "avg_pep": data.get("metrics", {}).get("avg_pep", 0),
                "avg_correctness": data.get("metrics", {}).get("avg_correctness", 0)
            }
        
        ranked = sorted(pep_by_model.items(), key=lambda x: x[1]["avg_pep"], reverse=True)
        
        return {
            "ranking": [{"model_key": k, **v} for k, v in ranked],
            "best_pep_model": ranked[0][0] if ranked else None,
            "interpretation": "PEP = Correctness / log10(Parameters). Higher is better efficiency."
        }
    
    def generate_text_report(self, output_file: str = None) -> str:
        """Gera relatório completo em formato texto"""
        report = []
        report.append("=" * 80)
        report.append("RELATÓRIO DE BENCHMARK - ORQUESTRAÇÃO IoT DE ESTUFAS COM LLMs")
        report.append("=" * 80)
        report.append(f"Data de geração: {datetime.now().strftime('%d/%m/%Y %H:%M:%S')}")
        report.append(f"Total de experimentos: {self.metadata.get('total_experiments', 0)}")
        report.append("")
        
        report.append("-" * 80)
        report.append("MÉTRICAS AGREGADAS")
        report.append("-" * 80)
        
        metrics = self.aggregate_metrics
        report.append(f"1. PEP (Pontuação de Eficiência de Parâmetros): {metrics.get('avg_pep', 0):.4f}")
        report.append(f"2. Corretude Média: {metrics.get('avg_correctness', 0):.2%}")
        report.append(f"3. Taxa de Sucesso: {metrics.get('success_rate', 0):.2%}")
        report.append(f"4. Latência Fim-a-Fim Média: {metrics.get('avg_end_to_end_latency_ms', 0):.2f} ms")
        report.append(f"5. Latência de Inferência Média: {metrics.get('avg_inference_latency_ms', 0):.2f} ms")
        report.append(f"6. Consumo de Tokens:")
        report.append(f"   - Total Input: {metrics.get('total_input_tokens', 0):,}")
        report.append(f"   - Total Output: {metrics.get('total_output_tokens', 0):,}")
        report.append(f"   - Média Input: {metrics.get('avg_input_tokens', 0):.0f}")
        report.append(f"   - Média Output: {metrics.get('avg_output_tokens', 0):.0f}")
        report.append(f"7. Taxa de Violação de Restrições: {metrics.get('constraint_violation_rate', 0):.2%}")
        report.append(f"8. Taxa de Erro de Sintaxe: {metrics.get('syntax_error_rate', 0):.2%}")
        report.append(f"9. C_task (Custo Médio por Tarefa): ${metrics.get('avg_cost_per_task', 0):.6f}")
        report.append(f"10. PVO (Viabilidade Operacional Média): {metrics.get('avg_pvo', 0):.4f}")
        report.append(f"")
        report.append(f"CUSTO TOTAL DO EXPERIMENTO: ${metrics.get('total_cost', 0):.4f}")
        report.append("")
        
        report.append("-" * 80)
        report.append("RANKING DE MODELOS (por Corretude)")
        report.append("-" * 80)
        
        for i, model in enumerate(self.get_model_ranking(), 1):
            m = model["all_metrics"]
            report.append(f"\n{i}. {model['model_name']}")
            report.append(f"   Parâmetros: {model['model_parameters']:,}")
            report.append(f"   PEP: {m.get('avg_pep', 0):.4f}")
            report.append(f"   Corretude: {m.get('avg_correctness', 0):.2%}")
            report.append(f"   Sucesso: {m.get('success_rate', 0):.2%}")
            report.append(f"   Latência: {m.get('avg_inference_latency_ms', 0):.2f} ms")
            report.append(f"   Violações: {m.get('constraint_violation_rate', 0):.2%}")
            report.append(f"   Erros Sintaxe: {m.get('syntax_error_rate', 0):.2%}")
            report.append(f"   Custo Total: ${m.get('total_cost', 0):.4f}")
            report.append(f"   PVO: {m.get('avg_pvo', 0):.4f}")
        report.append("")
        
        report.append("-" * 80)
        report.append("RANKING DE FORMATOS I/O")
        report.append("-" * 80)
        
        for i, fmt in enumerate(self.get_format_ranking(), 1):
            m = fmt["all_metrics"]
            report.append(f"\n{i}. {fmt['format'].upper()}")
            report.append(f"   Corretude: {m.get('avg_correctness', 0):.2%}")
            report.append(f"   Sucesso: {m.get('success_rate', 0):.2%}")
            report.append(f"   Erros Sintaxe: {m.get('syntax_error_rate', 0):.2%}")
        report.append("")
        
        report.append("-" * 80)
        report.append("RANKING DE SYSTEM MESSAGES")
        report.append("-" * 80)
        
        for i, sm in enumerate(self.get_system_message_ranking(), 1):
            m = sm["all_metrics"]
            report.append(f"\n{i}. {sm['system_message_id']}")
            report.append(f"   Corretude: {m.get('avg_correctness', 0):.2%}")
            report.append(f"   Sucesso: {m.get('success_rate', 0):.2%}")
            report.append(f"   Violações: {m.get('constraint_violation_rate', 0):.2%}")
        report.append("")
        
        report.append("-" * 80)
        report.append("ANÁLISE POR CATEGORIA DE PROMPT")
        report.append("-" * 80)
        
        cat_analysis = self.get_prompt_category_analysis()
        for cat, data in cat_analysis.items():
            report.append(f"\n{cat.upper()}:")
            report.append(f"   Experimentos: {data['count']}")
            report.append(f"   Corretude: {data['avg_correctness']:.2%}")
            report.append(f"   Sucesso: {data['success_rate']:.2%}")
            if data.get('hallucination_detection_rate') is not None:
                report.append(f"   Detecção de Alucinação: {data['hallucination_detection_rate']:.2%}")
        report.append("")
        
        report.append("-" * 80)
        report.append("TOP 10 MELHORES COMBINAÇÕES")
        report.append("-" * 80)
        
        for i, combo in enumerate(self.get_best_combinations(10), 1):
            report.append(f"\n{i}. {combo['model_name']} + {combo['system_message_id']} + {combo['input_format'].upper()}")
            report.append(f"   Corretude: {combo['avg_correctness']:.2%}")
            report.append(f"   PEP: {combo['avg_pep']:.4f}")
            report.append(f"   Sucesso: {combo['success_rate']:.2%}")
        report.append("")
        
        report.append("-" * 80)
        report.append("ANÁLISE DE EFICIÊNCIA DE PARÂMETROS (PEP)")
        report.append("-" * 80)
        
        pep = self.get_pep_analysis()
        report.append(f"\n{pep['interpretation']}")
        report.append("\nRanking por eficiência:")
        for i, model in enumerate(pep["ranking"], 1):
            report.append(f"  {i}. {model['model_name']}: PEP={model['avg_pep']:.4f} (Params={model['parameters']:,})")
        report.append("")
        
        report.append("=" * 80)
        report.append("FIM DO RELATÓRIO")
        report.append("=" * 80)
        
        report_text = "\n".join(report)
        
        if output_file:
            with open(output_file, 'w', encoding='utf-8') as f:
                f.write(report_text)
            print(f"Relatório salvo em: {output_file}")
        
        return report_text
    
    def export_for_latex(self, output_file: str) -> str:
        """Exporta tabelas em formato LaTeX para artigo acadêmico"""
        latex = []
        
        latex.append("% Tabela 1: Comparação de Desempenho entre Modelos LLM")
        latex.append("\\begin{table}[htbp]")
        latex.append("\\centering")
        latex.append("\\caption{Comparação de Desempenho entre Modelos LLM como Orquestradores IoT}")
        latex.append("\\begin{tabular}{lrrrrrr}")
        latex.append("\\hline")
        latex.append("\\textbf{Modelo} & \\textbf{Params} & \\textbf{PEP} & \\textbf{Corretude} & \\textbf{Sucesso} & \\textbf{Violação} & \\textbf{Sintaxe} \\\\")
        latex.append("\\hline")
        
        for model in self.get_model_ranking():
            m = model["all_metrics"]
            params = f"{model['model_parameters'] / 1e9:.0f}B"
            latex.append(
                f"{model['model_key']} & {params} & "
                f"{m.get('avg_pep', 0):.3f} & "
                f"{m.get('avg_correctness', 0)*100:.1f}\\% & "
                f"{m.get('success_rate', 0)*100:.1f}\\% & "
                f"{m.get('constraint_violation_rate', 0)*100:.1f}\\% & "
                f"{m.get('syntax_error_rate', 0)*100:.1f}\\% \\\\"
            )
        
        latex.append("\\hline")
        latex.append("\\end{tabular}")
        latex.append("\\label{tab:model-comparison}")
        latex.append("\\end{table}")
        latex.append("")
        
        latex.append("% Tabela 2: Desempenho por Formato de I/O")
        latex.append("\\begin{table}[htbp]")
        latex.append("\\centering")
        latex.append("\\caption{Desempenho por Formato de Input/Output}")
        latex.append("\\begin{tabular}{lccc}")
        latex.append("\\hline")
        latex.append("\\textbf{Formato} & \\textbf{Corretude} & \\textbf{Sucesso} & \\textbf{Erro Sintaxe} \\\\")
        latex.append("\\hline")
        
        for fmt in self.get_format_ranking():
            m = fmt["all_metrics"]
            latex.append(
                f"{fmt['format'].upper()} & "
                f"{m.get('avg_correctness', 0)*100:.1f}\\% & "
                f"{m.get('success_rate', 0)*100:.1f}\\% & "
                f"{m.get('syntax_error_rate', 0)*100:.1f}\\% \\\\"
            )
        
        latex.append("\\hline")
        latex.append("\\end{tabular}")
        latex.append("\\label{tab:format-comparison}")
        latex.append("\\end{table}")
        latex.append("")
        
        latex.append("% Tabela 3: Análise por Categoria de Prompt")
        latex.append("\\begin{table}[htbp]")
        latex.append("\\centering")
        latex.append("\\caption{Desempenho por Categoria de Prompt}")
        latex.append("\\begin{tabular}{lccc}")
        latex.append("\\hline")
        latex.append("\\textbf{Categoria} & \\textbf{Corretude} & \\textbf{Sucesso} & \\textbf{Observação} \\\\")
        latex.append("\\hline")
        
        cat_analysis = self.get_prompt_category_analysis()
        for cat, data in cat_analysis.items():
            obs = ""
            if data.get('hallucination_detection_rate') is not None:
                obs = f"Det. Aluc.: {data['hallucination_detection_rate']*100:.1f}\\%"
            latex.append(
                f"{cat.capitalize()} & "
                f"{data['avg_correctness']*100:.1f}\\% & "
                f"{data['success_rate']*100:.1f}\\% & "
                f"{obs} \\\\"
            )
        
        latex.append("\\hline")
        latex.append("\\end{tabular}")
        latex.append("\\label{tab:prompt-category}")
        latex.append("\\end{table}")
        
        latex_content = "\n".join(latex)
        
        with open(output_file, 'w', encoding='utf-8') as f:
            f.write(latex_content)
        
        print(f"Tabelas LaTeX salvas em: {output_file}")
        return output_file


def run_analysis_cli():
    """Interface CLI para análise de resultados"""
    import argparse
    
    parser = argparse.ArgumentParser(description='Analisador de Resultados do Benchmark de Estufas')
    parser.add_argument('results_file', help='Arquivo JSON de resultados')
    parser.add_argument('--report', '-r', help='Gerar relatório texto')
    parser.add_argument('--latex', '-l', help='Gerar tabelas LaTeX')
    parser.add_argument('--summary', '-s', action='store_true', help='Mostrar apenas resumo')
    
    args = parser.parse_args()
    
    analyzer = ResultsAnalyzer(args.results_file)
    
    if args.summary:
        summary = analyzer.get_overall_summary()
        print("\nRESUMO DO BENCHMARK:")
        for key, value in summary.items():
            if isinstance(value, float):
                if 'rate' in key or 'correctness' in key or 'success' in key:
                    print(f"  {key}: {value:.2%}")
                else:
                    print(f"  {key}: {value:.4f}")
            else:
                print(f"  {key}: {value}")
    else:
        report = analyzer.generate_text_report(args.report)
        if not args.report:
            print(report)
    
    if args.latex:
        analyzer.export_for_latex(args.latex)


if __name__ == "__main__":
    run_analysis_cli()
