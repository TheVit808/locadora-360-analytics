from pathlib import Path
import sqlite3
import pandas as pd

ROOT = Path(__file__).resolve().parents[2]
DB = ROOT / "data" / "locadora_commercial.db"


def main():
    con = sqlite3.connect(DB)
    checks = {
        "eventos_sem_cliente": """
            SELECT COUNT(*) FROM FATO_FUNIL_EVENTO f
            LEFT JOIN CLIENTE c ON c.ID_Cliente = f.ID_Cliente
            WHERE c.ID_Cliente IS NULL
        """,
        "reservas_sem_evento_reserva": """
            SELECT COUNT(*) FROM RESERVA r
            WHERE NOT EXISTS (
                SELECT 1 FROM FATO_FUNIL_EVENTO f
                WHERE f.ID_Reserva = r.ID_Reserva
                  AND f.Tipo_Evento = 'RESERVA'
            )
        """,
        "campanhas_sem_custo": """
            SELECT COUNT(*) FROM DIM_CAMPANHA c
            LEFT JOIN FATO_CAMPANHA_CUSTO x ON x.ID_Campanha = c.ID_Campanha
            WHERE x.ID_Campanha IS NULL
        """,
        "jornadas_reserva_sem_cotacao": """
            SELECT COUNT(*) FROM (
                SELECT Journey_ID
                FROM FATO_FUNIL_EVENTO
                GROUP BY Journey_ID
                HAVING SUM(Tipo_Evento = 'RESERVA') > 0
                   AND SUM(Tipo_Evento = 'COTACAO') = 0
            )
        """,
    }
    for name, query in checks.items():
        value = con.execute(query).fetchone()[0]
        print(f"{name}: {value}")
        if value:
            raise SystemExit(f"Falha de qualidade: {name}")
    con.close()


if __name__ == "__main__":
    main()