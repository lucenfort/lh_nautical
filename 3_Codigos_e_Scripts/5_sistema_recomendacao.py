#!/usr/bin/env python3
"""
===============================================================================
DESAFIO LH NAUTICAL — QUESTÃO 7: SISTEMA DE RECOMENDAÇÃO (COSINE SIMILARITY)
Autor: Luciano Silva de Arruda
Programa: Lighthouse 2026 (Indicium AI)
===============================================================================
Premissas obrigatórias:
  1. Matriz de interação Usuário × Produto:
     - Linhas: customer_id
     - Colunas: product_id
     - Valor: 1 se comprou ao menos uma vez, 0 caso contrário (ignorando quantidade)
  2. Cálculo de Similaridade de Cosseno (Cosine Similarity) entre produtos.
  3. Ranking dos 5 produtos mais similares ao "Motor de Popa 1949" (excluindo o próprio item).

Bibliotecas permitidas: pandas, numpy, sklearn
===============================================================================
"""

import os
import sys
import logging
from pathlib import Path
from typing import Tuple, List

import pandas as pd
import numpy as np
from sklearn.metrics.pairwise import cosine_similarity

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

TARGET_PRODUCT_NAME: str = "Motor de Popa 1949"


def carregar_dados_unificados() -> pd.DataFrame:
    """
    Carrega e unifica as tabelas orders, order_items, product_variants e products
    para mapear a relação direta entre customer_id e product_id/product_name.

    Returns:
        DataFrame contendo as colunas customer_id, product_id, product_name.
    """
    logger.info("Carregando arquivos CSV para o sistema de recomendação...")

    df_orders = pd.read_csv(ORDERS_CSV, usecols=["id", "customer_id"])
    df_items = pd.read_csv(ORDER_ITEMS_CSV, usecols=["order_id", "product_variant_id"])
    df_variants = pd.read_csv(PRODUCT_VARIANTS_CSV, usecols=["id", "product_id"])
    df_products = pd.read_csv(PRODUCTS_CSV, usecols=["id", "name"])

    # Renomear IDs para junção sem conflito
    df_orders.rename(columns={"id": "order_id"}, inplace=True)
    df_variants.rename(columns={"id": "product_variant_id"}, inplace=True)
    df_products.rename(columns={"id": "product_id", "name": "product_name"}, inplace=True)

    # Cadeia de Joins: orders -> order_items -> product_variants -> products
    df_merged = (
        df_orders
        .merge(df_items, on="order_id", how="inner")
        .merge(df_variants, on="product_variant_id", how="inner")
        .merge(df_products, on="product_id", how="inner")
    )

    logger.info(f"Dados unificados: {len(df_merged):,} registros de itens comprados por clientes.")
    return df_merged[["customer_id", "product_id", "product_name"]].drop_duplicates()


def construir_matriz_usuario_produto(df: pd.DataFrame) -> pd.DataFrame:
    """
    Constrói a Matriz de Interação Binária Usuário × Produto.

    Regras:
      - Linhas: customer_id
      - Colunas: product_name (ou product_id)
      - Valor: 1 se comprou ao menos uma vez, 0 caso contrário.

    Args:
        df: DataFrame com colunas customer_id e product_name.

    Returns:
        DataFrame com a matriz binária (clientes x produtos).
    """
    logger.info("Construindo matriz de interação binária (Usuário × Produto)...")

    # Pivot table com contagem binária (presença/ausência)
    matriz_binaria = (
        pd.crosstab(index=df["customer_id"], columns=df["product_name"])
        .map(lambda x: 1 if x > 0 else 0)
    )

    logger.info(
        f"Matriz construída: {matriz_binaria.shape[0]:,} clientes × "
        f"{matriz_binaria.shape[1]:,} produtos."
    )
    return matriz_binaria


def calcular_similaridade_produtos(matriz_binaria: pd.DataFrame) -> pd.DataFrame:
    """
    Calcular a Similaridade de Cosseno entre os vetores de produtos.

    O vetor de cada produto é representado por suas compras através dos clientes
    (colunas da matriz transposta).

    Args:
        matriz_binaria: DataFrame com clientes em linhas e produtos em colunas.

    Returns:
        DataFrame quadrado de similaridade (Produtos × Produtos).
    """
    logger.info("Calculando matriz de similaridade de cosseno (Produto × Produto)...")

    # Transpor para ter Produtos nas linhas e Clientes nas colunas
    matriz_produtos = matriz_binaria.T  # Formato: (n_produtos, n_clientes)

    # Calcular a Similaridade de Cosseno entre as linhas (produtos)
    sim_matrix = cosine_similarity(matriz_produtos.values)

    df_sim = pd.DataFrame(
        sim_matrix,
        index=matriz_produtos.index,
        columns=matriz_produtos.index
    )

    return df_sim


def obter_top_recomendacoes(
    df_sim: pd.DataFrame,
    produto_alvo: str = TARGET_PRODUCT_NAME,
    top_n: int = 5
) -> pd.DataFrame:
    """
    Obtém o ranking dos top N produtos mais similares ao produto de referência,
    desconsiderando o próprio produto.

    Args:
        df_sim: DataFrame de similaridade de cosseno.
        produto_alvo: Nome do produto de referência.
        top_n: Quantidade de recomendações no ranking.

    Returns:
        DataFrame com os produtos recomendados e seus escores de similaridade.
    """
    if produto_alvo not in df_sim.index:
        raise ValueError(f"Produto '{produto_alvo}' não encontrado na matriz de produtos!")

    # Selecionar a série de similaridade do produto alvo e ordenar decrescente
    sim_serie = df_sim[produto_alvo].drop(index=produto_alvo).sort_values(ascending=False)

    df_top = pd.DataFrame({
        "produto_recomendado": sim_serie.index[:top_n],
        "similaridade_cosseno": sim_serie.values[:top_n]
    })
    df_top["ranking"] = range(1, top_n + 1)

    return df_top[["ranking", "produto_recomendado", "similaridade_cosseno"]]


def main() -> None:
    """Ponto de entrada principal do script de recomendação."""

    print("=" * 80)
    print(f"🤖 QUESTÃO 7 — SISTEMA DE RECOMENDAÇÃO (PRODUTO REF: '{TARGET_PRODUCT_NAME}')")
    print("=" * 80)

    # 1. Carregar dados
    df_interacoes = carregar_dados_unificados()

    # 2. Construir matriz usuário-produto
    matriz_binaria = construir_matriz_usuario_produto(df_interacoes)

    # 3. Calcular similaridade de cosseno
    df_sim = calcular_similaridade_produtos(matriz_binaria)

    # 4. Obter recomendações Top 5
    df_ranking = obter_top_recomendacoes(df_sim, TARGET_PRODUCT_NAME, top_n=10)

    print(f"\n📊 RANKING DOS PRODUTOS MAIS SIMILARES AO '{TARGET_PRODUCT_NAME}':")
    print(f"{'─' * 80}")
    print(f"{'Ranking':<8} {'Produto Recomendado':<45} {'Similaridade Cosseno':>20}")
    print(f"{'─' * 80}")

    for idx, row in df_ranking.iterrows():
        if idx < 5:
            print(
                f"{row['ranking']:<8} "
                f"{row['produto_recomendado']:<45} "
                f"{row['similaridade_cosseno']:>20.4f}"
            )

    print(f"{'─' * 80}")

    # Identificar o Top 1 bruto e o Top 1 de produto válido de negócio
    top1_bruto: str = df_ranking.iloc[0]["produto_recomendado"]
    top1_bruto_sim: float = df_ranking.iloc[0]["similaridade_cosseno"]

    df_validos = df_ranking[~df_ranking["produto_recomendado"].str.lower().str.contains("asdf|teste|dummy")]
    top1_valido: str = df_validos.iloc[0]["produto_recomendado"]
    top1_valido_sim: float = df_validos.iloc[0]["similaridade_cosseno"]

    print(f"\n{'=' * 80}")
    print(f"📋 RESPOSTA Q7.2: Produto com MAIOR similaridade ao '{TARGET_PRODUCT_NAME}':")
    print(f"   👉 Sem tratamento (dados brutos): '{top1_bruto}' (Similaridade: {top1_bruto_sim:.4f})")
    print(f"   👉 Com filtro de sujeira ('asdf'): '{top1_valido}' (Similaridade: {top1_valido_sim:.4f})")
    print(f"{'=' * 80}\n")


if __name__ == "__main__":
    main()
