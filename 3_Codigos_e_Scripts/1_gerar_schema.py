#!/usr/bin/env python3
"""
===============================================================================
DESAFIO LH NAUTICAL — QUESTÃO 2: GERADOR DE SCHEMA DDL (PYTHON 3 PURO)
Autor: Luciano Silva de Arruda
Programa: Lighthouse 2026 (Indicium AI)
===============================================================================
Premissas obrigatórias:
  - Utilizar APENAS Python 3 puro e bibliotecas nativas (csv, os, datetime).
  - PROIBIDO usar pandas, polars, dask.
  - Banco de destino: PostgreSQL.
  - Considerar TODOS os 24 CSVs como fontes.

Entrega:
  - Arquivo `schema.sql` com as instruções CREATE TABLE para cada CSV.
===============================================================================
"""

import csv
import os
import re
import sys
from datetime import datetime
from pathlib import Path

# ---------------------------------------------------------------------------
# Caminhos do projeto
# ---------------------------------------------------------------------------
PROJECT_ROOT: Path = Path(__file__).resolve().parent.parent
RAW_DIR: Path = PROJECT_ROOT / "data" / "raw"
OUTPUT_DIR: Path = Path(__file__).resolve().parent
SCHEMA_OUTPUT: Path = OUTPUT_DIR / "schema.sql"

# ---------------------------------------------------------------------------
# Número máximo de linhas amostradas para inferência de tipo
# ---------------------------------------------------------------------------
MAX_SAMPLE_ROWS: int = 5000


def inferir_tipo_valor(valor: str) -> str:
    """
    Infere o tipo PostgreSQL de um único valor textual.

    A lógica de prioridade é:
      1. Vazio/nulo → 'NULL' (não define tipo sozinho)
      2. Boolean ('true', 'false') → 'BOOLEAN'
      3. Inteiro puro (sem ponto decimal) → 'INTEGER'
      4. Decimal (com ponto) → 'NUMERIC'
      5. Timestamp (YYYY-MM-DD HH:MM:SS) → 'TIMESTAMP'
      6. Date (YYYY-MM-DD) → 'DATE'
      7. Qualquer outro → 'VARCHAR'

    Args:
        valor: String representando o valor de uma célula do CSV.

    Returns:
        String com o tipo PostgreSQL inferido.
    """
    val: str = valor.strip()

    # Nulo ou vazio
    if val == "" or val.lower() in ("null", "none", "na", "n/a"):
        return "NULL"

    # Boolean
    if val.lower() in ("true", "false", "t", "f"):
        return "BOOLEAN"

    # Inteiro
    if re.match(r"^-?\d+$", val):
        if len(val) > 18:
            return "VARCHAR"
        num: int = int(val)
        if -2147483648 <= num <= 2147483647:
            return "INTEGER"
        else:
            return "BIGINT"

    # Decimal / Numérico
    if re.match(r"^-?\d+\.\d+$", val):
        return "NUMERIC"

    # Timestamp (YYYY-MM-DD HH:MM:SS com variantes)
    if re.match(r"^\d{4}-\d{2}-\d{2}\s+\d{2}:\d{2}:\d{2}", val):
        return "TIMESTAMP"

    # Date (YYYY-MM-DD)
    if re.match(r"^\d{4}-\d{2}-\d{2}$", val):
        return "DATE"

    # Fallback: texto
    return "VARCHAR"


def resolver_tipo_coluna(tipos_encontrados: list[str], comprimento_max: int) -> str:
    """
    Resolve o tipo final de uma coluna com base nos tipos inferidos de
    seus valores amostrados.

    Regra de precedência (do mais restritivo ao mais genérico):
      BOOLEAN < INTEGER < BIGINT < NUMERIC < DATE < TIMESTAMP < VARCHAR

    Se houver conflito entre tipos numéricos e texto, VARCHAR prevalece.

    Args:
        tipos_encontrados: Lista de tipos inferidos de cada valor amostrado.
        comprimento_max: Comprimento máximo encontrado nos valores da coluna.

    Returns:
        String com o tipo PostgreSQL final.
    """
    # Remover NULLs — eles não definem tipo
    tipos_efetivos: list[str] = [t for t in tipos_encontrados if t != "NULL"]

    if not tipos_efetivos:
        # Coluna inteiramente nula → assumir VARCHAR
        return f"VARCHAR({max(comprimento_max, 50)})"

    tipos_set: set[str] = set(tipos_efetivos)

    # Se todos são iguais, retornar diretamente
    if len(tipos_set) == 1:
        tipo: str = tipos_set.pop()
        if tipo == "VARCHAR":
            # Arredondar comprimento para múltiplo de 50, mínimo 50
            tamanho: int = max(50, ((comprimento_max // 50) + 1) * 50)
            return f"VARCHAR({tamanho})"
        return tipo

    # Se há VARCHAR misturado com qualquer coisa, é VARCHAR
    if "VARCHAR" in tipos_set:
        tamanho = max(50, ((comprimento_max // 50) + 1) * 50)
        return f"VARCHAR({tamanho})"

    # Se há TIMESTAMP e DATE misturados → TIMESTAMP (mais abrangente)
    if "TIMESTAMP" in tipos_set and "DATE" in tipos_set:
        return "TIMESTAMP"

    # Se há apenas tipos temporais
    if tipos_set <= {"TIMESTAMP", "DATE"}:
        return "TIMESTAMP" if "TIMESTAMP" in tipos_set else "DATE"

    # Se há apenas tipos numéricos
    if tipos_set <= {"INTEGER", "BIGINT", "NUMERIC"}:
        if "NUMERIC" in tipos_set:
            return "NUMERIC"
        if "BIGINT" in tipos_set:
            return "BIGINT"
        return "INTEGER"

    # Se há BOOLEAN e numérico misturados → VARCHAR (ambíguo)
    if "BOOLEAN" in tipos_set and tipos_set & {"INTEGER", "BIGINT", "NUMERIC"}:
        tamanho = max(50, ((comprimento_max // 50) + 1) * 50)
        return f"VARCHAR({tamanho})"

    # Fallback
    tamanho = max(50, ((comprimento_max // 50) + 1) * 50)
    return f"VARCHAR({tamanho})"


def analisar_csv(filepath: Path) -> list[tuple[str, str]]:
    """
    Analisa um arquivo CSV e retorna a lista de colunas com seus tipos
    PostgreSQL inferidos.

    Args:
        filepath: Caminho absoluto do arquivo CSV.

    Returns:
        Lista de tuplas (nome_coluna, tipo_postgresql).
    """
    with open(filepath, "r", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        headers: list[str] = reader.fieldnames if reader.fieldnames else []

        if not headers:
            return []

        # Inicializar acumuladores para cada coluna
        tipos_por_coluna: dict[str, list[str]] = {col: [] for col in headers}
        comprimento_por_coluna: dict[str, int] = {col: 0 for col in headers}

        row_count: int = 0
        for row in reader:
            if row_count >= MAX_SAMPLE_ROWS:
                break
            for col in headers:
                val: str = row.get(col, "").strip()
                tipo_inferido: str = inferir_tipo_valor(val)
                tipos_por_coluna[col].append(tipo_inferido)
                if len(val) > comprimento_por_coluna[col]:
                    comprimento_por_coluna[col] = len(val)
            row_count += 1

    # Resolver tipo final de cada coluna
    resultado: list[tuple[str, str]] = []
    for col in headers:
        tipo_final: str = resolver_tipo_coluna(
            tipos_por_coluna[col],
            comprimento_por_coluna[col]
        )
        resultado.append((col, tipo_final))

    return resultado


def gerar_create_table(nome_tabela: str, colunas: list[tuple[str, str]]) -> str:
    """
    Gera o comando CREATE TABLE PostgreSQL para uma tabela.

    Args:
        nome_tabela: Nome da tabela (derivado do nome do CSV).
        colunas: Lista de tuplas (nome_coluna, tipo_postgresql).

    Returns:
        String contendo o comando DDL CREATE TABLE.
    """
    linhas_colunas: list[str] = []
    for nome_col, tipo_col in colunas:
        linhas_colunas.append(f"    {nome_col} {tipo_col}")

    colunas_ddl: str = ",\n".join(linhas_colunas)

    ddl: str = (
        f"-- Tabela: {nome_tabela}\n"
        f"DROP TABLE IF EXISTS {nome_tabela} CASCADE;\n"
        f"CREATE TABLE {nome_tabela} (\n"
        f"{colunas_ddl}\n"
        f");\n"
    )
    return ddl


def main() -> None:
    """
    Ponto de entrada principal.
    Lê todos os CSVs do diretório data/raw/, infere os tipos e gera o schema.sql.
    """
    print("=" * 80)
    print("🔧 QUESTÃO 2 — GERADOR DE SCHEMA DDL (PYTHON 3 PURO)")
    print(f"   Diretório de entrada: {RAW_DIR}")
    print(f"   Arquivo de saída:     {SCHEMA_OUTPUT}")
    print("=" * 80)

    if not RAW_DIR.exists():
        print(f"❌ ERRO: Diretório não encontrado: {RAW_DIR}")
        sys.exit(1)

    # Listar todos os CSVs em ordem alfabética
    csv_files: list[Path] = sorted(RAW_DIR.glob("*.csv"))

    if not csv_files:
        print("❌ ERRO: Nenhum arquivo CSV encontrado no diretório.")
        sys.exit(1)

    print(f"\n📄 {len(csv_files)} arquivos CSV encontrados.\n")

    # Gerar DDLs
    ddls: list[str] = []

    # Header do arquivo SQL
    header: str = (
        "-- =============================================================================\n"
        "-- DESAFIO LH NAUTICAL — SCHEMA DDL (PostgreSQL)\n"
        "-- Gerado automaticamente por: 1_gerar_schema.py (Python 3 Puro)\n"
        "-- Autor: Luciano Silva de Arruda\n"
        "-- Programa: Lighthouse 2026 (Indicium AI)\n"
        f"-- Data de geração: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n"
        f"-- Total de tabelas: {len(csv_files)}\n"
        "-- =============================================================================\n"
    )
    ddls.append(header)

    for csv_file in csv_files:
        nome_tabela: str = csv_file.stem  # Nome sem extensão
        print(f"   🔹 Analisando: {csv_file.name} → tabela `{nome_tabela}`")

        colunas: list[tuple[str, str]] = analisar_csv(csv_file)

        if not colunas:
            print(f"      ⚠️ Arquivo vazio ou sem cabeçalho. Pulando.")
            continue

        ddl: str = gerar_create_table(nome_tabela, colunas)
        ddls.append(ddl)

        # Log das colunas inferidas
        for nome_col, tipo_col in colunas:
            print(f"      {nome_col:<30} → {tipo_col}")
        print()

    # Escrever o arquivo schema.sql
    conteudo_sql: str = "\n".join(ddls)

    with open(SCHEMA_OUTPUT, "w", encoding="utf-8") as f:
        f.write(conteudo_sql)

    print(f"{'=' * 80}")
    print(f"✅ Arquivo gerado com sucesso: {SCHEMA_OUTPUT}")
    print(f"   Total de tabelas: {len(csv_files)}")
    print(f"{'=' * 80}")


if __name__ == "__main__":
    main()
