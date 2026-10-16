CREATE VIEW IF NOT EXISTS vw_conflitos_reserva AS
SELECT
    r1.ID_Reserva AS ID_Reserva_A,
    r2.ID_Reserva AS ID_Reserva_B,
    r1.ID_Veiculo,
    r1.Data_Retirada_Prevista AS Inicio_A,
    r1.Data_Devolucao_Prevista AS Fim_A,
    r2.Data_Retirada_Prevista AS Inicio_B,
    r2.Data_Devolucao_Prevista AS Fim_B,
    'RESERVA_SOBREPOSTA' AS Tipo_Conflito
FROM RESERVA r1
JOIN RESERVA r2
  ON r1.ID_Veiculo = r2.ID_Veiculo
 AND r1.ID_Reserva < r2.ID_Reserva
 AND r1.Status_Reserva IN ('Confirmada', 'Pendente', 'Em Locacao', 'Cancelada', 'Finalizada')
 AND r2.Status_Reserva IN ('Confirmada', 'Pendente', 'Em Locacao', 'Cancelada', 'Finalizada')
 AND r1.Data_Retirada_Prevista < r2.Data_Devolucao_Prevista
 AND r1.Data_Devolucao_Prevista > r2.Data_Retirada_Prevista;

CREATE VIEW IF NOT EXISTS vw_disponibilidade_categoria AS
WITH reservas AS (
    SELECT
        m.ID_Categoria,
        r.Data_Retirada_Prevista AS inicio,
        r.Data_Devolucao_Prevista AS fim,
        COUNT(*) AS qtd_reservada
    FROM RESERVA r
    JOIN VEICULO v ON v.ID_Veiculo = r.ID_Veiculo
    JOIN MODELO m ON m.ID_Modelo = v.ID_Modelo
    WHERE r.Status_Reserva IN ('Confirmada', 'Pendente', 'Em Locacao', 'Cancelada', 'Finalizada')
    GROUP BY m.ID_Categoria, r.Data_Retirada_Prevista, r.Data_Devolucao_Prevista
)
SELECT
    c.ID_Categoria,
    c.Nome_Categoria,
    COUNT(v.ID_Veiculo) AS qtd_frota_fisica,
    COALESCE(SUM(res.qtd_reservada), 0) AS qtd_reservada_nos_intervalos
FROM CATEGORIA c
LEFT JOIN MODELO m ON m.ID_Categoria = c.ID_Categoria
LEFT JOIN VEICULO v ON v.ID_Modelo = m.ID_Modelo
LEFT JOIN reservas res ON res.ID_Categoria = c.ID_Categoria
GROUP BY c.ID_Categoria, c.Nome_Categoria;

CREATE VIEW IF NOT EXISTS vw_excecoes_operacionais AS
SELECT ID_Reserva_A AS ID_Registro, Tipo_Conflito, 'ALTA' AS Severidade
FROM vw_conflitos_reservas

UNION ALL

SELECT r.ID_Reserva, 'RESERVA_EM_MANUTENCAO', 'ALTA'
FROM RESERVA r
JOIN MANUTENCAO m ON m.ID_Veiculo = r.ID_Veiculo
WHERE r.Status_Reserva IN ('Confirmada', 'Pendente', 'Em Locacao', 'Cancelada', 'Finalizada')
  AND r.Data_Retirada_Prevista < COALESCE(m.Data_Conclusao_Manutencao, '9999-12-31')
  AND r.Data_Devolucao_Prevista > m.Data_Retirada_Manutencao;