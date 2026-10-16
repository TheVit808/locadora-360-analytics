SELECT Tipo_Conflito, COUNT(*) AS quantidade
FROM vw_excecoes_operacionais
GROUP BY Tipo_Conflito
ORDER BY quantidade DESC;

SELECT Status_Veiculo, COUNT(*) AS quantidade
FROM VEICULO
GROUP BY Status_Veiculo
ORDER BY Status_Veiculo;

SELECT
    v.ID_Veiculo,
    v.Placa,
    COUNT(c.ID_Reserva_A) AS conflitos
FROM VEICULO v
LEFT JOIN vw_conflitos_reservas c ON c.ID_Veiculo = v.ID_Veiculo
GROUP BY v.ID_Veiculo, v.Placa
ORDER BY conflitos DESC;