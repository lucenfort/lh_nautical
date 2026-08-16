#!/usr/bin/env python3
"""
===============================================================================
LH NAUTICAL — GERADOR DE GRÁFICOS ANALÍTICOS EXECUTIVOS DE ALTA DEFINIÇÃO (300 DPI)
Design System Corporativo Náutico — Padrão Enterprise
Autor: Luciano Silva de Arruda
===============================================================================
"""

from pathlib import Path
import matplotlib.pyplot as plt
import matplotlib.ticker as ticker
import matplotlib.patches as mpatches
import pandas as pd
import numpy as np
from sklearn.metrics.pairwise import cosine_similarity

# Caminhos do Projeto
SRC_DIR = Path(__file__).resolve().parent
PROJECT_ROOT = SRC_DIR.parent
RAW_DIR = PROJECT_ROOT / "data" / "raw"
PROCESSED_DIR = PROJECT_ROOT / "data" / "processed"
PROCESSED_DIR.mkdir(parents=True, exist_ok=True)

REPORT_IMG_DIR = PROJECT_ROOT.parent / "lh_nautical_relatorio" / "images"
REPORT_IMG_DIR.mkdir(parents=True, exist_ok=True)

# -----------------------------------------------------------------------------
# Design Tokens & Paleta Náutica Corporativa
# -----------------------------------------------------------------------------
C_NAVY_DARK = "#0B2545"      # Azul Marinho Profundo (Títulos)
C_STEEL_BLUE = "#134074"     # Azul Aço (Barras Secundárias)
C_BLUE_ACCENT = "#2563EB"    # Azul Tecnológico (Destaques Principais)
C_BLUE_CYAN = "#4895EF"      # Azul Ciano (Barras Principais)
C_BLUE_LIGHT = "#93C5FD"     # Azul Suave
C_TEAL_SUCCESS = "#0D9488"   # Verde Teal (Produtos Válidos / Sucesso)
C_CORAL_ALERT = "#DC2626"    # Coral / Vermelho Alerta (Outliers, Ruídos, Inflados)
C_GRAY_DARK = "#1E293B"      # Texto de Eixos
C_GRAY_MUTED = "#64748B"     # Subtítulos e Anotações
C_GRAY_LINE = "#E2E8F0"      # Linhas de Grade Suaves
C_BG_CARD = "#F8FAFC"        # Fundo de Caixas / Legendas
C_WHITE = "#FFFFFF"          # Fundo Principal

# Configurações Globais do Matplotlib
plt.rcParams['font.family'] = 'sans-serif'
plt.rcParams['font.sans-serif'] = ['DejaVu Sans', 'Helvetica', 'Arial']
plt.rcParams['figure.facecolor'] = C_WHITE
plt.rcParams['axes.facecolor'] = C_WHITE
plt.rcParams['figure.dpi'] = 300
plt.rcParams['savefig.dpi'] = 300
plt.rcParams['savefig.bbox'] = 'tight'
plt.rcParams['savefig.pad_inches'] = 0.25

# -----------------------------------------------------------------------------
# Carregamento e Preparação dos Dados
# -----------------------------------------------------------------------------
df_orders = pd.read_csv(RAW_DIR / "orders.csv")
df_items = pd.read_csv(RAW_DIR / "order_items.csv")
df_variants = pd.read_csv(RAW_DIR / "product_variants.csv")
df_products = pd.read_csv(RAW_DIR / "products.csv")
df_categories = pd.read_csv(RAW_DIR / "categories.csv")

df_orders["placed_at"] = pd.to_datetime(df_orders["placed_at"])
df_orders["placed_date"] = df_orders["placed_at"].dt.date
df_orders["total"] = df_orders["total"].astype(float)


def salvar_em_destinos(fig, filename: str):
    """Salva a figura em alta resolução (300 DPI) nos diretórios necessários."""
    caminho_proc = PROCESSED_DIR / filename
    caminho_rep = REPORT_IMG_DIR / filename
    fig.savefig(caminho_proc, dpi=300, bbox_inches="tight", pad_inches=0.25)
    fig.savefig(caminho_rep, dpi=300, bbox_inches="tight", pad_inches=0.25)
    plt.close(fig)
    print(f"  ✅ Gráfico salvo (300 DPI): {filename}")


# =============================================================================
# 1. GRÁFICO 1 (Q1 — EDA): Distribuição do Total de Pedidos e Limite IQR
# =============================================================================
def gerar_grafico_1():
    fig, ax = plt.subplots(figsize=(11, 5.5))
    
    valores = df_orders["total"]
    q1 = valores.quantile(0.25)
    mediana = valores.median()
    q3 = valores.quantile(0.75)
    iqr = q3 - q1
    lim_sup = q3 + 1.5 * iqr
    media = valores.mean()
    
    n, bins, patches = ax.hist(valores, bins=45, color=C_STEEL_BLUE, alpha=0.85, edgecolor=C_WHITE, linewidth=0.8)
    
    l_med = ax.axvline(media, color=C_BLUE_ACCENT, linestyle="--", linewidth=2.0, label=f"Média Global: R$ {media:,.2f}")
    l_mediana = ax.axvline(mediana, color=C_TEAL_SUCCESS, linestyle="-", linewidth=2.0, label=f"Mediana (Q2): R$ {mediana:,.2f}")
    l_iqr = ax.axvline(lim_sup, color=C_CORAL_ALERT, linestyle=":", linewidth=2.2, label=f"Limite Superior IQR: R$ {lim_sup:,.2f} (452 Outliers Legítimos)")
    
    ax.set_title("Distribuição do Valor dos Pedidos — Auditoria Transacional (`orders`)", fontsize=13, fontweight='bold', color=C_NAVY_DARK, pad=16)
    ax.text(0, 1.02, "Concentração em faixas comerciais náuticas. Outliers representam vendas legítimas de lanchas e motores.", transform=ax.transAxes, fontsize=9.5, color=C_GRAY_MUTED)
    
    ax.set_xlabel("Valor Total do Pedido (R$)", fontsize=10, fontweight='bold', color=C_NAVY_DARK, labelpad=10)
    ax.set_ylabel("Quantidade de Pedidos", fontsize=10, fontweight='bold', color=C_NAVY_DARK, labelpad=10)
    ax.xaxis.set_major_formatter(ticker.FuncFormatter(lambda x, p: f"R$ {x*1e-3:,.0f}k" if x > 0 else "R$ 0"))
    ax.yaxis.set_major_formatter(ticker.FuncFormatter(lambda x, p: f"{int(x):,}"))
    
    ax.set_xlim(-1000, 135000)
    ax.set_ylim(0, max(n) * 1.18)
    
    # Legenda embaixo, limpa e desobstruída
    ax.legend(
        loc="upper center", bbox_to_anchor=(0.5, -0.16),
        ncol=3, fontsize=9.5, frameon=True,
        facecolor=C_BG_CARD, edgecolor=C_GRAY_LINE
    )
    
    ax.spines['top'].set_visible(False)
    ax.spines['right'].set_visible(False)
    ax.spines['left'].set_color(C_GRAY_LINE)
    ax.spines['bottom'].set_color(C_GRAY_LINE)
    ax.grid(axis='y', linestyle='--', alpha=0.5, color=C_GRAY_LINE)
    
    salvar_em_destinos(fig, "1_eda_distribuicao_pedidos.png")


# =============================================================================
# 2. GRÁFICO 2 (Q1 — EDA): Canais de Venda e Status dos Pedidos
# =============================================================================
def gerar_grafico_2():
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(13, 5.2))
    
    # Canal
    canal_counts = df_orders["channel"].value_counts()
    labels_canal = ["E-commerce", "Loja Física (POS)"]
    vals_canal = [canal_counts.get("ecommerce", 0), canal_counts.get("pos", 0)]
    tot_canal = sum(vals_canal)
    
    bars1 = ax1.bar(labels_canal, vals_canal, color=[C_BLUE_CYAN, C_STEEL_BLUE], width=0.52, edgecolor=C_WHITE)
    ax1.set_title("Volume por Canal de Venda", fontsize=11.5, fontweight='bold', color=C_NAVY_DARK, pad=12)
    ax1.set_ylabel("Quantidade de Pedidos", fontsize=9.5, fontweight='bold', color=C_NAVY_DARK)
    ax1.yaxis.set_major_formatter(ticker.FuncFormatter(lambda x, p: f"{int(x):,}"))
    ax1.set_ylim(0, max(vals_canal) * 1.25)
    
    for bar in bars1:
        yval = bar.get_height()
        pct = yval / tot_canal * 100
        ax1.text(bar.get_x() + bar.get_width()/2, yval + (max(vals_canal)*0.03), f"{int(yval):,}\n({pct:.1f}%)", ha='center', va='bottom', fontsize=9, fontweight='bold', color=C_NAVY_DARK)
    
    ax1.spines['top'].set_visible(False)
    ax1.spines['right'].set_visible(False)
    ax1.spines['left'].set_color(C_GRAY_LINE)
    ax1.spines['bottom'].set_color(C_GRAY_LINE)
    ax1.grid(axis='y', linestyle='--', alpha=0.5, color=C_GRAY_LINE)
    
    # Status
    status_counts = df_orders["status"].value_counts()
    status_map = {"paid": "Pago", "confirmed": "Confirmado", "cancelled": "Cancelado", "draft": "Rascunho"}
    colors_status = {"paid": C_TEAL_SUCCESS, "confirmed": C_BLUE_CYAN, "cancelled": C_CORAL_ALERT, "draft": C_GRAY_MUTED}
    
    labels_st = [status_map.get(k, k) for k in status_counts.index]
    vals_st = status_counts.values
    colors_st = [colors_status.get(k, C_STEEL_BLUE) for k in status_counts.index]
    tot_st = sum(vals_st)
    
    bars2 = ax2.bar(labels_st, vals_st, color=colors_st, width=0.58, edgecolor=C_WHITE)
    ax2.set_title("Volume por Status do Pedido", fontsize=11.5, fontweight='bold', color=C_NAVY_DARK, pad=12)
    ax2.yaxis.set_major_formatter(ticker.FuncFormatter(lambda x, p: f"{int(x):,}"))
    ax2.set_ylim(0, max(vals_st) * 1.25)
    
    for bar in bars2:
        yval = bar.get_height()
        pct = yval / tot_st * 100
        ax2.text(bar.get_x() + bar.get_width()/2, yval + (max(vals_st)*0.03), f"{int(yval):,}\n({pct:.1f}%)", ha='center', va='bottom', fontsize=9, fontweight='bold', color=C_NAVY_DARK)
    
    ax2.spines['top'].set_visible(False)
    ax2.spines['right'].set_visible(False)
    ax2.spines['left'].set_color(C_GRAY_LINE)
    ax2.spines['bottom'].set_color(C_GRAY_LINE)
    ax2.grid(axis='y', linestyle='--', alpha=0.5, color=C_GRAY_LINE)
    
    fig.suptitle("Composição Transacional — Canais de Venda e Status Operacionais", fontsize=13, fontweight='bold', color=C_NAVY_DARK, y=1.04)
    salvar_em_destinos(fig, "2_canais_e_status_pedidos.png")


# =============================================================================
# 3. GRÁFICO 3 (Q4): Top 10 Clientes Fiéis por Ticket Médio
# =============================================================================
def gerar_grafico_3():
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
    top10_fieis = (
        metricas[metricas["diversidade_categorias"] >= 13]
        .sort_values(by=["ticket_medio", "customer_id"], ascending=[False, True])
        .head(10)
        .reset_index(drop=True)
    )
    top10_fieis["ranking"] = top10_fieis.index + 1
    
    fig, ax = plt.subplots(figsize=(11.5, 6))
    y_labels = [f"#{r['ranking']} Cliente {r['customer_id']}" for _, r in top10_fieis.iterrows()]
    y_pos = np.arange(len(top10_fieis))
    
    bars = ax.barh(y_pos, top10_fieis["ticket_medio"], color=C_STEEL_BLUE, height=0.62, edgecolor=C_WHITE)
    bars[0].set_color(C_BLUE_ACCENT)  # Destaque Top 1 (#22)
    
    ax.set_yticks(y_pos)
    ax.set_yticklabels(y_labels, fontsize=9.5, fontweight='bold', color=C_NAVY_DARK)
    ax.invert_yaxis()
    
    ax.set_xlabel("Ticket Médio por Pedido (R$)", fontsize=10, fontweight='bold', color=C_NAVY_DARK, labelpad=10)
    ax.xaxis.set_major_formatter(ticker.FuncFormatter(lambda x, p: f"R$ {x*1e-3:,.0f}k" if x > 0 else "R$ 0"))
    
    # Folga ampla de 32% à direita para as anotações não serem cortadas
    ax.set_xlim(0, max(top10_fieis["ticket_medio"]) * 1.32)
    
    for i, bar in enumerate(bars):
        row = top10_fieis.iloc[i]
        val = row["ticket_medio"]
        lbl = f"R$ {val:,.2f}  ({row['frequencia']} pedidos | {row['diversidade_categorias']} categorias)"
        ax.text(val + 600, bar.get_y() + bar.get_height()/2, lbl, va='center', ha='left', fontsize=8.8, fontweight='bold', color=C_NAVY_DARK)
    
    ax.set_title("Top 10 Clientes de Alta Fidelidade — Ranking por Ticket Médio", fontsize=13, fontweight='bold', color=C_NAVY_DARK, pad=16)
    ax.text(0, 1.02, "Critério de Elite: Compras em 13 ou mais categorias distintas. Desempate por customer_id ASC.", transform=ax.transAxes, fontsize=9.5, color=C_GRAY_MUTED)
    
    ax.spines['top'].set_visible(False)
    ax.spines['right'].set_visible(False)
    ax.spines['left'].set_color(C_GRAY_LINE)
    ax.spines['bottom'].set_color(C_GRAY_LINE)
    ax.grid(axis='x', linestyle='--', alpha=0.5, color=C_GRAY_LINE)
    
    salvar_em_destinos(fig, "3_top10_clientes_fieis_ticket_medio.png")


# =============================================================================
# 4. GRÁFICO 4 (Q4): Categorias Mais Demandadas pelo Top 10
# =============================================================================
def gerar_grafico_4():
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
    top10_fieis = metricas[metricas["diversidade_categorias"] >= 13].sort_values(by=["ticket_medio", "customer_id"], ascending=[False, True]).head(10)
    top10_ids = top10_fieis["customer_id"].tolist()
    
    df_itens_top10 = df_chain[df_chain["customer_id"].isin(top10_ids)].merge(
        df_categories[["id", "name"]].rename(columns={"id": "category_id", "name": "category_name"}), on="category_id"
    )
    cat_ranking = df_itens_top10.groupby("category_name")["quantity"].sum().reset_index().sort_values(by="quantity", ascending=False).head(10).reset_index(drop=True)
    cat_ranking["ranking"] = cat_ranking.index + 1
    
    fig, ax = plt.subplots(figsize=(11.5, 6))
    y_pos = np.arange(len(cat_ranking))
    bars = ax.barh(y_pos, cat_ranking["quantity"], color=C_TEAL_SUCCESS, height=0.62, edgecolor=C_WHITE)
    bars[0].set_color(C_BLUE_ACCENT)  # Destaque Categoria Líder ("Hélices")
    
    ax.set_yticks(y_pos)
    ax.set_yticklabels(cat_ranking["category_name"], fontsize=9.5, fontweight='bold', color=C_NAVY_DARK)
    ax.invert_yaxis()
    
    ax.set_xlabel("Volume Total de Itens Comprados (Unidades)", fontsize=10, fontweight='bold', color=C_NAVY_DARK, labelpad=10)
    ax.set_xlim(0, max(cat_ranking["quantity"]) * 1.25)
    
    for i, bar in enumerate(bars):
        val = cat_ranking.iloc[i]["quantity"]
        ax.text(val + 8, bar.get_y() + bar.get_height()/2, f"{val:,} un.", va='center', ha='left', fontsize=9, fontweight='bold', color=C_NAVY_DARK)
    
    ax.set_title("Categorias Mais Demandadas — Grupo dos Top 10 Clientes Fiéis", fontsize=13, fontweight='bold', color=C_NAVY_DARK, pad=16)
    ax.text(0, 1.02, "Volume acumulado de compras pelo segmento VIP. 'Hélices' lidera o consumo com 492 unidades.", transform=ax.transAxes, fontsize=9.5, color=C_GRAY_MUTED)
    
    ax.spines['top'].set_visible(False)
    ax.spines['right'].set_visible(False)
    ax.spines['left'].set_color(C_GRAY_LINE)
    ax.spines['bottom'].set_color(C_GRAY_LINE)
    ax.grid(axis='x', linestyle='--', alpha=0.5, color=C_GRAY_LINE)
    
    salvar_em_destinos(fig, "4_top_categorias_compradas_vip.png")


# =============================================================================
# 5. GRÁFICO 5 (Q5): Vendas POS por Dia da Semana (Com Legenda Afastada Embaixo)
# =============================================================================
def gerar_grafico_5():
    min_date = df_orders["placed_date"].min()
    max_date = df_orders["placed_date"].max()
    full_calendar = pd.DataFrame({"data_calendario": pd.date_range(start=min_date, end=max_date, freq="D").date})
    full_calendar["dia_semana_num"] = pd.to_datetime(full_calendar["data_calendario"]).dt.dayofweek + 1
    dias_map = {1: "Segunda", 2: "Terça", 3: "Quarta", 4: "Quinta", 5: "Sexta", 6: "Sábado", 7: "Domingo"}
    full_calendar["dia_pt"] = full_calendar["dia_semana_num"].map(dias_map)
    
    vendas_pos = df_orders[df_orders["channel"] == "pos"].groupby("placed_date")["total"].sum().reset_index()
    vendas_pos.rename(columns={"placed_date": "data_calendario", "total": "vendas_pos"}, inplace=True)
    
    cal_vendas = full_calendar.merge(vendas_pos, on="data_calendario", how="left").fillna({"vendas_pos": 0.0})
    media_real = cal_vendas.groupby(["dia_semana_num", "dia_pt"]).agg(media_real=("vendas_pos", "mean")).reset_index()
    
    media_ingenua = vendas_pos.merge(full_calendar, on="data_calendario").groupby(["dia_semana_num", "dia_pt"])["vendas_pos"].mean().reset_index()
    media_ingenua.rename(columns={"vendas_pos": "media_ingenua"}, inplace=True)
    comp = media_real.merge(media_ingenua[["dia_semana_num", "media_ingenua"]], on="dia_semana_num").sort_values("dia_semana_num")
    
    fig, ax = plt.subplots(figsize=(11.5, 5.8))
    x = np.arange(len(comp))
    width = 0.36
    
    bars1 = ax.bar(x - width/2, comp["media_real"], width=width, label="Média Real (Com Calendário / Dias Zerados Inclusos)", color=C_BLUE_CYAN, edgecolor=C_WHITE)
    bars2 = ax.bar(x + width/2, comp["media_ingenua"], width=width, label="Média Ingênua (Sem Calendário / Inflada pelo Viés de Sobrevivência)", color=C_CORAL_ALERT, alpha=0.75, edgecolor=C_WHITE)
    
    # Destaque Quinta-feira como pior dia
    bars1[3].set_color(C_STEEL_BLUE)
    
    ax.set_xticks(x)
    ax.set_xticklabels(comp["dia_pt"], fontsize=10, fontweight='bold', color=C_NAVY_DARK)
    ax.set_ylabel("Média Diária de Vendas (R$)", fontsize=10, fontweight='bold', color=C_NAVY_DARK, labelpad=10)
    ax.yaxis.set_major_formatter(ticker.FuncFormatter(lambda v, p: f"R$ {v*1e-3:,.0f}k"))
    ax.set_ylim(0, max(comp["media_ingenua"]) * 1.22)
    
    for i in range(len(comp)):
        v_real = comp.iloc[i]["media_real"]
        v_ing = comp.iloc[i]["media_ingenua"]
        ax.text(x[i] - width/2, v_real + 2500, f"R$ {v_real*1e-3:,.1f}k", ha='center', va='bottom', fontsize=8.5, fontweight='bold', color=C_NAVY_DARK)
        ax.text(x[i] + width/2, v_ing + 2500, f"R$ {v_ing*1e-3:,.1f}k", ha='center', va='bottom', fontsize=8.5, fontweight='bold', color=C_CORAL_ALERT)
    
    ax.set_title("Performance de Vendas em Lojas Físicas (POS) — Impacto da Dimensão Temporal", fontsize=13, fontweight='bold', color=C_NAVY_DARK, pad=16)
    ax.text(0, 1.02, "Eliminação do viés de sobrevivência. A Quinta-feira registra a menor média real: R$ 157.154,32/dia.", transform=ax.transAxes, fontsize=9.5, color=C_GRAY_MUTED)
    
    # LEGENDA TOTALMENTE AFASTADA EMBAIXO
    ax.legend(
        loc="upper center", bbox_to_anchor=(0.5, -0.16),
        ncol=2, fontsize=9.5, frameon=True,
        facecolor=C_BG_CARD, edgecolor=C_GRAY_LINE
    )
    
    ax.spines['top'].set_visible(False)
    ax.spines['right'].set_visible(False)
    ax.spines['left'].set_color(C_GRAY_LINE)
    ax.spines['bottom'].set_color(C_GRAY_LINE)
    ax.grid(axis='y', linestyle='--', alpha=0.5, color=C_GRAY_LINE)
    
    salvar_em_destinos(fig, "5_vendas_pos_calendario_vies.png")


# =============================================================================
# 6. GRÁFICO 6 (Q6): Previsão de Demanda Mensal — Bússola de Bordo 702
# =============================================================================
def gerar_grafico_6():
    prod_ids = df_products[df_products["name"] == "Bússola de Bordo 702"]["id"].tolist()
    variant_ids = df_variants[df_variants["product_id"].isin(prod_ids)]["id"].tolist()
    df_merged = df_orders.rename(columns={"id": "order_id"}).merge(df_items[df_items["product_variant_id"].isin(variant_ids)], on="order_id")
    df_merged["ano_mes"] = pd.to_datetime(df_merged["placed_at"]).dt.to_period("M")
    
    df_mensal = df_merged.groupby("ano_mes")["quantity"].sum().reset_index()
    all_months = pd.period_range(start=df_merged["ano_mes"].min(), end=df_merged["ano_mes"].max(), freq="M")
    df_serie = pd.DataFrame({"ano_mes": all_months}).merge(df_mensal, on="ano_mes", how="left").fillna(0)
    df_serie["quantity"] = df_serie["quantity"].astype(int)
    df_serie["previsao_3m"] = df_serie["quantity"].shift(1).rolling(window=3).mean()
    
    recorte = df_serie[df_serie["ano_mes"] >= pd.Period("2024-06", freq="M")].copy()
    
    fig, ax = plt.subplots(figsize=(12, 5.8))
    x_labels = [str(m) for m in recorte["ano_mes"]]
    x_idx = np.arange(len(recorte))
    
    bars = ax.bar(x_idx, recorte["quantity"], color=C_STEEL_BLUE, alpha=0.75, width=0.6, label="Vendas Históricas Reais (Unidades)", edgecolor=C_WHITE)
    line = ax.plot(x_idx, recorte["previsao_3m"], color=C_CORAL_ALERT, marker="o", linewidth=2.4, markersize=5.5, label="Previsão Média Móvel 3M (Shift 1 - Sem Data Leakage)")
    
    # Destacar o 1º Trimestre de 2026
    idx_2026 = [i for i, m in enumerate(recorte["ano_mes"]) if m >= pd.Period("2026-01", freq="M")]
    for idx in idx_2026:
        bars[idx].set_color(C_BLUE_ACCENT)
        bars[idx].set_alpha(0.95)
    
    ax.set_xticks(x_idx)
    ax.set_xticklabels(x_labels, rotation=45, ha="right", fontsize=9, color=C_NAVY_DARK)
    ax.set_ylabel("Quantidade (Unidades)", fontsize=10, fontweight='bold', color=C_NAVY_DARK, labelpad=10)
    ax.set_ylim(0, max(recorte["quantity"]) * 1.25)
    
    ax.set_title("Modelagem Preditiva de Demanda Mensal — 'Bússola de Bordo 702'", fontsize=13, fontweight='bold', color=C_NAVY_DARK, pad=16)
    ax.text(0, 1.02, "Período de Teste: 1º Tri/2026 (Jan a Mar). Soma da Previsão: 149 unidades | MAE: 19,44 un/mês.", transform=ax.transAxes, fontsize=9.5, color=C_GRAY_MUTED)
    
    # Legenda embaixo afastada
    ax.legend(
        loc="upper center", bbox_to_anchor=(0.5, -0.22),
        ncol=2, fontsize=9.5, frameon=True,
        facecolor=C_BG_CARD, edgecolor=C_GRAY_LINE
    )
    
    ax.spines['top'].set_visible(False)
    ax.spines['right'].set_visible(False)
    ax.spines['left'].set_color(C_GRAY_LINE)
    ax.spines['bottom'].set_color(C_GRAY_LINE)
    ax.grid(axis='y', linestyle='--', alpha=0.5, color=C_GRAY_LINE)
    
    salvar_em_destinos(fig, "6_previsao_demanda_bussola_702.png")


# =============================================================================
# 7. GRÁFICO 7 (Q7): Sistema de Recomendação — Motor de Popa 1949
# =============================================================================
def gerar_grafico_7():
    df_merged = (
        df_orders[["id", "customer_id"]].rename(columns={"id": "order_id"})
        .merge(df_items, on="order_id")
        .merge(df_variants.rename(columns={"id": "product_variant_id"}), on="product_variant_id")
        .merge(df_products.rename(columns={"id": "product_id", "name": "product_name"}), on="product_id")
    )[["customer_id", "product_name"]].drop_duplicates()
    
    matriz_bin = pd.crosstab(index=df_merged["customer_id"], columns=df_merged["product_name"]).map(lambda x: 1 if x > 0 else 0)
    matriz_prod = matriz_bin.T
    sim_matrix = cosine_similarity(matriz_prod.values)
    df_sim = pd.DataFrame(sim_matrix, index=matriz_prod.index, columns=matriz_prod.index)
    
    target = "Motor de Popa 1949"
    ranking = df_sim[target].drop(index=target).sort_values(ascending=False).head(5).reset_index()
    ranking.columns = ["produto", "similaridade"]
    ranking["ranking"] = ranking.index + 1
    
    fig, ax = plt.subplots(figsize=(11.5, 5))
    y_pos = np.arange(len(ranking))
    colors = [C_CORAL_ALERT if p == "asdf" else C_TEAL_SUCCESS for p in ranking["produto"]]
    
    bars = ax.barh(y_pos, ranking["similaridade"], color=colors, height=0.55, edgecolor=C_WHITE)
    ax.set_yticks(y_pos)
    ax.set_yticklabels(ranking["produto"], fontsize=9.5, fontweight='bold', color=C_NAVY_DARK)
    ax.invert_yaxis()
    
    ax.set_xlabel("Similaridade de Cosseno", fontsize=10, fontweight='bold', color=C_NAVY_DARK, labelpad=10)
    
    # Margem ampla de 40% para conter perfeitamente o texto das anotações
    ax.set_xlim(0, max(ranking["similaridade"]) * 1.40)
    
    for i, bar in enumerate(bars):
        val = ranking.iloc[i]["similaridade"]
        tipo = "  (Ruído Cadastral / Teste)" if ranking.iloc[i]["produto"] == "asdf" else "  (Catálogo Comercial Válido)"
        ax.text(val + 0.005, bar.get_y() + bar.get_height()/2, f"{val:.4f}{tipo}", va='center', ha='left', fontsize=9, fontweight='bold', color=C_NAVY_DARK)
    
    ax.set_title(f"Top 5 Recomendações Item-Item em Relação a '{target}'", fontsize=13, fontweight='bold', color=C_NAVY_DARK, pad=16)
    ax.text(0, 1.02, "Similaridade de Cosseno calculada sobre a matriz binária de compras (2.000 clientes x 496 produtos).", transform=ax.transAxes, fontsize=9.5, color=C_GRAY_MUTED)
    
    ax.spines['top'].set_visible(False)
    ax.spines['right'].set_visible(False)
    ax.spines['left'].set_color(C_GRAY_LINE)
    ax.spines['bottom'].set_color(C_GRAY_LINE)
    ax.grid(axis='x', linestyle='--', alpha=0.5, color=C_GRAY_LINE)
    
    salvar_em_destinos(fig, "7_recomendacao_produtos_motor_1949.png")


def executar():
    print("=" * 80)
    print("⚓ LH NAUTICAL — GERAÇÃO DE GRÁFICOS ANALÍTICOS EXECUTIVOS (300 DPI)")
    print("=" * 80)
    gerar_grafico_1()
    gerar_grafico_2()
    gerar_grafico_3()
    gerar_grafico_4()
    gerar_grafico_5()
    gerar_grafico_6()
    gerar_grafico_7()
    print("=" * 80)
    print(f"🎉 Todos os 7 gráficos foram gerados e salvos com sucesso em 300 DPI!")


if __name__ == "__main__":
    executar()
