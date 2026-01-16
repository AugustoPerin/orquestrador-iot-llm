# orchestration_validator.py - Validador de respostas do LLM

import json
import re
from typing import Dict, Any, List, Optional
from dataclasses import dataclass

from greenhouse_config import (
    GREENHOUSES, CROP_TYPES, SENSORS, ACTUATORS,
    get_greenhouse_by_id, get_all_greenhouse_ids, get_valid_actions_for_actuator
)
from input_formatters import OutputParser


@dataclass
class ValidationResult:
    """Resultado da validação de uma resposta"""
    parsed_response: Optional[dict]
    syntax_valid: bool
    constraints_respected: bool
    correctness_score: float
    success: bool
    errors: List[str]
    warnings: List[str]
    hallucinations: List[str]


class OrchestrationValidator:
    """Validador de respostas do LLM contra restrições do sistema"""
    
    def __init__(self):
        self.valid_greenhouse_ids = set(get_all_greenhouse_ids())
        self.valid_sensors = set(SENSORS.keys())
        self.valid_actuators = set(ACTUATORS.keys())
        self.parser = OutputParser()
    
    def validate_response(
        self, 
        response: str, 
        expected: dict, 
        prompt_is_valid: bool,
        format_type: str = "json"
    ) -> ValidationResult:
        """
        Valida a resposta do LLM.
        
        Args:
            response: Resposta bruta do LLM
            expected: Resposta esperada
            prompt_is_valid: Se o prompt era válido (não é alucinação)
            format_type: Formato esperado da resposta
            
        Returns:
            ValidationResult com métricas
        """
        errors = []
        warnings = []
        hallucinations = []
        
        parsed = self.parser.parse_json_response(response)
        
        if parsed is None:
            return ValidationResult(
                parsed_response=None,
                syntax_valid=False,
                constraints_respected=True,
                correctness_score=0.0,
                success=False,
                errors=["Não foi possível extrair JSON válido da resposta"],
                warnings=[],
                hallucinations=[]
            )
        
        syntax_valid = self._validate_syntax(parsed)
        constraint_result = self._check_constraints(parsed, prompt_is_valid)
        constraints_respected = constraint_result["respected"]
        errors.extend(constraint_result["errors"])
        hallucinations = self._check_hallucinations(parsed)
        correctness_score = self._calculate_correctness(parsed, expected, prompt_is_valid)
        success = correctness_score >= 0.5 and syntax_valid and constraints_respected
        
        return ValidationResult(
            parsed_response=parsed,
            syntax_valid=syntax_valid,
            constraints_respected=constraints_respected,
            correctness_score=correctness_score,
            success=success,
            errors=errors,
            warnings=warnings,
            hallucinations=hallucinations
        )
    
    def _validate_syntax(self, parsed: dict) -> bool:
        """Valida se a resposta tem estrutura sintática correta"""
        if "error" not in parsed:
            return False
        if "message" not in parsed and "reason" not in parsed:
            return False
        return True
    
    def _check_constraints(self, parsed: dict, prompt_is_valid: bool) -> dict:
        """Verifica se a resposta viola restrições do sistema"""
        result = {"respected": True, "errors": []}
        
        if not prompt_is_valid:
            if not parsed.get("error", False):
                result["respected"] = False
                result["errors"].append(
                    "Aceitou comando inválido (deveria ter error=True)"
                )
                return result
        
        default_gh = parsed.get("greenhouse_id")
        if isinstance(default_gh, list):
            default_gh = default_gh[0] if default_gh else None
        elif not isinstance(default_gh, str):
            default_gh = None
        
        actions = parsed.get("actions", [])
        if isinstance(actions, dict):
            actions = [actions]
        elif not isinstance(actions, list):
            actions = []
        
        for action in actions:
            if isinstance(action, dict):
                action_errors = self._validate_action(action, default_gh)
                if action_errors:
                    result["respected"] = False
                    result["errors"].extend(action_errors)
        
        action_sequence = parsed.get("action_sequence", [])
        if isinstance(action_sequence, dict):
            action_sequence = [action_sequence]
        elif not isinstance(action_sequence, list):
            action_sequence = []
        
        for step in action_sequence:
            if isinstance(step, dict):
                action_errors = self._validate_action(step, default_gh)
                if action_errors:
                    result["respected"] = False
                    result["errors"].extend(action_errors)
        
        return result
    
    def _validate_action(self, action: dict, default_greenhouse: str = None) -> List[str]:
        """Valida uma ação individual"""
        errors = []
        
        if not isinstance(action, dict):
            return errors
        
        gh_id = action.get("greenhouse_id", default_greenhouse)
        if isinstance(gh_id, list):
            gh_id = gh_id[0] if gh_id else None
        if isinstance(gh_id, str) and gh_id not in self.valid_greenhouse_ids:
            errors.append(f"Estufa inexistente: {gh_id}")
        
        actuator = action.get("actuator")
        if isinstance(actuator, str) and actuator not in self.valid_actuators:
            errors.append(f"Atuador inexistente: {actuator}")
        
        if isinstance(actuator, str) and actuator in self.valid_actuators:
            action_value = action.get("action")
            if isinstance(action_value, str):
                valid_actions = get_valid_actions_for_actuator(actuator)
                if action_value not in valid_actions:
                    errors.append(
                        f"Ação '{action_value}' inválida para {actuator}. "
                        f"Válidas: {valid_actions}"
                    )
        
        return errors
    
    def _check_hallucinations(self, parsed: dict) -> List[str]:
        """Identifica referências a recursos inexistentes (alucinações)"""
        hallucinations = []
        
        gh_id = parsed.get("greenhouse_id")
        if isinstance(gh_id, list):
            for gid in gh_id:
                if isinstance(gid, str) and gid not in self.valid_greenhouse_ids:
                    hallucinations.append(f"Estufa inexistente: {gid}")
        elif isinstance(gh_id, str) and gh_id not in self.valid_greenhouse_ids:
            hallucinations.append(f"Estufa inexistente: {gh_id}")
        
        actions = parsed.get("actions", [])
        if isinstance(actions, dict):
            actions = [actions]
        elif not isinstance(actions, list):
            actions = []
            
        for action in actions:
            if isinstance(action, dict):
                gh = action.get("greenhouse_id")
                if isinstance(gh, str) and gh not in self.valid_greenhouse_ids:
                    hallucinations.append(f"Estufa inexistente em ação: {gh}")
                
                actuator = action.get("actuator")
                if isinstance(actuator, str) and actuator not in self.valid_actuators:
                    hallucinations.append(f"Atuador inexistente: {actuator}")
        
        sensor_status = parsed.get("sensor_status", {})
        if isinstance(sensor_status, dict):
            for sensor in sensor_status.keys():
                if sensor not in self.valid_sensors:
                    hallucinations.append(f"Sensor inexistente: {sensor}")
        
        return hallucinations
    
    def _calculate_correctness(
        self, 
        parsed: dict, 
        expected: dict, 
        prompt_is_valid: bool
    ) -> float:
        """Calcula score de corretude (0.0 a 1.0)"""
        score = 0.0
        total_checks = 0
        
        total_checks += 1
        expected_error = expected.get("error", not prompt_is_valid)
        actual_error = parsed.get("error", not prompt_is_valid)
        if expected_error == actual_error:
            score += 1.0
        
        if not prompt_is_valid:
            total_checks += 1
            if parsed.get("reason") or parsed.get("message"):
                score += 1.0
            return score / total_checks
        
        expected_actions = expected.get("actions", [])
        actual_actions = parsed.get("actions", [])
        action_sequence = parsed.get("action_sequence", [])
        
        if isinstance(actual_actions, dict):
            actual_actions = [actual_actions]
        elif not isinstance(actual_actions, list):
            actual_actions = []
        
        if isinstance(action_sequence, dict):
            action_sequence = [action_sequence]
        elif not isinstance(action_sequence, list):
            action_sequence = []
        
        all_actual_actions = actual_actions + [
            {"actuator": s.get("actuator"), "action": s.get("action")} 
            for s in action_sequence if isinstance(s, dict)
        ]
        
        if expected_actions:
            for exp_action in expected_actions:
                total_checks += 1
                for act_action in all_actual_actions:
                    if isinstance(act_action, dict):
                        if (exp_action.get("actuator") == act_action.get("actuator") and
                            exp_action.get("action") == act_action.get("action")):
                            score += 1.0
                            break

                        elif exp_action.get("actuator") == act_action.get("actuator"):
                            score += 0.5
                            break
        
        if "greenhouse_id" in expected:
            total_checks += 1
            if expected.get("greenhouse_id") == parsed.get("greenhouse_id"):
                score += 1.0
        
        if "sensor_status" in expected:
            total_checks += 1
            if "sensor_status" in parsed:
                score += 1.0
        
        return score / total_checks if total_checks > 0 else 0.0
    
    def calculate_metrics(
        self, 
        validation_result: ValidationResult,
        prompt_category: str
    ) -> dict:
        """
        Calcula métricas adicionais baseadas na validação.
        
        Args:
            validation_result: Resultado da validação
            prompt_category: "simple", "complex", ou "hallucination"
            
        Returns:
            Dict com métricas calculadas
        """
        return {
            "correctness": validation_result.correctness_score,
            "success": 1.0 if validation_result.success else 0.0,
            "syntax_error": 0.0 if validation_result.syntax_valid else 1.0,
            "constraint_violation": 0.0 if validation_result.constraints_respected else 1.0,
            "hallucination_count": len(validation_result.hallucinations),
            "error_count": len(validation_result.errors),
            "prompt_category": prompt_category
        }
