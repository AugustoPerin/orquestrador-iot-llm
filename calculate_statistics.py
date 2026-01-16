import json
import numpy as np
from scipy import stats

with open('results/greenhouse_benchmark_results_20251227_012228.json', 'r') as f:
    data = json.load(f)

print("=" * 80)
print("ESTATÍSTICAS DO BENCHMARK - greenhouse_benchmark_results_20251227_012228.json")
print("=" * 80)
print()

print("MÉTRICAS AGREGADAS GERAIS:")
print("-" * 80)
aggregate = data['aggregate_metrics']
print(f"Total de experimentos: {aggregate['total_experiments']}")
print(f"PEP médio: {aggregate['avg_pep']:.6f}")
print(f"Corretude média: {aggregate['avg_correctness']:.6f}")
print(f"Taxa de sucesso: {aggregate['success_rate']:.6f}")
print(f"Latência média (ms): {aggregate['avg_inference_latency_ms']:.2f}")
print(f"Taxa de violação de restrições: {aggregate['constraint_violation_rate']:.6f}")
print(f"Taxa de erro de sintaxe: {aggregate['syntax_error_rate']:.6f}")
print(f"Custo médio por tarefa: ${aggregate['avg_cost_per_task']:.8f}")
print(f"Custo total: ${aggregate['total_cost']:.2f}")
print()

print("ESTATÍSTICAS POR MODELO:")
print("=" * 80)
print()

models_data = []
for model_id, model_info in data['by_model'].items():
    model_name = model_info['model_name']
    metrics = model_info['metrics']
    
    models_data.append({
        'id': model_id,
        'name': model_name,
        'pep': metrics['avg_pep'],
        'correctness': metrics['avg_correctness'],
        'success_rate': metrics['success_rate'],
        'latency': metrics['avg_inference_latency_ms'],
        'cost': metrics['avg_cost_per_task'],
        'constraint_violation': metrics['constraint_violation_rate'],
        'syntax_error': metrics['syntax_error_rate'],
        'count': metrics['count']
    })
    
    print(f"Modelo: {model_name}")
    print(f"  ID: {model_id}")
    print(f"  Experimentos: {metrics['count']}")
    print(f"  PEP médio: {metrics['avg_pep']:.6f}")
    print(f"  Corretude média: {metrics['avg_correctness']:.6f}")
    print(f"  Taxa de sucesso: {metrics['success_rate']:.6f}")
    print(f"  Latência média (ms): {metrics['avg_inference_latency_ms']:.2f}")
    print(f"  Taxa de violação: {metrics['constraint_violation_rate']:.6f}")
    print(f"  Taxa de erro de sintaxe: {metrics['syntax_error_rate']:.6f}")
    print(f"  Custo médio: ${metrics['avg_cost_per_task']:.8f}")
    print()

print("=" * 80)
print("DESVIO PADRÃO E INTERVALO DE CONFIANÇA (95%) ENTRE MODELOS:")
print("=" * 80)
print()

pep_values = [m['pep'] for m in models_data]
correctness_values = [m['correctness'] for m in models_data]
success_rate_values = [m['success_rate'] for m in models_data]
latency_values = [m['latency'] for m in models_data]
cost_values = [m['cost'] for m in models_data]
constraint_violation_values = [m['constraint_violation'] for m in models_data]
syntax_error_values = [m['syntax_error'] for m in models_data]

def calculate_ci_95(values):
    n = len(values)
    mean = np.mean(values)
    std = np.std(values, ddof=1) 
    se = std / np.sqrt(n)
    
    t_critical = stats.t.ppf(0.975, n-1)
    ci_margin = t_critical * se
    
    return mean, std, se, (mean - ci_margin, mean + ci_margin)

mean, std, se, ci = calculate_ci_95(pep_values)
print(f"PEP (Preferência de Execução de Plantas):")
print(f"  Média: {mean:.6f}")
print(f"  Desvio Padrão: {std:.6f}")
print(f"  Erro Padrão: {se:.6f}")
print(f"  IC 95%: [{ci[0]:.6f}, {ci[1]:.6f}]")
print()

mean, std, se, ci = calculate_ci_95(correctness_values)
print(f"Corretude:")
print(f"  Média: {mean:.6f}")
print(f"  Desvio Padrão: {std:.6f}")
print(f"  Erro Padrão: {se:.6f}")
print(f"  IC 95%: [{ci[0]:.6f}, {ci[1]:.6f}]")
print()

mean, std, se, ci = calculate_ci_95(success_rate_values)
print(f"Taxa de Sucesso:")
print(f"  Média: {mean:.6f}")
print(f"  Desvio Padrão: {std:.6f}")
print(f"  Erro Padrão: {se:.6f}")
print(f"  IC 95%: [{ci[0]:.6f}, {ci[1]:.6f}]")
print()

mean, std, se, ci = calculate_ci_95(latency_values)
print(f"Latência de Inferência (ms):")
print(f"  Média: {mean:.2f}")
print(f"  Desvio Padrão: {std:.2f}")
print(f"  Erro Padrão: {se:.2f}")
print(f"  IC 95%: [{ci[0]:.2f}, {ci[1]:.2f}]")
print()

mean, std, se, ci = calculate_ci_95(cost_values)
print(f"Custo por Tarefa ($):")
print(f"  Média: ${mean:.8f}")
print(f"  Desvio Padrão: ${std:.8f}")
print(f"  Erro Padrão: ${se:.8f}")
print(f"  IC 95%: [${ci[0]:.8f}, ${ci[1]:.8f}]")
print()

mean, std, se, ci = calculate_ci_95(constraint_violation_values)
print(f"Taxa de Violação de Restrições:")
print(f"  Média: {mean:.6f}")
print(f"  Desvio Padrão: {std:.6f}")
print(f"  Erro Padrão: {se:.6f}")
print(f"  IC 95%: [{ci[0]:.6f}, {ci[1]:.6f}]")
print()

mean, std, se, ci = calculate_ci_95(syntax_error_values)
print(f"Taxa de Erro de Sintaxe:")
print(f"  Média: {mean:.6f}")
print(f"  Desvio Padrão: {std:.6f}")
print(f"  Erro Padrão: {se:.6f}")
print(f"  IC 95%: [{ci[0]:.6f}, {ci[1]:.6f}]")
print()

print("=" * 80)
print("RESUMO ESTATÍSTICO:")
print("=" * 80)
print()
print(f"Número de modelos analisados: {len(models_data)}")
print(f"Total de experimentos: {sum(m['count'] for m in models_data)}")
print()
print("NOTA: Os desvios padrão e intervalos de confiança acima são calculados")
print("considerando a variabilidade ENTRE os modelos, não dentro de cada modelo.")
print("=" * 80)
