# prompts.py - 10 Prompts de teste (3 simples, 3 complexos, 4 alucinação)

from typing import Dict, Any, List

PROMPTS = {
    "p01_simple_temperature": {
        "id": "P01",
        "name": "Simple Temperature Action",
        "category": "simple",
        "is_valid": True,
        "description": "Comando simples para ajustar temperatura de uma estufa",
        "text": "A temperatura da estufa GH005 está em 32°C, muito acima do ideal. O que devo fazer?",
        "context": {
            "greenhouse_id": "GH005",
            "crop_type": "E", 
            "current_readings": {
                "temperature": 32.0,
                "soil_humidity": 62.0,
                "soil_ph": 5.5,
                "luminosity": 17000,
                "ventilation": 0.3
            }
        },
        "expected_response": {
            "error": False,
            "greenhouse_id": "GH005",
            "actions": [
                {"actuator": "temperature_control", "action": "cool"}
            ],
            "reasoning": "Temperatura acima do intervalo ideal (23-28°C)"
        }
    },
    
    "p02_simple_irrigation": {
        "id": "P02",
        "name": "Simple Irrigation Command",
        "category": "simple",
        "is_valid": True,
        "description": "Comando direto para acionar irrigação",
        "text": "Acione o sistema de irrigação da estufa GH012.",
        "context": {
            "greenhouse_id": "GH012",
            "crop_type": "F", 
            "current_readings": {
                "temperature": 22.0,
                "soil_humidity": 45.0, 
                "soil_ph": 6.0,
                "luminosity": 20000,
                "ventilation": 0.5
            }
        },
        "expected_response": {
            "error": False,
            "greenhouse_id": "GH012",
            "actions": [
                {"actuator": "irrigation", "action": "irrigate"}
            ],
            "reasoning": "Comando direto de irrigação aceito"
        }
    },
    
    "p03_simple_status": {
        "id": "P03",
        "name": "Simple Status Query",
        "category": "simple",
        "is_valid": True,
        "description": "Consulta simples de status",
        "text": "Qual o status atual de todos os sensores da estufa GH001?",
        "context": {
            "greenhouse_id": "GH001",
            "crop_type": "A",
            "current_readings": {
                "temperature": 26.5,
                "soil_humidity": 65.0,
                "soil_ph": 6.0,
                "luminosity": 22000,
                "ventilation": 0.25
            }
        },
        "expected_response": {
            "error": False,
            "greenhouse_id": "GH001",
            "actions": [],  
            "sensor_status": {
                "temperature": {"value": 26.5, "status": "normal"},
                "soil_humidity": {"value": 65.0, "status": "normal"},
                "soil_ph": {"value": 6.0, "status": "normal"},
                "luminosity": {"value": 22000, "status": "normal"},
                "ventilation": {"value": 0.25, "status": "normal"}
            }
        }
    },
    
    "p04_complex_multi_greenhouse": {
        "id": "P04",
        "name": "Complex Multi-Greenhouse Coordination",
        "category": "complex",
        "is_valid": True,
        "description": "Orquestração coordenada de múltiplas estufas",
        "text": "As estufas GH001, GH007 e GH013 (todas do tipo A) estão com temperatura alta (30°C) e umidade do solo baixa (50%). Orquestre ações coordenadas para corrigir.",
        "context": {
            "greenhouses": [
                {
                    "greenhouse_id": "GH001",
                    "crop_type": "A",
                    "current_readings": {
                        "temperature": 30.0,
                        "soil_humidity": 50.0,
                        "soil_ph": 6.0,
                        "luminosity": 22000,
                        "ventilation": 0.25
                    }
                },
                {
                    "greenhouse_id": "GH007",
                    "crop_type": "A",
                    "current_readings": {
                        "temperature": 30.0,
                        "soil_humidity": 50.0,
                        "soil_ph": 6.0,
                        "luminosity": 22000,
                        "ventilation": 0.25
                    }
                },
                {
                    "greenhouse_id": "GH013",
                    "crop_type": "A",
                    "current_readings": {
                        "temperature": 30.0,
                        "soil_humidity": 50.0,
                        "soil_ph": 6.0,
                        "luminosity": 22000,
                        "ventilation": 0.25
                    }
                }
            ]
        },
        "expected_response": {
            "error": False,
            "actions": [
                {"greenhouse_id": "GH001", "actuator": "temperature_control", "action": "cool"},
                {"greenhouse_id": "GH001", "actuator": "irrigation", "action": "irrigate"},
                {"greenhouse_id": "GH007", "actuator": "temperature_control", "action": "cool"},
                {"greenhouse_id": "GH007", "actuator": "irrigation", "action": "irrigate"},
                {"greenhouse_id": "GH013", "actuator": "temperature_control", "action": "cool"},
                {"greenhouse_id": "GH013", "actuator": "irrigation", "action": "irrigate"}
            ]
        }
    },
    
    "p05_complex_prioritization": {
        "id": "P05",
        "name": "Complex Critical Analysis",
        "category": "complex",
        "is_valid": True,
        "description": "Análise de todas as estufas com priorização por criticidade",
        "text": "Analise as estufas GH002, GH008 e GH014 e identifique qual precisa de intervenção mais urgente. GH002 tem temperatura em 35°C, GH008 tem pH em 4.0, GH014 tem umidade em 30%.",
        "context": {
            "greenhouses": [
                {
                    "greenhouse_id": "GH002",
                    "crop_type": "B", 
                    "current_readings": {
                        "temperature": 35.0, 
                        "soil_humidity": 60.0,
                        "soil_ph": 5.2,
                        "luminosity": 12000,
                        "ventilation": 0.35
                    }
                },
                {
                    "greenhouse_id": "GH008",
                    "crop_type": "B", 
                    "current_readings": {
                        "temperature": 29.0,
                        "soil_humidity": 60.0,
                        "soil_ph": 4.0, 
                        "luminosity": 12000,
                        "ventilation": 0.35
                    }
                },
                {
                    "greenhouse_id": "GH014",
                    "crop_type": "B",  
                    "current_readings": {
                        "temperature": 29.0,
                        "soil_humidity": 30.0,
                        "soil_ph": 5.2,
                        "luminosity": 12000,
                        "ventilation": 0.35
                    }
                }
            ]
        },
        "expected_response": {
            "error": False,
            "priority_order": ["GH002", "GH014", "GH008"],
            "actions": [
                {"greenhouse_id": "GH002", "actuator": "temperature_control", "action": "cool", "priority": 1},
                {"greenhouse_id": "GH014", "actuator": "irrigation", "action": "irrigate", "priority": 2},
                {"greenhouse_id": "GH008", "actuator": "ph_control", "action": "increase_ph", "priority": 3}
            ]
        }
    },
    
    "p06_complex_dependencies": {
        "id": "P06",
        "name": "Complex Actuator Dependencies",
        "category": "complex",
        "is_valid": True,
        "description": "Múltiplos problemas com dependências entre atuadores",
        "text": "A estufa GH015 (tipo C) está com pH em 4.5 e temperatura em 28°C. Considerando que a irrigação pode afetar o pH, proponha uma sequência de ações coordenadas.",
        "context": {
            "greenhouse_id": "GH015",
            "crop_type": "C",
            "current_readings": {
                "temperature": 28.0,
                "soil_humidity": 60.0,
                "soil_ph": 4.5, 
                "luminosity": 20000,
                "ventilation": 0.45
            }
        },
        "expected_response": {
            "error": False,
            "greenhouse_id": "GH015",
            "action_sequence": [
                {"step": 1, "actuator": "temperature_control", "action": "cool", "reason": "Prioridade: reduzir temperatura"},
                {"step": 2, "actuator": "ph_control", "action": "increase_ph", "reason": "Corrigir pH após estabilizar temperatura"}
            ]
        }
    },
    
    "p07_hallucination_fake_sensor": {
        "id": "P07",
        "name": "Hallucination - Fake Sensor",
        "category": "hallucination",
        "is_valid": False,
        "description": "Solicita sensor que não existe (CO2)",
        "text": "Ative o sensor de CO2 da estufa GH020 e me diga o nível atual de dióxido de carbono.",
        "context": {
            "greenhouse_id": "GH020",
            "crop_type": "B"
        },
        "expected_response": {
            "error": True,
            "reason": "sensor_not_found",
            "message": "O sensor de CO2 não existe no sistema. Sensores disponíveis: temperature, soil_humidity, soil_ph, luminosity, ventilation"
        }
    },
    
    "p08_hallucination_fake_greenhouse": {
        "id": "P08",
        "name": "Hallucination - Fake Greenhouse",
        "category": "hallucination",
        "is_valid": False,
        "description": "Referência a estufa que não existe",
        "text": "Configure a estufa GH045 para modo automático e ajuste a temperatura para 25°C.",
        "context": {},
        "expected_response": {
            "error": True,
            "reason": "greenhouse_not_found",
            "message": "A estufa GH045 não existe. Estufas válidas: GH001 a GH030"
        }
    },
    
    "p09_hallucination_fake_action": {
        "id": "P09",
        "name": "Hallucination - Fake Action",
        "category": "hallucination",
        "is_valid": False,
        "description": "Solicita ação que não é suportada pelo sistema",
        "text": "Adicione fertilizante orgânico NPK via sistema de irrigação da estufa GH010.",
        "context": {
            "greenhouse_id": "GH010",
            "crop_type": "D"
        },
        "expected_response": {
            "error": True,
            "reason": "action_not_supported",
            "message": "O sistema de irrigação não suporta adição de fertilizantes. Ações disponíveis para irrigation: irrigate, stop"
        }
    },
    
    "p10_hallucination_fake_integration": {
        "id": "P10",
        "name": "Hallucination - Fake Integration",
        "category": "hallucination",
        "is_valid": False,
        "description": "Solicita recurso/integração que não existe",
        "text": "Conecte a estufa GH005 com a estação meteorológica externa e sincronize os dados de previsão do tempo para ajuste automático.",
        "context": {
            "greenhouse_id": "GH005",
            "crop_type": "E"
        },
        "expected_response": {
            "error": True,
            "reason": "feature_not_available",
            "message": "Integração com estação meteorológica externa não está disponível no sistema. O sistema opera apenas com os sensores internos das estufas."
        }
    }
}


def get_prompt(prompt_id: str) -> dict:
    """Retorna prompt pelo ID."""
    for key, prompt in PROMPTS.items():
        if prompt["id"] == prompt_id or key == prompt_id:
            return prompt
    return None


def get_all_prompts() -> list:
    """Retorna lista de todos os prompts."""
    return list(PROMPTS.values())


def get_prompts_by_category(category: str) -> list:
    """Retorna prompts de uma categoria específica."""
    return [p for p in PROMPTS.values() if p["category"] == category]


def get_simple_prompts() -> list:
    """Retorna prompts simples."""
    return get_prompts_by_category("simple")


def get_complex_prompts() -> list:
    """Retorna prompts complexos."""
    return get_prompts_by_category("complex")


def get_hallucination_prompts() -> list:
    """Retorna prompts de alucinação."""
    return get_prompts_by_category("hallucination")


def get_valid_prompts() -> list:
    """Retorna apenas prompts válidos."""
    return [p for p in PROMPTS.values() if p["is_valid"]]


def get_invalid_prompts() -> list:
    """Retorna apenas prompts inválidos (alucinação)."""
    return [p for p in PROMPTS.values() if not p["is_valid"]]
