#!/usr/bin/env python3
"""
===============================================================================
DESAFIO LH NAUTICAL — GERADOR DE DIAGRAMAS ARQUITETURAIS & SQL (300 DPI)
Autor: Luciano Silva de Arruda
Programa: Lighthouse 2026 (Indicium AI)
===============================================================================
Gera representações visuais elegantes e de nível enterprise para:
  1. Diagrama de Entidade-Relacionamento (DER / Data Warehouse Relacional)
  2. Diagrama de Linhagem e Arquitetura de Pipeline SQL / Data Flow
===============================================================================
"""

import matplotlib.pyplot as plt
import matplotlib.patches as patches
from pathlib import Path

# Configurações globais de layout
PROJECT_ROOT = Path(__file__).resolve().parent.parent
OUTPUT_DIR = PROJECT_ROOT / "data" / "processed"
REPORT_IMG_DIR = PROJECT_ROOT.parent / "lh_nautical_relatorio" / "images"
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
REPORT_IMG_DIR.mkdir(parents=True, exist_ok=True)

# Paleta Náutica Corporativa
C_PRIMARY = "#0B2545"      # Azul Marinho Profundo (Fatos Principais)
C_SECONDARY = "#134074"    # Azul Oceânico
C_ACCENT = "#0077B6"       # Azul Ciano Náutico (Dimensões Principais)
C_TEAL = "#0096C7"         # Teal Náutico
C_GOLD = "#C57B57"         # Bronze / Destaque
C_BG_CARD = "#F8FAFC"      # Fundo do Card
C_BORDER = "#CBD5E1"       # Borda Suave
C_TEXT_DARK = "#0F172A"    # Texto Escuro
C_TEXT_MUTED = "#64748B"   # Texto Secundário
C_WHITE = "#FFFFFF"

plt.rcParams["font.family"] = "sans-serif"
plt.rcParams["font.sans-serif"] = ["DejaVu Sans", "Helvetica", "Arial"]


def draw_table_card(ax, x, y, width, height, title, columns, header_color, is_fact=False):
    """Desenha um card de tabela relacional moderno com cabeçalho colorido e colunas."""
    # Sombra suave
    shadow = patches.FancyBboxPatch(
        (x + 0.008, y - 0.008), width, height,
        boxstyle="round,pad=0.01,rounding_size=0.03",
        facecolor="#E2E8F0", edgecolor="none", zorder=1
    )
    ax.add_patch(shadow)

    # Card principal
    card = patches.FancyBboxPatch(
        (x, y), width, height,
        boxstyle="round,pad=0.01,rounding_size=0.03",
        facecolor=C_BG_CARD, edgecolor=C_BORDER, linewidth=1.2, zorder=2
    )
    ax.add_patch(card)

    # Cabeçalho da Tabela
    h_height = height * 0.24
    header = patches.FancyBboxPatch(
        (x, y + height - h_height), width, h_height,
        boxstyle="round,pad=0.01,rounding_size=0.03",
        facecolor=header_color, edgecolor="none", zorder=3
    )
    ax.add_patch(header)
    
    # Retângulo para cobrir cantos inferiores arredondados do cabeçalho
    rect_fill = patches.Rectangle(
        (x, y + height - h_height), width, h_height * 0.4,
        facecolor=header_color, edgecolor="none", zorder=3
    )
    ax.add_patch(rect_fill)

    # Título da Tabela
    badge = " [FATO]" if is_fact else " [DIMENSÃO]"
    ax.text(
        x + width / 2, y + height - h_height / 2,
        f"{title.upper()}{badge}",
        color=C_WHITE, fontsize=10, fontweight="bold",
        ha="center", va="center", zorder=4
    )

    # Linhas de Colunas
    n_cols = len(columns)
    spacing = (height - h_height) / (n_cols + 1)
    for i, col in enumerate(columns):
        col_y = y + height - h_height - (i + 1) * spacing + spacing * 0.15
        
        # Identifica PK / FK
        if col.startswith("PK:"):
            txt_color = "#B91C1C"
            prefix = "[PK] "
            col_text = col.replace("PK:", "").strip()
            fw = "bold"
        elif col.startswith("FK:"):
            txt_color = "#1D4ED8"
            prefix = "[FK] "
            col_text = col.replace("FK:", "").strip()
            fw = "semibold" if "semibold" in plt.rcParams.get("font.weight", "") else "bold"
        else:
            txt_color = C_TEXT_DARK
            prefix = "     "
            col_text = col
            fw = "normal"

        ax.text(
            x + 0.02, col_y, f"{prefix}{col_text}",
            color=txt_color, fontsize=8.5, fontweight=fw,
            ha="left", va="center", zorder=4
        )


def draw_relationship(ax, p1, p2, label="", color="#475569", connectionstyle="arc3,rad=0.0"):
    """Desenha uma linha conectora elegante entre tabelas relacionais."""
    arrow = patches.FancyArrowPatch(
        p1, p2,
        connectionstyle=connectionstyle,
        arrowstyle="-|>",
        color=color,
        linewidth=1.8,
        mutation_scale=14,
        linestyle="--",
        zorder=5
    )
    ax.add_patch(arrow)
    if label:
        mid_x = (p1[0] + p2[0]) / 2
        mid_y = (p1[1] + p2[1]) / 2
        ax.text(
            mid_x, mid_y, label,
            fontsize=8, fontweight="bold", color=C_PRIMARY,
            bbox=dict(boxstyle="round,pad=0.2", facecolor=C_WHITE, edgecolor=C_BORDER, alpha=0.9),
            ha="center", va="center", zorder=6
        )


def gerar_diagrama_erd():
    """Gera o Diagrama de Entidade-Relacionamento do Data Warehouse da LH Nautical."""
    fig, ax = plt.subplots(figsize=(18, 11), dpi=300)
    ax.set_xlim(0, 1)
    ax.set_ylim(0, 1)
    ax.axis("off")

    # Fundo moderno
    fig.patch.set_facecolor("#FFFFFF")

    # Título do Diagrama
    ax.text(
        0.5, 0.96, "DIAGRAMA DE ENTIDADE-RELACIONAMENTO (DER) — DATA WAREHOUSE",
        fontsize=18, fontweight="bold", color=C_PRIMARY, ha="center", va="center"
    )
    ax.text(
        0.5, 0.93, "Modelo Dimensional do ERP LH Nautical (24 Tabelas | 433.424 Registros | PostgreSQL / SQLite)",
        fontsize=11, color=C_TEXT_MUTED, ha="center", va="center"
    )

    # 1. TABELA FATO: ORDERS (Centro-Esquerda)
    draw_table_card(
        ax, x=0.34, y=0.48, width=0.26, height=0.36,
        title="orders",
        columns=[
            "PK: id (INTEGER)",
            "    order_number (VARCHAR)",
            "FK: customer_id (INTEGER)",
            "FK: salesperson_id (INTEGER)",
            "FK: location_id (INTEGER)",
            "    channel (pos / e-commerce)",
            "    status (paid, confirmed, ...)",
            "    total (NUMERIC - R$)",
            "    placed_at (TIMESTAMP)"
        ],
        header_color=C_PRIMARY, is_fact=True
    )

    # 2. TABELA FATO: ORDER_ITEMS (Centro-Direita)
    draw_table_card(
        ax, x=0.67, y=0.48, width=0.26, height=0.36,
        title="order_items",
        columns=[
            "PK: id (INTEGER)",
            "FK: order_id (INTEGER)",
            "FK: product_variant_id (INTEGER)",
            "    quantity (INTEGER)",
            "    unit_price (NUMERIC)",
            "    icms_rate (NUMERIC)",
            "    ipi_rate (NUMERIC)",
            "    line_total (NUMERIC)"
        ],
        header_color=C_PRIMARY, is_fact=True
    )

    # 3. TABELA FATO: PAYMENTS (Inferior Esquerda)
    draw_table_card(
        ax, x=0.34, y=0.10, width=0.26, height=0.30,
        title="payments",
        columns=[
            "PK: id (INTEGER)",
            "FK: order_id (INTEGER)",
            "    method (credit_card, pix, ...)",
            "    installments (INTEGER)",
            "    amount (NUMERIC - R$)",
            "    status (paid, refunded)",
            "    paid_at (TIMESTAMP)"
        ],
        header_color="#1E293B", is_fact=True
    )

    # 4. DIMENSÃO: CUSTOMERS (Extremo Esquerda Superior)
    draw_table_card(
        ax, x=0.04, y=0.55, width=0.23, height=0.32,
        title="customers",
        columns=[
            "PK: id (INTEGER)",
            "    first_name (VARCHAR)",
            "    last_name (VARCHAR)",
            "    customer_type (individual/company)",
            "    email (VARCHAR)",
            "    created_at (TIMESTAMP)"
        ],
        header_color=C_ACCENT
    )

    # 5. DIMENSÃO: EMPLOYEES / VENDEDORES (Extremo Esquerda Inferior)
    draw_table_card(
        ax, x=0.04, y=0.14, width=0.23, height=0.28,
        title="employees",
        columns=[
            "PK: id (INTEGER)",
            "    first_name (VARCHAR)",
            "    role (salesperson, manager)",
            "FK: location_id (INTEGER)",
            "    is_active (BOOLEAN)"
        ],
        header_color="#475569"
    )

    # 6. DIMENSÃO: PRODUCT_VARIANTS (Direita Meio)
    draw_table_card(
        ax, x=0.67, y=0.10, width=0.26, height=0.30,
        title="product_variants",
        columns=[
            "PK: id (INTEGER)",
            "FK: product_id (INTEGER)",
            "    sku (VARCHAR)",
            "    sale_price (NUMERIC)",
            "    cost_price (NUMERIC)",
            "    weight_kg (NUMERIC)"
        ],
        header_color=C_TEAL
    )

    # 7. DIMENSÃO: PRODUCTS (Extremo Direita Superior)
    draw_table_card(
        ax, x=0.74, y=0.70, width=0.22, height=0.22,
        title="products",
        columns=[
            "PK: id (INTEGER)",
            "    name (VARCHAR)",
            "FK: category_id (INTEGER)",
            "FK: brand_id (INTEGER)",
            "    unit_of_measure (VARCHAR)"
        ],
        header_color=C_SECONDARY
    )

    # 8. DIMENSÃO: CATEGORIES (Extremo Direita Topo)
    draw_table_card(
        ax, x=0.48, y=0.86, width=0.18, height=0.12,
        title="categories",
        columns=[
            "PK: id (INTEGER)",
            "    name (Hélices, Motores...)"
        ],
        header_color="#0D9488"
    )

    # Conexões e Relacionamentos
    draw_relationship(ax, (0.27, 0.70), (0.34, 0.70), label="1 : N", color=C_PRIMARY)
    draw_relationship(ax, (0.27, 0.26), (0.34, 0.54), label="1 : N", color="#64748B", connectionstyle="arc3,rad=-0.15")
    draw_relationship(ax, (0.60, 0.66), (0.67, 0.66), label="1 : N", color=C_PRIMARY)
    draw_relationship(ax, (0.47, 0.48), (0.47, 0.40), label="1 : N", color=C_PRIMARY)
    draw_relationship(ax, (0.80, 0.40), (0.80, 0.48), label="1 : N", color=C_TEAL)
    draw_relationship(ax, (0.85, 0.70), (0.85, 0.40), label="1 : N", color=C_SECONDARY)
    draw_relationship(ax, (0.74, 0.81), (0.66, 0.90), label="1 : N", color="#0D9488", connectionstyle="arc3,rad=0.15")

    # Legenda explicativa inferior
    legenda_text = (
        "Legenda: [PK] Chave Primária | [FK] Chave Estrangeira | "
        "Tabelas Fato (Azul Escuro) concentram 249.864 registros operacionais | "
        "Dimensões (Azul Ciano/Teal) alimentam filtros analíticos e IA"
    )
    ax.text(
        0.5, 0.03, legenda_text,
        fontsize=9, color=C_PRIMARY, fontweight="medium",
        ha="center", va="center",
        bbox=dict(boxstyle="round,pad=0.4", facecolor="#F1F5F9", edgecolor=C_BORDER)
    )

    plt.tight_layout()
    erd_file = OUTPUT_DIR / "8_diagrama_entidade_relacionamento.png"
    plt.savefig(erd_file, dpi=300, bbox_inches="tight")
    plt.savefig(REPORT_IMG_DIR / "8_diagrama_entidade_relacionamento.png", dpi=300, bbox_inches="tight")
    plt.close()
    print(f"✅ DER gerado: {erd_file}")


def gerar_diagrama_pipeline_sql():
    """Gera o Diagrama de Linhagem & Arquitetura do Pipeline SQL e IA."""
    fig, ax = plt.subplots(figsize=(18, 9), dpi=300)
    ax.set_xlim(0, 1)
    ax.set_ylim(0, 1)
    ax.axis("off")
    fig.patch.set_facecolor("#FFFFFF")

    # Título do Diagrama
    ax.text(
        0.5, 0.95, "ARQUITETURA DE LINHAGEM DE DADOS & PIPELINE ANALÍTICO SQL",
        fontsize=18, fontweight="bold", color=C_PRIMARY, ha="center", va="center"
    )
    ax.text(
        0.5, 0.91, "Do Dado Bruto aos Modelos de IA e Tomada de Decisão Executiva (LH Nautical)",
        fontsize=11, color=C_TEXT_MUTED, ha="center", va="center"
    )

    # 4 Colunas do Pipeline (Bronze -> Silver -> Gold/CTEs -> Inteligência/IA)
    col_w = 0.20
    spacing = 0.04
    start_x = 0.03
    
    stages = [
        {
            "num": "CAMADA 1", "title": "CAMADA BRONZE (RAW)",
            "color": "#475569",
            "items": [
                "24 Arquivos CSV (ERP)",
                "433.424 Registros Totais",
                "orders.csv (48.998 lins)",
                "order_items (147.320 lins)",
                "payments (53.546 lins)",
                "customers (2.000 lins)",
                "0_auditoria_csvs.py (EDA)"
            ]
        },
        {
            "num": "CAMADA 2", "title": "CAMADA SILVER (SCHEMA)",
            "color": C_ACCENT,
            "items": [
                "1_gerar_schema.py (Python Puro)",
                "Inferência Estrita DDL",
                "sql/schema.sql (PostgreSQL)",
                "2_carregar_dados.py (Ingestão)",
                "Data Warehouse Relacional",
                "Soma Q3.2 = 251.864 registros",
                "Integridade Transacional"
            ]
        },
        {
            "num": "CAMADA 3", "title": "CAMADA GOLD (CTEs SQL)",
            "color": C_PRIMARY,
            "items": [
                "Q4: Top 10 Clientes Fiéis",
                "• Segregação Faturamento/Itens",
                "• Filtro Diversidade >= 13",
                "• Categoria Hélices: 492 un",
                "Q5: Dimensão de Calendário",
                "• GENERATE_SERIES (2.557 dias)",
                "• Quinta: R$ 157.154/dia (Pior)"
            ]
        },
        {
            "num": "CAMADA 4", "title": "CAMADA IA & ENTREGÁVEIS",
            "color": "#059669",
            "items": [
                "Q6: Demanda Bússola 702",
                "• Média Móvel 3M sem leakage",
                "• Previsão: 149 un (1º Tri/26)",
                "Q7: Recomendação de Motores",
                "• Similaridade de Cosseno",
                "• Motor 5331 (Score 0.2566)",
                "Dashboard Streamlit & PDF"
            ]
        }
    ]

    for i, stage in enumerate(stages):
        x = start_x + i * (col_w + spacing)
        y = 0.12
        h = 0.72

        # Card de fundo
        card = patches.FancyBboxPatch(
            (x, y), col_w, h,
            boxstyle="round,pad=0.01,rounding_size=0.03",
            facecolor=C_BG_CARD, edgecolor=C_BORDER, linewidth=1.2, zorder=2
        )
        ax.add_patch(card)

        # Cabeçalho
        h_h = 0.13
        header = patches.FancyBboxPatch(
            (x, y + h - h_h), col_w, h_h,
            boxstyle="round,pad=0.01,rounding_size=0.03",
            facecolor=stage["color"], edgecolor="none", zorder=3
        )
        ax.add_patch(header)
        
        rect = patches.Rectangle(
            (x, y + h - h_h), col_w, h_h * 0.3,
            facecolor=stage["color"], edgecolor="none", zorder=3
        )
        ax.add_patch(rect)

        ax.text(
            x + col_w / 2, y + h - h_h * 0.35, stage["num"],
            color="#E2E8F0", fontsize=9, fontweight="bold", ha="center", va="center", zorder=4
        )
        ax.text(
            x + col_w / 2, y + h - h_h * 0.75, stage["title"],
            color=C_WHITE, fontsize=10.5, fontweight="bold", ha="center", va="center", zorder=4
        )

        # Itens da Etapa
        item_spacing = (h - h_h) / (len(stage["items"]) + 1)
        for j, item in enumerate(stage["items"]):
            item_y = y + h - h_h - (j + 1) * item_spacing + item_spacing * 0.15
            is_bullet = item.startswith("•")
            fw = "medium" if not is_bullet else "normal"
            fc = C_TEXT_DARK if not is_bullet else "#334155"
            fs = 9.5 if not is_bullet else 8.5
            
            ax.text(
                x + (0.025 if is_bullet else 0.015), item_y, item,
                color=fc, fontsize=fs, fontweight=fw,
                ha="left", va="center", zorder=4
            )

        # Setas conectores entre estágios
        if i < len(stages) - 1:
            arrow_x_start = x + col_w + 0.005
            arrow_x_end = arrow_x_start + spacing - 0.01
            arrow_y = y + h * 0.5
            arrow = patches.FancyArrowPatch(
                (arrow_x_start, arrow_y), (arrow_x_end, arrow_y),
                arrowstyle="-|>",
                color=C_GOLD,
                linewidth=2.5,
                mutation_scale=18,
                zorder=5
            )
            ax.add_patch(arrow)

    # Rodapé explicativo
    ax.text(
        0.5, 0.04,
        "Fluxo Automatizado de Engenharia: Ingestão Idempotente ➔ Modelagem Dimensional SQL ➔ Feature Engineering ➔ Previsão e Recomendação",
        fontsize=9.5, color=C_PRIMARY, fontweight="medium",
        ha="center", va="center",
        bbox=dict(boxstyle="round,pad=0.4", facecolor="#F1F5F9", edgecolor=C_BORDER)
    )

    plt.tight_layout()
    pipe_file = OUTPUT_DIR / "9_arquitetura_pipeline_sql.png"
    plt.savefig(pipe_file, dpi=300, bbox_inches="tight")
    plt.savefig(REPORT_IMG_DIR / "9_arquitetura_pipeline_sql.png", dpi=300, bbox_inches="tight")
    plt.close()
    print(f"✅ Pipeline gerado: {pipe_file}")


if __name__ == "__main__":
    from gerar_erd_graphviz import gerar_erd_graphviz
    gerar_erd_graphviz()
    gerar_diagrama_pipeline_sql()
