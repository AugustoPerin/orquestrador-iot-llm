# greenhouse_simulator.py - Simulador de 30 estufas com sensores e atuadores

import random
from typing import Dict, List, Any, Optional
from dataclasses import dataclass, field
from copy import deepcopy

from greenhouse_config import (
    GREENHOUSES, CROP_TYPES, SENSORS, ACTUATORS,
    get_greenhouse_by_id, get_greenhouses_by_crop_type
)


@dataclass
class GreenhouseState:
    """Estado atual de uma estufa"""
    greenhouse_id: str
    crop_type: str
    sensors: Dict[str, float] = field(default_factory=dict)
    actuators: Dict[str, str] = field(default_factory=dict)
    
    def is_in_comfort_zone(self, sensor: str) -> bool:
        """Verifica se um sensor está na zona de conforto"""
        comfort = CROP_TYPES[self.crop_type]["comfort_ranges"].get(sensor)
        if comfort and sensor in self.sensors:
            value = self.sensors[sensor]
            return comfort["min"] <= value <= comfort["max"]
        return True
    
    def get_deviation(self, sensor: str) -> float:
        """Retorna o desvio do valor ideal (0 se dentro da faixa)"""
        comfort = CROP_TYPES[self.crop_type]["comfort_ranges"].get(sensor)
        if comfort and sensor in self.sensors:
            value = self.sensors[sensor]
            if value < comfort["min"]:
                return comfort["min"] - value
            elif value > comfort["max"]:
                return value - comfort["max"]
        return 0.0


class GreenhouseSimulator:
    """Simulador de 30 estufas com estados e validação"""
    
    def __init__(self, seed: int = None):
        """
        Inicializa o simulador.
        
        Args:
            seed: Seed para reprodutibilidade
        """
        if seed is not None:
            random.seed(seed)
        
        self.states: Dict[str, GreenhouseState] = {}
        self._initialize_states()
    
    def _initialize_states(self):
        """Inicializa estados de todas as 30 estufas"""
        for gh in GREENHOUSES:
            gh_id = gh["id"]
            crop_type = gh["crop_type"]
            comfort = CROP_TYPES[crop_type]["comfort_ranges"]
            
            sensors = {}
            for sensor_id, ranges in comfort.items():
                mid = (ranges["min"] + ranges["max"]) / 2
                variance = (ranges["max"] - ranges["min"]) / 4
                sensors[sensor_id] = round(random.gauss(mid, variance), 2)
                sensors[sensor_id] = max(ranges["min"], min(ranges["max"], sensors[sensor_id]))
            
            self.states[gh_id] = GreenhouseState(
                greenhouse_id=gh_id,
                crop_type=crop_type,
                sensors=sensors,
                actuators={act: "off" for act in ACTUATORS.keys()}
            )
    
    def get_state(self, greenhouse_id: str) -> Optional[GreenhouseState]:
        """Retorna estado de uma estufa"""
        return self.states.get(greenhouse_id)
    
    def get_all_states(self) -> Dict[str, GreenhouseState]:
        """Retorna estados de todas as estufas"""
        return self.states
    
    def generate_scenario_for_prompt(self, prompt: dict) -> dict:
        """
        Gera um cenário baseado no contexto do prompt.
        
        Args:
            prompt: Dicionário com dados do prompt
            
        Returns:
            Contexto com estados das estufas relevantes
        """
        context = deepcopy(prompt.get("context", {}))
        
        if "current_readings" in context:
            gh_id = context.get("greenhouse_id")
            if gh_id and gh_id in self.states:
                for sensor, value in context["current_readings"].items():
                    self.states[gh_id].sensors[sensor] = value
        
        if "greenhouses" in context:
            for gh_data in context["greenhouses"]:
                gh_id = gh_data.get("greenhouse_id")
                if gh_id and gh_id in self.states:
                    for sensor, value in gh_data.get("current_readings", {}).items():
                        self.states[gh_id].sensors[sensor] = value
        
        return context
    
    def apply_random_deviation(self, greenhouse_id: str, sensor: str, 
                                direction: str = "random", magnitude: float = None) -> float:
        """
        Aplica um desvio aleatório a um sensor.
        
        Args:
            greenhouse_id: ID da estufa
            sensor: ID do sensor
            direction: "up", "down", ou "random"
            magnitude: Magnitude do desvio (se None, calcula automaticamente)
            
        Returns:
            Novo valor do sensor
        """
        state = self.states.get(greenhouse_id)
        if not state or sensor not in state.sensors:
            return None
        
        comfort = CROP_TYPES[state.crop_type]["comfort_ranges"].get(sensor)
        if not comfort:
            return state.sensors[sensor]
        
        range_size = comfort["max"] - comfort["min"]
        
        if magnitude is None:
            magnitude = range_size * random.uniform(0.2, 0.5)
        
        if direction == "random":
            direction = random.choice(["up", "down"])
        
        if direction == "up":
            new_value = state.sensors[sensor] + magnitude
        else:
            new_value = state.sensors[sensor] - magnitude
        
        state.sensors[sensor] = round(new_value, 2)
        return state.sensors[sensor]
    
    def validate_action(self, greenhouse_id: str, actuator: str, action: str) -> dict:
        """
        Valida se uma ação é permitida.
        
        Args:
            greenhouse_id: ID da estufa
            actuator: ID do atuador
            action: Ação a executar
            
        Returns:
            Dict com resultado da validação
        """
        result = {
            "valid": True,
            "errors": [],
            "warnings": []
        }
        
        if greenhouse_id not in self.states:
            result["valid"] = False
            result["errors"].append(f"Estufa {greenhouse_id} não existe")
            return result
        
        if actuator not in ACTUATORS:
            result["valid"] = False
            result["errors"].append(f"Atuador {actuator} não existe")
            return result
        
        valid_actions = ACTUATORS[actuator]["actions"]
        if action not in valid_actions:
            result["valid"] = False
            result["errors"].append(
                f"Ação '{action}' não é válida para {actuator}. "
                f"Ações válidas: {valid_actions}"
            )
            return result
        
        return result
    
    def execute_action(self, greenhouse_id: str, actuator: str, action: str) -> dict:
        """
        Executa uma ação (simulada) em uma estufa.
        
        Args:
            greenhouse_id: ID da estufa
            actuator: ID do atuador
            action: Ação a executar
            
        Returns:
            Resultado da execução
        """
        validation = self.validate_action(greenhouse_id, actuator, action)
        if not validation["valid"]:
            return {
                "success": False,
                "errors": validation["errors"]
            }
        
        state = self.states[greenhouse_id]
        state.actuators[actuator] = action
        
        affected_sensor = ACTUATORS[actuator]["affects"]
        comfort = CROP_TYPES[state.crop_type]["comfort_ranges"].get(affected_sensor)
        
        if comfort and affected_sensor in state.sensors:
            current = state.sensors[affected_sensor]
            target = (comfort["min"] + comfort["max"]) / 2
            
            if action not in ["off", "stop"]:
                adjustment = (target - current) * 0.3
                state.sensors[affected_sensor] = round(current + adjustment, 2)
        
        return {
            "success": True,
            "greenhouse_id": greenhouse_id,
            "actuator": actuator,
            "action": action,
            "new_state": state.actuators[actuator]
        }
    
    def get_critical_greenhouses(self) -> List[dict]:
        """Retorna estufas com parâmetros fora da zona de conforto"""
        critical = []
        
        for gh_id, state in self.states.items():
            issues = []
            for sensor in state.sensors.keys():
                if not state.is_in_comfort_zone(sensor):
                    deviation = state.get_deviation(sensor)
                    issues.append({
                        "sensor": sensor,
                        "value": state.sensors[sensor],
                        "deviation": deviation
                    })
            
            if issues:
                critical.append({
                    "greenhouse_id": gh_id,
                    "crop_type": state.crop_type,
                    "issues": issues,
                    "severity": sum(i["deviation"] for i in issues)
                })
        
        critical.sort(key=lambda x: x["severity"], reverse=True)
        return critical


def create_test_scenario(scenario_type: str = "normal") -> Dict[str, Any]:
    """
    Cria um cenário de teste predefinido.
    
    Args:
        scenario_type: "normal", "critical", "mixed"
        
    Returns:
        Dicionário com estados das estufas
    """
    simulator = GreenhouseSimulator(seed=42)
    
    if scenario_type == "critical":
        for gh_id in ["GH001", "GH005", "GH010"]:
            simulator.apply_random_deviation(gh_id, "temperature", "up", 10.0)
            simulator.apply_random_deviation(gh_id, "soil_humidity", "down", 20.0)
    
    elif scenario_type == "mixed":
        simulator.apply_random_deviation("GH002", "temperature", "up", 8.0)
        simulator.apply_random_deviation("GH008", "soil_ph", "down", 1.5)
        simulator.apply_random_deviation("GH015", "luminosity", "down", 10000)
    
    return {
        "simulator": simulator,
        "states": {gh_id: {
            "greenhouse_id": gh_id,
            "crop_type": state.crop_type,
            "sensors": state.sensors,
            "actuators": state.actuators
        } for gh_id, state in simulator.states.items()}
    }
