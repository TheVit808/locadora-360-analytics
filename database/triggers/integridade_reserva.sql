PRAGMA foreign_keys = ON;

DROP TRIGGER IF EXISTS reserva_validar_datas;
DROP TRIGGER IF EXISTS reserva_sem_sobreposicao;
DROP TRIGGER IF EXISTS reserva_evento_insert;
DROP TRIGGER IF EXISTS reserva_evento_status;
DROP TRIGGER IF EXISTS reserva_data_sem_sobreposicao;
DROP TRIGGER IF EXISTS reserva_sem_aluguel_ativo;
DROP TRIGGER IF EXISTS reserva_sem_manutencao;
DROP TRIGGER IF EXISTS update_reserva_sem_aluguel_ativo;
DROP TRIGGER IF EXISTS update_reserva_sem_manutencao;
DROP TRIGGER IF EXISTS insert_manutencao_conflita_reserva;
DROP TRIGGER IF EXISTS update_manutencao_conflita_reserva;

CREATE TRIGGER reserva_validar_datas_update
BEFORE INSERT ON RESERVA
FOR EACH ROW
WHEN NEW.Data_Devolucao_Prevista <= NEW.Data_Retirada_Prevista
BEGIN
    SELECT RAISE(ABORT, 'RESERVA_INTERVALO_INVALIDO');
END;

CREATE TRIGGER reserva_sem_sobreposicao
BEFORE INSERT ON RESERVA
FOR EACH ROW
WHEN NEW.Status_Reserva NOT IN ('Cancelada', 'Finalizada')
 AND EXISTS (
    SELECT 1
    FROM RESERVA r
    WHERE r.ID_Veiculo = NEW.ID_Veiculo
      AND r.Status_Reserva NOT IN ('Cancelada', 'Finalizada')
      AND NEW.Data_Retirada_Prevista < r.Data_Devolucao_Prevista
      AND NEW.Data_Devolucao_Prevista > r.Data_Retirada_Prevista
 )
BEGIN
    SELECT RAISE(ABORT, 'RESERVA_SOBREPOSTA_VEICULO');
END;

CREATE TRIGGER reserva_evento_insert
AFTER INSERT ON RESERVA
FOR EACH ROW
BEGIN
    INSERT INTO RESERVA_EVENTO (
        ID_Reserva, Tipo_Evento, Status_Novo, Observacao
    ) VALUES (
        NEW.ID_Reserva, 'CRIADA', NEW.Status_Reserva, 'Reserva inserida'
    );
END;

CREATE TRIGGER reserva_evento_status
AFTER UPDATE OF Status_Reserva ON RESERVA
FOR EACH ROW
WHEN OLD.Status_Reserva IS NOT NEW.Status_Reserva
BEGIN
    INSERT INTO RESERVA_EVENTO (
        ID_Reserva, Tipo_Evento, Status_Anterior, Status_Novo, Observacao
    ) VALUES (
        NEW.ID_Reserva, 'STATUS_ALTERADO', OLD.Status_Reserva,
        NEW.Status_Reserva, 'Status alterado'
    );
END;

CREATE TRIGGER reserva_data_sem_sobreposicao
BEFORE UPDATE OF Data_Retirada_Prevista, Data_Devolucao_Prevista, id_veiculo, status_reserva ON RESERVA
FOR EACH ROW
WHEN NEW.Status_Reserva NOT IN ('Cancelada', 'Finalizada')
BEGIN
    SELECT CASE 
        WHEN EXISTS (
            SELECT 1
            FROM RESERVA r
            WHERE r.ID_Veiculo = NEW.ID_Veiculo
              AND r.ID_Reserva <> OLD.ID_Reserva
              AND r.Status_Reserva NOT IN ('Cancelada', 'Finalizada')
              AND NEW.Data_Retirada_Prevista < r.Data_Devolucao_Prevista
              AND NEW.Data_Devolucao_Prevista > r.Data_Retirada_Prevista
        )
        THEN RAISE(ABORT, 'RESERVA_SOBREPOSTA_VEICULO')
    END;
END;

CREATE TRIGGER reserva_sem_aluguel_ativo
BEFORE INSERT ON RESERVA
FOR EACH ROW
WHEN NEW.Status_Reserva IN ('Confirmada', 'Pendente')
 AND EXISTS (
    SELECT 1
    FROM ALUGUEL a
    WHERE a.ID_Veiculo = NEW.ID_Veiculo
      AND a.Data_Devolucao_Real IS NULL
      AND NEW.Data_Retirada_Prevista < COALESCE(a.Data_Devolucao_Real, '9999-12-31')
      AND NEW.Data_Devolucao_Prevista > a.Data_Retirada_Real
 )
BEGIN
    SELECT RAISE(ABORT, 'RESERVA_CONFLITA_ALUGUEL_ATIVO');
END;

CREATE TRIGGER reserva_sem_manutencao
BEFORE INSERT ON RESERVA
FOR EACH ROW
WHEN NEW.Status_Reserva IN ('Confirmada', 'Pendente')
 AND EXISTS (
    SELECT 1
    FROM MANUTENCAO m
    WHERE m.ID_Veiculo = NEW.ID_Veiculo
      AND NEW.Data_Retirada_Prevista < COALESCE(m.Data_Conclusao_Manutencao, '9999-12-31')
      AND NEW.Data_Devolucao_Prevista > m.Data_Retirada_Manutencao
 )
BEGIN
    SELECT RAISE(ABORT, 'RESERVA_CONFLITA_MANUTENCAO');
END;

CREATE TRIGGER update_reserva_sem_aluguel_ativo
BEFORE UPDATE OF Data_Retirada_Prevista, Data_Devolucao_Prevista, ID_Veiculo, Status_Reserva ON RESERVA
FOR EACH ROW
WHEN NEW.Status_Reserva IN ('Confirmada', 'Pendente') 
  AND EXISTS (
    SELECT 1
    FROM ALUGUEL a
    WHERE a.ID_Veiculo = NEW.ID_Veiculo
      AND a.Data_Devolucao_Real IS NULL
      AND NEW.Data_Retirada_Prevista < COALESCE(a.Data_Devolucao_Real, '9999-12-31')
      AND NEW.Data_Devolucao_Prevista > a.Data_Retirada_Real
  )
BEGIN
    SELECT RAISE(ABORT, 'RESERVA_CONFLITA_ALUGUEL_ATIVO');
END;

CREATE TRIGGER update_reserva_sem_manutencao
BEFORE UPDATE OF Data_Retirada_Prevista, Data_Devolucao_Prevista, ID_Veiculo, Status_Reserva ON RESERVA
FOR EACH ROW
WHEN NEW.Status_Reserva IN ('Confirmada', 'Pendente') 
  AND EXISTS (
    SELECT 1
    FROM MANUTENCAO m
    WHERE m.ID_Veiculo = NEW.ID_Veiculo
      AND NEW.Data_Retirada_Prevista < COALESCE(m.Data_Conclusao_Manutencao, '9999-12-31')
      AND NEW.Data_Devolucao_Prevista > m.Data_Retirada_Manutencao
  )
BEGIN
    SELECT RAISE(ABORT, 'RESERVA_CONFLITA_MANUTENCAO');
END;

CREATE TRIGGER insert_manutencao_conflita_reserva
BEFORE INSERT ON MANUTENCAO
FOR EACH ROW
WHEN EXISTS (
    SELECT 1
    FROM RESERVA r
    WHERE r.ID_Veiculo = NEW.ID_Veiculo
      AND r.Status_Reserva IN ('Confirmada', 'Pendente')
      AND NEW.Data_Retirada_Manutencao < r.Data_Devolucao_Prevista
      AND COALESCE(NEW.Data_Conclusao_Manutencao, '9999-12-31') > r.Data_Retirada_Prevista
)
BEGIN
    SELECT RAISE(ABORT, 'MANUTENCAO_CONFLITA_RESERVA_EXISTENTE');
END;

CREATE TRIGGER update_manutencao_conflita_reserva
BEFORE UPDATE OF Data_Retirada_Manutencao, Data_Conclusao_Manutencao, ID_Veiculo ON MANUTENCAO
FOR EACH ROW
WHEN EXISTS (
    SELECT 1
    FROM RESERVA r
    WHERE r.ID_Veiculo = NEW.ID_Veiculo
      AND r.Status_Reserva IN ('Confirmada', 'Pendente')
      AND NEW.Data_Retirada_Manutencao < r.Data_Devolucao_Prevista
      AND COALESCE(NEW.Data_Conclusao_Manutencao, '9999-12-31') > r.Data_Retirada_Prevista
)
BEGIN
    SELECT RAISE(ABORT, 'MANUTENCAO_CONFLITA_RESERVA_EXISTENTE');
END;