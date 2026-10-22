# Premissas comerciais sintéticas

- Os eventos de pesquisa e cotação são gerados por código e não representam logs reais.
- A semente aleatória da geração é 20261019.
- O valor bruto é diária da categoria multiplicada pelos dias previstos.
- O desconto é aplicado sobre o valor bruto.
- O custo de campanha é sintético e separado em mídia, benefício e operação.
- ROI = (receita líquida estimada - custo de campanha) / custo de campanha.
- Campanhas sem custo não possuem ROI.
- O efeito de desconto, upgrade e lift de conversão é uma simulação de sensibilidade, não uma previsão causal.
- A atribuição da campanha está registrada em DIM_CAMPANHA[Premissa_Atribuicao].