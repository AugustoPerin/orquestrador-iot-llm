# Orquestrador IoT LLM - Simulador de Estufa
Título do Artigo: Orquestração de dispositivos IoT em cenários complexos com interação humana baseada em LLMs

Resumo do Artigo:
O uso de LLMs na orquestração de dispositivos IoT oferece uma alta flexibilidade semântica para a interpretação de comandos, mas sua natureza probabilística impõe desafios à segurança operacional. A possibilidade de alucinações em sistemas de atuação física exige estratégias de mitigação que vão além da capacidade nativa do modelo. Para mitigar esses riscos, propõe-se uma arquitetura híbrida que combina a capacidade generativa das LLMs com uma camada de validação determinística focada em restrições de segurança física. A metodologia avaliou 1.250 cenários únicos de agricultura inteligente, sendo 12.500 execuções no total, atingindo 74,34% de sucesso global. Os resultados indicam que a segurança não é intrínseca ao modelo, mas dependente da engenharia de prompt: instruções técnicas reduziram a taxa de violação de 41,88% para 1,80%. Adicionalmente, métricas de eficiência evidenciaram a compensação entre corretude e custo operacional. E por fim, que o formato XML supera o JSON na injeção de contexto para uma orquestração segura.

# Estrutura do Repositório

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
├── test_models_connection.py    # Teste de conexão
└── README.md                    # Documentação do projeto
```

# Selos Considerados

Os selos considerados são: Artefatos Disponíveis (SeloD), Funcionais (SeloF), Sustentáveis (SeloS) e Experimentos Reprodutíveis (SeloR).

# Informações básicas

O projeto configura um cenário de agricultura inteligente usando 30 estufas (GH001 a GH030) e 6 tipos de plantio, avaliando a orquestração IoT com diferentes modelos LLM via AWS Bedrock (Gemma 3, OpenAI, Qwen3, Llama 4, Ministral 3) e coletando latência, assertividade de endpoints e estruturação base para o throughput de 12.500 experimentos.

- **Requisitos de Sistema**: CPU 2 cores 3.00 GHz, 8 Gb de Memória RAM, 4 Gb de espaço livre no armazenamento.
- **Linguagem**: Python 3.11

# Dependências

As dependências Python para a execução do artefato de software estão contidas no arquivo `requirements.txt`:
- `boto3>=1.28.0`
- `pyyaml>=6.0`
- `python-dateutil>=2.8.2`

Além destas bibliotecas, para reproduzir os experimentos de forma fiel é necessário possuir uma conta na **AWS (Amazon Web Services)** e ativar explicitamente os Modelos Basais citados através do console do Amazon Bedrock.

# Preocupações com segurança

O sistema executa chamadas de API externas para o serviço na nuvem (AWS Bedrock). Então para não haver risco é recomendado não submeter chaves em repositórios abertos. Recomenda-se gerar credenciais da AWS restritas usando políticas estritas no AWS IAM com acesso apenas de Invocação de Modelos ao escopo de Bedrock, mitigando encargos financeiros. 

# Instalação

Abra o prompt de comando ou terminal do ambiente e acesse o diretório local do projeto extraído:

```bash
# Navegue até a pasta do projeto (caso não esteja lá ainda)
cd orquestrador-iot-llm

# Crie um ambiente virtual (recomendado para isolar as dependências)
python -m venv venv

# Ative o ambiente virtual
source venv/bin/activate

# Instale os requerimentos do pip
pip install -r requirements.txt
```

# Teste mínimo

Para garantir que a comunicação do Python está correta e a CLI carrega adequadamente sem iniciar todo o pipeline de experimento pesado:

1. Execute a configuração no terminal do módulo principal:
```bash
python main.py config
```
O teste mínimo é útil para observar algumas funcionalidades do artefato e mostrar os arquivos de sistema em uso, além da renderização em tela dos modelos listados.
Isso valida que não há erro de sintaxe nos scripts.

2. Identificação de Problemas durante o Processo:
```bash
python test_models_connection.py
```
Isso validará as suas chaves da AWS informadas no próximo passo.

# Experimentos

A configuração base em `config.py` e `benchmark_runner.py` planeja a execução de 5 Formatos I/O, 5 System Messages, 10 Prompts e 5 Modelos de LLM (totalizando os 12.500 ensaios/experimentos originais). 

Antes de prosseguir, certifique configurar suas credenciais. No Linux/Mac:
```bash
export AWS_ACCESS_KEY_ID="sua_chave_aws_aqui"
export AWS_SECRET_ACCESS_KEY="sua_secret_aws_aqui"
```
No Windows:
```cmd
set AWS_ACCESS_KEY_ID="sua_chave_aws_aqui"
set AWS_SECRET_ACCESS_KEY="sua_secret_aws_aqui"
```

## Reivindicações #1:
- **Objetivo**: Rodar o fluxo principal validando a execução dos prompts num ciclo que transita entre estufas com e sem falhas induzidas.
- **Comandos a serem executados**:
  ```bash
  python main.py run
  ```
- **Tempo esperado**: Estima-se 8 horas usando conexões residenciais.
- **Resultado esperado**: Como saída no diretório respectivo prever a criação de um ficheiro JSON denso agrupando toda latência de inferência em `results/greenhouse_benchmark_results_[TIMESTAMP].json`.

## Reivindicações #2:
- **Objetivo**: Extrair a latência do endpoint, PEP (Pontuação de Eficiência de Parâmetros), PVO e formatá-los. Permitindo revisores confirmar os % e os resumos contidos no artigo publicado.
- **Comandos a serem executados**:
  ```bash
  # Ver relatório diretamente no terminal
  python main.py analyze results/greenhouse_benchmark_results_[TIMESTAMP].json

  # Gerar formatações de tabela em relatório
  python main.py analyze results/greenhouse_benchmark_results_[TIMESTAMP].json --report relatorio.txt

  # Gerar tabelas LaTeX prontas pro artigo científico
  python main.py analyze results/greenhouse_benchmark_results_[TIMESTAMP].json --latex tabelas.tex
  ```
- **Resultado esperado**: Impressão dos valores de benchmark extraídos detalhando Taxa de Erro de Sintaxe, Consumo de Tokens e Corretude, validando as asserções da pesquisa base.

# LICENSE

Este projeto está licenciado sob os termos da licença MIT. Consulte o arquivo LICENSE para mais detalhes.

