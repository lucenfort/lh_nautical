#!/usr/bin/env python3
"""
===============================================================================
LH NAUTICAL — SUÍTE DE TESTES AUTOMATIZADOS DO DASHBOARD STREAMLIT
Testes de Interface, Renderização, KPIs e Lógica Analítica
===============================================================================
"""

import pytest
import pandas as pd
import numpy as np
from streamlit.testing.v1 import AppTest


def test_dashboard_compiles_and_renders_without_exceptions(project_paths):
    """
    Garante que o dashboard Streamlit (app.py) compila, inicializa e executa
    todas as 5 abas sem lançar nenhuma exceção ou erro de sintaxe.
    """
    app_path = project_paths["root"] / "dashboard" / "app.py"
    assert app_path.exists(), "Arquivo dashboard/app.py não encontrado"
    
    at = AppTest.from_file(str(app_path), default_timeout=30)
    at.run()
    
    # Valida que não houve nenhuma exceção no Streamlit
    assert not at.exception, f"Exceção encontrada no dashboard: {at.exception}"


def test_dashboard_kpis_exact_values(project_paths):
    """
    Valida se os dados e métricas que alimentam os KPI Cards globais do dashboard
    possuem exatidão matemática com os resultados do ERP.
    """
    df_orders = pd.read_csv(project_paths["raw"] / "orders.csv")
    
    # 1. Total Faturamento Global
    total_fat = df_orders["total"].sum()
    assert abs(total_fat - 1406487201.80) < 1.0, f"Faturamento inesperado: {total_fat}"
    
    # 2. Total Pedidos
    assert len(df_orders) == 48998, f"Total de pedidos incorreto: {len(df_orders)}"
    
    # 3. Ticket Médio Global
    ticket_medio = df_orders["total"].mean()
    assert round(ticket_medio, 2) == 28704.99, f"Ticket médio incorreto: {ticket_medio:.2f}"


def test_dashboard_pos_calendar_thursday_worst_day(project_paths):
    """
    Valida a lógica da Aba 1 do Dashboard: Comprovação da Quinta-feira como pior dia nas lojas físicas.
    """
    df_orders = pd.read_csv(project_paths["raw"] / "orders.csv")
    df_orders["placed_date"] = pd.to_datetime(df_orders["placed_at"]).dt.date
    
    min_d = df_orders["placed_date"].min()
    max_d = df_orders["placed_date"].max()
    full_cal = pd.DataFrame({"data_calendario": pd.date_range(start=min_d, end=max_d, freq="D").date})
    full_cal["dia_semana_num"] = pd.to_datetime(full_cal["data_calendario"]).dt.dayofweek + 1
    dias_map = {1: "Segunda", 2: "Terça", 3: "Quarta", 4: "Quinta", 5: "Sexta", 6: "Sábado", 7: "Domingo"}
    full_cal["dia_pt"] = full_cal["dia_semana_num"].map(dias_map)
    
    vendas_pos_raw = df_orders[df_orders["channel"] == "pos"].groupby("placed_date")["total"].sum().reset_index()
    vendas_pos_raw.rename(columns={"placed_date": "data_calendario", "total": "vendas_pos"}, inplace=True)
    
    cal_vendas = full_cal.merge(vendas_pos_raw, on="data_calendario", how="left").fillna({"vendas_pos": 0.0})
    media_real = cal_vendas.groupby(["dia_semana_num", "dia_pt"]).agg(media_real=("vendas_pos", "mean")).reset_index()
    
    pior_dia_row = media_real.sort_values("media_real").iloc[0]
    assert pior_dia_row["dia_pt"] == "Quinta", f"Pior dia esperado 'Quinta', obtido: {pior_dia_row['dia_pt']}"
    assert round(pior_dia_row["media_real"], 2) == 157154.32, f"Média calculada: {pior_dia_row['media_real']:.2f}"


def test_dashboard_vip_segmentation_client22_and_helices(project_paths):
    """
    Valida a lógica da Aba 2 do Dashboard: Cliente #22 e Hélices como categoria líder.
    """
    df_orders = pd.read_csv(project_paths["raw"] / "orders.csv")
    df_items = pd.read_csv(project_paths["raw"] / "order_items.csv")
    df_variants = pd.read_csv(project_paths["raw"] / "product_variants.csv")
    df_products = pd.read_csv(project_paths["raw"] / "products.csv")
    df_categories = pd.read_csv(project_paths["raw"] / "categories.csv")
    
    fat_cliente = df_orders.groupby("customer_id").agg(
        faturamento_total=("total", "sum"),
        frequencia=("id", "nunique")
    ).reset_index()
    fat_cliente["ticket_medio"] = fat_cliente["faturamento_total"] / fat_cliente["frequencia"]
    
    df_chain = (
        df_orders[["id", "customer_id"]].rename(columns={"id": "order_id"})
        .merge(df_items[["order_id", "product_variant_id", "quantity"]], on="order_id")
        .merge(df_variants[["id", "product_id"]].rename(columns={"id": "product_variant_id"}), on="product_variant_id")
        .merge(df_products[["id", "category_id"]].rename(columns={"id": "product_id"}), on="product_id")
    )
    div_cliente = df_chain.groupby("customer_id")["category_id"].nunique().reset_index()
    div_cliente.rename(columns={"category_id": "diversidade_categorias"}, inplace=True)
    
    metricas = fat_cliente.merge(div_cliente, on="customer_id")
    top10 = metricas[metricas["diversidade_categorias"] >= 13].sort_values(by=["ticket_medio", "customer_id"], ascending=[False, True]).head(10)
    
    top1_id = top10.iloc[0]["customer_id"]
    top1_tm = top10.iloc[0]["ticket_medio"]
    assert top1_id == 22, f"Top 1 esperado Cliente 22, obtido: {top1_id}"
    assert round(top1_tm, 2) == 41839.94, f"Ticket Médio esperado: 41839.94, obtido: {top1_tm:.2f}"
    
    top10_ids = top10["customer_id"].tolist()
    df_itens_top10 = df_chain[df_chain["customer_id"].isin(top10_ids)].merge(
        df_categories[["id", "name"]].rename(columns={"id": "category_id", "name": "category_name"}), on="category_id"
    )
    cat_top1 = df_itens_top10.groupby("category_name")["quantity"].sum().sort_values(ascending=False)
    
    assert cat_top1.index[0] == "Hélices", f"Categoria líder esperada 'Hélices', obtido: {cat_top1.index[0]}"
    assert cat_top1.iloc[0] == 492, f"Quantidade de Hélices esperada: 492, obtido: {cat_top1.iloc[0]}"


def test_dashboard_cancelled_orders_losses(project_paths):
    """
    Valida a lógica da Aba 5 do Dashboard: Auditoria de cancelamentos e governança.
    """
    df_orders = pd.read_csv(project_paths["raw"] / "orders.csv")
    cancelados = df_orders[df_orders["status"] == "cancelled"]
    
    assert len(cancelados) == 4847, f"Cancelados esperado 4847, obtido {len(cancelados)}"
    pct_cancelados = len(cancelados) / len(df_orders) * 100
    assert abs(pct_cancelados - 9.89) < 0.1, f"Percentual de cancelamento: {pct_cancelados:.2f}%"
