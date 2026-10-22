# Locadora 360 Analytics — Trilha B: Analytics Comercial

Camada analítica comercial sobre o modelo operacional da locadora. A Trilha B transforma reservas em jornadas sintéticas de funil, associa canais e campanhas, calcula conversões e receita líquida estimada e disponibiliza indicadores para Power BI, coortes, ocupação e simulações de desconto/upgrade.

> **Estado atual:** a branch contém a implementação e os artefatos gerados da Trilha B, mas ainda possui pendências de execução documentadas em [Limitações conhecidas](#limitações-conhecidas). Os valores comerciais não são faturamento real nem evidência causal de ROI.

## Escopo

A trilha cobre:

- jornadas de `PESQUISA`, `COTACAO`, `RESERVA`, `RETIRADA`, `DEVOLUCAO`, `NO_SHOW` e eventos relacionados;
- dimensões sintéticas de canal e campanha;
- custo de campanha separado em mídia, benefício e operação;
- receita bruta, desconto e receita líquida estimada;
- conversão entre etapas do funil;
- performance de campanha, coortes de clientes e ocupação prevista;
- cenários de desconto, custo de upgrade e lift de conversão;
- medidas DAX e artefatos de apresentação para Power BI.

## Arquitetura

```text
Banco operacional de referência
        │
        ├── RESERVA, CLIENTE, VEICULO, FILIAL, MODELO, CATEGORIA
        │
        ├── gerar_campanhas.py
        │       └── DIM_CANAL, DIM_CAMPANHA, FATO_CAMPANHA_CUSTO
        │
        └── gerar_eventos_funil.py
                └── FATO_FUNIL_EVENTO
                        ├── staging/eventos_funil.csv
                        ├── staging/funnel_events.csv
                        └── marts/fato_eventos_funil.parquet
                                │
                                ├── views comerciais / validação
                                ├── simular_campanhas.py
                                └── Power BI
```

Os principais artefatos estão em:

| Caminho | Responsabilidade |
|---|---|
| `database/schema/003_trilha_b_commercial.sql` | Dimensões e fatos comerciais. |
| `src/commercial/gerar_campanhas.py` | Carga de canais, campanhas e custos sintéticos. |
| `src/commercial/gerar_eventos_funil.py` | Geração determinística de jornadas e eventos. |
| `src/commercial/simular_campanhas.py` | Grade de cenários de desconto, upgrade e conversão. |
| `src/validation/validar_dados_comercial.py` | Checks de integridade comercial. |
| `database/views/` | Funil, coortes, ocupação e performance de campanha. |
| `powerbi/medidas.dax` | Medidas de funil, conversão, receita estimada, CAC e ROI. |
| `powerbi/dicionario_metricas.md` | Definições, granularidade e limitações das métricas. |
| `powerbi/dashboard_locadora.pbix` | Dashboard comercial da Trilha B. |
| `docs/trilha-b-report.md` | Lista de resultados esperados do dashboard. |
| `docs/premissas-comerciais.md` | Premissas dos dados e da simulação. |

## Modelo comercial

A Trilha B acrescenta três estruturas principais ao banco SQLite:

- `DIM_CANAL`: canais `ORGANICO`, `PAGO`, `PARCERIA` e `DIRETO`;
- `DIM_CAMPANHA`: período, canal, filial/categoria elegíveis, público, incentivo, desconto, custo, KPI e premissa de atribuição;
- `FATO_FUNIL_EVENTO`: uma linha por evento de uma jornada, identificada por `Journey_ID`, com cliente, canal, campanha, filial, categoria, veículo, reserva, data, valores e origem do dado;
- `FATO_CAMPANHA_CUSTO`: custos de mídia, benefício e operação, com `Custo_Total` calculado no banco.

O snapshot versionado em `data/locadora_commercial.db` contém 5 canais, 4 campanhas, 4 registros de custo, 10.000 jornadas e 26.619 eventos. A distribuição observada dos eventos é:

| Evento | Jornadas |
|---|---:|
| Pesquisa | 10.000 |
| Cotação | 8.757 |
| Reserva | 2.794 |
| Retirada | 2.424 |
| Devolução | 2.274 |
| No-show | 370 |

Os eventos são marcados com `Origem_Dado = 'sintetico'`. A semente usada pelos geradores é `20261019`.

## Regras de geração e atribuição

As jornadas não convertidas são criadas com pesquisa e, em 83% dos casos, cotação. As jornadas convertidas são derivadas das reservas existentes no banco operacional de referência. Para cada reserva, o gerador cria pesquisa, cotação, reserva e, probabilisticamente, retirada/devolução ou no-show.

O valor bruto é a diária da categoria multiplicada pelos dias previstos. O desconto é uma fração sintética do valor bruto e a receita líquida estimada é o bruto menos o desconto. Não é faturamento contábil nem caixa recebido.

A campanha é escolhida por compatibilidade de canal e, quando informados, filial e categoria; somente parte das jornadas elegíveis recebe campanha. As premissas cadastradas em `DIM_CAMPANHA.Premissa_Atribuicao` são distintas por campanha:

| Campanha | Premissa registrada |
|---|---|
| Semana Economica | Primeiro toque pago recebe a atribuição. |
| SUV Ferias | Último toque antes da reserva. |
| Corporativo Parceiros | Código de parceiro informado na cotação. |
| Retencao Clientes | Cliente elegível exposto à campanha. |

Essas são premissas sintéticas gravadas como dado da campanha, não uma medição de atribuição baseada em logs reais. Não há grupo de controle, randomização ou custo comercial completo; portanto, o ROI é descritivo/simulado e não causal.

## Métricas e medidas DAX

`powerbi/medidas.dax` define:

- volume por etapa: `Pesquisas`, `Cotações`, `Reservas`, `Retiradas`, `Devoluções`, `Cancelamentos` e `No Shows`;
- conversões: `Conversão Pesquisa-Cotação`, `Conversão Cotação-Reserva` e `Conversão Reserva-Retirada`;
- `Taxa de Cancelamento`;
- `Receita Líquida Estimada` e `Receita por Retirada`;
- `Custo de Campanha`;
- `ROI Campanha`, calculado como `(receita líquida estimada - custo) / custo`, retornando vazio quando não há custo;
- `CAC Estimado`, `Ticket Médio Estimado` e `Upgrade Rate`.

No snapshot analisado, as taxas simples do funil são aproximadamente 87,57% de pesquisa para cotação, 31,91% de cotação para reserva, 86,76% de reserva para retirada e 93,81% de retirada para devolução. A receita líquida estimada somada aos eventos de devolução é R$ 3.691.782,00. Esses números dependem da geração sintética e não devem ser interpretados como desempenho real.

## Simulações

`src/commercial/simular_campanhas.py` lê as reservas do mart e avalia 36 combinações de:

- desconto de 0%, 5%, 10% e 15%;
- custo de upgrade de R$ 0, R$ 25 e R$ 50;
- lift de conversão de 0%, 5% e 10%.

A probabilidade simulada é `clip(0,35 + lift - desconto × 0,20, 0,01, 0,95)`. O resultado é gravado em `data/staging/simulacoes_campanhas.csv`, com reservas esperadas e receita esperada. A simulação é análise de sensibilidade; não estima efeito causal de preço, desconto ou upgrade.

## Execução local pretendida

A branch usa Python, SQLite, pandas, NumPy, PyArrow e pytest. O fluxo pretendido é:

```bash
# na raiz do repositório
cp data/raw_sample/DB_LOCADORA.seed.db data/locadora_commercial.db
python src/commercial/gerar_campanhas.py
python src/commercial/gerar_eventos_funil.py
python src/validation/validar_dados_comercial.py
python -m pytest -q
```

Para abrir os resultados no Power BI, use `powerbi/dashboard_locadora.pbix` e valide as consultas, relacionamentos, medidas e credenciais conforme o ambiente local.

## Validação

O script de validação verifica:

1. eventos sem cliente correspondente;
2. reservas sem evento `RESERVA`;
3. campanhas sem registro de custo;
4. jornadas com reserva sem cotação.

As views previstas incluem `vw_funil_comercial`, `vw_coorte_clientes`, `vw_ocupacao_frota` e `vw_performance_campanha`. Elas devem ser aplicadas ao banco após a criação das tabelas comerciais.

## Limitações conhecidas

A branch analisada ainda não está pronta para uma execução limpa de CI:

- `.github/workflows/ci.yml` chama `generate_campaigns.py`, `generate_funnel_events.py` e `validate_commercial_data.py`, mas os arquivos versionados têm os nomes `gerar_campanhas.py`, `gerar_eventos_funil.py` e `validar_dados_comercial.py`;
- as views comerciais referenciam `FACT_FUNIL_EVENTO` e `FACT_CAMPANHA_CUSTO`, enquanto o schema cria `FATO_FUNIL_EVENTO` e `FATO_CAMPANHA_CUSTO`; na validação realizada, as views falharam com `no such table: main.FACT_FUNIL_EVENTO`;
- `src/db.py` contém conteúdo duplicado e uma assinatura corrompida (`sqlite3.Cofrom pathlib...`), causando `SyntaxError` ao carregar a configuração de testes;
- a suíte `pytest` não concluiu por causa desse erro de sintaxe;
- `data/locadora_test.db` contém as tabelas comerciais, mas não contém eventos de funil no snapshot analisado;
- `requirements.txt` é um inventário amplo de ambiente/Jupyter e não um conjunto mínimo de dependências da Trilha B;
- os dados e custos são sintéticos, e `Receita_Liquida_Estimada` não substitui a futura camada de faturamento;
- a atribuição de campanha é uma premissa por campanha, não uma atribuição observada em eventos reais.

## Próximos passos recomendados

1. Corrigir os nomes dos scripts no workflow ou criar aliases compatíveis.
2. Padronizar `FATO_*` versus `FACT_*` no schema, views, validação e Power BI.
3. Restaurar `src/db.py` para uma implementação única e tipada de `connect`.
4. Reexecutar geração, validação e testes em banco temporário limpo.
5. Substituir receita estimada por uma fato de faturamento na próxima trilha.
6. Evoluir as premissas de atribuição para uma especificação de identidade, janela e evidência de exposição.
7. Separar dependências mínimas de produção das dependências de notebook e ambiente local.

## Licença e responsabilidade

A branch não define uma licença de software. Antes de redistribuir código, dados ou dashboards, defina uma licença e confirme as condições de uso dos dados sintéticos e dos artefatos derivados.
