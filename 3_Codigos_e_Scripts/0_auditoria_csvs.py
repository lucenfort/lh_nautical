#!/usr/bin/env python3
"""
===============================================================================
DESAFIO LH NAUTICAL - SCRIPT DE AUDITORIA DOS ARQUIVOS CSV
Autor: Luciano Silva de Arruda
Programa: Lighthouse 2026 (Indicium AI)
===============================================================================
Etapa 1 — Verificação de presença e integridade dos 24 arquivos CSV brutos.
Este script NÃO utiliza pandas (apenas bibliotecas nativas Python 3).

Objetivo:
  - Confirmar a existência dos 24 CSVs esperados em data/raw/
  - Para cada arquivo: contar linhas, colunas e listar os cabeçalhos
  - Gerar um relatório de integridade no terminal
===============================================================================
"""

import csv
import os
import sys
from pathlib import Path

# ---------------------------------------------------------------------------
# Caminhos do projeto
# ---------------------------------------------------------------------------
PROJECT_ROOT: Path = Path(__file__).resolve().parent.parent
RAW_DIR: Path = PROJECT_ROOT / "data" / "raw"

# ---------------------------------------------------------------------------
# Lista canônica dos 24 CSVs esperados (conforme documentação do desafio)
# ---------------------------------------------------------------------------
EXPECTED_CSVS: list[str] = [
    "addresses.csv",
    "attributes.csv",
    "brands.csv",
    "categories.csv",
    "customers.csv",
    "employees.csv",
    "fiscal_invoices.csv",
    "goods_receipt_items.csv",
    "goods_receipts.csv",
    "locations.csv",
    "order_items.csv",
    "orders.csv",
    "payments.csv",
    "product_suppliers.csv",
    "product_variants.csv",
    "products.csv",
    "purchase_order_items.csv",
    "purchase_orders.csv",
    "return_items.csv",
    "returns.csv",
    "stock_levels.csv",
    "stock_movements.csv",
    "suppliers.csv",
    "variant_attribute_values.csv",
]


def auditar_csv(filepath: Path) -> dict:
    """
    Audita um único arquivo CSV e retorna um dicionário com:
      - nome: nome do arquivo
      - existe: bool
      - linhas: total de linhas de dados (excluindo cabeçalho)
      - colunas: total de colunas
      - headers: lista de nomes das colunas
      - tamanho_kb: tamanho em KB
      - encoding_ok: se o arquivo pode ser lido como UTF-8

    Args:
        filepath: Caminho absoluto do arquivo CSV.

    Returns:
        Dicionário com as métricas de auditoria.
    """
    info: dict = {
        "nome": filepath.name,
        "existe": filepath.exists(),
        "linhas": 0,
        "colunas": 0,
        "headers": [],
        "tamanho_kb": 0.0,
        "encoding_ok": True,
    }

    if not filepath.exists():
        return info

    info["tamanho_kb"] = round(filepath.stat().st_size / 1024, 1)

    try:
        with open(filepath, "r", encoding="utf-8") as f:
            reader = csv.reader(f)
            headers = next(reader, [])
            info["headers"] = headers
            info["colunas"] = len(headers)

            # Contar linhas de dados (excluindo o cabeçalho)
            row_count: int = 0
            for _ in reader:
                row_count += 1
            info["linhas"] = row_count

    except UnicodeDecodeError:
        info["encoding_ok"] = False

    return info


def main() -> None:
    """Executa a auditoria completa dos 24 CSVs e imprime o relatório."""

    print("=" * 80)
    print("🔍 AUDITORIA DE INTEGRIDADE DOS ARQUIVOS CSV — LH NAUTICAL")
    print(f"   Diretório: {RAW_DIR}")
    print("=" * 80)

    if not RAW_DIR.exists():
        print(f"\n❌ ERRO: O diretório {RAW_DIR} não existe!")
        sys.exit(1)

    # Listar todos os CSVs encontrados no diretório
    csvs_encontrados: set[str] = {
        f.name for f in RAW_DIR.iterdir() if f.suffix.lower() == ".csv"
    }

    # Verificar arquivos esperados vs encontrados
    esperados_set: set[str] = set(EXPECTED_CSVS)
    faltantes: set[str] = esperados_set - csvs_encontrados
    extras: set[str] = csvs_encontrados - esperados_set

    print(f"\n📊 Resumo Geral:")
    print(f"   Arquivos esperados:   {len(EXPECTED_CSVS)}")
    print(f"   Arquivos encontrados: {len(csvs_encontrados)}")
    print(f"   Faltantes:            {len(faltantes)}")
    print(f"   Extras (inesperados): {len(extras)}")

    if faltantes:
        print(f"\n⚠️  ARQUIVOS FALTANTES: {sorted(faltantes)}")
    if extras:
        print(f"\n⚠️  ARQUIVOS EXTRAS: {sorted(extras)}")

    # Auditar cada arquivo esperado
    print(f"\n{'─' * 80}")
    print(f"{'Arquivo':<32} {'Linhas':>10} {'Colunas':>8} {'Tamanho (KB)':>14} {'Status'}")
    print(f"{'─' * 80}")

    total_linhas: int = 0
    total_arquivos_ok: int = 0

    for csv_name in sorted(EXPECTED_CSVS):
        filepath: Path = RAW_DIR / csv_name
        info: dict = auditar_csv(filepath)

        if not info["existe"]:
            status = "❌ FALTANDO"
        elif not info["encoding_ok"]:
            status = "⚠️ ENCODING"
        else:
            status = "✅ OK"
            total_arquivos_ok += 1
            total_linhas += info["linhas"]

        print(
            f"{info['nome']:<32} "
            f"{info['linhas']:>10,} "
            f"{info['colunas']:>8} "
            f"{info['tamanho_kb']:>13,.1f} "
            f"{status}"
        )

    print(f"{'─' * 80}")
    print(f"{'TOTAL':<32} {total_linhas:>10,}")
    print(f"{'─' * 80}")

    # Detalhamento dos cabeçalhos de cada tabela
    print(f"\n{'=' * 80}")
    print("📋 CABEÇALHOS (COLUNAS) DE CADA TABELA")
    print(f"{'=' * 80}")

    for csv_name in sorted(EXPECTED_CSVS):
        filepath: Path = RAW_DIR / csv_name
        info: dict = auditar_csv(filepath)
        if info["existe"] and info["headers"]:
            table_name: str = csv_name.replace(".csv", "")
            print(f"\n🔹 {table_name} ({info['colunas']} colunas):")
            for i, col in enumerate(info["headers"], 1):
                print(f"   {i:>2}. {col}")

    # Veredicto final
    print(f"\n{'=' * 80}")
    if total_arquivos_ok == len(EXPECTED_CSVS) and len(faltantes) == 0:
        print("✅ AUDITORIA APROVADA: Todos os 24 arquivos CSV estão presentes e legíveis.")
    else:
        print("❌ AUDITORIA REPROVADA: Existem problemas que precisam ser resolvidos.")
    print(f"{'=' * 80}")


if __name__ == "__main__":
    main()
