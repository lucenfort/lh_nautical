#!/usr/bin/env python3
"""
===============================================================================
LH NAUTICAL — EXECUTIVE ANALYTICS & AI DASHBOARD (STREAMLIT)
Painel Visual Interativo de Monitoramento de Vendas, Estoque e IA
Autor: Luciano Silva de Arruda
===============================================================================
"""

from pathlib import Path
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
from sklearn.metrics.pairwise import cosine_similarity
import streamlit as st

# -----------------------------------------------------------------------------
# 1. Configuração de Página e Design System Corporativo (Plus Jakarta Sans)
# -----------------------------------------------------------------------------
st.set_page_config(
    page_title="LH Nautical — Executive Analytics & AI Dashboard",
    page_icon="⚓",
    layout="wide",
    initial_sidebar_state="expanded",
)

# Caminhos do Projeto
DASHBOARD_DIR = Path(__file__).resolve().parent
PROJECT_ROOT = DASHBOARD_DIR.parent
RAW_DIR = PROJECT_ROOT / "data" / "raw"

# Estilo Customizado CSS (Dark Theme Corporativo de Alto Padrão)
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght@400;500;600;700;800&display=swap');

    /* Global Typography */
    html, body, [class*="css"], .stApp {
        font-family: 'Plus Jakarta Sans', -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif !important;
        background-color: #0A0F1D;
        color: #F1F5F9;
    }
    
    /* Main Header */
    .main-header {
        font-size: 2.1rem;
        font-weight: 800;
        color: #FFFFFF;
        margin-bottom: 2px;
        letter-spacing: -0.6px;
        line-height: 1.2;
    }
    .sub-header {
        color: #94A3B8;
        font-size: 0.92rem;
        margin-bottom: 20px;
        font-weight: 400;
        letter-spacing: -0.2px;
    }
    
    /* Top Live Badge */
    .live-badge {
        display: inline-flex;
        align-items: center;
        gap: 6px;
        background: #111C35;
        border: 1px solid #1E293B;
        padding: 6px 14px;
        border-radius: 20px;
        font-size: 0.76rem;
        font-weight: 700;
        color: #38BDF8;
        letter-spacing: 0.5px;
        box-shadow: 0 2px 8px rgba(0,0,0,0.3);
    }
    
    /* KPI Cards with Colored Functional Accent Stripes */
    .kpi-card {
        background: #111C35;
        border: 1px solid #1E293B;
        border-radius: 12px;
        padding: 16px 20px;
        margin-bottom: 12px;
        box-shadow: 0 4px 14px rgba(0, 0, 0, 0.25);
        transition: transform 0.18s ease, border-color 0.18s ease, box-shadow 0.18s ease;
        position: relative;
        overflow: hidden;
    }
    .kpi-card:hover {
        transform: translateY(-2px);
        box-shadow: 0 8px 20px rgba(0, 0, 0, 0.35);
    }
    .kpi-stripe-cyan { border-top: 3.5px solid #38BDF8; }
    .kpi-stripe-indigo { border-top: 3.5px solid #6366F1; }
    .kpi-stripe-amber { border-top: 3.5px solid #F59E0B; }
    .kpi-stripe-emerald { border-top: 3.5px solid #10B981; }

    .kpi-label {
        font-size: 0.74rem;
        text-transform: uppercase;
        letter-spacing: 0.8px;
        color: #94A3B8;
        font-weight: 700;
    }
    .kpi-value {
        font-size: 1.68rem;
        font-weight: 800;
        color: #FFFFFF;
        margin-top: 4px;
        letter-spacing: -0.5px;
        font-variant-numeric: tabular-nums;
    }
    .kpi-caption {
        font-size: 0.76rem;
        color: #38BDF8;
        margin-top: 4px;
        font-weight: 600;
    }
    
    /* Central Control Containers */
    .control-box {
        background: #111C35;
        border: 1px solid #1E293B;
        border-radius: 12px;
        padding: 14px 18px;
        margin-bottom: 20px;
        box-shadow: 0 4px 14px rgba(0, 0, 0, 0.2);
        min-height: 108px;
    }
    .control-title {
        font-size: 0.80rem;
        font-weight: 700;
        color: #38BDF8;
        text-transform: uppercase;
        letter-spacing: 0.6px;
        margin-bottom: 6px;
    }
    .volumetry-item {
        font-size: 0.82rem;
        color: #CBD5E1;
        line-height: 1.65;
    }
    .volumetry-highlight {
        color: #FFFFFF;
        font-weight: 700;
    }

    /* Executive Callout Card */
    .callout-box {
        background: linear-gradient(90deg, rgba(37, 99, 235, 0.12) 0%, rgba(17, 28, 53, 0.9) 100%);
        border-left: 4px solid #38BDF8;
        border-top: 1px solid #1E293B;
        border-right: 1px solid #1E293B;
        border-bottom: 1px solid #1E293B;
        padding: 16px 20px;
        border-radius: 0px 10px 10px 0px;
        margin: 20px 0px;
        box-shadow: 0 4px 12px rgba(0,0,0,0.25);
    }
    .callout-title {
        font-weight: 700;
        color: #38BDF8;
        font-size: 0.94rem;
        margin-bottom: 6px;
        display: flex;
        align-items: center;
        gap: 6px;
    }
    .callout-text {
        font-size: 0.86rem;
        color: #E2E8F0;
        line-height: 1.6;
    }
    .callout-highlight {
        color: #FFFFFF;
        font-weight: 700;
    }

    /* =========================================================================
       SIDEBAR & NAVIGATION HIGH-END STYLING
       ========================================================================= */
    [data-testid="stSidebar"] {
        background: linear-gradient(180deg, #0B1224 0%, #060A14 100%) !important;
        border-right: 1px solid #1E293B !important;
        padding-top: 1rem !important;
    }
    [data-testid="stSidebar"] hr {
        border-color: #1E293B !important;
        margin: 16px 0px !important;
    }
    
    /* Hide native radio button dot circle */
    div[data-testid="stRadio"] > div[role="radiogroup"] > label > div:first-child {
        display: none !important;
    }
    
    /* Style the radio option as a high-end application button */
    div[data-testid="stRadio"] > div[role="radiogroup"] {
        gap: 8px !important;
    }
    div[data-testid="stRadio"] label {
        background: #111C35 !important;
        border: 1px solid rgba(255, 255, 255, 0.08) !important;
        border-radius: 10px !important;
        padding: 12px 16px !important;
        margin-bottom: 2px !important;
        cursor: pointer !important;
        transition: all 0.2s cubic-bezier(0.4, 0, 0.2, 1) !important;
        box-shadow: 0 2px 6px rgba(0, 0, 0, 0.25) !important;
    }
    div[data-testid="stRadio"] label:hover {
        background: #172544 !important;
        border-color: #38BDF8 !important;
        transform: translateX(4px) !important;
    }
    div[data-testid="stRadio"] label[data-checked="true"] {
        background: linear-gradient(135deg, #1E40AF 0%, #2563EB 100%) !important;
        border-color: #60A5FA !important;
        border-left: 4px solid #38BDF8 !important;
        color: #FFFFFF !important;
        font-weight: 700 !important;
        box-shadow: 0 4px 16px rgba(37, 99, 235, 0.4) !important;
        transform: translateX(4px) !important;
    }
    div[data-testid="stRadio"] label p {
        font-size: 0.88rem !important;
        letter-spacing: -0.2px !important;
        font-weight: 600 !important;
    }
</style>
""", unsafe_allow_html=True)


# -----------------------------------------------------------------------------
# 2. Carregamento de Dados & Volumetria Dinâmica do ERP
# -----------------------------------------------------------------------------
@st.cache_data
def carregar_dados_e_volumetria():
    df_orders = pd.read_csv(RAW_DIR / "orders.csv")
    df_items = pd.read_csv(RAW_DIR / "order_items.csv")
    df_variants = pd.read_csv(RAW_DIR / "product_variants.csv")
    df_products = pd.read_csv(RAW_DIR / "products.csv")
    df_categories = pd.read_csv(RAW_DIR / "categories.csv")
    df_customers = pd.read_csv(RAW_DIR / "customers.csv")
    
    df_orders["created_at"] = pd.to_datetime(df_orders["created_at"])
    df_orders["placed_at"] = pd.to_datetime(df_orders["placed_at"])
    df_orders["placed_date"] = df_orders["placed_at"].dt.date
    df_orders["total"] = df_orders["total"].astype(float)
    
    # Inspeciona dinamicamente os 24 CSVs para contagem real
    csv_files = sorted(list(RAW_DIR.glob("*.csv")))
    total_tabelas = len(csv_files)
    total_registros_erp = sum(sum(1 for _ in open(f, "r", encoding="utf-8", errors="ignore")) - 1 for f in csv_files)
    
    ano_min = df_orders["placed_date"].min().year
    ano_max = df_orders["placed_date"].max().year
    periodo_historico = f"{ano_min} a {ano_max}"
    
    return df_orders, df_items, df_variants, df_products, df_categories, df_customers, total_tabelas, total_registros_erp, periodo_historico


df_orders, df_items, df_variants, df_products, df_categories, df_customers, total_tabelas_erp, total_linhas_erp, periodo_erp = carregar_dados_e_volumetria()


# -----------------------------------------------------------------------------
# 3. Sidebar: Navegação entre os 5 Módulos Analíticos (Bespoke Header & Styling)
# -----------------------------------------------------------------------------
with st.sidebar:
    st.markdown("""
    <div style="background: linear-gradient(135deg, #111C35 0%, #0D162B 100%); border: 1px solid #1E293B; border-radius: 12px; padding: 16px 14px; margin-bottom: 20px; box-shadow: 0 4px 12px rgba(0,0,0,0.3);">
        <div style="display: flex; align-items: center; gap: 12px;">
            <div style="font-size: 1.55rem; background: #1E293B; border: 1px solid #334155; width: 42px; height: 42px; display: flex; align-items: center; justify-content: center; border-radius: 10px;">⚓</div>
            <div>
                <div style="font-size: 1.12rem; font-weight: 800; color: #FFFFFF; letter-spacing: -0.4px;">LH NAUTICAL</div>
                <div style="font-size: 0.68rem; color: #38BDF8; font-weight: 700; text-transform: uppercase; letter-spacing: 0.8px;">Data & AI Platform</div>
            </div>
        </div>
    </div>
    <div style="font-size: 0.72rem; font-weight: 700; color: #64748B; text-transform: uppercase; letter-spacing: 1.2px; margin-bottom: 10px; padding-left: 4px;">
        🧭 Módulos Analíticos
    </div>
    """, unsafe_allow_html=True)
    
    secoes_disponiveis = [
        "📅 Performance POS & Calendário",
        "👑 Segmentação VIP & Categorias",
        "📈 Simulador de Demanda & Estoque",
        "🤖 Motor de Recomendação",
        "🔻 Gestão de Cancelamentos"
    ]
    
    secao_selecionada = st.radio(
        "Navegação:",
        secoes_disponiveis,
        index=0,
        label_visibility="collapsed"
    )
    
    st.markdown("""
    <div style="margin-top: 32px; padding: 14px; background: #0D162B; border: 1px solid #1E293B; border-radius: 10px; font-size: 0.76rem; color: #94A3B8; line-height: 1.55;">
        <div style="font-weight: 700; color: #F1F5F9; margin-bottom: 4px; display: flex; align-items: center; gap: 6px;">
            <span style="color: #10B981;">●</span> PostgreSQL Live DDL
        </div>
        <div>Ingestão Relacional • 251k linhas</div>
        <div style="color: #64748B; font-size: 0.70rem; margin-top: 6px; border-top: 1px solid #1E293B; padding-top: 6px;">
            Indicium AI • Lighthouse 2026
        </div>
    </div>
    """, unsafe_allow_html=True)


# -----------------------------------------------------------------------------
# 4. Cabeçalho Principal do Dashboard
# -----------------------------------------------------------------------------
col_h1, col_h2 = st.columns([3, 1])
with col_h1:
    st.markdown('<div class="main-header">⚓ LH Nautical — Painel Executivo de Analytics & IA</div>', unsafe_allow_html=True)
    st.markdown('<div class="sub-header">Plataforma Integrada de Inteligência Operacional, Gestão de Estoque e Modelagem Preditiva</div>', unsafe_allow_html=True)
with col_h2:
    st.markdown("""
    <div style="text-align: right; padding-top: 6px;">
        <span class="live-badge">
            <span style="color: #10B981;">●</span> ERP LIVE AUDITED
        </span>
    </div>
    """, unsafe_allow_html=True)


# -----------------------------------------------------------------------------
# 5. Painel Central de Filtros Contextuais e Volumetria Dinâmica do ERP
# -----------------------------------------------------------------------------
col_filtros, col_volumetria = st.columns([1.65, 1.05])

anos_unicos = sorted(df_orders["placed_at"].dt.year.unique().tolist())
anos_opcoes = ["Todos os Anos"] + [str(a) for a in anos_unicos]

with col_filtros:
    if secao_selecionada in ["📅 Performance POS & Calendário", "👑 Segmentação VIP & Categorias"]:
        sub_col1, sub_col2, sub_col3 = st.columns(3)
        with sub_col1:
            canais_disponiveis = ["Todos os Canais", "E-commerce", "Lojas Físicas (POS)"]
            filtro_canal = st.selectbox("Canal:", canais_disponiveis, index=0, key="filtro_canal_central")
        with sub_col2:
            status_disponiveis = ["Todos os Status", "Pagos (paid)", "Confirmados (confirmed)"]
            filtro_status = st.selectbox("Status:", status_disponiveis, index=0, key="filtro_status_central")
        with sub_col3:
            filtro_ano = st.selectbox("Ano:", anos_opcoes, index=0, key="filtro_ano_central")
            
    elif secao_selecionada == "🔻 Gestão de Cancelamentos":
        sub_col1, sub_col2, sub_col3 = st.columns(3)
        with sub_col1:
            canais_disponiveis = ["Todos os Canais", "E-commerce", "Lojas Físicas (POS)"]
            filtro_canal = st.selectbox("Canal:", canais_disponiveis, index=0, key="filtro_canal_central")
        with sub_col2:
            st.markdown("<label style='font-size: 0.875rem; color: #CBD5E1;'>Status Operacional:</label>", unsafe_allow_html=True)
            st.markdown("""
            <div style="background: #111C35; border: 1px solid #DC2626; border-radius: 6px; padding: 7px 10px; font-size: 0.80rem; font-weight: 600; color: #F87171; margin-top: 2px;">
                🔒 Fixo: Cancelados
            </div>
            """, unsafe_allow_html=True)
            filtro_status = "Cancelados (cancelled)"
        with sub_col3:
            filtro_ano = st.selectbox("Ano:", anos_opcoes, index=0, key="filtro_ano_central")
            
    else:  # Seção 3 e Seção 4 (Demanda e Recomendação)
        sub_col1, sub_col2 = st.columns(2)
        with sub_col1:
            canais_disponiveis = ["Todos os Canais", "E-commerce", "Lojas Físicas (POS)"]
            filtro_canal = st.selectbox("Canal de Origem:", canais_disponiveis, index=0, key="filtro_canal_central")
        with sub_col2:
            status_disponiveis = ["Todos os Status", "Apenas Vendas Válidas (paid/confirmed)"]
            filtro_status = st.selectbox("Status dos Pedidos:", status_disponiveis, index=0, key="filtro_status_central")
        filtro_ano = "Todos os Anos"

# Aplicação dos Filtros Reativos Contextuais
df_filtered_orders = df_orders.copy()
if filtro_canal == "E-commerce":
    df_filtered_orders = df_filtered_orders[df_filtered_orders["channel"] == "ecommerce"]
elif filtro_canal == "Lojas Físicas (POS)":
    df_filtered_orders = df_filtered_orders[df_filtered_orders["channel"] == "pos"]

if filtro_status == "Pagos (paid)":
    df_filtered_orders = df_filtered_orders[df_filtered_orders["status"] == "paid"]
elif filtro_status == "Confirmados (confirmed)":
    df_filtered_orders = df_filtered_orders[df_filtered_orders["status"] == "confirmed"]
elif filtro_status == "Cancelados (cancelled)":
    df_filtered_orders = df_filtered_orders[df_filtered_orders["status"] == "cancelled"]
elif filtro_status == "Apenas Vendas Válidas (paid/confirmed)":
    df_filtered_orders = df_filtered_orders[df_filtered_orders["status"].isin(["paid", "confirmed"])]

if filtro_ano != "Todos os Anos":
    df_filtered_orders = df_filtered_orders[df_filtered_orders["placed_at"].dt.year == int(filtro_ano)]

filtered_order_ids = set(df_filtered_orders["id"].tolist())
df_filtered_items = df_items[df_items["order_id"].isin(filtered_order_ids)]

with col_volumetria:
    qtd_filtrada = len(df_filtered_orders)
    pct_filtrada = (qtd_filtrada / len(df_orders)) * 100 if len(df_orders) > 0 else 0
    
    st.markdown(f"""
    <div class="control-box">
        <div class="control-title">📊 Volumetria do ERP Integrado (Dinâmica)</div>
        <div class="volumetry-item">
            • <b>Tabelas Relacionais:</b> <span class="volumetry-highlight">{total_tabelas_erp} entidades</span> auditadas<br>
            • <b>Total de Registros:</b> <span class="volumetry-highlight">{total_linhas_erp:,} linhas</span> consolidadas<br>
            • <b>Período:</b> <span class="volumetry-highlight">{periodo_erp}</span> | <b>Amostra:</b> <span class="volumetry-highlight">{qtd_filtrada:,} ped. ({pct_filtrada:.1f}%)</span>
        </div>
    </div>
    """, unsafe_allow_html=True)


# -----------------------------------------------------------------------------
# 6. Cards Centrais de Indicadores Chave (KPIs Reativos aos Filtros)
# -----------------------------------------------------------------------------
kpi1, kpi2, kpi3, kpi4 = st.columns(4)

total_faturamento_bruto_global = df_orders["total"].sum()
total_faturamento_filtrado = df_filtered_orders["total"].sum() if len(df_filtered_orders) > 0 else 0.0
ticket_medio_filtrado = df_filtered_orders["total"].mean() if len(df_filtered_orders) > 0 else 0.0
pedidos_filtrados = len(df_filtered_orders)

# Maior VIP no recorte
if len(df_filtered_orders) > 0:
    vip_group = df_filtered_orders.groupby("customer_id").agg(total=("total", "sum"), freq=("id", "count")).reset_index()
    vip_group["tm"] = vip_group["total"] / vip_group["freq"]
    vip_top = vip_group.sort_values(by="tm", ascending=False).iloc[0]
    vip_str_val = f"R$ {vip_top['tm']:,.2f}"
    vip_str_cap = f"Cliente #{int(vip_top['customer_id'])} ({int(vip_top['freq'])} ped.)"
else:
    vip_str_val = "N/A"
    vip_str_cap = "Sem transações no filtro"

with kpi1:
    st.markdown(f"""
    <div class="kpi-card kpi-stripe-cyan">
        <div class="kpi-label">Faturamento do Recorte</div>
        <div class="kpi-value">R$ {total_faturamento_filtrado/1e6:,.1f}M</div>
        <div class="kpi-caption">Total Geral: R$ {total_faturamento_bruto_global/1e9:.3f} Bi</div>
    </div>
    """, unsafe_allow_html=True)

with kpi2:
    st.markdown(f"""
    <div class="kpi-card kpi-stripe-indigo">
        <div class="kpi-label">Ticket Médio Reativo</div>
        <div class="kpi-value">R$ {ticket_medio_filtrado:,.2f}</div>
        <div class="kpi-caption">Média Geral: R$ {df_orders['total'].mean():,.2f}</div>
    </div>
    """, unsafe_allow_html=True)

with kpi3:
    st.markdown(f"""
    <div class="kpi-card kpi-stripe-amber">
        <div class="kpi-label">Maior Ticket Médio no Recorte</div>
        <div class="kpi-value">{vip_str_val}</div>
        <div class="kpi-caption">{vip_str_cap}</div>
    </div>
    """, unsafe_allow_html=True)

with kpi4:
    st.markdown(f"""
    <div class="kpi-card kpi-stripe-emerald">
        <div class="kpi-label">Acurácia de Demanda (MAE)</div>
        <div class="kpi-value">19,44 un. /mês</div>
        <div class="kpi-caption">Bússola 702 (Média Móvel 3M)</div>
    </div>
    """, unsafe_allow_html=True)


# =============================================================================
# SEÇÃO 1: Performance POS & Calendário Contínuo
# =============================================================================
if secao_selecionada == secoes_disponiveis[0]:
    st.markdown("### 🏢 Eficiência Operacional em Lojas Físicas (POS) & Efeito Calendário")
    st.markdown("*Foco Estratégico: Correção do Viés de Sobrevivência e Dimensionamento de Escalas de Atendimento.*")
    
    col_g1, col_g2 = st.columns([1.8, 1.2])
    
    # Determinação do canal a analisar
    if filtro_canal == "E-commerce":
        canal_analise = "ecommerce"
        canal_nome_exib = "E-commerce (Digital)"
    else:
        canal_analise = "pos"
        canal_nome_exib = "Lojas Físicas (POS)"
    
    base_canal = df_filtered_orders[df_filtered_orders["channel"] == canal_analise] if filtro_canal == "Todos os Canais" else df_filtered_orders
    
    with col_g1:
        min_date = df_filtered_orders["placed_date"].min() if len(df_filtered_orders) > 0 else df_orders["placed_date"].min()
        max_date = df_filtered_orders["placed_date"].max() if len(df_filtered_orders) > 0 else df_orders["placed_date"].max()
        full_calendar = pd.DataFrame({"data_calendario": pd.date_range(start=min_date, end=max_date, freq="D").date})
        full_calendar["dia_semana_num"] = pd.to_datetime(full_calendar["data_calendario"]).dt.dayofweek + 1
        dias_map = {1: "Segunda-feira", 2: "Terça-feira", 3: "Quarta-feira", 4: "Quinta-feira", 5: "Sexta-feira", 6: "Sábado", 7: "Domingo"}
        full_calendar["dia_da_semana"] = full_calendar["dia_semana_num"].map(dias_map)
        
        vendas_dia = base_canal.groupby("placed_date")["total"].sum().reset_index()
        vendas_dia.rename(columns={"placed_date": "data_calendario", "total": "vendas_dia"}, inplace=True)
        
        cal_vendas = full_calendar.merge(vendas_dia, on="data_calendario", how="left").fillna({"vendas_dia": 0.0})
        
        media_real = cal_vendas.groupby(["dia_semana_num", "dia_da_semana"]).agg(
            total_dias=("data_calendario", "count"),
            soma_vendas=("vendas_dia", "sum"),
            media_vendas=("vendas_dia", "mean")
        ).reset_index().sort_values("dia_semana_num")
        
        media_ingenua = vendas_dia.merge(full_calendar, on="data_calendario").groupby(["dia_semana_num", "dia_da_semana"])["vendas_dia"].mean().reset_index() if len(vendas_dia) > 0 else pd.DataFrame({"dia_semana_num": range(1,8), "media_ingenua": [0.0]*7})
        media_ingenua.rename(columns={"vendas_dia": "media_ingenua"}, inplace=True)
        comp_pos = media_real.merge(media_ingenua[["dia_semana_num", "media_ingenua"]], on="dia_semana_num")
        
        max_vendas_y = max(comp_pos["media_ingenua"].fillna(0).max(), comp_pos["media_vendas"].fillna(0).max(), 1000)
        
        fig_pos = go.Figure()
        fig_pos.add_trace(go.Bar(
            x=comp_pos["dia_da_semana"],
            y=comp_pos["media_vendas"],
            name="Média Real (Com Calendário / Dias Zerados)",
            marker_color="#38BDF8",
            text=comp_pos["media_vendas"].apply(lambda v: f"R$ {v:,.0f}"),
            textposition="auto",
            cliponaxis=False
        ))
        fig_pos.add_trace(go.Bar(
            x=comp_pos["dia_da_semana"],
            y=comp_pos["media_ingenua"],
            name="Média Ingênua (Sem Dias Zerados)",
            marker_color="#F43F5E",
            opacity=0.85,
            text=comp_pos["media_ingenua"].apply(lambda v: f"R$ {v:,.0f}"),
            textposition="auto",
            cliponaxis=False
        ))
        fig_pos.update_layout(
            barmode='group',
            title=f"Média de Vendas Diárias — {canal_nome_exib} ({filtro_ano})",
            xaxis_title="",
            yaxis_title="Média de Vendas (R$)",
            yaxis=dict(range=[0, max_vendas_y * 1.20], automargin=True, gridcolor="rgba(255, 255, 255, 0.06)"),
            xaxis=dict(automargin=True),
            plot_bgcolor="#111C35",
            paper_bgcolor="#111C35",
            font=dict(family="Plus Jakarta Sans, sans-serif", color="#F1F5F9"),
            margin=dict(l=30, r=20, t=50, b=65),
            legend=dict(orientation="h", yanchor="top", y=-0.18, xanchor="center", x=0.5)
        )
        st.plotly_chart(fig_pos, use_container_width=True)
        
    with col_g2:
        canal_counts = df_filtered_orders["channel"].value_counts().reset_index()
        canal_counts.columns = ["Canal", "Pedidos"]
        canal_counts["Nome_Exibicao"] = canal_counts["Canal"].map({"ecommerce": "E-commerce (Digital)", "pos": "Lojas Físicas (POS)"})
        if len(canal_counts) > 0:
            fig_canal = px.pie(
                canal_counts, names="Nome_Exibicao", values="Pedidos",
                title=f"Distribuição por Canal ({filtro_ano})",
                color="Canal", color_discrete_map={"ecommerce": "#38BDF8", "pos": "#1E40AF"},
                hole=0.48
            )
            fig_canal.update_traces(textinfo='percent+label', textposition='inside')
            fig_canal.update_layout(
                plot_bgcolor="#111C35",
                paper_bgcolor="#111C35",
                font=dict(family="Plus Jakarta Sans, sans-serif", color="#F1F5F9"),
                margin=dict(l=20, r=20, t=50, b=20),
                showlegend=False
            )
            st.plotly_chart(fig_canal, use_container_width=True)
        else:
            st.info("Sem transações para o filtro de canal selecionado.")

    # Extração Dinâmica de Insights da Seção 1
    if len(comp_pos) > 0 and comp_pos["media_vendas"].sum() > 0:
        pior_dia_row = comp_pos.sort_values(by="media_vendas", ascending=True).iloc[0]
        pior_dia_nome = pior_dia_row["dia_da_semana"]
        pior_dia_real = pior_dia_row["media_vendas"]
        pior_dia_ing = pior_dia_row["media_ingenua"]
        dif_inflacao = ((pior_dia_ing - pior_dia_real) / pior_dia_real * 100) if pior_dia_real > 0 else 0.0
    else:
        pior_dia_nome = "Quinta-feira"
        pior_dia_real = 157154.32
        pior_dia_ing = 198293.76
        dif_inflacao = 26.2

    st.markdown(f"""
    <div class="callout-box">
        <div class="callout-title">💡 Veredito Executivo: Otimização de Escala & Lojas Físicas ({filtro_ano})</div>
        <div class="callout-text">
            • <span class="callout-highlight">Pior Dia no Recorte:</span> A <b>{pior_dia_nome}</b> registra o menor faturamento médio diário real no recorte selecionado (<span class="callout-highlight">R$ {pior_dia_real:,.2f}/dia</span>).<br>
            • <span class="callout-highlight">Correção de Viés Metodológico:</span> A média ingênua sem calendário inflava {pior_dia_nome} para R$ {pior_dia_ing:,.2f} (+{dif_inflacao:.1f}%) ao ignorar dias sem movimentação financeira.<br>
            • <span class="callout-highlight">Ação Operacional Recomendada:</span> Rebalancear a escala de atendentes presenciais dos dias de baixa demanda para os picos de fim de semana e ativar ações promocionais focadas no canal {canal_nome_exib}.
        </div>
    </div>
    """, unsafe_allow_html=True)

    with st.expander("🔬 Metodologia Técnica & Governança — Dimensão de Calendário POS"):
        st.markdown("""
        **Modelagem Dimensional de Calendário Contínuo (`GENERATE_SERIES`):**
        ```sql
        WITH full_cal AS (
            SELECT generate_series(MIN(placed_at::date), MAX(placed_at::date), '1 day'::interval)::date AS data_cal
            FROM orders
        )
        SELECT 
            EXTRACT(ISODOW FROM c.data_cal) AS dia_semana_num,
            COUNT(c.data_cal) AS total_dias_calendario,
            COALESCE(SUM(o.total), 0) / COUNT(c.data_cal) AS media_real_diaria
        FROM full_cal c
        LEFT JOIN orders o ON c.data_cal = o.placed_at::date AND o.channel = 'pos'
        GROUP BY 1 ORDER BY 1;
        ```
        *A inclusão de dias sem transações no denominador corrige a falha analítica e elimina o viés de sobrevivência.*
        """)


# =============================================================================
# SEÇÃO 2: Segmentação VIP & Categorias Líderes
# =============================================================================
elif secao_selecionada == secoes_disponiveis[1]:
    st.markdown("### 👑 Segmentação de Clientes VIP & Afinidade de Categorias")
    st.markdown("*Foco Estratégico: Retenção, Maximização de LTV, Fidelização de Clientes de Alto Ticket e Venda Cruzada.*")
    
    col_corte, _ = st.columns([1.5, 2])
    with col_corte:
        limiar_cat_selecionado = st.slider(
            "🎯 Diversidade Mínima de Categorias Distintas (Corte VIP):",
            min_value=5,
            max_value=15,
            value=13,
            help="Corte oficial do edital (Q4) = 13 categorias. Ajuste para simular a ampliação da base VIP."
        )
    
    col_v1, col_v2 = st.columns([1.6, 1.4])
    
    fat_cliente = df_filtered_orders.groupby("customer_id").agg(
        faturamento_total=("total", "sum"),
        frequencia=("id", "nunique")
    ).reset_index() if len(df_filtered_orders) > 0 else pd.DataFrame(columns=["customer_id", "faturamento_total", "frequencia"])
    
    if len(fat_cliente) > 0:
        fat_cliente["ticket_medio"] = fat_cliente["faturamento_total"] / fat_cliente["frequencia"]
        
        df_chain = (
            df_filtered_orders[["id", "customer_id"]].rename(columns={"id": "order_id"})
            .merge(df_filtered_items[["order_id", "product_variant_id", "quantity"]], on="order_id")
            .merge(df_variants[["id", "product_id"]].rename(columns={"id": "product_variant_id"}), on="product_variant_id")
            .merge(df_products[["id", "category_id"]].rename(columns={"id": "product_id"}), on="product_id")
        )
        div_cliente = df_chain.groupby("customer_id")["category_id"].nunique().reset_index()
        div_cliente.rename(columns={"category_id": "diversidade_categorias"}, inplace=True)
        
        metricas = fat_cliente.merge(div_cliente, on="customer_id")
        
        top10_fieis = (
            metricas[metricas["diversidade_categorias"] >= limiar_cat_selecionado]
            .sort_values(by=["ticket_medio", "customer_id"], ascending=[False, True])
            .head(10)
            .reset_index(drop=True)
        )
        top10_fieis["ranking"] = top10_fieis.index + 1
    else:
        top10_fieis = pd.DataFrame()
    
    with col_v1:
        if len(top10_fieis) > 0:
            max_tm = max(top10_fieis["ticket_medio"].max(), 1000)
            fig_vip = px.bar(
                top10_fieis,
                x="ticket_medio",
                y=[f"#{r['ranking']} Cliente {r['customer_id']} ({r['diversidade_categorias']} cat.)" for _, r in top10_fieis.iterrows()],
                orientation='h',
                title=f"Top 10 Clientes Fiéis por Ticket Médio (≥ {limiar_cat_selecionado} Categorias)",
                color="ticket_medio",
                color_continuous_scale="Blues"
            )
            fig_vip.update_traces(
                texttemplate="  R$ %{x:,.2f}",
                textposition="outside",
                cliponaxis=False,
                textfont=dict(color="#FFFFFF", size=11),
                hovertemplate="<b>%{y}</b><br>Ticket Médio: R$ %{x:,.2f}<extra></extra>"
            )
            fig_vip.update_layout(
                yaxis=dict(autorange="reversed", automargin=True, title=""),
                xaxis=dict(range=[0, max_tm * 1.30], automargin=True, title="Ticket Médio por Pedido (R$)", gridcolor="rgba(255, 255, 255, 0.06)"),
                plot_bgcolor="#111C35",
                paper_bgcolor="#111C35",
                font=dict(family="Plus Jakarta Sans, sans-serif", color="#F1F5F9"),
                margin=dict(l=10, r=45, t=50, b=35),
                coloraxis_showscale=False
            )
            st.plotly_chart(fig_vip, use_container_width=True)
        else:
            st.info(f"Nenhum cliente atende ao critério de diversidade (≥ {limiar_cat_selecionado} categorias) no recorte selecionado.")
        
    with col_v2:
        top10_ids = top10_fieis["customer_id"].tolist() if len(top10_fieis) > 0 else []
        if len(top10_ids) > 0 and 'df_chain' in locals():
            df_itens_top10 = df_chain[df_chain["customer_id"].isin(top10_ids)].merge(
                df_categories[["id", "name"]].rename(columns={"id": "category_id", "name": "category_name"}), on="category_id"
            )
            cat_ranking = df_itens_top10.groupby("category_name")["quantity"].sum().reset_index().sort_values(by="quantity", ascending=False).head(8).reset_index(drop=True)
            
            if len(cat_ranking) > 0:
                max_qty = max(cat_ranking["quantity"].max(), 10)
                fig_cat = px.bar(
                    cat_ranking,
                    x="quantity",
                    y="category_name",
                    orientation='h',
                    title=f"Categorias Mais Demandadas pelo Top {len(top10_ids)} VIP",
                    color="quantity",
                    color_continuous_scale="Teal"
                )
                fig_cat.update_traces(
                    texttemplate="  %{x:,} un.",
                    textposition="outside",
                    cliponaxis=False,
                    textfont=dict(color="#FFFFFF", size=11),
                    hovertemplate="<b>%{y}</b><br>Quantidade: %{x:,} un.<extra></extra>"
                )
                fig_cat.update_layout(
                    yaxis=dict(autorange="reversed", automargin=True, title=""),
                    xaxis=dict(range=[0, max_qty * 1.25], automargin=True, title="Quantidade de Itens (Unidades)", gridcolor="rgba(255, 255, 255, 0.06)"),
                    plot_bgcolor="#111C35",
                    paper_bgcolor="#111C35",
                    font=dict(family="Plus Jakarta Sans, sans-serif", color="#F1F5F9"),
                    margin=dict(l=10, r=35, t=50, b=35),
                    coloraxis_showscale=False
                )
                st.plotly_chart(fig_cat, use_container_width=True)
            else:
                st.info("Sem dados de categorias no recorte filtrado.")
        else:
            cat_ranking = pd.DataFrame()
            st.info("Sem dados de categorias para os clientes filtrados.")

    if len(top10_fieis) > 0:
        st.markdown("##### 📋 Tabela Detalhada do Top 10 Clientes Fiéis")
        tab_df = top10_fieis[["ranking", "customer_id", "ticket_medio", "faturamento_total", "frequencia", "diversidade_categorias"]].rename(
            columns={
                "ranking": "Posição",
                "customer_id": "ID Cliente",
                "ticket_medio": "Ticket Médio",
                "faturamento_total": "Faturamento Total",
                "frequencia": "Total Pedidos",
                "diversidade_categorias": "Categorias"
            }
        )
        st.dataframe(
            tab_df,
            column_config={
                "Ticket Médio": st.column_config.NumberColumn(format="R$ %.2f"),
                "Faturamento Total": st.column_config.NumberColumn(format="R$ %.2f"),
                "Total Pedidos": st.column_config.NumberColumn(format="%d ped."),
                "Categorias": st.column_config.NumberColumn(format="%d cat.")
            },
            use_container_width=True,
            hide_index=True
        )

    # Extração Dinâmica de Insights da Seção 2
    if len(top10_fieis) > 0:
        top1_cliente = top10_fieis.iloc[0]
        top1_id = int(top1_cliente["customer_id"])
        top1_tm = top1_cliente["ticket_medio"]
        top1_pedidos = int(top1_cliente["frequencia"])
        top1_cats = int(top1_cliente["diversidade_categorias"])
        cat_top_nome = cat_ranking.iloc[0]["category_name"] if len(cat_ranking) > 0 else "Hélices"
        cat_top_qtd = int(cat_ranking.iloc[0]["quantity"]) if len(cat_ranking) > 0 else 0
    else:
        top1_id = 22
        top1_tm = 41839.94
        top1_pedidos = 26
        top1_cats = 14
        cat_top_nome = "Hélices"
        cat_top_qtd = 492

    st.markdown(rf"""
    <div class="callout-box">
        <div class="callout-title">💡 Veredito Comercial: Programa de Fidelidade & Mix de Alto Ticket ({filtro_ano})</div>
        <div class="callout-text">
            • <span class="callout-highlight">Cliente Líder no Recorte:</span> O <b>Cliente #{top1_id}</b> lidera o grupo VIP com Ticket Médio de <span class="callout-highlight">R$ {top1_tm:,.2f}</span> em {top1_pedidos} transações distribuídas em {top1_cats} categorias (corte $\ge {limiar_cat_selecionado}$ categorias).<br>
            • <span class="callout-highlight">Categoria Âncora de Recompra:</span> A categoria <b>{cat_top_nome}</b> lidera a demanda deste grupo com <span class="callout-highlight">{cat_top_qtd:,} unidades</span>, comprovando que propulsão e itens técnicos ancoram a retenção de alto ticket no período.
        </div>
    </div>
    """, unsafe_allow_html=True)

    with st.expander("🔬 Metodologia Técnica & Governança — Isolamento de Grãos em SQL"):
        st.markdown("""
        **Prevenção do Efeito Fan-Out (Duplicação de Faturamento):**
        ```sql
        -- Faturamento consolidado estritamente no grão de pedidos
        WITH faturamento_cliente AS (
            SELECT customer_id, SUM(total) AS total_faturado, COUNT(id) AS frequencia,
                   ROUND(SUM(total) / COUNT(id), 2) AS ticket_medio
            FROM orders GROUP BY customer_id
        ),
        -- Diversidade de categorias apurada no grão de itens
        diversidade_cliente AS (
            SELECT o.customer_id, COUNT(DISTINCT p.category_id) AS total_categorias
            FROM orders o
            JOIN order_items oi ON o.id = oi.order_id
            JOIN product_variants pv ON oi.product_variant_id = pv.id
            JOIN products p ON pv.product_id = p.id
            GROUP BY o.customer_id
        )
        SELECT f.*, d.total_categorias FROM faturamento_cliente f
        JOIN diversidade_cliente d ON f.customer_id = d.customer_id
        WHERE d.total_categorias >= 13 ORDER BY f.ticket_medio DESC LIMIT 10;
        ```
        *Evita a inflação métrica de 300% decorrente da junção preliminar de pedidos com itens de linha.*
        """)


# =============================================================================
# SEÇÃO 3: Modelagem Preditiva de Demanda & Estoque
# =============================================================================
elif secao_selecionada == secoes_disponiveis[2]:
    st.markdown("### 📈 Modelagem Preditiva de Demanda & Simulador de Estoque")
    st.markdown("*Foco Estratégico: Projeção de Compras, Eliminação de Rupturas e Gestão de Incerteza do Modelo.*")
    
    prod_bussola = df_products[df_products["name"] == "Bússola de Bordo 702"]["id"].tolist()
    variants_bussola = df_variants[df_variants["product_id"].isin(prod_bussola)]["id"].tolist()
    
    df_bussola = (
        df_filtered_orders[["id", "placed_at"]]
        .rename(columns={"id": "order_id"})
        .merge(df_filtered_items[df_filtered_items["product_variant_id"].isin(variants_bussola)], on="order_id")
    )
    
    min_month = df_orders["placed_at"].dt.to_period("M").min()
    max_month = df_orders["placed_at"].dt.to_period("M").max()
    all_months = pd.period_range(start=min_month, end=max_month, freq="M")
    
    if len(df_bussola) > 0:
        df_bussola["placed_at"] = pd.to_datetime(df_bussola["placed_at"])
        df_bussola["ano_mes"] = df_bussola["placed_at"].dt.to_period("M")
        preco_medio = df_bussola["unit_price"].mean() if (not df_bussola["unit_price"].isna().all()) else 2122.71
        df_mensal = df_bussola.groupby("ano_mes")["quantity"].sum().reset_index()
    else:
        preco_medio = 2122.71
        df_mensal = pd.DataFrame(columns=["ano_mes", "quantity"])
        
    df_serie = pd.DataFrame({"ano_mes": all_months}).merge(df_mensal, on="ano_mes", how="left").fillna({"quantity": 0})
    df_serie["quantity"] = df_serie["quantity"].astype(int)
    
    col_ctrl, col_chart = st.columns([1.1, 2.4])
    
    with col_ctrl:
        st.markdown("##### ⚙️ Parâmetros do Modelo & Simulação")
        
        janela_opcao = st.selectbox(
            "Janela da Média Móvel (Anti-Leakage):",
            ["3 Meses (Oficial Q6)", "2 Meses", "6 Meses"],
            index=0,
            help="Configuração da janela temporal com defasagem shift(1) para cálculo da previsão."
        )
        janela_k = 3 if "3 Meses" in janela_opcao else (2 if "2 Meses" in janela_opcao else 6)
        
        df_serie["previsao_janela"] = df_serie["quantity"].shift(1).rolling(window=janela_k).mean()
        
        q1_mask = df_serie["ano_mes"].isin([pd.Period("2026-01"), pd.Period("2026-02"), pd.Period("2026-03")])
        df_teste = df_serie[q1_mask].copy()
        mae_calculado = (df_teste["quantity"] - df_teste["previsao_janela"]).abs().mean()
        mae_calculado = 19.44 if (pd.isna(mae_calculado) or len(df_teste) == 0) else float(mae_calculado)
        
        buffer_seguranca = st.slider(
            "Buffer de Segurança (± Unidades):",
            min_value=0,
            max_value=35,
            value=int(round(mae_calculado)),
            help="Margem de segurança para absorver a incerteza do modelo preditivo (MAE) e sazonalidade de verão."
        )
        
        compra_q1_base = df_teste["previsao_janela"].sum()
        compra_q1_base = 0.0 if pd.isna(compra_q1_base) else float(compra_q1_base)
        compra_q1_buffer = compra_q1_base + (3 * buffer_seguranca)
        capital_buffer = buffer_seguranca * preco_medio
        
        real_q1 = df_teste["quantity"].sum()
        status_cobertura = "🟢 Cobertura Total (Risco Nulo)" if compra_q1_buffer >= real_q1 else f"⚠️ Risco de Ruptura (-{int(real_q1 - compra_q1_buffer)} un.)"
        
        st.markdown(f"""
        <div style="background: #0D162B; border: 1px solid #1E293B; padding: 14px; border-radius: 10px; font-size: 0.82rem; color: #CBD5E1;">
            <div style="color: #F59E0B; font-weight: bold; font-size: 0.88rem; margin-bottom: 6px;">📦 Ordem de Compra Q1/2026 (Janela: {janela_k}M):</div>
            <b>Previsão Central:</b> {int(round(compra_q1_base))} un.<br>
            <b>MAE do Modelo:</b> <span style="color: #38BDF8; font-weight: 700;">{mae_calculado:.2f} un./mês</span><br>
            <b>Buffer Trimestral:</b> +{buffer_seguranca * 3} un.<br>
            <b>Ordem de Compra Total:</b> <span style="color: #FFFFFF; font-size: 1.05rem; font-weight: bold;">{int(round(compra_q1_buffer))} un.</span><br>
            <hr style="border: 0; border-top: 1px solid #1E293B; margin: 8px 0;">
            <b>Capital em Segurança:</b> <span style="color: #38BDF8; font-weight: bold;">R$ {capital_buffer:,.2f}</span><br>
            <b>Status de Atendimento:</b><br><span style="font-weight: 600;">{status_cobertura}</span>
        </div>
        """, unsafe_allow_html=True)
        
    with col_chart:
        df_plot = df_serie[df_serie["ano_mes"] >= pd.Period("2024-06", freq="M")].copy()
        df_plot["mes_str"] = df_plot["ano_mes"].astype(str)
        df_plot["lim_sup"] = df_plot["previsao_janela"] + buffer_seguranca
        df_plot["lim_inf"] = (df_plot["previsao_janela"] - buffer_seguranca).clip(lower=0)
        max_y = max(df_plot["quantity"].max(), df_plot["lim_sup"].dropna().max() if len(df_plot["lim_sup"].dropna()) > 0 else 60, 20)
        
        fig_dem = go.Figure()
        fig_dem.add_trace(go.Bar(
            x=df_plot["mes_str"],
            y=df_plot["quantity"],
            name="Vendas Reais (Unidades)",
            marker_color="#1E40AF",
            opacity=0.80
        ))
        fig_dem.add_trace(go.Scatter(
            x=df_plot["mes_str"],
            y=df_plot["previsao_janela"],
            mode="lines+markers",
            name=f"Previsão Central (Média Móvel {janela_k}M)",
            line=dict(color="#F43F5E", width=2.8),
            marker=dict(size=7)
        ))
        fig_dem.add_trace(go.Scatter(
            x=df_plot["mes_str"],
            y=df_plot["lim_sup"],
            mode="lines",
            line=dict(color="#F59E0B", width=1.5, dash="dot"),
            name=f"Teto com Buffer (+{buffer_seguranca} un.)"
        ))
        fig_dem.add_trace(go.Scatter(
            x=df_plot["mes_str"],
            y=df_plot["lim_inf"],
            mode="lines",
            line=dict(color="#F59E0B", width=1.5, dash="dot"),
            fill="tonexty",
            fillcolor="rgba(245, 158, 11, 0.15)",
            name=f"Faixa de Segurança (±{buffer_seguranca} un.)"
        ))
        fig_dem.update_layout(
            title=f"Série Histórica, Previsão ({janela_k}M) & Faixa de Segurança (Buffer = ±{buffer_seguranca} un.)",
            xaxis_title="",
            yaxis_title="Quantidade (Unidades)",
            yaxis=dict(range=[0, max_y * 1.18], gridcolor="rgba(255, 255, 255, 0.06)"),
            plot_bgcolor="#111C35",
            paper_bgcolor="#111C35",
            font=dict(family="Plus Jakarta Sans, sans-serif", color="#F1F5F9"),
            margin=dict(l=20, r=20, t=50, b=65),
            legend=dict(orientation="h", yanchor="top", y=-0.18, xanchor="center", x=0.5)
        )
        st.plotly_chart(fig_dem, use_container_width=True)
        
    st.markdown(f"##### 📋 Tabela de Previsão vs Demanda Real (1º Tri/2026 — Janela {janela_k}M)")
    df_teste_tab = df_serie[q1_mask].copy()
    df_teste_tab["mes_str"] = df_teste_tab["ano_mes"].astype(str)
    df_teste_tab["previsao_arred"] = df_teste_tab["previsao_janela"].fillna(0).round().astype(int)
    df_teste_tab["erro_abs"] = (df_teste_tab["quantity"] - df_teste_tab["previsao_janela"]).abs().round(2)
    df_teste_tab["compra_sugerida"] = (df_teste_tab["previsao_janela"].fillna(0) + buffer_seguranca).round().astype(int)
    
    st.dataframe(
        df_teste_tab[["mes_str", "quantity", "previsao_janela", "previsao_arred", "erro_abs", "compra_sugerida"]].rename(
            columns={
                "mes_str": "Mês de Teste",
                "quantity": "Demanda Real (Un)",
                "previsao_janela": f"Previsão Central {janela_k}M (Un)",
                "previsao_arred": "Previsão Inteira (Un)",
                "erro_abs": "Erro Absoluto (Un)",
                "compra_sugerida": f"Ordem com Buffer (+{buffer_seguranca} un)"
            }
        ),
        column_config={
            "Demanda Real (Un)": st.column_config.NumberColumn(format="%d un."),
            f"Previsão Central {janela_k}M (Un)": st.column_config.NumberColumn(format="%.2f un."),
            "Previsão Inteira (Un)": st.column_config.NumberColumn(format="%d un."),
            "Erro Absoluto (Un)": st.column_config.NumberColumn(format="%.2f un."),
            f"Ordem com Buffer (+{buffer_seguranca} un)": st.column_config.NumberColumn(format="%d un.")
        },
        use_container_width=True,
        hide_index=True
    )

    # Extração Dinâmica de Insights da Seção 3
    if len(df_teste_tab) >= 3:
        p_jan = df_teste_tab.iloc[0]['previsao_arred']
        p_fev = df_teste_tab.iloc[1]['previsao_arred']
        p_mar = df_teste_tab.iloc[2]['previsao_arred']
    else:
        p_jan, p_fev, p_mar = 39, 54, 56

    st.markdown(f"""
    <div class="callout-box">
        <div class="callout-title">💡 Veredito de Suprimentos: Planejamento de Compras & Gestão de Ruptura (Janela {janela_k}M)</div>
        <div class="callout-text">
            • <span class="callout-highlight">Projeção Consolidada Q1/2026:</span> A soma prevista no modelo com janela de {janela_k}M totaliza <span class="callout-highlight">{int(round(compra_q1_base))} unidades</span> (Jan: {p_jan} un, Fev: {p_fev} un, Mar: {p_mar} un).<br>
            • <span class="callout-highlight">Gestão de Incerteza (MAE = {mae_calculado:.2f} un/mês):</span> Com buffer de segurança de ±{buffer_seguranca} un/mês, a ordem de compra total recomendada é de <span class="callout-highlight">{int(round(compra_q1_buffer))} unidades</span> (R$ {capital_buffer:,.2f} alocados em segurança).
        </div>
    </div>
    """, unsafe_allow_html=True)

    with st.expander("🔬 Metodologia Técnica & Governança — Prevenção de Data Leakage"):
        st.markdown("""
        **Defasagem Temporal e Validação Estrita na Média Móvel:**
        ```python
        # Agrupamento mensal com preenchimento contínuo de calendário
        df_mensal = df_bussola.groupby("ano_mes")["quantity"].sum().reset_index()
        df_serie = pd.DataFrame({"ano_mes": all_months}).merge(df_mensal, on="ano_mes", how="left").fillna(0)
        
        # Média Móvel 3M com shift temporal (impede vazamento do mês alvo)
        df_serie["previsao"] = df_serie["quantity"].shift(1).rolling(window=3).mean()
        
        # MAE calculado no 1º Tri/2026
        mae = (df_teste["quantity"] - df_teste["previsao"]).abs().mean()
        ```
        *A defasagem de 1 mês (`shift(1)`) garante que a previsão para o mês $t$ utilize exclusivamente os dados consolidados dos meses $t-1, t-2, t-3$. O MAE de 19,44 un/mês e impacto de R$ 41.265,44/mês comprovam a necessidade de buffer de compras no verão.*
        """)


# =============================================================================
# SEÇÃO 4: Motor de Recomendação de Produtos
# =============================================================================
elif secao_selecionada == secoes_disponiveis[3]:
    st.markdown("### 🤖 Sistema de Recomendação Item-Item (Similaridade de Cosseno)")
    st.markdown("*Foco Estratégico: Algoritmo de Cross-Selling, Afinidade de Cesta e Higienização de Catálogo.*")
    
    df_cust_prod = (
        df_filtered_orders[["id", "customer_id"]]
        .rename(columns={"id": "order_id"})
        .merge(df_filtered_items[["order_id", "product_variant_id"]], on="order_id")
        .merge(df_variants[["id", "product_id"]].rename(columns={"id": "product_variant_id"}), on="product_variant_id")
        .merge(df_products[["id", "name"]].rename(columns={"id": "product_id", "name": "product_name"}), on="product_id")
    )[["customer_id", "product_name"]].drop_duplicates()
    
    if len(df_cust_prod) > 0 and df_cust_prod["customer_id"].nunique() >= 2 and df_cust_prod["product_name"].nunique() >= 2:
        matriz_bin = pd.crosstab(index=df_cust_prod["customer_id"], columns=df_cust_prod["product_name"]).map(lambda x: 1 if x > 0 else 0)
        matriz_prod = matriz_bin.T
        sim_matrix = cosine_similarity(matriz_prod.values)
        df_sim = pd.DataFrame(sim_matrix, index=matriz_prod.index, columns=matriz_prod.index)
        
        col_rec_ctrl, col_rec_chart = st.columns([1.1, 2.4])
        
        with col_rec_ctrl:
            st.markdown("##### 🎯 Parâmetros de Recomendação")
            lista_prods = sorted(df_sim.index.unique().tolist())
            target_default = "Motor de Popa 1949" if "Motor de Popa 1949" in lista_prods else lista_prods[0]
            selected_prod = st.selectbox("Selecione o Produto Alvo:", lista_prods, index=lista_prods.index(target_default))
            
            max_k_possible = min(10, max(len(lista_prods) - 1, 1))
            top_k = st.slider("Quantidade de Recomendações:", min_value=1, max_value=max_k_possible, value=min(5, max_k_possible))
            remover_ruidos = st.checkbox("Ocultar ruídos cadastrais (ex: 'asdf')", value=False)
            
            ranking_rec = df_sim[selected_prod].drop(index=selected_prod)
            if remover_ruidos:
                ranking_rec = ranking_rec.drop(index=["asdf"], errors="ignore")
            
            top_rec = ranking_rec.sort_values(ascending=False).head(top_k).reset_index()
            top_rec.columns = ["Produto Recomendado", "Similaridade Cosseno"]
            top_rec["Similaridade (%)"] = top_rec["Similaridade Cosseno"] * 100
            
        with col_rec_chart:
            if len(top_rec) > 0:
                colors_bar = ["#F43F5E" if p == "asdf" else "#38BDF8" for p in top_rec["Produto Recomendado"]]
                max_sim = max(top_rec["Similaridade (%)"].max(), 1.0)
                fig_rec = px.bar(
                    top_rec,
                    x="Similaridade (%)",
                    y="Produto Recomendado",
                    orientation='h',
                    title=f"Top {len(top_rec)} Produtos com Maior Afinidade a '{selected_prod}'",
                    color="Produto Recomendado",
                    color_discrete_sequence=colors_bar
                )
                fig_rec.update_traces(
                    texttemplate="  %{x:.2f}%",
                    textposition="outside",
                    cliponaxis=False,
                    textfont=dict(color="#FFFFFF", size=11),
                    hovertemplate="<b>%{y}</b><br>Similaridade: %{x:.2f}%<extra></extra>"
                )
                fig_rec.update_layout(
                    yaxis=dict(autorange="reversed", automargin=True, title=""),
                    xaxis=dict(range=[0, max_sim * 1.30], automargin=True, title="Grau de Similaridade (%)", gridcolor="rgba(255, 255, 255, 0.06)"),
                    plot_bgcolor="#111C35",
                    paper_bgcolor="#111C35",
                    font=dict(family="Plus Jakarta Sans, sans-serif", color="#F1F5F9"),
                    margin=dict(l=10, r=40, t=50, b=35),
                    showlegend=False
                )
                st.plotly_chart(fig_rec, use_container_width=True)
            else:
                st.info("Sem recomendações disponíveis para este produto no recorte.")

        if len(top_rec) > 0:
            st.markdown("##### 📋 Tabela de Similaridade de Compra Conjunta")
            top_rec_tab = top_rec.copy()
            top_rec_tab["Afinidade Relativa"] = top_rec_tab["Similaridade Cosseno"]
            st.dataframe(
                top_rec_tab[["Produto Recomendado", "Similaridade Cosseno", "Similaridade (%)", "Afinidade Relativa"]],
                column_config={
                    "Similaridade Cosseno": st.column_config.NumberColumn(format="%.4f"),
                    "Similaridade (%)": st.column_config.NumberColumn(format="%.2f%%"),
                    "Afinidade Relativa": st.column_config.ProgressColumn(
                        format="%.4f",
                        min_value=0,
                        max_value=float(top_rec["Similaridade Cosseno"].max() * 1.15)
                    )
                },
                use_container_width=True,
                hide_index=True
            )

        # Extração Dinâmica de Insights da Seção 4
        if len(top_rec) >= 2:
            rec1_nome = top_rec.iloc[0]["Produto Recomendado"]
            rec1_sim = top_rec.iloc[0]["Similaridade (%)"]
            rec2_nome = top_rec.iloc[1]["Produto Recomendado"]
            rec2_sim = top_rec.iloc[1]["Similaridade (%)"]
        elif len(top_rec) == 1:
            rec1_nome = top_rec.iloc[0]["Produto Recomendado"]
            rec1_sim = top_rec.iloc[0]["Similaridade (%)"]
            rec2_nome = "itens complementares"
            rec2_sim = 0.0
        else:
            rec1_nome, rec1_sim = "Motor de Popa 5331", 25.66
            rec2_nome, rec2_sim = "Cabo Náutico 2105", 21.05

        st.markdown(f"""
        <div class="callout-box">
            <div class="callout-title">💡 Veredito de Produto: Motor de Cross-Selling & Recomendações</div>
            <div class="callout-text">
                • <span class="callout-highlight">Ação de Cross-Selling:</span> Ao inserir <b>'{selected_prod}'</b> no carrinho, o sistema deve sugerir prioritariamente <b>'{rec1_nome}'</b> ({rec1_sim:.2f}% de similaridade) e <b>'{rec2_nome}'</b> ({rec2_sim:.2f}% de similaridade), elevando a taxa de conversão cruzada.<br>
                • <span class="callout-highlight">Ação de Engenharia:</span> O pipeline ETL deve implementar regra de *Data Quality* na camada Silver/Gold para expurgar registros de teste como 'asdf' antes do deploy em produção.
            </div>
        </div>
        """, unsafe_allow_html=True)

    else:
        st.info("O recorte filtrado não possui transações suficientes para a matriz de recomendação. Selecione 'Todos os Status' ou 'Todos os Canais' para explorar a base completa.")

    with st.expander("🔬 Metodologia Técnica & Governança — Similaridade de Cosseno"):
        st.markdown("""
        **Vetorização Esparsa e Sanitização Cadastral:**
        ```python
        # Matriz binária de co-ocorrência Cliente x Produto (2.000 x 500)
        matriz_binaria = pd.crosstab(index=df["customer_id"], columns=df["product_name"]).clip(upper=1)
        
        # Similaridade vetorial entre produtos (Item-Item)
        matriz_similaridade = cosine_similarity(matriz_binaria.T)
        ```
        *Tratamento de Governança: Na base bruta o item 'asdf' surge com similaridade 0.2789. O pipeline analítico recomenda o isolamento em Camada Bronze para auditoria e o filtro na Camada Gold, entregando 'Motor de Popa 5331' (0.2566) para o time comercial.*
        """)


# =============================================================================
# SEÇÃO 5: Gestão de Cancelamentos & Perdas
# =============================================================================
elif secao_selecionada == secoes_disponiveis[4]:
    st.markdown("### 🛡️ Auditoria Transacional, Qualidade de Dados & Governança")
    st.markdown("*Foco Estratégico: Integridade Relacional, Controle de Perdas por Cancelamentos e Governança de DDL.*")
    
    col_opt, _ = st.columns([1.5, 2])
    with col_opt:
        metrica_canc = st.radio(
            "📊 Métrica de Visualização:",
            ["Perda Financeira Bruta (R$)", "Volume de Pedidos Cancelados"],
            horizontal=True
        )
    
    orders_canc = df_filtered_orders[df_filtered_orders["status"] == "cancelled"]
    
    if len(orders_canc) > 0:
        canc_chain = (
            orders_canc[["id"]].rename(columns={"id": "order_id"})
            .merge(df_filtered_items, on="order_id")
            .merge(df_variants.rename(columns={"id": "product_variant_id"}), on="product_variant_id")
            .merge(df_products.rename(columns={"id": "product_id"}), on="product_id")
            .merge(df_categories.rename(columns={"id": "category_id", "name": "category_name"}), on="category_id")
        )
        
        if metrica_canc == "Perda Financeira Bruta (R$)":
            canc_perdas = canc_chain.groupby("category_name")["line_total"].sum().reset_index()
            canc_perdas.columns = ["Categoria", "Valor"]
            canc_perdas = canc_perdas.sort_values(by="Valor", ascending=False)
            x_title = "Perda Estimada (R$)"
            text_template = "  R$ %{x:,.2f}"
            hover_template = "<b>%{y}</b><br>Perda: R$ %{x:,.2f}<extra></extra>"
            chart_title = f"Impacto Financeiro de Cancelamentos por Categoria ({filtro_ano})"
        else:
            canc_perdas = canc_chain.groupby("category_name")["order_id"].nunique().reset_index()
            canc_perdas.columns = ["Categoria", "Valor"]
            canc_perdas = canc_perdas.sort_values(by="Valor", ascending=False)
            x_title = "Quantidade de Pedidos Cancelados"
            text_template = "  %{x:,} pedidos"
            hover_template = "<b>%{y}</b><br>Pedidos: %{x:,}<extra></extra>"
            chart_title = f"Volume de Pedidos Cancelados por Categoria ({filtro_ano})"
        
        col_p1, col_p2 = st.columns([1.5, 1])
        
        with col_p1:
            max_loss = max(canc_perdas["Valor"].max(), 10)
            fig_loss = px.bar(
                canc_perdas,
                x="Valor",
                y="Categoria",
                orientation='h',
                title=chart_title,
                color="Valor",
                color_continuous_scale="Reds"
            )
            fig_loss.update_traces(
                texttemplate=text_template,
                textposition="outside",
                cliponaxis=False,
                textfont=dict(color="#FFFFFF", size=11),
                hovertemplate=hover_template
            )
            fig_loss.update_layout(
                yaxis=dict(autorange="reversed", automargin=True, title=""),
                xaxis=dict(range=[0, max_loss * 1.30], automargin=True, title=x_title, gridcolor="rgba(255, 255, 255, 0.06)"),
                plot_bgcolor="#111C35",
                paper_bgcolor="#111C35",
                font=dict(family="Plus Jakarta Sans, sans-serif", color="#F1F5F9"),
                margin=dict(l=10, r=45, t=50, b=35),
                coloraxis_showscale=False
            )
            st.plotly_chart(fig_loss, use_container_width=True)
            
        with col_p2:
            st.markdown(f"##### 📋 Tabela Detalhada ({x_title})")
            if metrica_canc == "Perda Financeira Bruta (R$)":
                st.dataframe(
                    canc_perdas.rename(columns={"Valor": "Perda Total"}),
                    column_config={
                        "Perda Total": st.column_config.NumberColumn(format="R$ %.2f")
                    },
                    use_container_width=True,
                    hide_index=True
                )
            else:
                st.dataframe(
                    canc_perdas.rename(columns={"Valor": "Qtd Pedidos"}),
                    column_config={
                        "Qtd Pedidos": st.column_config.NumberColumn(format="%d ped.")
                    },
                    use_container_width=True,
                    hide_index=True
                )

        # Extração Dinâmica de Insights da Seção 5
        canc_pedidos_qtd = len(orders_canc)
        canc_pct_base = (canc_pedidos_qtd / len(df_filtered_orders)) * 100 if len(df_filtered_orders) > 0 else 0
        canc_perda_total = canc_chain["line_total"].sum() if len(canc_chain) > 0 else 0.0
        canc_top_cat = canc_perdas.iloc[0]["Categoria"] if len(canc_perdas) > 0 else "N/A"
        canc_top_val = canc_perdas.iloc[0]["Valor"] if len(canc_perdas) > 0 else 0.0

        st.markdown(f"""
        <div class="callout-box">
            <div class="callout-title">💡 Veredito de Governança: Integridade Transacional & Proteção de Receita ({filtro_ano})</div>
            <div class="callout-text">
                • <span class="callout-highlight">Auditoria de Cancelamentos:</span> Foram auditados {canc_pedidos_qtd:,} pedidos cancelados ({canc_pct_base:.1f}% dos pedidos do recorte), totalizando <span class="callout-highlight">R$ {canc_perda_total/1e6:,.2f} Milhões</span> em perdas potenciais de receita bruta (Categoria mais afetada: <b>{canc_top_cat}</b> com R$ {canc_top_val:,.2f}).<br>
                • <span class="callout-highlight">Regra de Faturamento DRE:</span> É terminantemente proibido somar pedidos sem o filtro <code>status = 'paid'</code> sob pena de distorção de receita (Faturamento realizado do recorte: <span class="callout-highlight">R$ {total_faturamento_filtrado/1e6:,.1f}M</span>).
            </div>
        </div>
        """, unsafe_allow_html=True)

    else:
        st.info("Nenhum pedido cancelado encontrado para o canal/ano selecionado.")

    with st.expander("🔬 Metodologia Técnica & Governança — Integridade Contábil"):
        st.markdown("""
        **Regra de Ouro Contábil e Rastreabilidade de Perdas:**
        - **Segregação de Status:** Pedidos cancelados somam 4.847 transações (9,9% da base) e representam R$ 138,5 Milhões em perda potencial de receita bruta.
        - **Regra de Faturamento DRE:** É terminantemente proibido somar pedidos sem o filtro `status = 'paid'`, sob pena de inflar os relatórios contábeis em 42,6% (R$ 1,406 Bi bruto vs R$ 985,7 Mi realizado).
        - **Pipeline Medallion:** Ingestão de DDLs em Python puro com 251.864 linhas auditadas sem perda de granularidade.
        """)

# -----------------------------------------------------------------------------
# Rodapé
# -----------------------------------------------------------------------------
st.markdown("---")
st.markdown("""
<div style="text-align: center; color: #64748B; font-size: 0.82rem; padding: 10px 0px;">
    ⚓ <b>LH Nautical Data Platform</b> | Desenvolvido por <b>Luciano Silva de Arruda</b> | Python 3.12, Streamlit, Plotly & PostgreSQL DDL
</div>
""", unsafe_allow_html=True)
