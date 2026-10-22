CREATE VIEW IF NOT EXISTS vw_performance_campanha AS
WITH etapas AS (
    SELECT
        ID_Campanha,
        COUNT(DISTINCT CASE WHEN Tipo_Evento = 'PESQUISA' THEN Journey_ID END) AS pesquisas,
        COUNT(DISTINCT CASE WHEN Tipo_Evento = 'COTACAO' THEN Journey_ID END) AS cotacoes,
        COUNT(DISTINCT CASE WHEN Tipo_Evento = 'RESERVA' THEN Journey_ID END) AS reservas,
        COUNT(DISTINCT CASE WHEN Tipo_Evento = 'RETIRADA' THEN Journey_ID END) AS retiradas,
        COUNT(DISTINCT CASE WHEN Tipo_Evento = 'DEVOLUCAO' THEN Journey_ID END) AS devolucoes,
        SUM(CASE WHEN Tipo_Evento = 'DEVOLUCAO' THEN COALESCE(Receita_Liquida_Estimada, 0) ELSE 0 END) AS receita
    FROM FACT_FUNIL_EVENTO
    WHERE ID_Campanha IS NOT NULL
    GROUP BY ID_Campanha
)
SELECT
    c.ID_Campanha,
    c.Nome_Campanha,
    c.Data_Inicio,
    c.Data_Fim,
    c.KPI_Primario,
    c.Premissa_Atribuicao,
    COALESCE(e.pesquisas, 0) AS pesquisas,
    COALESCE(e.cotacoes, 0) AS cotacoes,
    COALESCE(e.reservas, 0) AS reservas,
    COALESCE(e.retiradas, 0) AS retiradas,
    COALESCE(e.devolucoes, 0) AS devolucoes,
    COALESCE(e.receita, 0) AS receita,
    x.Custo_Total,
    CASE
        WHEN x.Custo_Total > 0 THEN (e.receita - x.Custo_Total) / x.Custo_Total
        ELSE NULL
    END AS roi,
    CASE
        WHEN e.pesquisas > 0 THEN 1.0 * e.reservas / e.pesquisas
        ELSE NULL
    END AS conversao_pesquisa_reserva
FROM DIM_CAMPANHA c
LEFT JOIN etapas e ON e.ID_Campanha = c.ID_Campanha
LEFT JOIN FACT_CAMPANHA_CUSTO x ON x.ID_Campanha = c.ID_Campanha;