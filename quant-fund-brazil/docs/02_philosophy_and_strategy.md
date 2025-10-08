## 2. Filosofia e Estratégia: O "Coração" Quant

A filosofia de investimento é a essência de um fundo quantitativo. Ela define a lógica e a vantagem competitiva que o fundo buscará explorar no mercado. Esta seção aborda os principais componentes que formam a filosofia e a estratégia de um fundo quant.

### Fonte de Alpha

O "alpha" representa o retorno excedente de um investimento em relação a um benchmark. A fonte de alpha é, portanto, a origem dos lucros do fundo. Algumas das fontes de alpha mais comuns em estratégias quantitativas são:

*   **Tendência (Momentum):** Baseia-se na premissa de que ativos que tiveram um bom desempenho no passado recente continuarão a ter um bom desempenho no futuro próximo. A estratégia consiste em comprar ativos com forte tendência de alta e vender ativos com tendência de baixa.
*   **Reversão à Média:** Opera com base na ideia de que os preços dos ativos tendem a retornar à sua média histórica. A estratégia envolve a compra de ativos que estão sendo negociados abaixo de sua média e a venda de ativos que estão sendo negociados acima.
*   **Arbitragem Estatística:** Explora discrepâncias de preço entre ativos correlacionados. Um exemplo clássico é o *pairs trading*, onde se compra uma ação e se vende outra de um par que historicamente se move em conjunto.
*   **Fatores (Smart Beta):** Estratégias que se baseiam em fatores de mercado bem documentados, como:
    *   **Valor:** Comprar ações que estão "baratas" em relação aos seus fundamentos.
    *   **Qualidade:** Investir em empresas com balanços sólidos e alta lucratividade.
    *   **Baixa Volatilidade:** Montar uma carteira de ações com baixa volatilidade histórica.
*   **Microestrutura de Mercado:** Explora ineficiências de curtíssimo prazo no livro de ofertas (*order book*). Essas estratégias são geralmente de alta frequência (HFT) e exigem uma infraestrutura tecnológica avançada.

### Horizonte Temporal

O horizonte temporal da estratégia define o período médio em que as posições são mantidas:

| Horizonte | Período | Complexidade | Infraestrutura |
| :--- | :--- | :--- | :--- |
| **Alta Frequência (HFT)** | Segundos ou milissegundos | Muito Alta | Colossal |
| **Médio Prazo (Swing)** | Dias ou semanas | Média | Acessível |
| **Longo Prazo** | Meses | Baixa | Simples |

Para um fundo iniciante, as estratégias de **médio prazo** são as mais acessíveis, pois não exigem a infraestrutura de baixa latência do HFT.

### Universo de Ativos

O universo de ativos define em quais mercados e instrumentos financeiros o fundo irá operar. As opções mais comuns no mercado brasileiro são:

*   **Ações da B3:** Incluindo os principais índices como Ibovespa (IBOV) e Small Caps (SMLL).
*   **Futuros:** Contratos futuros de índice (IND), dólar (DOL) e juros (DI).
*   **Opções:** Derivativos que dão o direito de comprar ou vender um ativo a um preço pré-determinado.
*   **ETFs (Exchange Traded Funds):** Fundos de índice negociados em bolsa.

### Exemplo Prático: Estratégia de Momentum em Ações

Para ilustrar os conceitos, vamos esboçar uma estratégia simples de momentum:

*   **Hipótese:** Ações que performaram bem nos últimos 3 meses tendem a continuar performando bem no próximo mês.
*   **Universo:** Ações componentes do índice Ibovespa.
*   **Sinal:** Rankear as ações do Ibovespa pelo seu retorno dos últimos 63 dias úteis (aproximadamente 3 meses).
*   **Regra de Execução:** No primeiro dia útil de cada mês, montar uma carteira comprando as 5 ações com maior retorno (top 5) e vendendo a descoberto as 5 ações com menor retorno (bottom 5). Manter a posição por um mês e rebalancear no início do mês seguinte.

Esta é uma estratégia *long-short*, que busca lucrar tanto com a alta das ações "vencedoras" quanto com a queda das "perdedoras", ao mesmo tempo em que neutraliza parte do risco de mercado.

