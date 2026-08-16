import pytest
import pandas as pd
from pathlib import Path

def test_raw_csv_files_count(project_paths):
    """Garante que todos os 24 arquivos CSV brutos estão presentes."""
    csv_files = list(project_paths["raw"].glob("*.csv"))
    assert len(csv_files) == 24, f"Esperado 24 CSVs brutos, encontrado: {len(csv_files)}"

def test_central_tables_row_counts(project_paths):
    """Validação: Soma das 4 tabelas centrais = 251.864 registros."""
    tabelas_esperadas = {
        "customers.csv": 2000,
        "orders.csv": 48998,
        "order_items.csv": 147320,
        "payments.csv": 53546
    }
    
    total_linhas = 0
    for csv_name, expected_count in tabelas_esperadas.items():
        csv_file = project_paths["raw"] / csv_name
        assert csv_file.exists(), f"Arquivo {csv_name} não encontrado"
        df = pd.read_csv(csv_file)
        assert len(df) == expected_count, f"{csv_name} possui {len(df)} linhas, esperado {expected_count}"
        total_linhas += len(df)
        
    assert total_linhas == 251864, f"Soma acumulada deu {total_linhas}, esperado 251864"

def test_orders_total_mean(df_orders):
    """Validação: Média do total de orders = 28704.99."""
    media_total = df_orders["total"].mean()
    assert round(media_total, 2) == 28704.99, f"Média calculada: {media_total:.2f}, esperada: 28704.99"

def test_orders_iqr_outliers(df_orders):
    """Validação: Limite IQR e contagem de outliers legítimos."""
    q1 = df_orders["total"].quantile(0.25)
    q3 = df_orders["total"].quantile(0.75)
    iqr = q3 - q1
    limite_superior = q3 + 1.5 * iqr
    outliers = df_orders[df_orders["total"] > limite_superior]
    
    assert abs(limite_superior - 82598.0) < 2.0, f"Limite IQR: {limite_superior:.2f}, esperado ~82598"
    assert len(outliers) in [452, 453], f"Outliers encontrados: {len(outliers)}, esperado 452"
