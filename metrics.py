# metrics.py - Sistema de métricas para avaliação dos LLMs

import json
import math
from typing import Dict, Any, Optional, List
from dataclasses import dataclass, asdict, field
from enum import Enum
from datetime import datetime


class MetricStatus(Enum):
    SUCCESS = "success"
    FAILURE = "failure"
    PARTIAL = "partial"
    ERROR = "error"


@dataclass
class ExperimentMetrics:
    """Classe para armazenar métricas de um experimento"""
    
    run_id: str
    model_key: str
    model_name: str
    model_parameters: int
    system_message_id: str
    prompt_id: str
    prompt_category: str 
    input_format: str
    run_number: int
    timestamp: str = field(default_factory=lambda: datetime.now().isoformat())
    price_per_1k_input: float = 0.0
    price_per_1k_output: float = 0.0
    pep: float = 0.0
    correctness: float = 0.0
    success: float = 0.0
    end_to_end_latency_ms: float = 0.0
    inference_latency_ms: float = 0.0
    input_tokens: int = 0
    output_tokens: int = 0
    total_tokens: int = 0
    constraint_violation: float = 0.0
    syntax_error: float = 0.0
    cost_per_task: float = 0.0
    pvo: float = 0.0
    expected_response: Dict[str, Any] = field(default_factory=dict)
    actual_response: str = ""
    parsed_response: Optional[Dict[str, Any]] = None
    error_details: Optional[str] = None
    hallucinations: List[str] = field(default_factory=list)
    status: str = "pending"
    
    def to_dict(self) -> dict:
        """Converte para dicionário serializável"""
        d = asdict(self)
        return d
    
    def calculate_cost_per_task(self):
        """
        Calcula C_task - Custo por Tarefa
        
        Fórmula: C_task = (T_in * P_in / 1000) + (T_out * P_out / 1000)
        """
        self.cost_per_task = (
            (self.input_tokens * self.price_per_1k_input / 1000) +
            (self.output_tokens * self.price_per_1k_output / 1000)
        )
        return self.cost_per_task
    
    def calculate_pep(self):
        """
        Calcula PEP - Pontuação de Eficiência de Parâmetros
        
        Fórmula: PEP = Corretude / log10(número de parâmetros)
        """
        if self.model_parameters <= 1:
            self.pep = 0.0
        else:
            self.pep = self.correctness / math.log10(self.model_parameters)
        return self.pep
    
    def calculate_pvo(self):
        """
        Calcula PVO - Pontuação de Viabilidade Operacional
        
        Fórmula: PVO = Corretude / (log10(Params em Bilhões) * (1 + C_task))
        
        Onde Params em Bilhões = model_parameters / 1e9
        """
        params_billions = self.model_parameters / 1e9
        
        if params_billions <= 0:
            self.pvo = 0.0
        else:
            log_params = math.log10(params_billions)
            if log_params <= 0:
                log_params = abs(log_params) if log_params != 0 else 0.1
            
            denominator = log_params * (1 + self.cost_per_task)
            self.pvo = self.correctness / denominator if denominator > 0 else 0.0
        
        return self.pvo
    
    def calculate_all_derived_metrics(self):
        """
        Calcula todas as métricas derivadas: C_task, PEP e PVO
        """
        self.calculate_cost_per_task()
        self.calculate_pep()
        self.calculate_pvo()
        return self


def calculate_pep(correctness: float, num_parameters: int) -> float:
    """
    Função auxiliar para calcular PEP.
    
    PEP = Corretude / log10(número de parâmetros)
    
    Args:
        correctness: Score de corretude (0.0 a 1.0)
        num_parameters: Número de parâmetros do modelo
        
    Returns:
        Valor do PEP
    """
    if num_parameters <= 1:
        return 0.0
    return correctness / math.log10(num_parameters)


class MetricsAggregator:
    """Agregador de métricas para análise estatística"""
    
    def __init__(self):
        self.results: List[ExperimentMetrics] = []
    
    def add_result(self, metrics: ExperimentMetrics):
        """Adiciona resultado ao agregador"""
        self.results.append(metrics)
    
    def get_count(self) -> int:
        """Retorna número total de resultados"""
        return len(self.results)
    
    def calculate_aggregate_metrics(self) -> dict:
        """
        Calcula as 10 métricas agregadas para todos os resultados.
        """
        if not self.results:
            return {}
        
        n = len(self.results)

        return {
            "total_experiments": n,
            "avg_pep": sum(r.pep for r in self.results) / n,
            "avg_correctness": sum(r.correctness for r in self.results) / n,
            "success_rate": sum(r.success for r in self.results) / n,
            "avg_end_to_end_latency_ms": sum(r.end_to_end_latency_ms for r in self.results) / n,
            "avg_inference_latency_ms": sum(r.inference_latency_ms for r in self.results) / n,
            "total_input_tokens": sum(r.input_tokens for r in self.results),
            "total_output_tokens": sum(r.output_tokens for r in self.results),
            "avg_input_tokens": sum(r.input_tokens for r in self.results) / n,
            "avg_output_tokens": sum(r.output_tokens for r in self.results) / n,
            "constraint_violation_rate": sum(r.constraint_violation for r in self.results) / n,
            "syntax_error_rate": sum(r.syntax_error for r in self.results) / n,
            "avg_cost_per_task": sum(r.cost_per_task for r in self.results) / n,
            "total_cost": sum(r.cost_per_task for r in self.results),
            "avg_pvo": sum(r.pvo for r in self.results) / n
        }
    
    def group_by_model(self) -> Dict[str, dict]:
        """Agrupa métricas por modelo"""
        groups = {}
        
        for r in self.results:
            if r.model_key not in groups:
                groups[r.model_key] = {
                    "model_name": r.model_name,
                    "model_parameters": r.model_parameters,
                    "results": []
                }
            groups[r.model_key]["results"].append(r)
        
        for model_key, data in groups.items():
            results = data["results"]
            n = len(results)
            groups[model_key]["metrics"] = {
                "count": n,
                "avg_pep": sum(r.pep for r in results) / n,
                "avg_correctness": sum(r.correctness for r in results) / n,
                "success_rate": sum(r.success for r in results) / n,
                "avg_inference_latency_ms": sum(r.inference_latency_ms for r in results) / n,
                "avg_output_tokens": sum(r.output_tokens for r in results) / n,
                "constraint_violation_rate": sum(r.constraint_violation for r in results) / n,
                "syntax_error_rate": sum(r.syntax_error for r in results) / n,
                "avg_cost_per_task": sum(r.cost_per_task for r in results) / n,
                "total_cost": sum(r.cost_per_task for r in results),
                "avg_pvo": sum(r.pvo for r in results) / n
            }
            del groups[model_key]["results"]
        
        return groups
    
    def group_by_format(self) -> Dict[str, dict]:
        """Agrupa métricas por formato de I/O"""
        groups = {}
        
        for r in self.results:
            if r.input_format not in groups:
                groups[r.input_format] = {"results": []}
            groups[r.input_format]["results"].append(r)
        
        for fmt, data in groups.items():
            results = data["results"]
            n = len(results)
            groups[fmt]["metrics"] = {
                "count": n,
                "avg_correctness": sum(r.correctness for r in results) / n,
                "success_rate": sum(r.success for r in results) / n,
                "syntax_error_rate": sum(r.syntax_error for r in results) / n
            }
            del groups[fmt]["results"]
        
        return groups
    
    def group_by_system_message(self) -> Dict[str, dict]:
        """Agrupa métricas por system message"""
        groups = {}
        
        for r in self.results:
            if r.system_message_id not in groups:
                groups[r.system_message_id] = {"results": []}
            groups[r.system_message_id]["results"].append(r)
        
        for sm_id, data in groups.items():
            results = data["results"]
            n = len(results)
            groups[sm_id]["metrics"] = {
                "count": n,
                "avg_correctness": sum(r.correctness for r in results) / n,
                "success_rate": sum(r.success for r in results) / n,
                "constraint_violation_rate": sum(r.constraint_violation for r in results) / n
            }
            del groups[sm_id]["results"]
        
        return groups
    
    def group_by_prompt_category(self) -> Dict[str, dict]:
        """Agrupa métricas por categoria de prompt"""
        groups = {}
        
        for r in self.results:
            if r.prompt_category not in groups:
                groups[r.prompt_category] = {"results": []}
            groups[r.prompt_category]["results"].append(r)
        
        for cat, data in groups.items():
            results = data["results"]
            n = len(results)
            groups[cat]["metrics"] = {
                "count": n,
                "avg_correctness": sum(r.correctness for r in results) / n,
                "success_rate": sum(r.success for r in results) / n,
                "hallucination_detection_rate": (
                    sum(1 for r in results if r.syntax_error == 0 and r.correctness > 0.5) / n
                    if cat == "hallucination" else None
                )
            }
            del groups[cat]["results"]
        
        return groups
    
    def export_to_json(self, filepath: str) -> str:
        """Exporta todos os resultados para JSON"""
        output = {
            "metadata": {
                "total_experiments": len(self.results),
                "export_timestamp": datetime.now().isoformat()
            },
            "aggregate_metrics": self.calculate_aggregate_metrics(),
            "by_model": self.group_by_model(),
            "by_format": self.group_by_format(),
            "by_system_message": self.group_by_system_message(),
            "by_prompt_category": self.group_by_prompt_category(),
            "detailed_results": [r.to_dict() for r in self.results]
        }
        
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(output, f, indent=2, ensure_ascii=False, default=str)
        
        return filepath
    
    def load_from_json(self, filepath: str):
        """Carrega resultados de um arquivo JSON"""
        with open(filepath, 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        self.results = []
        for r in data.get("detailed_results", []):
            metrics = ExperimentMetrics(
                run_id=r["run_id"],
                model_key=r["model_key"],
                model_name=r["model_name"],
                model_parameters=r["model_parameters"],
                system_message_id=r["system_message_id"],
                prompt_id=r["prompt_id"],
                prompt_category=r["prompt_category"],
                input_format=r["input_format"],
                run_number=r["run_number"],
                pep=r.get("pep", 0.0),
                correctness=r.get("correctness", 0.0),
                success=r.get("success", 0.0),
                end_to_end_latency_ms=r.get("end_to_end_latency_ms", 0.0),
                inference_latency_ms=r.get("inference_latency_ms", 0.0),
                input_tokens=r.get("input_tokens", 0),
                output_tokens=r.get("output_tokens", 0),
                total_tokens=r.get("total_tokens", 0),
                constraint_violation=r.get("constraint_violation", 0.0),
                syntax_error=r.get("syntax_error", 0.0),
                status=r.get("status", "unknown")
            )
            self.results.append(metrics)
