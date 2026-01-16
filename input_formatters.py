# input_formatters.py - Formatadores para os 5 formatos de I/O (MarkDown, XML, YAML, JSON, TOON)

import json
import yaml
from typing import Dict, Any, List

class InputFormatter:
    """Classe para formatar inputs nos 5 formatos suportados"""
    
    @staticmethod
    def format_markdown(system_message: str, prompt: str, context: dict) -> str:
        """Formata input em Markdown"""
        
        context_section = ""
        if "greenhouse_id" in context:
            gh = context
            context_section = f"""### Estado da Estufa {gh.get('greenhouse_id', 'N/A')}
- **Tipo de Plantio**: {gh.get('crop_type', 'N/A')}
- **Leituras Atuais**:
  - Temperatura: {gh.get('current_readings', {}).get('temperature', 'N/A')}°C
  - Umidade do Solo: {gh.get('current_readings', {}).get('soil_humidity', 'N/A')}%
  - pH do Solo: {gh.get('current_readings', {}).get('soil_ph', 'N/A')}
  - Luminosidade: {gh.get('current_readings', {}).get('luminosity', 'N/A')} lux
  - Ventilação: {gh.get('current_readings', {}).get('ventilation', 'N/A')} m/s
"""
        elif "greenhouses" in context:
            context_section = "### Estados das Estufas\n"
            for gh in context["greenhouses"]:
                readings = gh.get('current_readings', {})
                context_section += f"""
#### Estufa {gh.get('greenhouse_id', 'N/A')} (Tipo {gh.get('crop_type', 'N/A')})
- Temperatura: {readings.get('temperature', 'N/A')}°C
- Umidade do Solo: {readings.get('soil_humidity', 'N/A')}%
- pH do Solo: {readings.get('soil_ph', 'N/A')}
- Luminosidade: {readings.get('luminosity', 'N/A')} lux
- Ventilação: {readings.get('ventilation', 'N/A')} m/s
"""
        
        md = f"""# Sistema de Controle de Estufas IoT

## Contexto do Sistema
{context_section}

---

## Comando do Usuário
> {prompt}

---

## Instruções de Resposta
Responda em formato JSON válido com a seguinte estrutura:
```json
{{
  "error": boolean,
  "greenhouse_id": "string ou null",
  "actions": [
    {{"actuator": "string", "action": "string"}}
  ],
  "message": "string",
  "reasoning": "string (opcional)"
}}
```

Se houver erro, inclua:
```json
{{
  "error": true,
  "reason": "string",
  "message": "string"
}}
```
"""
        return md
    
    @staticmethod
    def format_xml(system_message: str, prompt: str, context: dict) -> str:
        """Formata input em XML"""
        
        greenhouses_xml = ""
        if "greenhouse_id" in context:
            readings = context.get('current_readings', {})
            greenhouses_xml = f"""
        <greenhouse id="{context.get('greenhouse_id', '')}" crop_type="{context.get('crop_type', '')}">
            <sensors>
                <temperature unit="celsius">{readings.get('temperature', 'N/A')}</temperature>
                <soil_humidity unit="percent">{readings.get('soil_humidity', 'N/A')}</soil_humidity>
                <soil_ph unit="pH">{readings.get('soil_ph', 'N/A')}</soil_ph>
                <luminosity unit="lux">{readings.get('luminosity', 'N/A')}</luminosity>
                <ventilation unit="m/s">{readings.get('ventilation', 'N/A')}</ventilation>
            </sensors>
        </greenhouse>"""
        elif "greenhouses" in context:
            for gh in context["greenhouses"]:
                readings = gh.get('current_readings', {})
                greenhouses_xml += f"""
        <greenhouse id="{gh.get('greenhouse_id', '')}" crop_type="{gh.get('crop_type', '')}">
            <sensors>
                <temperature unit="celsius">{readings.get('temperature', 'N/A')}</temperature>
                <soil_humidity unit="percent">{readings.get('soil_humidity', 'N/A')}</soil_humidity>
                <soil_ph unit="pH">{readings.get('soil_ph', 'N/A')}</soil_ph>
                <luminosity unit="lux">{readings.get('luminosity', 'N/A')}</luminosity>
                <ventilation unit="m/s">{readings.get('ventilation', 'N/A')}</ventilation>
            </sensors>
        </greenhouse>"""
        
        xml = f"""<?xml version="1.0" encoding="UTF-8"?>
<greenhouse_control_system>
    <current_state>
        <greenhouses>{greenhouses_xml}
        </greenhouses>
    </current_state>
    
    <user_command>
        <![CDATA[{prompt}]]>
    </user_command>
    
    <response_format>
        <instruction>Responda em JSON válido</instruction>
        <schema>
            <field name="error" type="boolean" required="true"/>
            <field name="greenhouse_id" type="string" required="false"/>
            <field name="actions" type="array" required="false">
                <item>
                    <field name="actuator" type="string"/>
                    <field name="action" type="string"/>
                </item>
            </field>
            <field name="message" type="string" required="true"/>
            <field name="reason" type="string" required="false"/>
        </schema>
    </response_format>
</greenhouse_control_system>
"""
        return xml
    
    @staticmethod
    def format_yaml(system_message: str, prompt: str, context: dict) -> str:
        """Formata input em YAML"""
        
        greenhouses_data = []
        if "greenhouse_id" in context:
            greenhouses_data.append({
                "id": context.get("greenhouse_id"),
                "crop_type": context.get("crop_type"),
                "sensors": context.get("current_readings", {})
            })
        elif "greenhouses" in context:
            for gh in context["greenhouses"]:
                greenhouses_data.append({
                    "id": gh.get("greenhouse_id"),
                    "crop_type": gh.get("crop_type"),
                    "sensors": gh.get("current_readings", {})
                })
        
        data = {
            "greenhouse_control_system": {
                "current_state": {
                    "greenhouses": greenhouses_data
                },
                "user_command": prompt,
                "response_format": {
                    "type": "json",
                    "schema": {
                        "error": "boolean (required)",
                        "greenhouse_id": "string (optional)",
                        "actions": "array of {actuator, action} (optional)",
                        "message": "string (required)",
                        "reason": "string (if error)"
                    }
                }
            }
        }
        return yaml.dump(data, default_flow_style=False, allow_unicode=True, sort_keys=False)
    
    @staticmethod
    def format_json(system_message: str, prompt: str, context: dict) -> str:
        """Formata input em JSON"""
        
        greenhouses_data = []
        if "greenhouse_id" in context:
            greenhouses_data.append({
                "id": context.get("greenhouse_id"),
                "crop_type": context.get("crop_type"),
                "sensors": context.get("current_readings", {})
            })
        elif "greenhouses" in context:
            for gh in context["greenhouses"]:
                greenhouses_data.append({
                    "id": gh.get("greenhouse_id"),
                    "crop_type": gh.get("crop_type"),
                    "sensors": gh.get("current_readings", {})
                })
        
        data = {
            "greenhouse_control_system": {
                "current_state": {
                    "greenhouses": greenhouses_data
                },
                "user_command": prompt,
                "response_format": {
                    "type": "json",
                    "required_fields": ["error", "message"],
                    "optional_fields": ["greenhouse_id", "actions", "reason", "reasoning"]
                }
            }
        }
        return json.dumps(data, indent=2, ensure_ascii=False)
    
    @staticmethod
    def format_toon(system_message: str, prompt: str, context: dict) -> str:
        """
        Formata input em TOON (formato tabular compacto)
        
        TOON Format:
        - Objetos aninhados usam indentação
        - Arrays simples: name[count]: value1,value2,...
        - Arrays de objetos: name[count]{field1,field2,...}:
            value1,value2,...
            value1,value2,...
        """
        
        greenhouses = []
        if "greenhouse_id" in context:
            readings = context.get("current_readings", {})
            greenhouses.append({
                "id": context.get("greenhouse_id", ""),
                "crop_type": context.get("crop_type", ""),
                "temperature": readings.get("temperature", ""),
                "soil_humidity": readings.get("soil_humidity", ""),
                "soil_ph": readings.get("soil_ph", ""),
                "luminosity": readings.get("luminosity", ""),
                "ventilation": readings.get("ventilation", "")
            })
        elif "greenhouses" in context:
            for gh in context["greenhouses"]:
                readings = gh.get("current_readings", {})
                greenhouses.append({
                    "id": gh.get("greenhouse_id", ""),
                    "crop_type": gh.get("crop_type", ""),
                    "temperature": readings.get("temperature", ""),
                    "soil_humidity": readings.get("soil_humidity", ""),
                    "soil_ph": readings.get("soil_ph", ""),
                    "luminosity": readings.get("luminosity", ""),
                    "ventilation": readings.get("ventilation", "")
                })
        
        gh_count = len(greenhouses)
        gh_lines = []
        for gh in greenhouses:
            gh_lines.append(f"  {gh['id']},{gh['crop_type']},{gh['temperature']},{gh['soil_humidity']},{gh['soil_ph']},{gh['luminosity']},{gh['ventilation']}")
        
        toon = f"""greenhouse_control_system
  current_state
    greenhouses[{gh_count}]{{id,crop_type,temperature,soil_humidity,soil_ph,luminosity,ventilation}}:
{chr(10).join(gh_lines)}
  user_command: {prompt}
  response_format
    type: json
    required_fields[2]: error,message
    optional_fields[4]: greenhouse_id,actions,reason,reasoning
"""
        return toon
    
    @classmethod
    def format(cls, format_type: str, system_message: str, prompt: str, context: dict) -> str:
        """Formata input no formato especificado"""
        formatters = {
            "markdown": cls.format_markdown,
            "xml": cls.format_xml,
            "yaml": cls.format_yaml,
            "json": cls.format_json,
            "toon": cls.format_toon
        }
        
        formatter = formatters.get(format_type.lower())
        if not formatter:
            raise ValueError(f"Formato não suportado: {format_type}")
        
        return formatter(system_message, prompt, context)


class OutputParser:
    """Parser para extrair respostas estruturadas dos diferentes formatos"""
    
    @staticmethod
    def parse_json_response(response: str) -> dict:
        """Extrai JSON da resposta do LLM"""
        import re
        
        try:
            return json.loads(response.strip())
        except:
            pass
        
        patterns = [
            r'```json\s*(.*?)\s*```',
            r'```\s*(.*?)\s*```',
            r'\{[^{}]*(?:\{[^{}]*\}[^{}]*)*\}'
        ]
        
        for pattern in patterns:
            matches = re.findall(pattern, response, re.DOTALL)
            for match in matches:
                try:
                    cleaned = match.strip()
                    if not cleaned.startswith('{'):
                        json_start = cleaned.find('{')
                        if json_start >= 0:
                            cleaned = cleaned[json_start:]
                    return json.loads(cleaned)
                except:
                    continue
        
        return None
    
    @staticmethod
    def validate_response_structure(parsed: dict) -> dict:
        """Valida se a resposta tem a estrutura esperada"""
        result = {
            "valid": True,
            "missing_fields": [],
            "extra_fields": []
        }
        
        required_fields = ["error", "message"]
        optional_fields = ["greenhouse_id", "actions", "reason", "reasoning", 
                          "sensor_status", "action_sequence", "priority_order"]
        
        for field in required_fields:
            if field not in parsed:
                result["valid"] = False
                result["missing_fields"].append(field)
        
        return result


def get_all_formats() -> list:
    """Retorna lista de todos os formatos suportados"""
    return ["markdown", "xml", "yaml", "json", "toon"]
