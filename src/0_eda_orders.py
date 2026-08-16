#!/usr/bin/env python3
"""
===============================================================================
LH NAUTICAL — ANÁLISE EXPLORATÓRIA E AUDITORIA DA TABELA ORDERS (EDA)
Autor: Luciano Silva de Arruda
Projeto: LH Nautical — Plataforma de Engenharia de Dados & Analytics
===============================================================================
Premissas:
  - Utilizar apenas a tabela `orders` em seu estado bruto.
  - Não realizar limpeza nem mutação de dados nesta etapa exploratória.
  - Extrair volumetria, intervalos temporais, métricas de valor e diagnóstico IQR.
===============================================================================
"""

import csv
import sys
from pathlib import Path

# Resolução de Caminhos
SRC_DIR = Path(__file__).resolve().parent
PROJECT_ROOT = SRC_DIR.parent
DATA_DIR = PROJECT_ROOT / "data" / "raw"
ORDERS_CSV = DATA_DIR / "orders.csv"


def executar_eda_orders():
    if not ORDERS_CSV.exists():
        print(f"❌ Erro: Arquivo {ORDERS_CSV} não encontrado.")
        sys.exit(1)

    rows = []
    with open(ORDERS_CSV, "r", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        headers = reader.fieldnames
        for r in reader:
            rows.append(r)

    total_linhas = len(rows)
    total_colunas = len(headers)

    datas_created = [r["created_at"].strip() for r in rows if r.get("created_at")]
    data_min = min(datas_created)
    data_max = max(datas_created)

    valores_total = [float(r["total"]) for r in rows if r.get("total")]
    val_min = min(valores_total)
    val_max = max(valores_total)
    val_avg = sum(valores_total) / len(valores_total)

    # Detecção de Outliers via Método do Intervalo Interquartil (IQR)
    sorted_tot = sorted(valores_total)
    n_tot = len(sorted_tot)
    q1 = sorted_tot[n_tot // 4]
    mediana = sorted_tot[n_tot // 2]
    q3 = sorted_tot[(3 * n_tot) // 4]
    iqr = q3 - q1
    lim_inferior = q1 - 1.5 * iqr
    lim_superior = q3 + 1.5 * iqr
    outliers_acima = sum(1 for v in sorted_tot if v > lim_superior)

    # Contagem de nulos em salesperson_id e distribuição de canais/status
    nulos_salesperson = sum(1 for r in rows if not r.get("salesperson_id") or r.get("salesperson_id").strip() == "")
    pedidos_ecommerce = sum(1 for r in rows if r.get("channel") == "ecommerce")
    pedidos_pos = sum(1 for r in rows if r.get("channel") == "pos")

    status_counts = {}
    for r in rows:
        st = r.get("status", "desconhecido")
        status_counts[st] = status_counts.get(st, 0) + 1

    print("=" * 80)
    print("⚓ LH NAUTICAL — RELATÓRIO DE AUDITORIA EXPLORATÓRIA (`orders`)")
    print("=" * 80)
    print(f"Total de Linhas:             {total_linhas:,}")
    print(f"Total de Colunas (Atributos):{total_colunas}")
    print(f"Data Mínima (created_at):    {data_min}")
    print(f"Data Máxima (created_at):    {data_max}")
    print(f"Valor Mínimo (total):        R$ {val_min:,.2f}")
    print(f"Valor Máximo (total):        R$ {val_max:,.2f}")
    print(f"Valor Médio (total):         R$ {val_avg:,.2f}  (Média Exata: {val_avg:.2f})")
    print("-" * 80)
    print("📊 ANÁLISE DE DISPERSÃO E OUTLIERS (IQR):")
    print(f"1º Quartil (Q1 - 25%):       R$ {q1:,.2f}")
    print(f"Mediana (Q2 - 50%):          R$ {mediana:,.2f}")
    print(f"3º Quartil (Q3 - 75%):       R$ {q3:,.2f}")
    print(f"IQR (Q3 - Q1):               R$ {iqr:,.2f}")
    print(f"Limite Superior (Q3+1.5*IQR):R$ {lim_superior:,.2f}")
    print(f"Outliers Identificados:      {outliers_acima:,} pedidos ({outliers_acima/total_linhas*100:.2f}%)")
    print("-" * 80)
    print("📋 QUALIDADE DE DADOS E GOVERNANÇA:")
    print(f"Nulos em salesperson_id:     {nulos_salesperson:,} ({nulos_salesperson/total_linhas*100:.1f}%)")
    print(f"Canal E-commerce:            {pedidos_ecommerce:,} ({pedidos_ecommerce/total_linhas*100:.1f}%)")
    print(f"Canal Loja Física (POS):     {pedidos_pos:,} ({pedidos_pos/total_linhas*100:.1f}%)")
    print("Distribuição por Status:")
    for st, cnt in sorted(status_counts.items(), key=lambda x: x[1], reverse=True):
        print(f"  • {st:<12}: {cnt:>6,} pedidos ({cnt/total_linhas*100:>5.1f}%)")
    print("=" * 80)

    return {
        "total_linhas": total_linhas,
        "total_colunas": total_colunas,
        "data_min": data_min,
        "data_max": data_max,
        "valor_min": val_min,
        "valor_max": val_max,
        "valor_medio": val_avg,
        "outliers_acima": outliers_acima,
        "lim_superior_iqr": lim_superior
    }


if __name__ == "__main__":
    executar_eda_orders()
