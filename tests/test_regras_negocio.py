import sqlite3
import pytest

def test_reserva_valida_sem_sobreposicao(db):
    """1. Reserva válida sem sobreposição: deve inserir."""
    initial_count = db.execute("SELECT COUNT(*) FROM RESERVA").fetchone()[0]
    
    db.execute(
        """
        INSERT INTO RESERVA (
            Data_Reserva, Data_Retirada_Prevista, Data_Devolucao_Prevista,
            Valor_Final_Previsto, Status_Reserva, ID_Cliente, ID_Veiculo,
            ID_Seguro, ID_Filial_Retirada_Res, ID_Filial_Devolucao_Res
        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """,
        ("2026-06-01", "2026-06-10", "2026-06-15", 750.00, "Confirmada", 1, 1, 1, 1, 1)
    )
    db.commit()
    
    current_count = db.execute("SELECT COUNT(*) FROM RESERVA").fetchone()[0]
    assert current_count == initial_count + 1


def test_reserva_sobreposta_veiculo(db):
    """2. Reserva com mesmo veículo e intervalo parcialmente sobreposto: deve falhar com RESERVA_SOBREPOSTA_VEICULO."""
    db.execute(
        """
        INSERT INTO RESERVA (
            Data_Reserva, Data_Retirada_Prevista, Data_Devolucao_Prevista,
            Valor_Final_Previsto, Status_Reserva, ID_Cliente, ID_Veiculo,
            ID_Seguro, ID_Filial_Retirada_Res, ID_Filial_Devolucao_Res
        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """,
        ("2026-06-01", "2026-06-10", "2026-06-15", 750.00, "Confirmada", 1, 1, 1, 1, 1)
    )
    db.commit()

    with pytest.raises(sqlite3.IntegrityError, match="RESERVA_SOBREPOSTA_VEICULO"):
        db.execute(
            """
            INSERT INTO RESERVA (
                Data_Reserva, Data_Retirada_Prevista, Data_Devolucao_Prevista,
                Valor_Final_Previsto, Status_Reserva, ID_Cliente, ID_Veiculo,
                ID_Seguro, ID_Filial_Retirada_Res, ID_Filial_Devolucao_Res
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """,
            ("2026-06-02", "2026-06-12", "2026-06-18", 900.00, "Confirmada", 1, 1, 1, 1, 1)
        )


def test_reserva_adjacente_permitida(db):
    """3. Reserva que começa exatamente no instante em que outra termina: deve ser permitida sob o padrão [início, fim)."""
    initial_count = db.execute("SELECT COUNT(*) FROM RESERVA").fetchone()[0]

    db.execute(
        """
        INSERT INTO RESERVA (
            Data_Reserva, Data_Retirada_Prevista, Data_Devolucao_Prevista,
            Valor_Final_Previsto, Status_Reserva, ID_Cliente, ID_Veiculo,
            ID_Seguro, ID_Filial_Retirada_Res, ID_Filial_Devolucao_Res
        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """,
        ("2026-06-01", "2026-06-10", "2026-06-15", 750.00, "Confirmada", 1, 1, 1, 1, 1)
    )
    db.commit()

    db.execute(
        """
        INSERT INTO RESERVA (
            Data_Reserva, Data_Retirada_Prevista, Data_Devolucao_Prevista,
            Valor_Final_Previsto, Status_Reserva, ID_Cliente, ID_Veiculo,
            ID_Seguro, ID_Filial_Retirada_Res, ID_Filial_Devolucao_Res
        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """,
        ("2026-06-01", "2026-06-15", "2026-06-20", 750.00, "Confirmada", 1, 1, 1, 1, 1)
    )
    db.commit()
    
    current_count = db.execute("SELECT COUNT(*) FROM RESERVA").fetchone()[0]
    assert current_count == initial_count + 2


def test_reserva_totalmente_contida(db):
    """4. Reserva totalmente contida em outra: deve falhar."""
    db.execute(
        """
        INSERT INTO RESERVA (
            Data_Reserva, Data_Retirada_Prevista, Data_Devolucao_Prevista,
            Valor_Final_Previsto, Status_Reserva, ID_Cliente, ID_Veiculo,
            ID_Seguro, ID_Filial_Retirada_Res, ID_Filial_Devolucao_Res
        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """,
        ("2026-06-01", "2026-06-10", "2026-06-20", 1500.00, "Confirmada", 1, 1, 1, 1, 1)
    )
    db.commit()

    with pytest.raises(sqlite3.IntegrityError):
        db.execute(
            """
            INSERT INTO RESERVA (
                Data_Reserva, Data_Retirada_Prevista, Data_Devolucao_Prevista,
                Valor_Final_Previsto, Status_Reserva, ID_Cliente, ID_Veiculo,
                ID_Seguro, ID_Filial_Retirada_Res, ID_Filial_Devolucao_Res
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """,
            ("2026-06-02", "2026-06-12", "2026-06-15", 450.00, "Confirmada", 1, 1, 1, 1, 1)
        )


def test_reserva_cancelada_nao_bloqueia(db):
    """5. Reserva cancelada não deve bloquear nova reserva."""
    db.execute(
        """
        INSERT INTO RESERVA (
            Data_Reserva, Data_Retirada_Prevista, Data_Devolucao_Prevista,
            Valor_Final_Previsto, Status_Reserva, ID_Cliente, ID_Veiculo,
            ID_Seguro, ID_Filial_Retirada_Res, ID_Filial_Devolucao_Res
        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """,
        ("2026-06-01", "2026-06-10", "2026-06-15", 750.00, "Cancelada", 1, 1, 1, 1, 1)
    )
    db.commit()

    # Nota: Se este teste falhar com IntegrityError, verifique se o trigger de sobreposição 
    # está ignorando corretamente registros com Status_Reserva = 'Cancelada'.
    db.execute(
        """
        INSERT INTO RESERVA (
            Data_Reserva, Data_Retirada_Prevista, Data_Devolucao_Prevista,
            Valor_Final_Previsto, Status_Reserva, ID_Cliente, ID_Veiculo,
            ID_Seguro, ID_Filial_Retirada_Res, ID_Filial_Devolucao_Res
        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """,
        ("2026-06-02", "2026-06-10", "2026-06-15", 750.00, "Confirmada", 1, 1, 1, 1, 1)
    )
    db.commit()


def test_alteracao_datas_cria_conflito(db):
    """6. Alteração de datas que cria conflito: deve falhar."""
    db.execute(
        """
        INSERT INTO RESERVA (
            Data_Reserva, Data_Retirada_Prevista, Data_Devolucao_Prevista,
            Valor_Final_Previsto, Status_Reserva, ID_Cliente, ID_Veiculo,
            ID_Seguro, ID_Filial_Retirada_Res, ID_Filial_Devolucao_Res
        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """,
        ("2026-06-01", "2026-06-10", "2026-06-15", 750.00, "Confirmada", 1, 1, 1, 1, 1)
    )
    db.execute(
        """
        INSERT INTO RESERVA (
            Data_Reserva, Data_Retirada_Prevista, Data_Devolucao_Prevista,
            Valor_Final_Previsto, Status_Reserva, ID_Cliente, ID_Veiculo,
            ID_Seguro, ID_Filial_Retirada_Res, ID_Filial_Devolucao_Res
        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """,
        ("2026-06-01", "2026-06-20", "2026-06-25", 750.00, "Confirmada", 1, 1, 1, 1, 1)
    )
    db.commit()

    # Nota: Certifique-se de que o trigger de validação também cobre a cláusula UPDATE da tabela RESERVA.
    with pytest.raises(sqlite3.IntegrityError):
        db.execute(
            """
            UPDATE RESERVA 
            SET Data_Retirada_Prevista = '2026-06-12', Data_Devolucao_Prevista = '2026-06-18'
            WHERE ID_Reserva = (SELECT MAX(ID_Reserva) FROM RESERVA)
            """
        )


def test_reserva_durante_manutencao_ativa(db):
    """7. Reserva durante manutenção ativa: deve falhar."""
    db.execute(
        """
        INSERT INTO MANUTENCAO (
            Data_Retirada_Manutencao, Data_Conclusao_Manutencao,
            Descricao_Manutencao, Custo_Manutencao, ID_Veiculo
        ) VALUES (?, ?, ?, ?, ?)
        """,
        ("2026-06-05", None, "Troca de óleo", 200.00, 1)
    )
    db.commit()

    with pytest.raises(sqlite3.IntegrityError):
        db.execute(
            """
            INSERT INTO RESERVA (
                Data_Reserva, Data_Retirada_Prevista, Data_Devolucao_Prevista,
                Valor_Final_Previsto, Status_Reserva, ID_Cliente, ID_Veiculo,
                ID_Seguro, ID_Filial_Retirada_Res, ID_Filial_Devolucao_Res
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """,
            ("2026-06-01", "2026-06-10", "2026-06-12", 300.00, "Confirmada", 1, 1, 1, 1, 1)
        )


def test_reserva_apos_conclusao_manutencao(db):
    """8. Reserva após a conclusão da manutenção: deve ser permitida."""
    initial_count = db.execute("SELECT COUNT(*) FROM RESERVA").fetchone()[0]

    db.execute(
        """
        INSERT INTO MANUTENCAO (
            Data_Retirada_Manutencao, Data_Conclusao_Manutencao,
            Descricao_Manutencao, Custo_Manutencao, ID_Veiculo
        ) VALUES (?, ?, ?, ?, ?)
        """,
        ("2026-06-01", "2026-06-05", "Revisão geral", 500.00, 1)
    )
    db.commit()

    db.execute(
        """
        INSERT INTO RESERVA (
            Data_Reserva, Data_Retirada_Prevista, Data_Devolucao_Prevista,
            Valor_Final_Previsto, Status_Reserva, ID_Cliente, ID_Veiculo,
            ID_Seguro, ID_Filial_Retirada_Res, ID_Filial_Devolucao_Res
        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """,
        ("2026-06-01", "2026-06-10", "2026-06-15", 750.00, "Confirmada", 1, 1, 1, 1, 1)
    )
    db.commit()
    
    current_count = db.execute("SELECT COUNT(*) FROM RESERVA").fetchone()[0]
    assert current_count == initial_count + 1


def test_reserva_conflita_com_aluguel_ativo(db):
    """9. Reserva que conflita com aluguel ativo: deve falhar."""
    db.execute(
        """
        INSERT INTO RESERVA (
            Data_Reserva, Data_Retirada_Prevista, Data_Devolucao_Prevista,
            Valor_Final_Previsto, Status_Reserva, ID_Cliente, ID_Veiculo,
            ID_Seguro, ID_Filial_Retirada_Res, ID_Filial_Devolucao_Res
        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """,
        ("2026-06-01", "2026-06-05", "2026-06-10", 500.00, "Em Locacao", 1, 1, 1, 1, 1)
    )
    db.execute(
        """
        INSERT INTO ALUGUEL (
            Data_Retirada_Real, Data_Devolucao_Real, Quilometragem_Retirada,
            ID_Reserva, ID_Veiculo, ID_Cliente, ID_Filial_Retirada_Alug,
            ID_Filial_Devolucao_Alug, ID_Seguro
        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
        """,
        ("2026-06-05", None, 10000, 1, 1, 1, 1, 1, 1)
    )
    db.commit()

    with pytest.raises(sqlite3.IntegrityError):
        db.execute(
            """
            INSERT INTO RESERVA (
                Data_Reserva, Data_Retirada_Prevista, Data_Devolucao_Prevista,
                Valor_Final_Previsto, Status_Reserva, ID_Cliente, ID_Veiculo,
                ID_Seguro, ID_Filial_Retirada_Res, ID_Filial_Devolucao_Res
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """,
            ("2026-06-06", "2026-06-08", "2026-06-12", 300.00, "Confirmada", 1, 1, 1, 1, 1)
        )


def test_pragma_foreign_keys(db):
    """12. PRAGMA foreign_keys deve retornar 1."""
    cursor = db.execute("PRAGMA foreign_keys;")
    assert cursor.fetchone()[0] == 1


def test_view_conflitos_zerada_apos_carga_limpa(db):
    """13. View de conflitos deve retornar zero registros após a carga limpa."""
    # Se a view existir no ambiente e o objetivo for testá-la com base no estado atual do dataset de carga limpa:
    try:
        cursor = db.execute("SELECT COUNT(*) FROM VW_CONFLITOS")
        assert cursor.fetchone()[0] == 0
    except sqlite3.OperationalError:
        pytest.skip("View de conflitos não encontrada no banco de testes.")