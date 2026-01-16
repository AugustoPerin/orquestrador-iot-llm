# config.py - Configurações do sistema de pesquisa LLM para IoT em Estufas
import os

MODELS = {
    "gemma3_12b": {
        "model_id": "google.gemma-3-12b-it",
        "name": "Google - Gemma 3 (12B)",
        "provider": "google",
        "parameters": 12_000_000_000,
        "price_per_1k_input": 0.00009,
        "price_per_1k_output": 0.00029
    },
    "gpt_oss_20b": {
        "model_id": "openai.gpt-oss-20b-1:0",
        "name": "OpenAI - gpt-oss (20B)",
        "provider": "openai",
        "parameters": 20_000_000_000,
        "price_per_1k_input": 0.00007,
        "price_per_1k_output": 0.0003
    },
    "qwen3_32b": {
        "model_id": "qwen.qwen3-32b-v1:0",
        "name": "Qwen - Qwen3 (32B)",
        "provider": "qwen",
        "parameters": 32_000_000_000,
        "price_per_1k_input": 0.00015,
        "price_per_1k_output": 0.0006
    },
    "llama4_maverick_17b": {
        "model_id": "us.meta.llama4-maverick-17b-instruct-v1:0",
        "name": "Meta - Llama 4 Maverick (17B)",
        "provider": "meta",
        "parameters": 17_000_000_000,
        "price_per_1k_input": 0.00024,
        "price_per_1k_output": 0.00097
    },
    "ministral3_14b": {
        "model_id": "mistral.ministral-3-14b-instruct",
        "name": "Mistral AI - Ministral 3 (14B)",
        "provider": "mistral",
        "parameters": 14_000_000_000,
        "price_per_1k_input": 0.00020,
        "price_per_1k_output": 0.00020
    }
}

IO_FORMATS = ["markdown", "xml", "yaml", "json", "toon"]

AWS_CONFIG = {
    "region": "us-east-1",
    "access_key": os.environ.get("AWS_ACCESS_KEY_ID", "sua_chave_de_acesso_aqui"),
    "secret_key": os.environ.get("AWS_SECRET_ACCESS_KEY", "sua_chave_secreta_aqui"),
}

BENCHMARK_CONFIG = {
    "runs_per_combination": 10,
    "timeout_seconds": 120,
    "output_dir": "results",
    "checkpoint_every": 100,
    "save_intermediate": True
}