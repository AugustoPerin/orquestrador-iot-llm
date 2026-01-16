# greenhouse_config.py - Configuração das 30 estufas e intervalos de conforto

from typing import Dict, List, Any
import random

CROP_TYPES = {
    "A": {
        "name": "Tipo A",
        "comfort_ranges": {
            "temperature": {"min": 25.0, "max": 28.0, "unit": "°C"},
            "soil_humidity": {"min": 60.0, "max": 70.0, "unit": "%"},
            "soil_ph": {"min": 5.5, "max": 6.5, "unit": "pH"},
            "luminosity": {"min": 15000, "max": 30000, "unit": "lux"},
            "ventilation": {"min": 0.2, "max": 0.3, "unit": "m/s"}
        }
    },
    "B": {
        "name": "Tipo B",
        "comfort_ranges": {
            "temperature": {"min": 28.0, "max": 30.0, "unit": "°C"},
            "soil_humidity": {"min": 50.0, "max": 70.0, "unit": "%"},
            "soil_ph": {"min": 5.0, "max": 5.5, "unit": "pH"},
            "luminosity": {"min": 10000, "max": 15000, "unit": "lux"},
            "ventilation": {"min": 0.3, "max": 0.4, "unit": "m/s"}
        }
    },
    "C": {
        "name": "Tipo C",
        "comfort_ranges": {
            "temperature": {"min": 23.0, "max": 25.0, "unit": "°C"},
            "soil_humidity": {"min": 55.0, "max": 65.0, "unit": "%"},
            "soil_ph": {"min": 5.5, "max": 7.5, "unit": "pH"},
            "luminosity": {"min": 15000, "max": 25000, "unit": "lux"},
            "ventilation": {"min": 0.4, "max": 0.5, "unit": "m/s"}
        }
    },
    "D": {
        "name": "Tipo D",
        "comfort_ranges": {
            "temperature": {"min": 20.0, "max": 22.0, "unit": "°C"},
            "soil_humidity": {"min": 55.0, "max": 70.0, "unit": "%"},
            "soil_ph": {"min": 5.5, "max": 7.0, "unit": "pH"},
            "luminosity": {"min": 10000, "max": 20000, "unit": "lux"},
            "ventilation": {"min": 0.3, "max": 0.5, "unit": "m/s"}
        }
    },
    "E": {
        "name": "Tipo E",
        "comfort_ranges": {
            "temperature": {"min": 23.0, "max": 28.0, "unit": "°C"},
            "soil_humidity": {"min": 60.0, "max": 65.0, "unit": "%"},
            "soil_ph": {"min": 5.0, "max": 6.0, "unit": "pH"},
            "luminosity": {"min": 15000, "max": 20000, "unit": "lux"},
            "ventilation": {"min": 0.2, "max": 0.4, "unit": "m/s"}
        }
    },
    "F": {
        "name": "Tipo F",
        "comfort_ranges": {
            "temperature": {"min": 20.0, "max": 25.0, "unit": "°C"},
            "soil_humidity": {"min": 55.0, "max": 70.0, "unit": "%"},
            "soil_ph": {"min": 5.0, "max": 7.5, "unit": "pH"},
            "luminosity": {"min": 10000, "max": 30000, "unit": "lux"},
            "ventilation": {"min": 0.4, "max": 0.6, "unit": "m/s"}
        }
    }
}

SENSORS = {
    "temperature": {
        "name": "Sensor de Temperatura",
        "unit": "°C",
        "description": "Mede a temperatura ambiente da estufa"
    },
    "soil_humidity": {
        "name": "Sensor de Umidade do Solo",
        "unit": "%",
        "description": "Mede a umidade do solo"
    },
    "soil_ph": {
        "name": "Sensor de pH do Solo",
        "unit": "pH",
        "description": "Mede o pH do solo"
    },
    "luminosity": {
        "name": "Sensor de Luminosidade",
        "unit": "lux",
        "description": "Mede a intensidade luminosa"
    },
    "ventilation": {
        "name": "Sensor de Ventilação",
        "unit": "m/s",
        "description": "Mede a velocidade do ar"
    }
}

ACTUATORS = {
    "temperature_control": {
        "name": "Controlador de Temperatura",
        "actions": ["heat", "cool", "off"],
        "affects": "temperature",
        "description": "Aquece ou resfria a estufa"
    },
    "irrigation": {
        "name": "Sistema de Irrigação",
        "actions": ["irrigate", "stop"],
        "affects": "soil_humidity",
        "description": "Controla a irrigação do solo"
    },
    "ph_control": {
        "name": "Controlador de pH",
        "actions": ["increase_ph", "decrease_ph", "off"],
        "affects": "soil_ph",
        "description": "Ajusta o pH do solo"
    },
    "lighting": {
        "name": "Sistema de Iluminação",
        "actions": ["on", "off", "dim"],
        "affects": "luminosity",
        "description": "Controla a iluminação artificial"
    },
    "fan": {
        "name": "Sistema de Ventilação",
        "actions": ["on", "off", "low", "medium", "high"],
        "affects": "ventilation",
        "description": "Controla os ventiladores"
    }
}

def generate_greenhouses() -> List[Dict[str, Any]]:
    """
    Gera 30 estufas distribuídas entre os 6 tipos de plantio (5 de cada tipo).
    """
    greenhouses = []
    crop_type_list = list(CROP_TYPES.keys())
    
    for i in range(30):
        crop_type = crop_type_list[i % 6]
        crop_config = CROP_TYPES[crop_type]
        
        greenhouse = {
            "id": f"GH{str(i + 1).zfill(3)}",
            "crop_type": crop_type,
            "crop_name": crop_config["name"],
            "comfort_ranges": crop_config["comfort_ranges"],
            "sensors": {
                sensor_id: {
                    **sensor_info,
                    "current_value": None 
                }
                for sensor_id, sensor_info in SENSORS.items()
            },
            "actuators": {
                actuator_id: {
                    **actuator_info,
                    "current_state": "off"
                }
                for actuator_id, actuator_info in ACTUATORS.items()
            }
        }
        greenhouses.append(greenhouse)
    
    return greenhouses

GREENHOUSES = generate_greenhouses()


def get_greenhouse_by_id(greenhouse_id: str) -> Dict[str, Any]:
    """Retorna uma estufa pelo ID."""
    for gh in GREENHOUSES:
        if gh["id"] == greenhouse_id:
            return gh
    return None


def get_greenhouses_by_crop_type(crop_type: str) -> List[Dict[str, Any]]:
    """Retorna todas as estufas de um tipo de plantio."""
    return [gh for gh in GREENHOUSES if gh["crop_type"] == crop_type]


def get_all_greenhouse_ids() -> List[str]:
    """Retorna lista de todos os IDs de estufas."""
    return [gh["id"] for gh in GREENHOUSES]


def get_valid_actions_for_actuator(actuator_id: str) -> List[str]:
    """Retorna ações válidas para um atuador."""
    if actuator_id in ACTUATORS:
        return ACTUATORS[actuator_id]["actions"]
    return []
