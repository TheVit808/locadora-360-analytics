from pathlib import Path
import sqlite3
import uuid
import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parents[2]
DB = ROOT / "data" / "locadora_commercial.db"
OUT = ROOT / "data" / "staging" / "eventos_funil.csv"
RNG = np.random.default_rng(20261019)

def main():
    con = sqlite3.connect(DB)
    con.execute("PRAGMA foreign_keys = ON")
    
    clientes = pd.read_sql_query("SELECT ID_Cliente FROM CLIENTE", con)
    reservas = pd.read_sql_query(
        """
        SELECT
            r.ID_Reserva, r.ID_Cliente, r.ID_Veiculo,
            r.ID_Filial_Retirada_Res AS ID_Filial,
            r.Data_Reserva, r.Data_Retirada_Prevista,
            r.Data_Devolucao_Prevista,
            v.ID_Modelo, m.ID_Categoria,
            c.Valor_Diaria
        FROM RESERVA r
        JOIN VEICULO v ON v.ID_Veiculo = r.ID_Veiculo
        JOIN MODELO m ON m.ID_Modelo = v.ID_Modelo
        JOIN CATEGORIA c ON c.ID_Categoria = m.ID_Categoria
        """,
        con,
    )
    
    print(f"Linhas em RESERVA com joins válidos: {len(reservas)}")
    
    canais = pd.read_sql_query("SELECT ID_Canal FROM DIM_CANAL", con)
    campanhas = pd.read_sql_query(
        "SELECT ID_Campanha, Data_Inicio, Data_Fim, ID_Filial, ID_Categoria, ID_Canal FROM DIM_CAMPANHA",
        con,
    )
    
    rows = []
    event_id = 1
    def add(**kwargs):
        nonlocal event_id
        rows.append({"ID_Evento": event_id, **kwargs})
        event_id += 1

    # Jornadas não convertidas
    for _ in range(7206):
        customer = int(RNG.choice(clientes.ID_Cliente))
        channel = int(RNG.choice(canais.ID_Canal))
        day = pd.Timestamp("2025-01-01") + pd.Timedelta(days=int(RNG.integers(0, 365)))
        journey = str(uuid.uuid4())
        campaign = int(RNG.choice(campanhas.ID_Campanha)) if RNG.random() < .45 else None
        category = int(RNG.integers(1, 6))
        branch = int(RNG.integers(1, 11))
        add(Journey_ID=journey, ID_Cliente=customer, ID_Canal=channel,
            ID_Campanha=campaign, ID_Filial=branch, ID_Categoria=category,
            ID_Veiculo=None, ID_Reserva=None, Tipo_Evento="PESQUISA",
            Data_Evento=day.isoformat(), Valor_Cotacao=None, Valor_Bruto=None,
            Desconto=0, Receita_Liquida_Estimada=0, Dispositivo="web",
            Origem_Dado="sintetico")
        if RNG.random() < .83:
            quote_day = day + pd.Timedelta(hours=int(RNG.integers(1, 72)))
            quote = float(RNG.choice([80, 120, 180, 200, 450]) * RNG.integers(2, 8))
            add(Journey_ID=journey, ID_Cliente=customer, ID_Canal=channel,
                ID_Campanha=campaign, ID_Filial=branch, ID_Categoria=category,
                ID_Veiculo=None, ID_Reserva=None, Tipo_Evento="COTACAO",
                Data_Evento=quote_day.isoformat(), Valor_Cotacao=quote,
                Valor_Bruto=quote, Desconto=0, Receita_Liquida_Estimada=0,
                Dispositivo="web", Origem_Dado="sintetico")

    # Jornadas convertidas
    for row in reservas.itertuples(index=False):
        journey = str(uuid.uuid4())
        channel = int(RNG.choice(canais.ID_Canal))
        matching = campanhas[
            (campanhas.ID_Canal == channel)
            & ((campanhas.ID_Filial.isna()) | (campanhas.ID_Filial == row.ID_Filial))
            & ((campanhas.ID_Categoria.isna()) | (campanhas.ID_Categoria == row.ID_Categoria))
        ]
        campaign = int(RNG.choice(matching.ID_Campanha)) if len(matching) and RNG.random() < .65 else None
        start = pd.Timestamp(row.Data_Reserva)
        pickup = pd.Timestamp(row.Data_Retirada_Prevista)
        dropoff = pd.Timestamp(row.Data_Devolucao_Prevista)
        days = max(1, (dropoff - pickup).days)
        gross = float(row.Valor_Diaria * days)
        discount = float(gross * RNG.choice([0, 0, 0.05, 0.10]))
        net = gross - discount
        
        add(Journey_ID=journey, ID_Cliente=int(row.ID_Cliente), ID_Canal=channel,
            ID_Campanha=campaign, ID_Filial=int(row.ID_Filial),
            ID_Categoria=int(row.ID_Categoria), ID_Veiculo=int(row.ID_Veiculo),
            ID_Reserva=int(row.ID_Reserva), Tipo_Evento="PESQUISA",
            Data_Evento=(start - pd.Timedelta(days=int(RNG.integers(1, 14)))).isoformat(),
            Valor_Cotacao=None, Valor_Bruto=None, Desconto=0,
            Receita_Liquida_Estimada=0, Dispositivo="web", Origem_Dado="sintetico")
        
        add(Journey_ID=journey, ID_Cliente=int(row.ID_Cliente), ID_Canal=channel,
            ID_Campanha=campaign, ID_Filial=int(row.ID_Filial),
            ID_Categoria=int(row.ID_Categoria), ID_Veiculo=int(row.ID_Veiculo),
            ID_Reserva=int(row.ID_Reserva), Tipo_Evento="COTACAO",
            Data_Evento=(start - pd.Timedelta(days=int(RNG.integers(0, 5)))).isoformat(),
            Valor_Cotacao=gross, Valor_Bruto=gross, Desconto=discount,
            Receita_Liquida_Estimada=net, Dispositivo="web", Origem_Dado="sintetico")
        
        add(Journey_ID=journey, ID_Cliente=int(row.ID_Cliente), ID_Canal=channel,
            ID_Campanha=campaign, ID_Filial=int(row.ID_Filial),
            ID_Categoria=int(row.ID_Categoria), ID_Veiculo=int(row.ID_Veiculo),
            ID_Reserva=int(row.ID_Reserva), Tipo_Evento="RESERVA",
            Data_Evento=start.isoformat(), Valor_Cotacao=gross,
            Valor_Bruto=gross, Desconto=discount,
            Receita_Liquida_Estimada=net, Dispositivo="web", Origem_Dado="sintetico")
        
        if RNG.random() < .86:
            add(Journey_ID=journey, ID_Cliente=int(row.ID_Cliente), ID_Canal=channel,
                ID_Campanha=campaign, ID_Filial=int(row.ID_Filial),
                ID_Categoria=int(row.ID_Categoria), ID_Veiculo=int(row.ID_Veiculo),
                ID_Reserva=int(row.ID_Reserva), Tipo_Evento="RETIRADA",
                Data_Evento=(pickup + pd.Timedelta(hours=10)).isoformat(),
                Valor_Cotacao=gross, Valor_Bruto=gross, Desconto=discount,
                Receita_Liquida_Estimada=net, Dispositivo="balcao", Origem_Dado="sintetico")
            if RNG.random() < .94:
                add(Journey_ID=journey, ID_Cliente=int(row.ID_Cliente), ID_Canal=channel,
                    ID_Campanha=campaign, ID_Filial=int(row.ID_Filial),
                    ID_Categoria=int(row.ID_Categoria), ID_Veiculo=int(row.ID_Veiculo),
                    ID_Reserva=int(row.ID_Reserva), Tipo_Evento="DEVOLUCAO",
                    Data_Evento=(dropoff + pd.Timedelta(hours=18)).isoformat(),
                    Valor_Cotacao=gross, Valor_Bruto=gross, Desconto=discount,
                    Receita_Liquida_Estimada=net, Dispositivo="balcao", Origem_Dado="sintetico")
        else:
            add(Journey_ID=journey, ID_Cliente=int(row.ID_Cliente), ID_Canal=channel,
                ID_Campanha=campaign, ID_Filial=int(row.ID_Filial),
                ID_Categoria=int(row.ID_Categoria), ID_Veiculo=int(row.ID_Veiculo),
                ID_Reserva=int(row.ID_Reserva), Tipo_Evento="NO_SHOW",
                Data_Evento=pickup.isoformat(), Valor_Cotacao=gross,
                Valor_Bruto=gross, Desconto=discount,
                Receita_Liquida_Estimada=0, Dispositivo="balcao", Origem_Dado="sintetico")

    events = pd.DataFrame(rows)
    
    # Converte colunas com nulos para o tipo object para que o SQLite grave inteiros puros e NULLs corretos
    for col in ["ID_Reserva", "ID_Veiculo", "ID_Campanha"]:
        if col in events.columns:
            events[col] = events[col].astype(object).where(events[col].notna(), None)

    OUT.parent.mkdir(parents=True, exist_ok=True)
    events.to_csv(OUT, index=False)
    (ROOT / "data" / "marts").mkdir(parents=True, exist_ok=True)
    events.to_parquet(ROOT / "data" / "marts" / "fato_eventos_funil.parquet", index=False)
    events.to_sql("FATO_FUNIL_EVENTO", con, if_exists="replace", index=False)
    con.commit()
    con.close()
    print(f"Total de eventos gerados e gravados: {len(events):,}")

if __name__ == "__main__":
    main()