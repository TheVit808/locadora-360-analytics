from pathlib import Path
import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parents[2]
INPUT = ROOT / "data" / "marts" / "fato_eventos_funil.parquet"
OUTPUT = ROOT / "data" / "staging" / "simulacoes_campanhas.csv"
RNG = np.random.default_rng(20261019)


def main():
    events = pd.read_parquet(INPUT)
    reservations = events[events["Tipo_Evento"] == "RESERVA"].copy()
    reservations["Valor_Base"] = reservations["Valor_Bruto"].fillna(0)

    scenarios = []
    for discount in [0.00, 0.05, 0.10, 0.15]:
        for upgrade_cost in [0.00, 25.00, 50.00]:
            for conversion_lift in [0.00, 0.05, 0.10]:
                probability = np.clip(
                    0.35 + conversion_lift - discount * 0.20,
                    0.01,
                    0.95,
                )
                expected_reservations = len(reservations) * probability
                expected_revenue = (
                    expected_reservations
                    * reservations["Valor_Base"].mean()
                    * (1 - discount)
                    - expected_reservations * upgrade_cost
                )
                scenarios.append({
                    "Desconto": discount,
                    "Custo_Upgrade": upgrade_cost,
                    "Lift_Conversao": conversion_lift,
                    "Probabilidade_Conversao": probability,
                    "Reservas_Esperadas": expected_reservations,
                    "Receita_Esperada": expected_revenue,
                })

    result = pd.DataFrame(scenarios)
    result.to_csv(OUTPUT, index=False)
    print(result.sort_values("Receita_Esperada", ascending=False).head(10).to_string(index=False))


if __name__ == "__main__":
    main()