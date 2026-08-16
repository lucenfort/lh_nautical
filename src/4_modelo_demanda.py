#!/usr/bin/env python3
"""
===============================================================================
LH NAUTICAL — MODELAGEM PREDITIVA DE DEMANDA (MÉDIA MÓVEL 3M BASELINE)
Autor: Luciano Silva de Arruda
Projeto: LH Nautical — Plataforma de Engenharia de Dados & Analytics
===============================================================================
Premissas Obrigatórias:
  - Divisão Temporal: Treino até 31/12/2025 | Teste no 1º Trimestre de 2026 (Jan a Mar/2026).
  - Granularidade: Mensal (unidades vendidas - quantity).
  - Produto Alvo: "Bússola de Bordo 702".
  - Modelo Baseline: Média Móvel de 3 meses.
  - Prevenção Anti-Leakage: Uso obrigatório de shift(1).
  - Métrica de Avaliação: MAE (Mean Absolute Error).
===============================================================================
"""

import sys
from pathlib import Path
import pandas as pd
import numpy as np

# Resolução de Caminhos
SRC_DIR = Path(__file__).resolve().parent
PROJECT_ROOT = SRC_DIR.parent
DATA_DIR = PROJECT_ROOT / "data" / "raw"


def executar_previsao_demanda():
    print("=" * 80)
    print("⚓ LH NAUTICAL — MODELO PREDITIVO DE DEMANDA: BÚSSOLA DE BORDO 702")
    print("=" * 80)

    # 1. Carregamento dos dados relacionais
    df_orders = pd.read_csv(DATA_DIR / "orders.csv", usecols=["id", "placed_at", "total"])
    df_items = pd.read_csv(DATA_DIR / "order_items.csv", usecols=["order_id", "product_variant_id", "quantity", "unit_price"])
    df_variants = pd.read_csv(DATA_DIR / "product_variants.csv", usecols=["id", "product_id"])
    df_products = pd.read_csv(DATA_DIR / "products.csv", usecols=["id", "name"])

    # 2. Filtragem do Produto Alvo
    target_product = "Bússola de Bordo 702"
    prod_ids = df_products[df_products["name"] == target_product]["id"].tolist()
    if not prod_ids:
        print(f"❌ Produto '{target_product}' não encontrado.")
        sys.exit(1)

    variant_ids = df_variants[df_variants["product_id"].isin(prod_ids)]["id"].tolist()

    # 3. Unificação relacional
    df_merged = (
        df_orders.rename(columns={"id": "order_id"})
        .merge(df_items[df_items["product_variant_id"].isin(variant_ids)], on="order_id")
    )
    df_merged["placed_at"] = pd.to_datetime(df_merged["placed_at"])
    df_merged["ano_mes"] = df_merged["placed_at"].dt.to_period("M")
    preco_medio = df_merged["unit_price"].mean()

    # 4. Agregação mensal contínua (sem saltos temporais)
    df_mensal = df_merged.groupby("ano_mes")["quantity"].sum().reset_index()
    all_months = pd.period_range(start=df_merged["ano_mes"].min(), end=df_merged["ano_mes"].max(), freq="M")
    df_serie = pd.DataFrame({"ano_mes": all_months}).merge(df_mensal, on="ano_mes", how="left").fillna(0)
    df_serie["quantity"] = df_serie["quantity"].astype(int)

    # 5. Modelo Baseline: Média Móvel de 3 Meses com shift(1) anti-leakage
    df_serie["previsao_3m"] = df_serie["quantity"].shift(1).rolling(window=3).mean()

    # 6. Avaliação no 1º Trimestre de 2026
    mask_teste = (df_serie["ano_mes"] >= pd.Period("2026-01", freq="M")) & (df_serie["ano_mes"] <= pd.Period("2026-03", freq="M"))
    df_teste = df_serie[mask_teste].copy()
    df_teste["erro_absoluto"] = (df_teste["quantity"] - df_teste["previsao_3m"]).abs()

    soma_prevista_float = df_teste["previsao_3m"].sum()
    soma_prevista_int = int(round(soma_prevista_float))
    soma_real = df_teste["quantity"].sum()
    mae_unidades = df_teste["erro_absoluto"].mean()
    impacto_financeiro = mae_unidades * preco_medio

    print("📅 RESULTADOS DO 1º TRIMESTRE DE 2026:")
    for _, row in df_teste.iterrows():
        mes_str = str(row["ano_mes"])
        q_real = int(row["quantity"])
        q_prev = row["previsao_3m"]
        err = row["erro_absoluto"]
        print(f"  • {mes_str}: Real = {q_real:>2} un | Previsão 3M = {q_prev:>5.2f} un (Arred: {round(q_prev):>2} un) | Erro = {err:>5.2f} un")

    print("-" * 80)
    print("📊 CONSOLIDAÇÃO DE MÉTRICAS:")
    print(f"  👉 Soma da Previsão (Número Inteiro): {soma_prevista_int} unidades  (Exato: {soma_prevista_float:.2f})")
    print(f"  👉 Total de Vendas Reais Ocorridas:    {soma_real} unidades")
    print(f"  👉 MAE Médio Mensal:                  {mae_unidades:.2f} unidades / mês")
    print(f"  👉 Preço Médio Unitário:              R$ {preco_medio:,.2f}")
    print(f"  👉 Impacto Financeiro do Erro (MAE):  R$ {impacto_financeiro:,.2f} / mês")
    print("=" * 80)

    return {
        "soma_prevista_int": soma_prevista_int,
        "soma_prevista_float": soma_prevista_float,
        "mae_unidades": mae_unidades,
        "impacto_financeiro": impacto_financeiro,
        "df_teste": df_teste
    }


if __name__ == "__main__":
    executar_previsao_demanda()
