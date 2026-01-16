# test_models_connection.py - Script para testar conexão com cada modelo

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from config import MODELS
from bedrock_client import BedrockClient

def test_all_models():
    """Testa conexão com cada um dos 5 modelos LLM"""
    
    client = BedrockClient()
    
    system_message = """Você é um controlador de estufas IoT. Responda em JSON com o formato:
{"error": false, "message": "sua resposta", "actions": []}"""
    
    user_message = """A estufa GH001 está com temperatura em 30°C. O que fazer?"""
    
    print("\n" + "=" * 70)
    print("TESTE DE CONEXÃO COM MODELOS AWS BEDROCK")
    print("=" * 70)
    
    results = []
    
    for model_key, model_config in MODELS.items():
        print(f"\nTestando: {model_config['name']}")
        print(f"   Model ID: {model_config['model_id']}")
        print("   Aguarde...")
        
        try:
            result = client.invoke_model(
                model_key=model_key,
                system_message=system_message,
                user_message=user_message,
                max_tokens=512,
                temperature=0.1
            )
            
            if result["success"]:
                print(f"   SUCESSO!")
                print(f"   Latência: {result['inference_latency_ms']:.2f}ms")
                print(f"   Tokens: {result['input_tokens']} in / {result['output_tokens']} out")
                print(f"   Resposta (preview): {result['response'][:200]}...")
                results.append({
                    "model": model_key,
                    "status": "success",
                    "latency_ms": result['inference_latency_ms']
                })
            else:
                print(f"   FALHA: {result.get('error', 'Erro desconhecido')}")
                results.append({
                    "model": model_key,
                    "status": "error",
                    "error": result.get('error')
                })
                
        except Exception as e:
            print(f"   EXCEÇÃO: {str(e)}")
            results.append({
                "model": model_key,
                "status": "exception",
                "error": str(e)
            })
    
    print("\n" + "=" * 70)
    print("RESUMO DOS TESTES")
    print("=" * 70)
    
    success_count = sum(1 for r in results if r["status"] == "success")
    print(f"\nModelos funcionando: {success_count}/{len(MODELS)}")
    
    for r in results:
        status_icon = "Ok" if r["status"] == "success" else "Erro"
        latency = f" ({r.get('latency_ms', 0):.0f}ms)" if r["status"] == "success" else ""
        error = f" - {r.get('error', '')[:50]}" if r["status"] != "success" else ""
        print(f"  {status_icon} {r['model']}{latency}{error}")
    
    print("\n" + "=" * 70)
    
    return results


if __name__ == "__main__":
    test_all_models()
