# bedrock_client.py - Cliente AWS Bedrock para inferência

import boto3
import json
import time
import random
from typing import Dict, Any, Optional
from config import MODELS, AWS_CONFIG


class BedrockClient:
    """Cliente para interagir com AWS Bedrock usando a Converse API"""
    
    def __init__(self):
        self.client = boto3.client(
            'bedrock-runtime',
            region_name=AWS_CONFIG['region'],
            aws_access_key_id=AWS_CONFIG['access_key'],
            aws_secret_access_key=AWS_CONFIG['secret_key']
        )
        self.models = MODELS
    
    def invoke_model(
        self, 
        model_key: str, 
        system_message: str, 
        user_message: str,
        max_tokens: int = 2048,
        temperature: float = 0.1
    ) -> Dict[str, Any]:
        """
        Invoca um modelo no Bedrock usando a Converse API (formato universal)
        
        Returns:
            Dict com:
            - response: resposta do modelo
            - inference_latency_ms: latência de inferência
            - input_tokens: tokens de entrada
            - output_tokens: tokens de saída
            - total_tokens: total de tokens
            - raw_response: resposta bruta
        """
        model_config = self.models.get(model_key)
        if not model_config:
            raise ValueError(f"Modelo não encontrado: {model_key}")
        
        model_id = model_config['model_id']
        
        start_time = time.perf_counter()
        
        try:
            response = self.client.converse(
                modelId=model_id,
                messages=[
                    {
                        "role": "user",
                        "content": [
                            {"text": user_message}
                        ]
                    }
                ],
                system=[
                    {"text": system_message}
                ],
                inferenceConfig={
                    "maxTokens": max_tokens,
                    "temperature": temperature,
                    "topP": 0.9
                }
            )
            
            end_time = time.perf_counter()
            inference_latency_ms = (end_time - start_time) * 1000
            
            output_message = response.get('output', {}).get('message', {})
            content_blocks = output_message.get('content', [])
            
            response_text = ""
            for block in content_blocks:
                if 'text' in block:
                    response_text += block['text']
            
            usage = response.get('usage', {})
            input_tokens = usage.get('inputTokens', 0)
            output_tokens = usage.get('outputTokens', 0)
            
            return {
                "success": True,
                "response": response_text,
                "inference_latency_ms": inference_latency_ms,
                "input_tokens": input_tokens,
                "output_tokens": output_tokens,
                "total_tokens": input_tokens + output_tokens,
                "raw_response": response,
                "model_id": model_id,
                "model_name": model_config['name'],
                "model_parameters": model_config['parameters'],
                "stop_reason": response.get('stopReason', 'unknown')
            }
            
        except Exception as e:
            end_time = time.perf_counter()
            return {
                "success": False,
                "error": str(e),
                "inference_latency_ms": (end_time - start_time) * 1000,
                "input_tokens": 0,
                "output_tokens": 0,
                "total_tokens": 0,
                "raw_response": None,
                "model_id": model_id,
                "model_name": model_config['name'],
                "model_parameters": model_config['parameters']
            }
    
    def list_available_models(self) -> list:
        """Lista modelos disponíveis configurados"""
        return [
            {
                "key": key,
                "name": config["name"],
                "model_id": config["model_id"],
                "parameters": config["parameters"]
            }
            for key, config in self.models.items()
        ]
