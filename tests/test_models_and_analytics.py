import pytest
import pandas as pd
import numpy as np
from sklearn.metrics.pairwise import cosine_similarity

def test_demand_forecast_no_data_leakage(project_paths):
    """
    Garante ausência de vazamento temporal (shift 1) e valida a soma de 149 unidades para o 1º Tri/2026.
    """
    df_orders = pd.read_csv(project_paths["raw"] / "orders.csv")
    df_items = pd.read_csv(project_paths["raw"] / "order_items.csv")
    df_variants = pd.read_csv(project_paths["raw"] / "product_variants.csv")
    df_products = pd.read_csv(project_paths["raw"] / "products.csv")
    
    prod_bussola = df_products[df_products["name"] == "Bússola de Bordo 702"]["id"].tolist()
    variants_bussola = df_variants[df_variants["product_id"].isin(prod_bussola)]["id"].tolist()
    
    df_buss = (
        df_orders[["id", "placed_at"]].rename(columns={"id": "order_id"})
        .merge(df_items[df_items["product_variant_id"].isin(variants_bussola)], on="order_id")
    )
    df_buss["ano_mes"] = pd.to_datetime(df_buss["placed_at"]).dt.to_period("M")
    df_mensal = df_buss.groupby("ano_mes")["quantity"].sum().reset_index()
    
    all_m = pd.period_range(start=df_buss["ano_mes"].min(), end=df_buss["ano_mes"].max(), freq="M")
    df_serie = pd.DataFrame({"ano_mes": all_m}).merge(df_mensal, on="ano_mes", how="left").fillna(0)
    
    # Previsão estritamente com shift(1)
    df_serie["previsao"] = df_serie["quantity"].shift(1).rolling(3).mean()
    
    # Teste no 1º Tri/2026
    teste_2026 = df_serie[df_serie["ano_mes"].isin([pd.Period("2026-01", "M"), pd.Period("2026-02", "M"), pd.Period("2026-03", "M")])]
    soma_prevista = teste_2026["previsao"].sum()
    
    assert round(soma_prevista) == 149, f"Soma prevista arredondada: {round(soma_prevista)}, esperada: 149"
    assert round(soma_prevista, 2) == 148.67, f"Soma prevista exata: {soma_prevista:.2f}, esperada: 148.67"

def test_cosine_recommendation_math_properties(project_paths):
    """
    Valida propriedades matemáticas do cosseno e o ranking de recomendação do Motor de Popa 1949.
    """
    df_orders = pd.read_csv(project_paths["raw"] / "orders.csv")
    df_items = pd.read_csv(project_paths["raw"] / "order_items.csv")
    df_variants = pd.read_csv(project_paths["raw"] / "product_variants.csv")
    df_products = pd.read_csv(project_paths["raw"] / "products.csv")
    
    df_cust_prod = (
        df_orders[["id", "customer_id"]].rename(columns={"id": "order_id"})
        .merge(df_items[["order_id", "product_variant_id"]], on="order_id")
        .merge(df_variants[["id", "product_id"]].rename(columns={"id": "product_variant_id"}), on="product_variant_id")
        .merge(df_products[["id", "name"]].rename(columns={"id": "product_id", "name": "product_name"}), on="product_id")
    )[["customer_id", "product_name"]].drop_duplicates()

    matriz_bin = pd.crosstab(index=df_cust_prod["customer_id"], columns=df_cust_prod["product_name"]).map(lambda x: 1 if x > 0 else 0)
    matriz_prod = matriz_bin.T
    sim_matrix = cosine_similarity(matriz_prod.values)
    
    # 1. Diagonal principal deve ser identicamente 1.0 (auto-similaridade)
    np.testing.assert_allclose(np.diag(sim_matrix), 1.0, atol=1e-5)
    
    # 2. Matriz deve ser simétrica
    np.testing.assert_allclose(sim_matrix, sim_matrix.T, atol=1e-5)
    
    # 3. Todos os valores devem estar em [0.0, 1.0]
    assert (sim_matrix >= -1e-6).all() and (sim_matrix <= 1.0 + 1e-6).all()
    
    # 4. Similaridades do Motor de Popa 1949
    df_sim = pd.DataFrame(sim_matrix, index=matriz_prod.index, columns=matriz_prod.index)
    target = "Motor de Popa 1949"
    rec_ranking = df_sim[target].drop(index=target).sort_values(ascending=False)
    
    top1_raw = rec_ranking.index[0]
    assert top1_raw == "asdf", f"Top 1 na base bruta: {top1_raw}, esperado 'asdf'"
    assert round(rec_ranking["asdf"], 4) == 0.2789, f"Similaridade 'asdf': {rec_ranking['asdf']:.4f}, esperada 0.2789"
    
    rec_clean = rec_ranking.drop(index=["asdf"], errors="ignore")
    top1_clean = rec_clean.index[0]
    assert top1_clean == "Motor de Popa 5331", f"Top 1 no catálogo limpo: {top1_clean}, esperado 'Motor de Popa 5331'"
    assert round(rec_clean["Motor de Popa 5331"], 4) == 0.2566, f"Similaridade Motor 5331: {rec_clean['Motor de Popa 5331']:.4f}, esperada 0.2566"

def test_pos_calendar_dimension_worst_day(project_paths):
    """
    Comprova que a Quinta-feira é o pior dia da semana em lojas físicas com dimensão de calendário.
    """
    df_orders = pd.read_csv(project_paths["raw"] / "orders.csv")
    df_orders["placed_at"] = pd.to_datetime(df_orders["placed_at"])
    df_orders["placed_date"] = df_orders["placed_at"].dt.date
    
    min_date = df_orders["placed_date"].min()
    max_date = df_orders["placed_date"].max()
    full_cal = pd.DataFrame({"data_cal": pd.date_range(start=min_date, end=max_date, freq="D").date})
    full_cal["dia_num"] = pd.to_datetime(full_cal["data_cal"]).dt.dayofweek + 1
    dias_map = {1: "Segunda-feira", 2: "Terça-feira", 3: "Quarta-feira", 4: "Quinta-feira", 5: "Sexta-feira", 6: "Sábado", 7: "Domingo"}
    full_cal["dia_pt"] = full_cal["dia_num"].map(dias_map)

    vendas_pos = df_orders[df_orders["channel"] == "pos"].groupby("placed_date")["total"].sum().reset_index()
    vendas_pos.rename(columns={"placed_date": "data_cal", "total": "vendas_pos"}, inplace=True)
    cal_vendas = full_cal.merge(vendas_pos, on="data_cal", how="left").fillna({"vendas_pos": 0.0})

    media_real = cal_vendas.groupby("dia_pt")["vendas_pos"].mean().sort_values()
    pior_dia = media_real.index[0]
    pior_media = media_real.iloc[0]
    
    assert pior_dia == "Quinta-feira", f"Pior dia encontrado: {pior_dia}, esperado 'Quinta-feira'"
    assert round(pior_media, 2) == 157154.32, f"Média calculada: {pior_media:.2f}, esperada: 157154.32"
