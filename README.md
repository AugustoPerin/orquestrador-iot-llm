# Orquestração de dispositivos IoT usando LLMs

Sistema automatizado para avaliação de eficiência da Orquestração de dispositivos IoT em um cenário complexo de agricultura inteligente usando LLMs.

## Descrição do Experimento

### Cenário
- **30 Estufas** numeradas de GH001 a GH030
- **6 Tipos de Plantio** (A, B, C, D, E, F) - 5 estufas de cada
- **5 Sensores** por estufa: Temperatura, Umidade do Solo, pH do Solo, Luminosidade, Ventilação
- **5 Atuadores** por estufa: Controlador de Temperatura, Irrigação, Controlador de pH, Iluminação, Ventilação

### Parâmetros do Experimento
| Parâmetro | Quantidade |
|-----------|------------|
| System Messages | 5 |
| Prompts | 10 (3 simples + 3 complexos + 4 alucinação) |
| Modelos LLM | 5 |
| Formatos I/O | 5 (MarkDown, XML, YAML, JSON, TOON) |
| Runs por combinação | 10 |
| **TOTAL** | **12.500 experimentos** |

### Modelos LLM (AWS Bedrock)
1. Google - Gemma 3 (12B)
2. OpenAI - gpt-oss (20B)
3. Qwen - Qwen3 (32B)
4. Meta - Llama 4 Maverick (17B)
5. Mistral AI - Ministral 3 (14B)

### Métricas Avaliadas
1. **PEP** - Pontuação de Eficiência de Parâmetros
2. **PVO** - Pontuação de Viabilidade Operacional
2. **Corretude** - % de tarefas cumpridas corretamente
3. **Sucesso** - % de tarefas cumpridas de qualquer forma
4. **Latência Fim-a-Fim** - Tempo total da operação (ms)
5. **Latência de Inferência** - Tempo de inferência do LLM (ms)
6. **Consumo de Tokens** - Tokens de entrada e saída
7. **Taxa de Violação de Restrições** - % de violações das regras
8. **Taxa de Erro de Sintaxe** - % de respostas com formato inválido

## Instalação

```bash
cd greenhouse_llm_research
pip install -r requirements.txt
```

## Uso

### Mostrar Configuração
```bash
python main.py config
```

### Executar Avaliação
```bash
export AWS_ACCESS_KEY_ID="sua_chave_aws"
export AWS_SECRET_ACCESS_KEY="sua_secret_aws"

python main.py run
```

### Analisar Resultados
```bash
# Ver relatório no terminal
python main.py analyze results/greenhouse_benchmark_results_*.json

# Gerar relatório em arquivo
python main.py analyze results/arquivo.json --report relatorio.txt

# Gerar tabelas LaTeX
python main.py analyze results/arquivo.json --latex tabelas.tex
```

## Estrutura do Projeto

```
orquestrador-iot-llm/
├── config.py                    # Configurações gerais e modelos LLM
├── greenhouse_config.py         # Configuração das estufas e intervalos
├── system_messages.py           # 5 System Messages
├── prompts.py                   # 10 Prompts de teste
├── input_formatters.py          # Formatadores para 5 formatos I/O
├── greenhouse_simulator.py      # Simulador de 30 estufas
├── orchestration_validator.py   # Validador de respostas
├── metrics.py                   # Sistema de métricas
├── bedrock_client.py            # Cliente AWS Bedrock
├── benchmark_runner.py          # Executor do benchmark
├── results_analyzer.py          # Análise de resultados
├── main.py                      # Ponto de entrada CLI
├── requirements.txt             # Dependências
└── results/                     # Diretório de resultados
```

## Intervalos de Conforto por Tipo de Plantio

| Tipo | Temperatura (°C) | Umidade Solo (%) | pH do Solo | Luminosidade (Lux) | Ventilação (m/s) |
|------|------------------|------------------|------------|-------------------|------------------|
| A | 25 - 28 | 60 - 70 | 5.5 - 6.5 | 15000 - 30000 | 0.2 - 0.3 |
| B | 28 - 30 | 50 - 70 | 5.0 - 5.5 | 10000 - 15000 | 0.3 - 0.4 |
| C | 23 - 25 | 55 - 65 | 5.5 - 7.5 | 15000 - 25000 | 0.4 - 0.5 |
| D | 20 - 22 | 55 - 70 | 5.5 - 7.0 | 10000 - 20000 | 0.3 - 0.5 |
| E | 23 - 28 | 60 - 65 | 5.0 - 6.0 | 15000 - 20000 | 0.2 - 0.4 |
| F | 20 - 25 | 55 - 70 | 5.0 - 7.5 | 10000 - 30000 | 0.4 - 0.6 |

## Objetivo do Experimento

Validar se LLMs são bons agentes orquestradores de dispositivos IoT em cenários complexos com interação humana, medindo:
- Capacidade de interpretar comandos em linguagem natural
- Precisão nas ações geradas
- Respeito às restrições do sistema
- Detecção de comandos impossíveis (alucinações)
- Eficiência em relação ao tamanho do modelo
