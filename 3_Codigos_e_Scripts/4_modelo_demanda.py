#!/usr/bin/env python3
"""
===============================================================================
DESAFIO LH NAUTICAL — QUESTÃO 6: PREVISÃO DE DEMANDA (MÉDIA MÓVEL 3M)
Autor: Luciano Silva de Arruda
Programa: Lighthouse 2026 (Indicium AI)
===============================================================================
Premissas obrigatórias:
  1. Produto Alvo: "Bússola de Bordo 702"
  2. Período de Treino: Dados até 31/12/2025
  3. Período de Teste: Primeiro trimestre de 2026 (01/01/2026 a 31/03/2026)
  4. Agregação em base mensal (SUM de quantidade de unidades vendidas)
  5. Modelo Baseline: Média Móvel de 3 meses (Rolling 3M) sem data leakage
  6. Métrica de Avaliação: MAE (Mean Absolute Error) em unidades e tradução em R$

Bibliotecas permitidas: pandas, numpy, matplotlib / seaborn
===============================================================================
"""

import os
import sys
import logging
from pathlib import Path
from typing import Tuple, List, Dict

import pandas as pd
import numpy as np

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

ORDERS_CSV: Path = RAW_DIR / "orders.csv"
ORDER_ITEMS_CSV: Path = RAW_DIR / "order_items.csv"
PRODUCT_VARIANTS_CSV: Path = RAW_DIR / "product_variants.csv"
PRODUCTS_CSV: Path = RAW_DIR / "products.csv"

TARGET_PRODUCT_NAME: str = "Bússola de Bordo 702"


def carregar_dados_demanda() -> Tuple[pd.DataFrame, float]:
    """
    Carrega e unifica as tabelas orders, order_items, product_variants e products,
    filtrando apenas as vendas do produto 'Bússola de Bordo 702'.

    Returns:
        Tuple (df_historico_mensal, preco_medio_unitario)
    """
    logger.info(f"Carregando histórico de vendas para o produto '{TARGET_PRODUCT_NAME}'...")

    df_orders = pd.read_csv(ORDERS_CSV, usecols=["id", "placed_at", "status"])
    df_items = pd.read_csv(ORDER_ITEMS_CSV, usecols=["order_id", "product_variant_id", "quantity", "unit_price"])
    df_variants = pd.read_csv(PRODUCT_VARIANTS_CSV, usecols=["id", "product_id"])
    df_products = pd.read_csv(PRODUCTS_CSV, usecols=["id", "name"])

    # Filtrar apenas o produto alvo
    product_ids = df_products[df_products["name"] == TARGET_PRODUCT_NAME]["id"].tolist()
    if not product_ids:
        raise ValueError(f"Produto '{TARGET_PRODUCT_NAME}' não encontrado na tabela products!")

    # Filtrar variantes do produto alvo
    variant_ids = df_variants[df_variants["product_id"].isin(product_ids)]["id"].tolist()

    # Filtrar itens de pedidos do produto alvo
    df_items_target = df_items[df_items["product_variant_id"].isin(variant_ids)].copy()

    # Unir com orders para obter a data (placed_at)
    df_merged = df_orders.merge(df_items_target, left_on="id", right_on="order_id", how="inner")

    # Converter data
    df_merged["placed_at"] = pd.to_datetime(df_merged["placed_at"])
    df_merged["ano_mes"] = df_merged["placed_at"].dt.to_period("M")

    # Calcular preço médio unitário do produto para tradução financeira em R$
    preco_medio: float = float(df_merged["unit_price"].mean())

    logger.info(f"Registros encontrados para '{TARGET_PRODUCT_NAME}': {len(df_merged):,} itens transacionados.")
    logger.info(f"Preço médio unitário praticado: R$ {preco_medio:,.2f}")

    return df_merged, preco_medio


def construir_serie_temporal_mensal(df: pd.DataFrame) -> pd.DataFrame:
    """
    Agrupa as vendas por mês, preenchendo meses sem venda com 0 para criar uma
    série temporal contínua e completa de 2020 a 2026.

    Args:
        df: DataFrame com histórico transacional.

    Returns:
        DataFrame com colunas [ano_mes, quantidade_real].
    """
    # Soma total de unidades vendidas por mês
    df_mensal = df.groupby("ano_mes")["quantity"].sum().reset_index()
    df_mensal.rename(columns={"quantity": "quantidade_real"}, inplace=True)

    # Garantir grade mensal contínua do primeiro ao último mês do dataset
    min_period = df["ano_mes"].min()
    max_period = df["ano_mes"].max()
    full_periods = pd.period_range(start=min_period, end=max_period, freq="M")

    df_full = pd.DataFrame({"ano_mes": full_periods})
    df_full = df_full.merge(df_mensal, on="ano_mes", how="left").fillna({"quantidade_real": 0})
    df_full["quantidade_real"] = df_full["quantidade_real"].astype(int)

    return df_full


def executar_modelo_baseline_3m(df_serie: pd.DataFrame) -> Tuple[pd.DataFrame, Dict[str, float]]:
    """
    Executa a Média Móvel de 3 Meses (Rolling 3M) sem data leakage.

    Treino: até 2025-12
    Teste: 2026-01 a 2026-03

    Args:
        df_serie: DataFrame contendo a série temporal mensal completa.

    Returns:
        Tuple (df_resultado_teste, dict_metricas)
    """
    logger.info("Executando modelo de Média Móvel 3M (Rolling 3M Baseline)...")

    # Criar coluna de Média Móvel 3M (deslocada por 1 mês para evitar data leakage)
    # A previsão para o mês M usa a média dos meses (M-3, M-2, M-1)
    df_serie["previsao_3m"] = df_serie["quantidade_real"].shift(1).rolling(window=3).mean()

    # Separar Treino e Teste
    treino_mask = df_serie["ano_mes"] <= pd.Period("2025-12", freq="M")
    teste_mask = (df_serie["ano_mes"] >= pd.Period("2026-01", freq="M")) & (
        df_serie["ano_mes"] <= pd.Period("2026-03", freq="M")
    )

    df_treino = df_serie[treino_mask].copy()
    df_teste = df_serie[teste_mask].copy()

    # Previsão arredondada para o 1º trimestre de 2026
    df_teste["previsao_inteira"] = df_teste["previsao_3m"].round().astype(int)
    df_teste["erro_absoluto"] = (df_teste["quantidade_real"] - df_teste["previsao_3m"]).abs()

    # Cálculo da métrica MAE no período de teste
    mae_unidades: float = float(df_teste["erro_absoluto"].mean())
    soma_previsao_bruta: float = float(df_teste["previsao_3m"].sum())
    soma_previsao_inteira: int = int(round(soma_previsao_bruta))
    soma_real: int = int(df_teste["quantidade_real"].sum())

    metricas = {
        "mae_unidades": mae_unidades,
        "soma_previsao_bruta": soma_previsao_bruta,
        "soma_previsao_inteira": soma_previsao_inteira,
        "soma_real": soma_real,
    }

    return df_teste, metricas


def main() -> None:
    """Ponto de entrada principal da Questão 6."""

    print("=" * 80)
    print(f"📈 QUESTÃO 6 — PREVISÃO DE DEMANDA MENSAL ('{TARGET_PRODUCT_NAME}')")
    print("=" * 80)

    # 1. Carregar histórico
    df_merged, preco_medio = carregar_dados_demanda()

    # 2. Construir série temporal mensal
    df_serie = construir_serie_temporal_mensal(df_merged)

    # 3. Executar baseline 3M
    df_teste, metricas = executar_modelo_baseline_3m(df_serie)

    # Converter MAE em R$ (Tradução Financeira)
    mae_financeiro_rs: float = metricas["mae_unidades"] * preco_medio

    print(f"\n📊 RESULTADOS DO 1º TRIMESTRE DE 2026 (PERÍODO DE TESTE):")
    print(f"{'─' * 80}")
    print(f"{'Mês/Ano':<12} {'Real (Unidades)':<18} {'Previsão (3M Exata)':<22} {'Previsão (Inteira)':<20} {'Erro Absoluto':>10}")
    print(f"{'─' * 80}")

    for _, row in df_teste.iterrows():
        print(
            f"{str(row['ano_mes']):<12} "
            f"{row['quantidade_real']:<18} "
            f"{row['previsao_3m']:<22.2f} "
            f"{row['previsao_inteira']:<20} "
            f"{row['erro_absoluto']:>10.2f}"
        )

    print(f"{'─' * 80}")
    print(f"{'TOTAL 1º TRI':<12} {metricas['soma_real']:<18} {metricas['soma_previsao_bruta']:<22.2f} {metricas['soma_previsao_inteira']:<20}")
    print(f"{'─' * 80}\n")

    print("=" * 80)
    print("📋 RESPOSTAS DAS PERGUNTAS DA QUESTÃO 6:")
    print("=" * 80)
    print(f"✅ Q6.2 — Soma total da previsão para o 1º Tri/2026 (arredondada):")
    print(f"   👉 {metricas['soma_previsao_inteira']} unidades (Soma exata das previsões: {metricas['soma_previsao_bruta']:.2f})")
    print(f"   👉 Vendas Reais Ocorridas no 1º Tri/2026: {metricas['soma_real']} unidades")
    print(f"\n📏 Métrica de Avaliação (MAE — Mean Absolute Error):")
    print(f"   👉 MAE em Unidades: {metricas['mae_unidades']:.2f} unidades / mês")
    print(f"   👉 MAE Financeiro Traduzido: R$ {mae_financeiro_rs:,.2f} / mês (Preço Médio: R$ {preco_medio:,.2f})")
    print("=" * 80 + "\n")


if __name__ == "__main__":
    main()
