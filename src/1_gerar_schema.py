#!/usr/bin/env python3
"""
===============================================================================
LH NAUTICAL — GERADOR DE SCHEMA POSTGRESQL DDL VIA INFERÊNCIA ESTATÍSTICA
Autor: Luciano Silva de Arruda
Projeto: LH Nautical — Plataforma de Engenharia de Dados & Analytics
===============================================================================
Premissas Obrigatórias:
  - Utilizar estritamente Python 3 puro e bibliotecas nativas da standard library.
  - PROIBIDO: pandas, polars, dask, pyspark.
  - Banco de Dados de Destino: PostgreSQL 16.
===============================================================================
"""

import csv
import os
import re
from datetime import datetime
from pathlib import Path

# Resolução de Caminhos
SRC_DIR = Path(__file__).resolve().parent
PROJECT_ROOT = SRC_DIR.parent
CSV_DIR = PROJECT_ROOT / "data" / "raw"
SQL_DIR = PROJECT_ROOT / "sql"
OUTPUT_SQL = SQL_DIR / "schema.sql"

SAMPLE_SIZE = 5000

# Expressões Regulares de Detecção de Padrões Numéricos e Temporais
RE_INTEGER = re.compile(r"^-?\d+$")
RE_NUMERIC = re.compile(r"^-?\d+[\.,]\d+$")
RE_DATE = re.compile(r"^\d{4}-\d{2}-\d{2}$")
RE_DATETIME = re.compile(
    r"^\d{4}-\d{2}-\d{2}[ T]\d{2}:\d{2}:\d{2}(\.\d+)?([+-]\d{2}:?\d{2}|Z)?$"
)
BOOLEAN_VALUES = {"true", "false", "t", "f"}


def inferir_tipo_valor(valor: str) -> str:
    """Classifica o tipo PostgreSQL de um valor textual unitário."""
    v = valor.strip()
    if not v or v.lower() in ("null", "none", "na", "n/a"):
        return "NULL"
    if v.lower() in BOOLEAN_VALUES:
        return "BOOLEAN"
    if RE_INTEGER.match(v):
        if len(v) > 18:
            return "VARCHAR"
        num = int(v)
        if -2147483648 <= num <= 2147483647:
            return "INTEGER"
        return "BIGINT"
    if RE_NUMERIC.match(v):
        return "NUMERIC"
    if RE_DATE.match(v):
        try:
            datetime.strptime(v, "%Y-%m-%d")
            return "DATE"
        except ValueError:
            pass
    if RE_DATETIME.match(v):
        return "TIMESTAMP"
    return "VARCHAR"


TYPE_HIERARCHY = {
    "NULL": 0,
    "BOOLEAN": 1,
    "INTEGER": 2,
    "BIGINT": 3,
    "NUMERIC": 4,
    "DATE": 5,
    "TIMESTAMP": 6,
    "VARCHAR": 7
}


def combinar_tipos(tipo_atual: str, novo_tipo: str) -> str:
    """Resolve a coerção hierárquica entre tipos observados em uma mesma coluna."""
    if tipo_atual == "NULL":
        return novo_tipo
    if novo_tipo == "NULL":
        return tipo_atual
    if tipo_atual == novo_tipo:
        return tipo_atual

    conjunto = {tipo_atual, novo_tipo}

    # Se houver mistura de booleano com numérico (ex: coluna com 0, 1 e 2+)
    if "BOOLEAN" in conjunto:
        if conjunto <= {"BOOLEAN", "INTEGER"}:
            return "INTEGER"
        if conjunto <= {"BOOLEAN", "BIGINT"}:
            return "BIGINT"
        if conjunto <= {"BOOLEAN", "NUMERIC"}:
            return "NUMERIC"
        return "VARCHAR"

    # Hierarquia numérica: INTEGER -> BIGINT -> NUMERIC
    if conjunto == {"INTEGER", "BIGINT"}:
        return "BIGINT"
    if conjunto <= {"INTEGER", "BIGINT", "NUMERIC"}:
        return "NUMERIC"

    # Hierarquia temporal: DATE -> TIMESTAMP
    if conjunto == {"DATE", "TIMESTAMP"}:
        return "TIMESTAMP"

    return "VARCHAR"


def analisar_csv(caminho_csv: Path, max_linhas: int = SAMPLE_SIZE) -> tuple[list[str], dict[str, str], dict[str, int]]:
    """Lê uma amostra do CSV e infere os tipos e comprimentos máximos das colunas."""
    with open(caminho_csv, mode="r", encoding="utf-8", errors="replace") as f:
        reader = csv.reader(f)
        try:
            cabecalhos = next(reader)
        except StopIteration:
            return [], {}, {}

        # Sanitização de cabeçalhos
        colunas = [c.strip().strip('"').replace("\ufeff", "") for c in cabecalhos]
        tipos = {col: "NULL" for col in colunas}
        max_len = {col: 0 for col in colunas}

        for i, linha in enumerate(reader):
            if i >= max_linhas:
                break
            for j, col in enumerate(colunas):
                val = linha[j] if j < len(linha) else ""
                t = inferir_tipo_valor(val)
                tipos[col] = combinar_tipos(tipos[col], t)
                if len(val) > max_len[col]:
                    max_len[col] = len(val)

    return colunas, tipos, max_len


def mapear_tipo_sql(coluna: str, tipo_inferido: str, max_len: int) -> str:
    """Converte o tipo inferido na definição formal de tipo de dado PostgreSQL."""
    col_lower = coluna.lower()

    # Campos específicos de documentos fiscais ou códigos de identificação longos
    if col_lower in ("tax_id", "cpf", "cnpj", "barcode_ean", "ncm_code"):
        if tipo_inferido in ("BIGINT", "INTEGER"):
            return "BIGINT" if max_len > 9 else tipo_inferido
        elif tipo_inferido == "VARCHAR":
            return f"VARCHAR({max(50, ((max_len // 50) + 1) * 50)})"
        return "BIGINT"

    if col_lower == "id" or col_lower.endswith("_id"):
        if tipo_inferido in ("INTEGER", "BIGINT"):
            return tipo_inferido
        return "INTEGER"

    if tipo_inferido == "NULL":
        return "VARCHAR(100)"
    if tipo_inferido == "BOOLEAN":
        return "BOOLEAN"
    if tipo_inferido == "INTEGER":
        return "INTEGER"
    if tipo_inferido == "BIGINT":
        return "BIGINT"
    if tipo_inferido == "NUMERIC":
        return "NUMERIC(15, 2)"
    if tipo_inferido == "DATE":
        return "DATE"
    if tipo_inferido == "TIMESTAMP":
        return "TIMESTAMP"

    # VARCHAR com dimensionamento proporcional
    if max_len <= 50:
        return "VARCHAR(50)"
    elif max_len <= 100:
        return "VARCHAR(100)"
    elif max_len <= 255:
        return "VARCHAR(255)"
    else:
        return "TEXT"


def gerar_ddl_tabela(nome_tabela: str, colunas: list[str], tipos: dict[str, str], max_lens: dict[str, int]) -> str:
    """Gera o bloco SQL DDL para uma tabela específica."""
    linhas_ddl = [f"DROP TABLE IF EXISTS {nome_tabela} CASCADE;", f"CREATE TABLE {nome_tabela} ("]
    def_colunas = []

    for col in colunas:
        tipo_sql = mapear_tipo_sql(col, tipos[col], max_lens[col])
        def_colunas.append(f"    {col:<30} {tipo_sql}")

    linhas_ddl.append(",\n".join(def_colunas))
    linhas_ddl.append(");\n")
    return "\n".join(linhas_ddl)


def executar():
    print("=" * 80)
    print("⚓ LH NAUTICAL — GERADOR DE SCHEMA DDL POSTGRESQL (PYTHON PURO)")
    print("=" * 80)
    print(f"Diretório de Entrada CSV: {CSV_DIR}")
    print(f"Arquivo DDL de Saída:    {OUTPUT_SQL}")

    SQL_DIR.mkdir(parents=True, exist_ok=True)
    arquivos_csv = sorted(CSV_DIR.glob("*.csv"))

    if not arquivos_csv:
        print(f"❌ Nenhum arquivo CSV encontrado em {CSV_DIR}")
        return

    ddls = [
        "-- =============================================================================",
        "-- LH NAUTICAL — SCHEMA RELACIONAL DDL POSTGRESQL 16",
        "-- Autor: Luciano Silva de Arruda",
        "-- Projeto: LH Nautical — Plataforma de Engenharia de Dados & Analytics",
        "-- =============================================================================\n"
    ]

    for csv_file in arquivos_csv:
        tabela = csv_file.stem
        cols, tipos, max_lens = analisar_csv(csv_file)
        if not cols:
            continue
        ddl = gerar_ddl_tabela(tabela, cols, tipos, max_lens)
        ddls.append(ddl)
        print(f"  • Tabela: {tabela:<30} -> {len(cols):>2} colunas mapeadas com sucesso.")

    OUTPUT_SQL.write_text("\n".join(ddls), encoding="utf-8")
    print("-" * 80)
    print(f"✅ Sucesso: {len(arquivos_csv)} tabelas geradas em '{OUTPUT_SQL}'.")
    print("=" * 80)


if __name__ == "__main__":
    executar()
