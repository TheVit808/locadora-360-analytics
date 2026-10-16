import shutil
from pathlib import Path
import pytest
from src.db import connect

ROOT = Path(__file__).resolve().parents[1]
SEED = ROOT / "data" / "raw_sample" / "DB_LOCADORA.seed.db"

@pytest.fixture
def db(tmp_path):
    target = tmp_path / "test.db"
    shutil.copy(SEED, target)
    con = connect(target)
    con.executescript(
        (ROOT / "database" / "schema" / "002_trilha_a_integridade.sql")
        .read_text(encoding="utf-8")
    )
    con.executescript(
        (ROOT / "database" / "triggers" / "integridade_reserva.sql")
        .read_text(encoding="utf-8")
    )
    yield con
    con.close()