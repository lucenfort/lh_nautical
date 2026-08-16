import pytest
import pandas as pd
from pathlib import Path

@pytest.fixture(scope="session")
def project_paths():
    root = Path(__file__).resolve().parent.parent
    return {
        "root": root,
        "raw": root / "data" / "raw",
        "processed": root / "data" / "processed",
        "sql": root / "sql",
        "src": root / "src",
        "notebooks": root / "notebooks",
        "dashboard": root / "dashboard",
    }

@pytest.fixture(scope="session")
def df_orders(project_paths):
    orders_path = project_paths["raw"] / "orders.csv"
    assert orders_path.exists(), "Arquivo orders.csv não encontrado"
    return pd.read_csv(orders_path)
