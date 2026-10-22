CREATE VIEW IF NOT EXISTS vw_funil_comercial AS
SELECT
    COALESCE(ID_Campanha, 0) AS ID_Campanha,
    ID_Canal,
    ID_Filial,
    ID_Categoria,
    COUNT(DISTINCT CASE WHEN Tipo_Evento = 'PESQUISA' THEN Journey_ID END) AS Pesquisas,
    COUNT(DISTINCT CASE WHEN Tipo_Evento = 'COTACAO' THEN Journey_ID END) AS Cotacoes,
    COUNT(DISTINCT CASE WHEN Tipo_Evento = 'RESERVA' THEN Journey_ID END) AS Reservas,
    COUNT(DISTINCT CASE WHEN Tipo_Evento = 'CANCELAMENTO' THEN Journey_ID END) AS Cancelamentos,
    COUNT(DISTINCT CASE WHEN Tipo_Evento = 'RETIRADA' THEN Journey_ID END) AS Retiradas,
    COUNT(DISTINCT CASE WHEN Tipo_Evento = 'DEVOLUCAO' THEN Journey_ID END) AS Devolucoes,
    COUNT(DISTINCT CASE WHEN Tipo_Evento = 'NO_SHOW' THEN Journey_ID END) AS No_Shows,
    SUM(COALESCE(Receita_Liquida_Estimada, 0)) AS Receita_Liquida_Estimada
FROM FACT_FUNIL_EVENTO
GROUP BY COALESCE(ID_Campanha, 0), ID_Canal, ID_Filial, ID_Categoria;