# Dicionário de métricas comerciais

## Conversão Cotação-Reserva

- Definição: jornadas com evento RESERVA dividido por jornadas com evento COTACAO.
- Fórmula: Reservas / Cotações.
- Granularidade: jornada, com filtros de período, canal, campanha, filial e categoria.
- Fonte: FAT_FUNIL_EVENTO.
- Tipo: sintético/demonstrativo.
- Responsável: Analytics Comercial.

## Ocupação prevista

- Definição: dias comprometidos por reservas divididos pelos dias teóricos disponíveis da frota.
- Granularidade: veículo, filial, categoria e período.
- Fonte: RESERVA, VEICULO e MODELO.
- Cuidados: excluir sobreposições e explicitar a janela de análise.

## Receita líquida estimada

- Definição: valor bruto estimado menos descontos sintéticos.
- Fonte: FATO_FUNIL_EVENTO.
- Limitação: não substitui faturamento contábil.

## ROI de campanha

- Definição: (receita líquida atribuída menos custo total da campanha) dividido pelo custo total.
- Fonte: FATO_FUNIL_EVENTO e FATO_CAMPANHA_CUSTO.
- Regra: sem custo de campanha, retornar BLANK/NULL.
- Limitação: depende da premissa de atribuição e não representa causalidade.

## CAC estimado

- Definição: custo de campanha dividido pelo número de reservas atribuídas.
- Fonte: FATO_CAMPANHA_CUSTO e FATO_FUNIL_EVENTO.
- Limitação: não inclui todos os custos comerciais reais.