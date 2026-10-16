-- Criação de Triggers - Engenharia de Colunas Condicionais

-- Controle de Concorrencia - Impede Alugar Veículo Alugado
CREATE TRIGGER prevencao_aluguel_duplo
BEFORE INSERT ON ALUGUEL
FOR EACH ROW
WHEN EXISTS (
  SELECT 1 FROM ALUGUEL
  WHERE ID_Veiculo = NEW.ID_Veiculo
  AND Data_Devolucao_Real IS NULL
)
BEGIN
  SELECT RAISE(ABORT, 'Veiculo já está alugado');
END;

-- Atualizar Quilometragem do Veículo  
CREATE TRIGGER atualizar_km_veiculo
AFTER UPDATE OF Quilometragem_Devolucao ON ALUGUEL
FOR EACH ROW
WHEN NEW.Quilometragem_Devolucao IS NOT NULL
BEGIN
  UPDATE VEICULO
  SET Quilometragem_Atual = NEW.Quilometragem_Devolucao
  WHERE ID_Veiculo = NEW.ID_Veiculo;
END;  

-- Atualizar Status do Veículo
-- Para: Alugado  
CREATE TRIGGER atualizar_status_veiculo_alug
AFTER INSERT ON ALUGUEL
BEGIN
  UPDATE VEICULO
  SET Status_Veiculo = 'Alugado'
  WHERE ID_Veiculo = NEW.ID_Veiculo;
END;
-- Para: Disponivel  
CREATE TRIGGER atualizar_status_veiculo_disp
AFTER UPDATE OF Data_Devolucao_Real ON ALUGUEL
WHEN NEW.Data_Devolucao_Real IS NOT NULL
BEGIN
  UPDATE VEICULO
  SET Status_Veiculo = 'Disponivel'
  WHERE ID_Veiculo = NEW.ID_Veiculo;
END;
-- Para: Manutenção - Cadeia de Atualização
-- Inicio Manutenção
CREATE TRIGGER inicio_manutencao
AFTER INSERT ON MANUTENCAO
FOR EACH ROW
BEGIN
  UPDATE VEICULO
  SET Status_Veiculo = 'Manutencao'
  WHERE ID_Veiculo = NEW.ID_Veiculo;
-- encerra aluguel ativo
  UPDATE ALUGUEL
  SET Data_Devolucao_Real = CURRENT_TIMESTAMP
  WHERE ID_Veiculo = NEW.ID_Veiculo
  AND Data_Devolucao_Real IS NULL;
END;
-- Fim manutenção
CREATE TRIGGER fim_manutencao
AFTER UPDATE OF Data_Conclusao_Manutencao ON MANUTENCAO
FOR EACH ROW
WHEN NEW.Data_Conclusao_Manutencao IS NOT NULL
BEGIN
  UPDATE VEICULO
  SET Status_Veiculo = 'Disponivel'
  WHERE ID_Veiculo = NEW.ID_Veiculo;
END;

  
-- Calcular Valor Final Aluguel
CREATE TRIGGER calc_valor_alug
AFTER UPDATE OF Data_Devolucao_Real ON ALUGUEL
FOR EACH ROW
WHEN NEW.Data_Devolucao_Real IS NOT NULL
BEGIN
   UPDATE ALUGUEL
  SET Valor_Final = ROUND(
    (
      SELECT c.Valor_Diaria
      FROM VEICULO v
      JOIN MODELO m ON v.ID_Modelo = m.ID_Modelo
      JOIN CATEGORIA c ON m.ID_Categoria = c.ID_Categoria
      WHERE v.ID_Veiculo = NEW.ID_Veiculo
    ) * NEW.Dias_Locacao
  )
  WHERE ID_Aluguel = NEW.ID_Aluguel;
END; 
  
-- Definir Status da Reserva
CREATE TRIGGER status_reserva
AFTER UPDATE ON ALUGUEL
BEGIN
  UPDATE RESERVA
  SET Status_Reserva =
    CASE
      WHEN NEW.Data_Devolucao_Real IS NOT NULL THEN 'Concluido'
      WHEN NEW.Data_Retirada_Real IS NOT NULL AND NEW.Data_Devolucao_Real IS NULL THEN 'Em Locação'
      ELSE 'Em Espera'
    END
  WHERE ID_Reserva = NEW.ID_Reserva;
END;
  
