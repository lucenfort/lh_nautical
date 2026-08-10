#!/usr/bin/env python3
"""
===============================================================================
DESAFIO LH NAUTICAL — QUESTÃO 3: INGESTÃO/CARGA BRUTA NO POSTGRESQL
Autor: Luciano Silva de Arruda
Programa: Lighthouse 2026 (Indicium AI)
===============================================================================
Premissas obrigatórias:
  - Carregar TODOS os CSVs no PostgreSQL.
  - Utilizar Python 3 (bibliotecas externas permitidas nesta questão).
  - NÃO fazer tratamentos (remoção de nulos, correção de caracteres especiais).
  - Carga bruta respeitando o schema criado na Q2.

Entrega:
  - Dados carregados no banco PostgreSQL `lhnautical`.
  - Validação Q3.2: soma de linhas de customers + orders + order_items + payments.
===============================================================================
"""

import os
import sys
import logging
from pathlib import Path

import psycopg2
from psycopg2 import sql

# ---------------------------------------------------------------------------
# Configuração de logging
# ---------------------------------------------------------------------------
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    datefmt="%H:%M:%S",
)
logger: logging.Logger = logging.getLogger(__name__)

# ---------------------------------------------------------------------------
# Caminhos do projeto
# ---------------------------------------------------------------------------
PROJECT_ROOT: Path = Path(__file__).resolve().parent.parent
RAW_DIR: Path = PROJECT_ROOT / "data" / "raw"
SCHEMA_FILE: Path = Path(__file__).resolve().parent / "schema.sql"

# ---------------------------------------------------------------------------
# Configuração do banco de dados PostgreSQL
# ---------------------------------------------------------------------------
DB_CONFIG: dict = {
    "host": "localhost",
    "port": 5432,
    "dbname": "lhnautical",
    "user": "postgres",
    "password": "postgres",
}

# ---------------------------------------------------------------------------
# Ordem de carregamento (dimensões antes de fatos, para respeitar
# eventuais dependências lógicas)
# ---------------------------------------------------------------------------
LOAD_ORDER: list[str] = [
    "attributes",
    "brands",
    "categories",
    "suppliers",
    "customers",
    "employees",
    "locations",
    "products",
    "product_variants",
    "variant_attribute_values",
    "product_suppliers",
    "addresses",
    "orders",
    "order_items",
    "payments",
    "fiscal_invoices",
    "purchase_orders",
    "purchase_order_items",
    "goods_receipts",
    "goods_receipt_items",
    "returns",
    "return_items",
    "stock_levels",
    "stock_movements",
]


def executar_schema(conn) -> None:
    """
    Executa o arquivo schema.sql para criar (ou recriar) as tabelas.

    Args:
        conn: Conexão ativa com o PostgreSQL.
    """
    logger.info(f"Executando schema: {SCHEMA_FILE}")

    with open(SCHEMA_FILE, "r", encoding="utf-8") as f:
        schema_sql: str = f.read()

    with conn.cursor() as cur:
        cur.execute(schema_sql)
    conn.commit()

    logger.info("✅ Schema executado com sucesso (24 tabelas criadas).")


def carregar_csv(conn, nome_tabela: str, filepath: Path) -> int:
    """
    Carrega um arquivo CSV no PostgreSQL usando COPY ... FROM STDIN.
    NÃO realiza nenhum tratamento nos dados (carga bruta).

    Args:
        conn: Conexão ativa com o PostgreSQL.
        nome_tabela: Nome da tabela de destino.
        filepath: Caminho do arquivo CSV.

    Returns:
        Número de linhas carregadas.
    """
    copy_sql: str = f"COPY {nome_tabela} FROM STDIN WITH CSV HEADER DELIMITER ',' NULL ''"

    with conn.cursor() as cur:
        with open(filepath, "r", encoding="utf-8") as f:
            cur.copy_expert(copy_sql, f)
        conn.commit()

        # Contar linhas inseridas
        cur.execute(f"SELECT COUNT(*) FROM {nome_tabela};")
        count: int = cur.fetchone()[0]

    return count


def validar_q32(conn) -> int:
    """
    Executa a query de validação da Q3.2:
    Soma total de linhas de customers + orders + order_items + payments.

    Args:
        conn: Conexão ativa com o PostgreSQL.

    Returns:
        Soma total das 4 tabelas.
    """
    query: str = """
    -- =============================================================================
    -- VALIDAÇÃO Q3.2 — Soma total de linhas
    -- =============================================================================
    SELECT
        (SELECT COUNT(*) FROM customers) +
        (SELECT COUNT(*) FROM orders) +
        (SELECT COUNT(*) FROM order_items) +
        (SELECT COUNT(*) FROM payments) AS total_linhas_acumulado;
    """

    with conn.cursor() as cur:
        cur.execute(query)
        total: int = cur.fetchone()[0]

    return total


def main() -> None:
    """Ponto de entrada principal do script de carga."""

    print("=" * 80)
    print("📥 QUESTÃO 3 — INGESTÃO/CARGA BRUTA NO POSTGRESQL")
    print(f"   Diretório de dados: {RAW_DIR}")
    print(f"   Banco de dados:     {DB_CONFIG['dbname']}@{DB_CONFIG['host']}:{DB_CONFIG['port']}")
    print("=" * 80)

    # Verificar diretório de dados
    if not RAW_DIR.exists():
        logger.error(f"Diretório não encontrado: {RAW_DIR}")
        sys.exit(1)

    # Conectar ao PostgreSQL
    try:
        conn = psycopg2.connect(**DB_CONFIG)
        logger.info("✅ Conexão com PostgreSQL estabelecida.")
    except psycopg2.Error as e:
        logger.error(f"Falha na conexão: {e}")
        sys.exit(1)

    try:
        # 1. Executar o schema (recriar tabelas)
        executar_schema(conn)

        # 2. Carregar cada CSV
        print(f"\n{'─' * 80}")
        print(f"{'Tabela':<30} {'Arquivo CSV':<30} {'Linhas':>10} {'Status'}")
        print(f"{'─' * 80}")

        total_geral: int = 0

        for nome_tabela in LOAD_ORDER:
            csv_file: Path = RAW_DIR / f"{nome_tabela}.csv"

            if not csv_file.exists():
                print(f"{nome_tabela:<30} {csv_file.name:<30} {'—':>10} ❌ NÃO ENCONTRADO")
                continue

            try:
                linhas: int = carregar_csv(conn, nome_tabela, csv_file)
                total_geral += linhas
                print(f"{nome_tabela:<30} {csv_file.name:<30} {linhas:>10,} ✅")
            except Exception as e:
                conn.rollback()
                print(f"{nome_tabela:<30} {csv_file.name:<30} {'ERRO':>10} ❌ {e}")

        print(f"{'─' * 80}")
        print(f"{'TOTAL GERAL':<60} {total_geral:>10,}")
        print(f"{'─' * 80}")

        # 3. Validação Q3.2
        total_q32: int = validar_q32(conn)
        print(f"\n{'=' * 80}")
        print(f"📋 VALIDAÇÃO Q3.2:")
        print(f"   customers + orders + order_items + payments = {total_q32:,}")
        print(f"{'=' * 80}")

    finally:
        conn.close()
        logger.info("Conexão com PostgreSQL encerrada.")


if __name__ == "__main__":
    main()
