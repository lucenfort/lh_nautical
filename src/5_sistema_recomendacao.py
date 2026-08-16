#!/usr/bin/env python3
"""
===============================================================================
LH NAUTICAL — MOTOR DE RECOMENDAÇÃO ITEM-ITEM (SIMILARIDADE DE COSSENO)
Autor: Luciano Silva de Arruda
Projeto: LH Nautical — Plataforma de Engenharia de Dados & Analytics
===============================================================================
Premissas Obrigatórias:
  - Matriz de Interação Usuário x Produto binária (1 se comprou >= 1 vez, 0 caso contrário).
  - Cálculo de Similaridade de Cosseno entre vetores de produtos.
  - Item de Referência: "Motor de Popa 1949".
  - Geração do Ranking dos 5 produtos mais similares (excluindo o próprio item).
===============================================================================
"""

import sys
from pathlib import Path
import pandas as pd
import numpy as np
from sklearn.metrics.pairwise import cosine_similarity

# Resolução de Caminhos
SRC_DIR = Path(__file__).resolve().parent
PROJECT_ROOT = SRC_DIR.parent
DATA_DIR = PROJECT_ROOT / "data" / "raw"


def executar_sistema_recomendacao():
    print("=" * 80)
    print("⚓ LH NAUTICAL — SISTEMA DE RECOMENDAÇÃO ITEM-ITEM (COSINE SIMILARITY)")
    print("=" * 80)

    # 1. Carregamento dos dados transacionais e de catálogo
    df_orders = pd.read_csv(DATA_DIR / "orders.csv", usecols=["id", "customer_id"])
    df_items = pd.read_csv(DATA_DIR / "order_items.csv", usecols=["order_id", "product_variant_id"])
    df_variants = pd.read_csv(DATA_DIR / "product_variants.csv", usecols=["id", "product_id"])
    df_products = pd.read_csv(DATA_DIR / "products.csv", usecols=["id", "name"])

    # 2. Unificação da cadeia relacional (Cliente x Produto Adquirido)
    df_merged = (
        df_orders.rename(columns={"id": "order_id"})
        .merge(df_items, on="order_id")
        .merge(df_variants.rename(columns={"id": "product_variant_id"}), on="product_variant_id")
        .merge(df_products.rename(columns={"id": "product_id", "name": "product_name"}), on="product_id")
    )[["customer_id", "product_name"]].drop_duplicates()

    # 3. Construção da Matriz Binária de Interação (Usuário x Produto)
    matriz_binaria = pd.crosstab(
        index=df_merged["customer_id"],
        columns=df_merged["product_name"]
    ).map(lambda x: 1 if x > 0 else 0)

    num_clientes, num_produtos = matriz_binaria.shape
    print(f"Dimensões da Matriz de Interação: {num_clientes:,} Clientes x {num_produtos:,} Produtos")

    # 4. Cálculo da Similaridade de Cosseno (Produto x Produto)
    matriz_produtos = matriz_binaria.T
    sim_matrix = cosine_similarity(matriz_produtos.values)
    df_sim = pd.DataFrame(sim_matrix, index=matriz_produtos.index, columns=matriz_produtos.index)

    # 5. Ranking para o item de referência "Motor de Popa 1949"
    target_item = "Motor de Popa 1949"
    if target_item not in df_sim.index:
        print(f"❌ Produto '{target_item}' não encontrado na matriz.")
        sys.exit(1)

    ranking_completo = df_sim[target_item].drop(index=target_item).sort_values(ascending=False)
    top5_raw = ranking_completo.head(5).reset_index()
    top5_raw.columns = ["produto", "similaridade_cosseno"]
    top5_raw["ranking"] = top5_raw.index + 1

    print("-" * 80)
    print(f"🎯 TOP 5 RECOMENDAÇÕES PARA '{target_item}' (BASE BRUTA):")
    for _, row in top5_raw.iterrows():
        tipo = " ⚠️ [Ruído Cadastral / Teste]" if row["produto"] == "asdf" else " ✅ [Catálogo Comercial]"
        print(f"  #{row['ranking']} | {row['produto']:<30} | Similaridade: {row['similaridade_cosseno']:.4f}{tipo}")

    print("-" * 80)
    # Filtro de negócio (expurgando ruídos cadastrais)
    ranking_limpo = ranking_completo.drop(index=["asdf"], errors="ignore").head(5).reset_index()
    ranking_limpo.columns = ["produto", "similaridade_cosseno"]
    ranking_limpo["ranking"] = ranking_limpo.index + 1

    print(f"🏆 TOP 5 RECOMENDAÇÕES PARA '{target_item}' (CATÁLOGO HIGIENIZADO):")
    for _, row in ranking_limpo.iterrows():
        print(f"  #{row['ranking']} | {row['produto']:<30} | Similaridade: {row['similaridade_cosseno']:.4f}")

    print("-" * 80)
    print(f"👉 Item com Maior Similaridade na Base Bruta:        '{top5_raw.iloc[0]['produto']}' ({top5_raw.iloc[0]['similaridade_cosseno']:.4f})")
    print(f"👉 Produto Comercial Válido com Maior Afinidade:     '{ranking_limpo.iloc[0]['produto']}' ({ranking_limpo.iloc[0]['similaridade_cosseno']:.4f})")
    print("=" * 80)

    return {
        "df_sim": df_sim,
        "top5_raw": top5_raw,
        "ranking_limpo": ranking_limpo
    }


if __name__ == "__main__":
    executar_sistema_recomendacao()
