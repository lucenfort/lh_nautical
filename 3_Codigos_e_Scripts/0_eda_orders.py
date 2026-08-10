#!/usr/bin/env python3
"""
===============================================================================
DESAFIO LH NAUTICAL — ETAPA 2: ANÁLISE EXPLORATÓRIA (EDA) NA TABELA `orders`
Autor: Luciano Silva de Arruda
Programa: Lighthouse 2026 (Indicium AI)
===============================================================================
Questão 1 — EDA (Análise Exploratória de Dados)

Premissas obrigatórias:
  - Utilizar APENAS a tabela `orders`.
  - NÃO fazer limpeza nem tratamento dos dados.
  - Apenas observar, agregar e descrever.

Entregas:
  Q1.1 — Código SQL: total de linhas, intervalo de datas, MIN/MAX/AVG de `total`
  Q1.2 — Valor médio da coluna `total`
  Q1.3 — Diagnóstico de confiabilidade (outliers, nulos, consistência)
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
ORDERS_CSV: Path = RAW_DIR / "orders.csv"


def eda_orders_csv() -> None:
    """
    Realiza a Análise Exploratória da tabela `orders` diretamente sobre o CSV,
    utilizando APENAS Python 3 puro (sem pandas), conforme a premissa de EDA
    bruta e sem tratamento.

    Calcula:
      - Total de linhas (registros de dados, excluindo cabeçalho)
      - Total de colunas
      - Intervalo de datas (MIN e MAX de `created_at`)
      - MIN, MAX, AVG da coluna `total`
      - Contagem de nulos por coluna
      - Análise de outliers na coluna `total`
    """

    if not ORDERS_CSV.exists():
        print(f"❌ ERRO: Arquivo não encontrado: {ORDERS_CSV}")
        sys.exit(1)

    print("=" * 80)
    print("🔍 QUESTÃO 1 — EDA NA TABELA `orders` (DADOS BRUTOS, SEM TRATAMENTO)")
    print(f"   Arquivo: {ORDERS_CSV}")
    print("=" * 80)

    # -----------------------------------------------------------------------
    # 1. Leitura do CSV
    # -----------------------------------------------------------------------
    rows: list[dict] = []
    with open(ORDERS_CSV, "r", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        headers: list[str] = reader.fieldnames if reader.fieldnames else []
        for row in reader:
            rows.append(row)

    total_linhas: int = len(rows)
    total_colunas: int = len(headers)

    print(f"\n📊 PARTE 1 — Visão Geral da Tabela `orders`:")
    print(f"   1. Quantidade total de linhas:  {total_linhas:,}")
    print(f"   2. Quantidade total de colunas: {total_colunas}")
    print(f"   Colunas: {headers}")

    # -----------------------------------------------------------------------
    # 2. Intervalo de datas (created_at)
    # -----------------------------------------------------------------------
    datas_created_at: list[str] = []
    for row in rows:
        val: str = row.get("created_at", "").strip()
        if val:
            datas_created_at.append(val)

    if datas_created_at:
        data_min: str = min(datas_created_at)
        data_max: str = max(datas_created_at)
    else:
        data_min = "N/A"
        data_max = "N/A"

    print(f"   3. Intervalo de datas (created_at):")
    print(f"      Data mínima: {data_min}")
    print(f"      Data máxima: {data_max}")

    # -----------------------------------------------------------------------
    # 3. Estatísticas da coluna `total` (MIN, MAX, AVG)
    # -----------------------------------------------------------------------
    valores_total: list[float] = []
    total_nulos_total: int = 0

    for row in rows:
        val = row.get("total", "").strip()
        if val == "" or val.lower() == "null" or val.lower() == "none":
            total_nulos_total += 1
        else:
            try:
                valores_total.append(float(val))
            except ValueError:
                total_nulos_total += 1

    if valores_total:
        val_min: float = min(valores_total)
        val_max: float = max(valores_total)
        val_avg: float = sum(valores_total) / len(valores_total)
    else:
        val_min = 0.0
        val_max = 0.0
        val_avg = 0.0

    print(f"\n📊 PARTE 2 — Análise de Valores Numéricos (coluna `total`):")
    print(f"   1. Valor mínimo:  R$ {val_min:,.2f}")
    print(f"   2. Valor máximo:  R$ {val_max:,.2f}")
    print(f"   3. Valor médio:   R$ {val_avg:,.2f}")
    print(f"   Registros válidos: {len(valores_total):,}")
    print(f"   Registros nulos/inválidos na coluna `total`: {total_nulos_total}")

    # -----------------------------------------------------------------------
    # 4. Contagem de nulos/vazios por coluna
    # -----------------------------------------------------------------------
    print(f"\n📊 ANÁLISE DE NULOS/VAZIOS POR COLUNA:")
    print(f"   {'Coluna':<25} {'Nulos/Vazios':>12} {'% do Total':>10}")
    print(f"   {'─' * 50}")

    for col in headers:
        nulos: int = sum(
            1 for row in rows
            if row.get(col, "").strip() == ""
            or row.get(col, "").strip().lower() in ("null", "none")
        )
        pct: float = (nulos / total_linhas * 100) if total_linhas > 0 else 0
        flag: str = " ⚠️" if nulos > 0 else ""
        print(f"   {col:<25} {nulos:>12,} {pct:>9.1f}%{flag}")

    # -----------------------------------------------------------------------
    # 5. Análise de distribuição e outliers na coluna `total`
    # -----------------------------------------------------------------------
    if valores_total:
        sorted_vals: list[float] = sorted(valores_total)
        n: int = len(sorted_vals)

        # Quartis
        q1_idx: int = n // 4
        q2_idx: int = n // 2
        q3_idx: int = (3 * n) // 4

        q1: float = sorted_vals[q1_idx]
        mediana: float = sorted_vals[q2_idx]
        q3: float = sorted_vals[q3_idx]
        iqr: float = q3 - q1

        # Limites para detecção de outliers (método IQR)
        lower_bound: float = q1 - 1.5 * iqr
        upper_bound: float = q3 + 1.5 * iqr

        outliers_baixo: int = sum(1 for v in sorted_vals if v < lower_bound)
        outliers_alto: int = sum(1 for v in sorted_vals if v > upper_bound)

        # Valores negativos
        negativos: int = sum(1 for v in valores_total if v < 0)

        # Valores zerados
        zerados: int = sum(1 for v in valores_total if v == 0)

        print(f"\n📊 ANÁLISE DE DISTRIBUIÇÃO E OUTLIERS (coluna `total`):")
        print(f"   Q1 (25%):        R$ {q1:,.2f}")
        print(f"   Mediana (50%):   R$ {mediana:,.2f}")
        print(f"   Q3 (75%):        R$ {q3:,.2f}")
        print(f"   IQR:             R$ {iqr:,.2f}")
        print(f"   Limite inferior: R$ {lower_bound:,.2f}")
        print(f"   Limite superior: R$ {upper_bound:,.2f}")
        print(f"   Outliers abaixo: {outliers_baixo:,}")
        print(f"   Outliers acima:  {outliers_alto:,}")
        print(f"   Valores negativos: {negativos:,}")
        print(f"   Valores zerados:   {zerados:,}")

    # -----------------------------------------------------------------------
    # 6. Análise dos canais de venda (channel) e status
    # -----------------------------------------------------------------------
    channels: dict[str, int] = {}
    statuses: dict[str, int] = {}
    for row in rows:
        ch: str = row.get("channel", "").strip()
        st: str = row.get("status", "").strip()
        channels[ch] = channels.get(ch, 0) + 1
        statuses[st] = statuses.get(st, 0) + 1

    print(f"\n📊 DISTRIBUIÇÃO POR CANAL DE VENDA:")
    for ch, count in sorted(channels.items(), key=lambda x: -x[1]):
        print(f"   {ch:<15} {count:>8,} ({count/total_linhas*100:.1f}%)")

    print(f"\n📊 DISTRIBUIÇÃO POR STATUS:")
    for st, count in sorted(statuses.items(), key=lambda x: -x[1]):
        print(f"   {st:<15} {count:>8,} ({count/total_linhas*100:.1f}%)")

    # -----------------------------------------------------------------------
    # 7. Resposta formatada para Q1.2
    # -----------------------------------------------------------------------
    print(f"\n{'=' * 80}")
    print(f"📋 RESPOSTA Q1.2: Valor médio da coluna `total` = R$ {val_avg:,.2f}")
    print(f"{'=' * 80}")

    # -----------------------------------------------------------------------
    # SQL equivalente para Q1.1 (será usado no questionário)
    # -----------------------------------------------------------------------
    print(f"\n{'=' * 80}")
    print("📋 CÓDIGO SQL PARA Q1.1 (para referência e questionário):")
    print(f"{'=' * 80}")
    sql_q1: str = """
-- =============================================================================
-- QUESTÃO 1.1 — EDA na Tabela `orders` (Dados Brutos, Sem Tratamento)
-- Desafio LH Nautical — Lighthouse 2026 (Indicium AI)
-- Autor: Luciano Silva de Arruda
-- =============================================================================

-- Parte 1: Visão geral da tabela `orders`
-- Parte 2: Análise de valores numéricos da coluna `total`
SELECT
    COUNT(*)                                  AS total_linhas,
    MIN(created_at)                           AS data_minima,
    MAX(created_at)                           AS data_maxima,
    MIN(total)                                AS valor_minimo,
    MAX(total)                                AS valor_maximo,
    ROUND(AVG(total), 2)                      AS valor_medio
FROM orders;
"""
    print(sql_q1)


def main() -> None:
    """Ponto de entrada principal do script de EDA."""
    eda_orders_csv()


if __name__ == "__main__":
    main()
