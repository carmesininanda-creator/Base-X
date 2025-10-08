# Guia de Instalação e Uso

Este guia fornece instruções passo a passo para configurar o ambiente de desenvolvimento e começar a usar o projeto de fundo quantitativo.

## Pré-requisitos

Antes de começar, certifique-se de ter instalado em seu sistema:

*   **Python 3.8 ou superior:** O projeto foi desenvolvido e testado com Python 3.11, mas deve funcionar com versões 3.8+.
*   **pip:** O gerenciador de pacotes do Python.
*   **Git:** Para clonar o repositório e gerenciar o controle de versão.

## Instalação

### 1. Clonar o Repositório

Clone o repositório do GitHub para sua máquina local:

```bash
git clone https://github.com/carmesininanda-creator/Base-X.git
cd Base-X/quant-fund-brazil
```

### 2. Criar um Ambiente Virtual

É altamente recomendado usar um ambiente virtual para isolar as dependências do projeto:

```bash
python3 -m venv venv
```

### 3. Ativar o Ambiente Virtual

**No Linux/macOS:**

```bash
source venv/bin/activate
```

**No Windows:**

```bash
venv\Scripts\activate
```

### 4. Instalar as Dependências

Com o ambiente virtual ativado, instale todas as dependências do projeto:

```bash
pip install -r requirements.txt
```

## Uso Básico

### Executar o Exemplo de Momentum

O projeto inclui um exemplo completo de backtest da estratégia de momentum. Para executá-lo:

```bash
cd examples
python momentum_example.py
```

Este script irá:

1.  Baixar dados históricos de mercado para os últimos 2 anos.
2.  Gerar sinais de trading baseados na estratégia de momentum.
3.  Executar um backtest completo.
4.  Calcular métricas de performance.
5.  Gerar gráficos e salvar os resultados.

### Executar o Dashboard Interativo

O projeto também inclui um dashboard interativo construído com Streamlit. Para executá-lo:

```bash
cd examples
streamlit run dashboard.py
```

Isso abrirá uma interface web no seu navegador onde você pode:

*   Configurar os parâmetros da estratégia.
*   Selecionar o universo de ativos.
*   Executar backtests interativos.
*   Visualizar métricas de performance e risco em tempo real.

## Estrutura do Projeto

A estrutura do projeto é organizada da seguinte forma:

```
quant-fund-brazil/
├── config/                # Arquivos de configuração
│   └── config.yaml        # Configuração principal
├── docs/                  # Documentação
│   ├── 01_foundation_and_structure.md
│   ├── 02_philosophy_and_strategy.md
│   ├── 03_technological_infrastructure.md
│   ├── 04_system_development.md
│   ├── 05_operation_and_risk_management.md
│   ├── 06_compliance_and_regulatory.md
│   └── getting_started.md
├── examples/              # Exemplos e scripts de uso
│   ├── momentum_example.py
│   └── dashboard.py
├── src/                   # Código-fonte principal
│   ├── data/              # Módulo de dados
│   ├── strategies/        # Módulo de estratégias
│   ├── backtesting/       # Motor de backtesting
│   ├── risk/              # Gestão de risco
│   └── utils/             # Utilitários
├── .gitignore
├── README.md
└── requirements.txt
```

## Próximos Passos

Agora que você tem o projeto configurado, aqui estão algumas sugestões de próximos passos:

1.  **Explore a Documentação:** Leia os documentos na pasta `docs` para entender os conceitos fundamentais de fundos quantitativos.
2.  **Modifique os Parâmetros:** Experimente ajustar os parâmetros da estratégia de momentum no arquivo `config/config.yaml` e observe como isso afeta os resultados.
3.  **Crie Sua Própria Estratégia:** Use a classe `BaseStrategy` como base para implementar suas próprias estratégias de investimento.
4.  **Integre Novas Fontes de Dados:** Expanda o módulo `data` para incluir outras fontes de dados além do Yahoo Finance.

## Solução de Problemas

### Erro ao Baixar Dados

Se você encontrar erros ao baixar dados do Yahoo Finance, verifique:

*   Sua conexão com a internet.
*   Se os tickers estão no formato correto (ex: `PETR4.SA` para ações brasileiras).
*   Se o Yahoo Finance está acessível no momento.

### Dependências Faltando

Se você receber erros sobre módulos não encontrados, certifique-se de que:

*   O ambiente virtual está ativado.
*   Todas as dependências foram instaladas corretamente com `pip install -r requirements.txt`.

## Suporte

Para questões, sugestões ou problemas, abra uma *issue* no repositório do GitHub.
