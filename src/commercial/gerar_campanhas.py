from pathlib import Path
import sqlite3
import pandas as pd

ROOT = Path(__file__).resolve().parents[2]
DB = ROOT / "data" / "locadora_commercial.db"
SCHEMA = ROOT / "database" / "schema" / "003_trilha_b_commercial.sql"


def connect():
    con = sqlite3.connect(DB)
    con.execute("PRAGMA foreign_keys = ON")
    return con



def insert_or_ignore(table, conn, keys, data_iter):
    data = list(data_iter)

    if not data:
        return 0

    placeholders = ",".join(["?"] * len(keys))
    columns = ",".join(f'"{key}"' for key in keys)

    sql = (
        f'INSERT OR IGNORE INTO "{table.name}" '
        f'({columns}) VALUES ({placeholders})'
    )

    # conn é um cursor SQLite fornecido pelo Pandas.
    conn.executemany(sql, data)

    inseridos = conn.rowcount
    print(
        f"{table.name}: {inseridos} registro(s) inserido(s) "
        f"de {len(data)} recebido(s)."
    )

    return inseridos



def main():
    con = connect()

    print("Banco utilizado:", DB.resolve())
    print("Banco existe:", DB.exists())

    con.executescript(SCHEMA.read_text(encoding="utf-8"))

    print("Registros atuais em DIM_CANAL:")

    print(pd.read_sql_query(
        "SELECT * FROM DIM_CANAL ORDER BY ID_Canal",
        con
    ))

    canais = pd.DataFrame([
        (1, "Site Organico", "ORGANICO"),
        (2, "Google Ads", "PAGO"),
        (3, "Meta Ads", "PAGO"),
        (4, "Parceiros", "PARCERIA"),
        (5, "Balcao", "DIRETO"),
    ], columns=["ID_Canal", "Nome_Canal", "Tipo_Canal"])

    canais.to_sql(
        "DIM_CANAL",
        con,
        if_exists="append",
        index=False,
        method=insert_or_ignore
    )

    print("Registros após a carga:")

    con.commit()

    print(pd.read_sql_query(
        "SELECT * FROM DIM_CANAL ORDER BY ID_Canal",
        con
    ))

    filiais = pd.read_sql_query("SELECT ID_Filial FROM FILIAL ORDER BY ID_Filial", con)
    categorias = pd.read_sql_query("SELECT ID_Categoria FROM CATEGORIA ORDER BY ID_Categoria", con)

    campanhas = pd.DataFrame([
        (101, "Semana Economica", "2025-01-10", "2025-02-28", 1, 1, 2,
         "Novos clientes", "DESCONTO", .10, 18000, "COTACAO_RESERVA",
         "Primeiro toque pago recebe a atribuição"),
        (102, "SUV Ferias", "2025-06-01", "2025-07-31", 2, 3, 3,
         "Familias e lazer", "UPGRADE", 0, 24000, "RESERVA_RETIRADA",
         "Último toque antes da reserva"),
        (103, "Corporativo Parceiros", "2025-03-01", "2025-05-31", 3, None, 4,
         "Clientes corporativos sintéticos", "DIARIA_GRATIS", 0, 15000, "RECEITA_LIQUIDA",
         "Código de parceiro informado na cotação"),
        (104, "Retencao Clientes", "2025-09-01", "2025-10-31", None, None, 1,
         "Clientes com uma locação anterior", "FIDELIDADE", .05, 12000, "RECOMPRA",
         "Cliente elegível exposto à campanha"),
    ], columns=[
        "ID_Campanha", "Nome_Campanha", "Data_Inicio", "Data_Fim", "ID_Filial",
        "ID_Categoria", "ID_Canal", "Publico_Alvo", "Tipo_Incentivo",
        "Percentual_Desconto", "Custo_Campanha", "KPI_Primario", "Premissa_Atribuicao"
    ])

    campanhas.to_sql("DIM_CAMPANHA", con, if_exists="append", index=False, method=insert_or_ignore)

    custos = pd.DataFrame([
        (101, 12000, 4000, 2000),
        (102, 16000, 5000, 3000),
        (103, 7000, 5000, 3000),
        (104, 6000, 4000, 2000),
    ], columns=["ID_Campanha", "Custo_Midia", "Custo_Beneficio", "Custo_Operacional"])
    
    custos.to_sql("FATO_CAMPANHA_CUSTO", con, if_exists="append", index=False, method=insert_or_ignore)
    
    con.commit()
    con.close()


if __name__ == "__main__":
    main()