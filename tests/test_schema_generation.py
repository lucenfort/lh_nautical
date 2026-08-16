import pytest
import re
from pathlib import Path

def test_script_1_gerar_schema_pure_python(project_paths):
    """
    Garante que 1_gerar_schema.py utiliza exclusivamente Python padrão e
    NÃO importa bibliotecas proibidas (pandas, polars, dask, pyspark).
    """
    script_path = project_paths["root"] / "src" / "1_gerar_schema.py"
    assert script_path.exists(), "Script 1_gerar_schema.py não encontrado"
    
    code = script_path.read_text(encoding="utf-8")
    
    proibidos = ["pandas", "polars", "dask", "pyspark"]
    for p in proibidos:
        match = re.search(rf"\b(import\s+{p}|from\s+{p}\s+import)\b", code)
        assert match is None, f"VIOLAÇÃO: Import proibido de '{p}' detectado em 1_gerar_schema.py!"

def test_generated_schema_sql_content(project_paths):
    """Garante que sql/schema.sql foi gerado e contém definições DDL válidas com tipagem correta."""
    schema_path = project_paths["sql"] / "schema.sql"
    assert schema_path.exists(), "Arquivo sql/schema.sql não encontrado"
    
    sql_text = schema_path.read_text(encoding="utf-8")
    assert "CREATE TABLE customers" in sql_text
    assert "CREATE TABLE orders" in sql_text
    assert "CREATE TABLE order_items" in sql_text
    assert "CREATE TABLE payments" in sql_text
    
    # Validação de tipagem corrigida: quantity e installments não podem ser VARCHAR
    assert re.search(r"quantity\s+INTEGER", sql_text), "order_items.quantity deve ser INTEGER"
    assert re.search(r"installments\s+INTEGER", sql_text), "payments.installments deve ser INTEGER"

