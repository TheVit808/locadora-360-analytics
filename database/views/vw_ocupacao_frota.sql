CREATE VIEW IF NOT EXISTS vw_ocupacao_prevista AS
WITH limites AS (
    SELECT
        MIN(Data_Retirada_Prevista) AS inicio,
        MAX(Data_Devolucao_Prevista) AS fim
    FROM RESERVA
),
reservas AS (
    SELECT
        r.ID_Veiculo,
        v.ID_Filial_Atual AS ID_Filial,
        m.ID_Categoria,
        SUM(
            MAX(
                0,
                julianday(MIN(r.Data_Devolucao_Prevista, limites.fim))
                - julianday(MAX(r.Data_Retirada_Prevista, limites.inicio))
            )
        ) AS dias_reservados
    FROM RESERVA r
    JOIN VEICULO v ON v.ID_Veiculo = r.ID_Veiculo
    JOIN MODELO m ON m.ID_Modelo = v.ID_Modelo
    CROSS JOIN limites
    WHERE r.Status_Reserva IN ('Confirmada', 'Pendente', 'Em Locação', 'Concluido')
    GROUP BY r.ID_Veiculo, v.ID_Filial_Atual, m.ID_Categoria
), frota AS (
    SELECT
        v.ID_Veiculo,
        v.ID_Filial_Atual AS ID_Filial,
        m.ID_Categoria,
        julianday(limites.fim) - julianday(limites.inicio) AS dias_periodo
    FROM VEICULO v
    JOIN MODELO m ON m.ID_Modelo = v.ID_Modelo
    CROSS JOIN limites
)
SELECT
    f.ID_Filial,
    f.ID_Categoria,
    COUNT(*) AS qtd_veiculos,
    SUM(COALESCE(r.dias_reservados, 0)) AS dias_reservados,
    SUM(f.dias_periodo) AS dias_disponiveis_teoricos,
    SUM(COALESCE(r.dias_reservados, 0)) / NULLIF(SUM(f.dias_periodo), 0) AS ocupacao_prevista
FROM frota f
LEFT JOIN reservas r ON r.ID_Veiculo = f.ID_Veiculo
GROUP BY f.ID_Filial, f.ID_Categoria;