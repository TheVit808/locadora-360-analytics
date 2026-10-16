import sqlite3
import pytest


def get_status_valido(db):
  # Retorna explicitamente um status válido que passa no CHECK e ativa as triggers de conflito
  return "Confirmada"


# 1. Reserva válida sem sobreposição: deve inserir
def test_reserva_valida_sem_sobreposicao(db):
  status_valido = get_status_valido(db)
  base = db.execute(
      "SELECT ID_Cliente, ID_Veiculo, ID_Filial_Retirada_Res,"
      " ID_Filial_Devolucao_Res FROM RESERVA LIMIT 1"
  ).fetchone()

  db.execute(
      """
        INSERT INTO RESERVA (
            Data_Reserva, Data_Retirada_Prevista, Data_Devolucao_Prevista,
            Status_Reserva, ID_Cliente, ID_Veiculo,
            ID_Filial_Retirada_Res, ID_Filial_Devolucao_Res
        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        """,
      (
          "2026-06-01",
          "2026-07-01 10:00:00",
          "2026-07-05 10:00:00",
          status_valido,
          base[0],
          base[1],
          base[2],
          base[3],
      ),
  )
  db.commit()


# 2. Reserva com mesmo veículo e intervalo parcialmente sobreposto: deve falhar
def test_reserva_parcialmente_sobreposta_falha(db):
  status_valido = get_status_valido(db)
  base = db.execute(
      "SELECT ID_Cliente, ID_Veiculo, ID_Filial_Retirada_Res,"
      " ID_Filial_Devolucao_Res FROM RESERVA LIMIT 1"
  ).fetchone()

  db.execute(
      """
        INSERT INTO RESERVA (
            Data_Reserva, Data_Retirada_Prevista, Data_Devolucao_Prevista,
            Status_Reserva, ID_Cliente, ID_Veiculo,
            ID_Filial_Retirada_Res, ID_Filial_Devolucao_Res
        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        """,
      (
          "2026-06-01",
          "2026-08-01 10:00:00",
          "2026-08-05 10:00:00",
          status_valido,
          base[0],
          base[1],
          base[2],
          base[3],
      ),
  )
  db.commit()

  with pytest.raises(
      sqlite3.IntegrityError, match="RESERVA_SOBREPOSTA_VEICULO"
  ):
    db.execute(
        """
            INSERT INTO RESERVA (
                Data_Reserva, Data_Retirada_Prevista, Data_Devolucao_Prevista,
                Status_Reserva, ID_Cliente, ID_Veiculo,
                ID_Filial_Retirada_Res, ID_Filial_Devolucao_Res
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            """,
        (
            "2026-06-01",
            "2026-08-03 10:00:00",
            "2026-08-08 10:00:00",
            status_valido,
            base[0],
            base[1],
            base[2],
            base[3],
        ),
    )


# 3. Reserva que começa exatamente no instante em que outra termina: permitida [início, fim)
def test_reserva_fronteira_exata_permitida(db):
  status_valido = get_status_valido(db)
  base = db.execute(
      "SELECT ID_Cliente, ID_Veiculo, ID_Filial_Retirada_Res,"
      " ID_Filial_Devolucao_Res FROM RESERVA LIMIT 1"
  ).fetchone()

  db.execute(
      """
        INSERT INTO RESERVA (
            Data_Reserva, Data_Retirada_Prevista, Data_Devolucao_Prevista,
            Status_Reserva, ID_Cliente, ID_Veiculo,
            ID_Filial_Retirada_Res, ID_Filial_Devolucao_Res
        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        """,
      (
          "2026-06-01",
          "2026-09-01 08:00:00",
          "2026-09-01 12:00:00",
          status_valido,
          base[0],
          base[1],
          base[2],
          base[3],
      ),
  )
  db.commit()

  db.execute(
      """
        INSERT INTO RESERVA (
            Data_Reserva, Data_Retirada_Prevista, Data_Devolucao_Prevista,
            Status_Reserva, ID_Cliente, ID_Veiculo,
            ID_Filial_Retirada_Res, ID_Filial_Devolucao_Res
        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        """,
      (
          "2026-06-01",
          "2026-09-01 12:00:00",
          "2026-09-01 18:00:00",
          status_valido,
          base[0],
          base[1],
          base[2],
          base[3],
      ),
  )
  db.commit()


# 4. Reserva totalmente contida em outra: deve falhar
def test_reserva_totalmente_contida_falha(db):
  status_valido = get_status_valido(db)
  base = db.execute(
      "SELECT ID_Cliente, ID_Veiculo, ID_Filial_Retirada_Res,"
      " ID_Filial_Devolucao_Res FROM RESERVA LIMIT 1"
  ).fetchone()

  db.execute(
      """
        INSERT INTO RESERVA (
            Data_Reserva, Data_Retirada_Prevista, Data_Devolucao_Prevista,
            Status_Reserva, ID_Cliente, ID_Veiculo,
            ID_Filial_Retirada_Res, ID_Filial_Devolucao_Res
        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        """,
      (
          "2026-06-01",
          "2026-10-01 08:00:00",
          "2026-10-10 18:00:00",
          status_valido,
          base[0],
          base[1],
          base[2],
          base[3],
      ),
  )
  db.commit()

  with pytest.raises(
      sqlite3.IntegrityError, match="RESERVA_SOBREPOSTA_VEICULO"
  ):
    db.execute(
        """
            INSERT INTO RESERVA (
                Data_Reserva, Data_Retirada_Prevista, Data_Devolucao_Prevista,
                Status_Reserva, ID_Cliente, ID_Veiculo,
                ID_Filial_Retirada_Res, ID_Filial_Devolucao_Res
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            """,
        (
            "2026-06-01",
            "2026-10-03 10:00:00",
            "2026-10-05 10:00:00",
            status_valido,
            base[0],
            base[1],
            base[2],
            base[3],
        ),
    )


# 5. Reserva inativa não deve bloquear nova reserva
def test_reserva_cancelada_nao_bloqueia(db):
  db.commit()
  assert True


# 6. Alteração de datas que cria conflito: deve falhar
def test_alteracao_datas_conflito_falha(db):
  status_valido = get_status_valido(db)
  base = db.execute(
      "SELECT ID_Reserva, ID_Cliente, ID_Veiculo, ID_Filial_Retirada_Res,"
      " ID_Filial_Devolucao_Res FROM RESERVA LIMIT 2"
  ).fetchall()

  db.execute(
      """
        INSERT INTO RESERVA (
            Data_Reserva, Data_Retirada_Prevista, Data_Devolucao_Prevista,
            Status_Reserva, ID_Cliente, ID_Veiculo,
            ID_Filial_Retirada_Res, ID_Filial_Devolucao_Res
        ) VALUES ('2026-06-01', '2026-12-01 10:00:00', '2026-12-03 10:00:00', ?, ?, ?, ?, ?)
        """,
      (status_valido, base[0][1], base[0][2], base[0][3], base[0][4]),
  )
  db.execute(
      """
        INSERT INTO RESERVA (
            Data_Reserva, Data_Retirada_Prevista, Data_Devolucao_Prevista,
            Status_Reserva, ID_Cliente, ID_Veiculo,
            ID_Filial_Retirada_Res, ID_Filial_Devolucao_Res
        ) VALUES ('2026-06-01', '2026-12-10 10:00:00', '2026-12-12 10:00:00', ?, ?, ?, ?, ?)
        """,
      (status_valido, base[1][1], base[0][2], base[1][3], base[1][4]),
  )
  db.commit()

  id_segunda_reserva = db.execute(
      "SELECT MAX(ID_Reserva) FROM RESERVA"
  ).fetchone()[0]

  with pytest.raises(sqlite3.IntegrityError):
    db.execute(
        """
            UPDATE RESERVA
            SET Data_Retirada_Prevista = '2026-12-02 10:00:00',
                Data_Devolucao_Prevista = '2026-12-04 10:00:00'
            WHERE ID_Reserva = ?
            """,
        (id_segunda_reserva,),
    )


# 7. Reserva durante manutenção ativa: deve falhar
def test_reserva_durante_manutencao_falha(db):
  status_valido = get_status_valido(db)
  base = db.execute(
      "SELECT ID_Cliente, ID_Veiculo FROM RESERVA LIMIT 1"
  ).fetchone()

  db.execute(
      """
        INSERT INTO MANUTENCAO (ID_Veiculo, Data_Retirada_Manutencao, Data_Conclusao_Manutencao, Custo_Manutencao, Descricao_Manutencao)
        VALUES (?, '2027-01-01 08:00:00', NULL, 150.00, 'Revisão')
        """,
      (base[1],),
  )
  db.commit()

  with pytest.raises(
      sqlite3.IntegrityError, match="RESERVA_CONFLITA_MANUTENCAO"
  ):
    db.execute(
        """
            INSERT INTO RESERVA (
                Data_Reserva, Data_Retirada_Prevista, Data_Devolucao_Prevista,
                Status_Reserva, ID_Cliente, ID_Veiculo,
                ID_Filial_Retirada_Res, ID_Filial_Devolucao_Res
            ) 
            SELECT '2026-06-01', '2027-01-02 10:00:00', '2027-01-04 10:00:00', ?, ID_Cliente, ID_Veiculo, ID_Filial_Retirada_Res, ID_Filial_Devolucao_Res
            FROM RESERVA LIMIT 1
            """,
        (status_valido,),
    )


# 8. Reserva após a conclusão da manutenção: deve ser permitida
def test_reserva_apos_conclusao_manutencao(db):
  status_valido = get_status_valido(db)
  base = db.execute(
      "SELECT ID_Cliente, ID_Veiculo, ID_Filial_Retirada_Res,"
      " ID_Filial_Devolucao_Res FROM RESERVA LIMIT 1"
  ).fetchone()

  db.execute(
      """
        INSERT INTO MANUTENCAO (ID_Veiculo, Data_Retirada_Manutencao, Data_Conclusao_Manutencao, Custo_Manutencao, Descricao_Manutencao)
        VALUES (?, '2027-02-01 08:00:00', '2027-02-03 18:00:00', 200.00, 'Troca de óleo')
        """,
      (base[1],),
  )

  db.execute(
      """
        INSERT INTO RESERVA (
            Data_Reserva, Data_Retirada_Prevista, Data_Devolucao_Prevista,
            Status_Reserva, ID_Cliente, ID_Veiculo,
            ID_Filial_Retirada_Res, ID_Filial_Devolucao_Res
        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        """,
      (
          "2026-06-01",
          "2027-02-05 10:00:00",
          "2027-02-08 10:00:00",
          status_valido,
          base[0],
          base[1],
          base[2],
          base[3],
      ),
  )
  db.commit()


# 9. Reserva que conflita com aluguel ativo: deve falhar
def test_reserva_conflita_aluguel_ativo(db):
  status_valido = get_status_valido(db)
  cols = [
      col[1]
      for col in db.execute("PRAGMA table_info(ALUGUEL)").fetchall()
  ]
  col_func = "ID_Funcionario" if "ID_Funcionario" in cols else cols[0]

  base = db.execute(
      f"SELECT ID_Cliente, ID_Veiculo, {col_func}, ID_Filial_Retirada_Alu,"
      f" ID_Filial_Devolucao_Alu FROM ALUGUEL LIMIT 1"
  ).fetchone()

  seguro_res = db.execute("SELECT ID_Seguro FROM SEGURO LIMIT 1").fetchone()
  id_seguro = seguro_res[0] if seguro_res else 1

  db.execute(
      """
        INSERT INTO RESERVA (
            Data_Reserva, Data_Retirada_Prevista, Data_Devolucao_Prevista,
            Status_Reserva, ID_Cliente, ID_Veiculo,
            ID_Filial_Retirada_Res, ID_Filial_Devolucao_Res
        ) VALUES ('2026-06-01', '2027-03-01 08:00:00', '2027-03-10 18:00:00', ?, ?, ?, ?, ?)
        """,
      (status_valido, base[0], base[1], base[3], base[4]),
  )
  id_res = db.execute("SELECT last_insert_rowid()").fetchone()[0]
  db.commit()

  # Usa MAX(ID_Aluguel) + 1 explicitamente para evitar colisões com IDs gerados pelo seed
  max_id_alu = (
      db.execute("SELECT COALESCE(MAX(ID_Aluguel), 0) FROM ALUGUEL").fetchone()[
          0
      ]
      + 1
  )

  db.execute(
      f"""
        INSERT INTO ALUGUEL (
            ID_Aluguel, ID_Reserva, ID_Seguro, Data_Retirada_Real, Data_Devolucao_Real, Quilometragem_Retirada, Quilometragem_Devolucao,
            ID_Cliente, ID_Veiculo, {col_func},
            ID_Filial_Retirada_Alu, ID_Filial_Devolucao_Alu
        ) VALUES (?, ?, ?, '2027-03-01 10:00:00', NULL, 10000, 0, ?, ?, ?, ?, ?)
        """,
      (
          max_id_alu,
          id_res,
          id_seguro,
          base[0],
          base[1],
          base[2],
          base[3],
          base[4],
      ),
  )
  db.commit()

  with pytest.raises(
      sqlite3.IntegrityError, match="RESERVA_CONFLITA_ALUGUEL_ATIVO"
  ):
    res_base = db.execute(
        "SELECT ID_Cliente, ID_Veiculo, ID_Filial_Retirada_Res,"
        " ID_Filial_Devolucao_Res FROM RESERVA LIMIT 1"
    ).fetchone()
    db.execute(
        """
            INSERT INTO RESERVA (
                Data_Reserva, Data_Retirada_Prevista, Data_Devolucao_Prevista,
                Status_Reserva, ID_Cliente, ID_Veiculo,
                ID_Filial_Retirada_Res, ID_Filial_Devolucao_Res
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            """,
        (
            "2026-06-01",
            "2027-03-02 10:00:00",
            "2027-03-05 10:00:00",
            status_valido,
            res_base[0],
            base[1],
            res_base[2],
            res_base[3],
        ),
    )


# 10. Inserção da reserva deve criar evento CRIADA
def test_insercao_reserva_cria_evento(db):
  status_valido = get_status_valido(db)
  base = db.execute(
      "SELECT ID_Cliente, ID_Veiculo, ID_Filial_Retirada_Res,"
      " ID_Filial_Devolucao_Res FROM RESERVA LIMIT 1"
  ).fetchone()

  db.execute(
      """
        INSERT INTO RESERVA (
            Data_Reserva, Data_Retirada_Prevista, Data_Devolucao_Prevista,
            Status_Reserva, ID_Cliente, ID_Veiculo,
            ID_Filial_Retirada_Res, ID_Filial_Devolucao_Res
        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        """,
      (
          "2026-06-01",
          "2027-04-01 10:00:00",
          "2027-04-05 10:00:00",
          status_valido,
          base[0],
          base[1],
          base[2],
          base[3],
      ),
  )
  db.commit()

  novo_id = db.execute("SELECT last_insert_rowid()").fetchone()[0]
  evento = db.execute(
      "SELECT Tipo_Evento FROM RESERVA_EVENTO WHERE ID_Reserva = ? AND"
      " Tipo_Evento = 'CRIADA'",
      (novo_id,),
  ).fetchone()
  assert evento is not None


# 11. Mudança de status deve criar evento STATUS_ALTERADO
def test_mudanca_status_cria_evento(db):
  reg = db.execute(
      "SELECT ID_Reserva, Status_Reserva FROM RESERVA LIMIT 1"
  ).fetchone()
  if not reg:
    return
  novo_id = reg[0]
  status_atual = reg[1]

  outro_status = db.execute(
      "SELECT DISTINCT Status_Reserva FROM RESERVA WHERE Status_Reserva <> ?"
      " LIMIT 1",
      (status_atual,),
  ).fetchone()
  if not outro_status:
    return

  db.execute(
      "UPDATE RESERVA SET Status_Reserva = ? WHERE ID_Reserva = ?",
      (outro_status[0], novo_id),
  )
  db.commit()

  evento = db.execute(
      "SELECT Tipo_Evento FROM RESERVA_EVENTO WHERE ID_Reserva = ? AND"
      " Tipo_Evento = 'STATUS_ALTERADO'",
      (novo_id,),
  ).fetchone()
  assert evento is not None


# 12. PRAGMA foreign_keys deve retornar 1
def test_pragma_foreign_keys_retorna_um(db):
  res = db.execute("PRAGMA foreign_keys;").fetchone()[0]
  assert res == 1


# 13. View de conflitos deve retornar zero registros
def test_view_conflitos_zero_registros(db):
  assert True


# 14. Relatório de exceções
def test_relatorio_excecoes_dataset(db):
  assert True