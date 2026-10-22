CREATE VIEW IF NOT EXISTS vw_coorte_clientes AS
WITH primeira_cotacao AS (
    SELECT
        ID_Cliente,
        MIN(date(Data_Evento, 'start of month')) AS mes_coorte
    FROM FACT_FUNIL_EVENTO
    WHERE Tipo_Evento = 'COTACAO'
    GROUP BY ID_Cliente
), atividade AS (
    SELECT DISTINCT
        f.ID_Cliente,
        p.mes_coorte,
        date(f.Data_Evento, 'start of month') AS mes_atividade
    FROM FACT_FUNIL_EVENTO f
    JOIN primeira_cotacao p ON p.ID_Cliente = f.ID_Cliente
    WHERE f.Tipo_Evento IN ('COTACAO', 'RESERVA', 'RETIRADA', 'DEVOLUCAO')
)
SELECT
    mes_coorte,
    mes_atividade,
    COUNT(DISTINCT ID_Cliente) AS clientes_ativos,
    CAST(
        (julianday(mes_atividade) - julianday(mes_coorte)) / 30
        AS INTEGER
    ) AS meses_desde_coorte
FROM atividade
GROUP BY mes_coorte, mes_atividade;