# 📝 Gabarito Oficial de Respostas — Desafio LH Nautical
## Processo Seletivo Lighthouse 2026 (Indicium AI)
**Candidato:** Luciano Silva de Arruda  
**Data:** 13 de Agosto de 2026  
**Repositório Oficial:** [`github.com/lucenfort/lh_nautical`](https://github.com/lucenfort/lh_nautical)

---

> **Instrução de Uso:** Este documento contém os textos, códigos (SQL e Python) e valores numéricos formatados exatamente nos padrões exigidos pelo formulário de submissão da plataforma Indicium AI Academy, prontos para copiar e colar em cada campo.

---

# 🔍 Questão 1 — Análise Exploratória de Dados (EDA)

### 📌 Campo: Questão 1.1 — SQL (Código)
**Tipo:** Entrada de Texto / Código SQL  
**Conteúdo para Envio:**

```sql
-- =============================================================================
-- QUESTÃO 1.1 — EDA na Tabela `orders` (Dados Brutos, Sem Tratamento)
-- Desafio LH Nautical — Lighthouse 2026 (Indicium AI)
-- Autor: Luciano Silva de Arruda
-- =============================================================================

SELECT
    COUNT(*)                                  AS total_linhas,
    MIN(created_at)                           AS data_minima,
    MAX(created_at)                           AS data_maxima,
    MIN(total)                                AS valor_minimo,
    MAX(total)                                AS valor_maximo,
    ROUND(AVG(total), 2)                      AS valor_medio
FROM orders;
```

---

### 📌 Campo: Questão 1.2 — Validação (Valor Numérico)
**Tipo:** Caixa de Entrada Numérica / Texto Curto  
**Conteúdo para Envio:**

```
28704.99
```

---

### 📌 Campo: Questão 1.3 — Interpretação (Texto Dissertativo)
**Tipo:** Caixa de Texto Longo  
**Conteúdo para Envio:**

```
Diagnóstico de Confiabilidade da Tabela `orders`:

1. Outliers em `total`:
A coluna `total` varia de R$ 32,62 a R$ 127.262,02. Aplicando o método do Intervalo Interquartil (IQR), com Q1 = R$ 13.170,56, Q3 = R$ 40.941,93 e IQR = R$ 27.771,37, o Limite Superior de Outliers é de R$ 82.598,99 (Q3 + 1,5 * IQR). Foram identificados 452 pedidos acima desse limiar (0,92% da base) e nenhum valor negativo ou zerado. No setor de varejo náutico, embarcações completas e motores de popa de alta cilindrada custam rotineiramente acima de R$ 80.000,00, comprovando que esses pontos são transações comerciais legítimas e não erros de digitação.

2. Qualidade dos Dados (Valores Nulos e Inconsistências):
A coluna `salesperson_id` apresenta 49,2% de valores nulos (24.131 de 48.998 pedidos). Esse comportamento é justificado pela natureza multicanal da LH Nautical, onde as compras no e-commerce (70,1% das transações) ocorrem por autoatendimento digital (sem vendedor atribuído). As demais 12 colunas não possuem valores nulos. O campo `status` possui 4 categorias (paid: 70,1%, confirmed: 15,0%, cancelled: 9,9% e draft: 5,0%).

3. Prontidão para Análises de Receita:
A base bruta não está pronta para apuração de faturamento líquido sem filtros adicionais. Para análises financeiras confiáveis, é indispensável:
(a) Filtrar estritamente pedidos pagos (`status = 'paid'`), expurgando cancelamentos e rascunhos;
(b) Cruzar com `order_items` para decomposição de itens e categorias;
(c) Validar os recebimentos efetivos cruzando com a tabela `payments`.
A tabela é plenamente confiável como registro transacional bruto, mas exige tratamento relacional para inteligência de negócio.
```

---

# 📐 Questão 2 — Schema DDL PostgreSQL

### 📌 Campo: Questão 2.1 — Código Python (Upload / Código)
**Tipo:** Upload de Arquivo / Código Python  
**Arquivo:** `src/1_gerar_schema.py`  
**Conteúdo para Envio:**

```python
#!/usr/bin/env python3
"""
===============================================================================
DESAFIO LH NAUTICAL — QUESTÃO 2: GERADOR DE SCHEMA POSTGRESQL DDL
Autor: Luciano Silva de Arruda
Programa: Lighthouse 2026 (Indicium AI)
===============================================================================
Premissas obrigatórias:
  - Utilizar obrigatoriamente Python 3 puro e bibliotecas nativas.
  - PROIBIDO: pandas, polars, dask.
  - Banco de destino: PostgreSQL.
===============================================================================
"""

import csv
import os
import re
from datetime import datetime
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent.parent
CSV_DIR = PROJECT_ROOT / "data" / "raw"
OUTPUT_SQL = PROJECT_ROOT / "sql" / "schema.sql"

SAMPLE_SIZE = 5000

RE_INTEGER = re.compile(r"^-?\d+$")
RE_NUMERIC = re.compile(r"^-?\d+[\.,]\d+$")
RE_DATE = re.compile(r"^\d{4}-\d{2}-\d{2}$")
RE_DATETIME = re.compile(
    r"^\d{4}-\d{2}-\d{2}[ T]\d{2}:\d{2}:\d{2}(\.\d+)?([+-]\d{2}:?\d{2}|Z)?$"
)
BOOLEAN_VALUES = {"true", "false", "t", "f", "1", "0", "sim", "nao", "não", "yes", "no"}


def inferir_tipo_valor(valor: str) -> str:
    v = valor.strip()
    if not v:
        return "NULL"
    if v.lower() in BOOLEAN_VALUES:
        return "BOOLEAN"
    if RE_INTEGER.match(v):
        num = int(v)
        if -2147483648 <= num <= 2147483647:
            return "INTEGER"
        return "BIGINT"
    if RE_NUMERIC.match(v):
        return "NUMERIC"
    if RE_DATE.match(v):
        try:
            datetime.strptime(v, "%Y-%m-%d")
            return "DATE"
        except ValueError:
            pass
    if RE_DATETIME.match(v):
        return "TIMESTAMP"
    return "VARCHAR"


TYPE_HIERARCHY = {
    "NULL": 0, "BOOLEAN": 1, "INTEGER": 2, "BIGINT": 3,
    "NUMERIC": 4, "DATE": 5, "TIMESTAMP": 6, "VARCHAR": 7
}


def combinar_tipos(tipo_atual: str, novo_tipo: str) -> str:
    if tipo_atual == "NULL":
        return novo_tipo
    if novo_tipo == "NULL":
        return tipo_atual
    if tipo_atual == novo_tipo:
        return tipo_atual
    if {tipo_atual, novo_tipo} == {"INTEGER", "BIGINT"}:
        return "BIGINT"
    if {tipo_atual, novo_tipo} <= {"INTEGER", "BIGINT", "NUMERIC"}:
        return "NUMERIC"
    if {tipo_atual, novo_tipo} == {"DATE", "TIMESTAMP"}:
        return "TIMESTAMP"
    return "VARCHAR"


def analisar_csv(filepath: Path) -> dict:
    nome_tabela = filepath.stem
    colunas_tipos = {}
    max_lengths = {}

    with open(filepath, "r", encoding="utf-8-sig", errors="replace") as f:
        reader = csv.reader(f)
        try:
            headers = next(reader)
        except StopIteration:
            return {"tabela": nome_tabela, "colunas": {}}

        headers_limpos = [h.strip() for h in headers]
        colunas_tipos = {col: "NULL" for col in headers_limpos}
        max_lengths = {col: 0 for col in headers_limpos}

        for i, row in enumerate(reader):
            if i >= SAMPLE_SIZE:
                break
            for col, val in zip(headers_limpos, row):
                tipo_val = inferir_tipo_valor(val)
                colunas_tipos[col] = combinar_tipos(colunas_tipos[col], tipo_val)
                val_len = len(val.strip())
                if val_len > max_lengths[col]:
                    max_lengths[col] = val_len

    colunas_finais = {}
    for col, tipo in colunas_tipos.items():
        if tipo in ("NULL", "VARCHAR"):
            max_len = max_lengths[col]
            if max_len == 0 or max_len <= 50:
                colunas_finais[col] = "VARCHAR(50)"
            elif max_len <= 100:
                colunas_finais[col] = "VARCHAR(100)"
            elif max_len <= 255:
                colunas_finais[col] = "VARCHAR(255)"
            else:
                colunas_finais[col] = "TEXT"
        else:
            colunas_finais[col] = tipo

    return {"tabela": nome_tabela, "colunas": colunas_finais}


def gerar_ddl_tabela(info: dict) -> str:
    nome_tabela = info["tabela"]
    colunas = info["colunas"]
    linhas_ddl = [f"DROP TABLE IF EXISTS {nome_tabela} CASCADE;", f"CREATE TABLE {nome_tabela} ("]
    defs = [f"    {col} {tipo}" for col, tipo in colunas.items()]
    linhas_ddl.append(",\n".join(defs))
    linhas_ddl.append(");\n")
    return "\n".join(linhas_ddl)


def main():
    arquivos_csv = sorted(CSV_DIR.glob("*.csv"))
    OUTPUT_SQL.parent.mkdir(parents=True, exist_ok=True)
    
    with open(OUTPUT_SQL, "w", encoding="utf-8") as f_out:
        f_out.write("-- =============================================================================\n")
        f_out.write("-- DESAFIO LH NAUTICAL — SCHEMA DDL (PostgreSQL)\n")
        f_out.write("-- Gerado automaticamente por: 1_gerar_schema.py (Python 3 Puro)\n")
        f_out.write(f"-- Data: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
        f_out.write("-- =============================================================================\n\n")

        for csv_file in arquivos_csv:
            info = analisar_csv(csv_file)
            ddl = gerar_ddl_tabela(info)
            f_out.write(f"-- Tabela: {info['tabela']}\n")
            f_out.write(ddl + "\n")

    print(f"✅ Schema gerado com sucesso em: {OUTPUT_SQL}")


if __name__ == "__main__":
    main()
```

---

### 📌 Campo: Questão 2.2 — Arquivo `schema.sql` (Upload)
**Tipo:** Upload de Arquivo / Código SQL  
**Arquivo:** `sql/schema.sql`  
**Resumo do Arquivo:** Contém 24 instruções DDL com `DROP TABLE IF EXISTS CASCADE` e `CREATE TABLE` tipadas em PostgreSQL (`INTEGER`, `BIGINT`, `NUMERIC`, `BOOLEAN`, `TIMESTAMP`, `DATE`, `VARCHAR`).

---

# 📥 Questão 3 — Carregamento de Dados (Ingestão)

### 📌 Campo: Questão 3.1 — Código Python (Ingestão / Carga)
**Tipo:** Upload de Arquivo / Código Python  
**Arquivo:** `src/2_carregar_dados.py`  
**Conteúdo para Envio:**

```python
#!/usr/bin/env python3
"""
===============================================================================
DESAFIO LH NAUTICAL — QUESTÃO 3: INGESTÃO BRUTA NO POSTGRESQL / DATA WAREHOUSE
Autor: Luciano Silva de Arruda
Programa: Lighthouse 2026 (Indicium AI)
===============================================================================
"""

import sys
import logging
from pathlib import Path
import pandas as pd

PROJECT_ROOT = Path(__file__).resolve().parent.parent
RAW_DIR = PROJECT_ROOT / "data" / "raw"
DB_CONFIG = {
    "host": "localhost",
    "port": 5432,
    "dbname": "lhnautical",
    "user": "postgres",
    "password": "postgres",
}

LOAD_ORDER = [
    "attributes", "brands", "categories", "suppliers", "customers",
    "employees", "locations", "products", "product_variants",
    "variant_attribute_values", "product_suppliers", "addresses",
    "orders", "order_items", "payments", "fiscal_invoices",
    "purchase_orders", "purchase_order_items", "goods_receipts",
    "goods_receipt_items", "returns", "return_items",
    "stock_levels", "stock_movements"
]


def carregar_postgresql():
    import psycopg2
    conn = psycopg2.connect(**DB_CONFIG)
    cur = conn.cursor()
    
    total_geral = 0
    for tabela in LOAD_ORDER:
        csv_path = RAW_DIR / f"{tabela}.csv"
        if not csv_path.exists():
            continue
        with open(csv_path, "r", encoding="utf-8") as f:
            cur.copy_expert(f"COPY {tabela} FROM STDIN WITH CSV HEADER DELIMITER ',' NULL ''", f)
        conn.commit()
        cur.execute(f"SELECT COUNT(*) FROM {tabela}")
        qtd = cur.fetchone()[0]
        total_geral += qtd
        print(f"Tabela {tabela:<30} | {qtd:>10,} linhas carregadas.")
        
    cur.execute("""
        SELECT
            (SELECT COUNT(*) FROM customers) +
            (SELECT COUNT(*) FROM orders) +
            (SELECT COUNT(*) FROM order_items) +
            (SELECT COUNT(*) FROM payments) AS total_q32;
    """)
    total_q32 = cur.fetchone()[0]
    conn.close()
    print(f"\nTotal Geral: {total_geral:,} | Total Q3.2: {total_q32:,}")


if __name__ == "__main__":
    carregar_postgresql()
```

---

### 📌 Campo: Questão 3.2 — Validação (Valor Numérico)
**Tipo:** Caixa de Entrada Numérica / Texto Curto  
**Conteúdo para Envio:**

```
251864
```

*(Detalhamento: `customers`: 2.000 + `orders`: 48.998 + `order_items`: 147.320 + `payments`: 53.546 = 251.864).*

---

# 👑 Questão 4 — Análise de Clientes (Clientes Fiéis & Categorias)

### 📌 Campo: Questão 4.1 — Código SQL
**Tipo:** Entrada de Texto / Código SQL  
**Conteúdo para Envio:**

```sql
-- =============================================================================
-- QUESTÃO 4.1 — TOP 10 CLIENTES FIÉIS E CATEGORIA LÍDER
-- Desafio LH Nautical — Lighthouse 2026 (Indicium AI)
-- Autor: Luciano Silva de Arruda
-- =============================================================================

-- Parte 1: Top 10 Clientes Fiéis por Ticket Médio (Diversidade >= 13 Categorias)
WITH faturamento_por_cliente AS (
    SELECT
        customer_id,
        SUM(total)                                              AS faturamento_total,
        COUNT(DISTINCT id)                                      AS frequencia,
        ROUND(SUM(total) / COUNT(DISTINCT id), 2)              AS ticket_medio
    FROM orders
    GROUP BY customer_id
),
diversidade_por_cliente AS (
    SELECT
        o.customer_id,
        COUNT(DISTINCT p.category_id)                           AS diversidade_categorias
    FROM orders AS o
    INNER JOIN order_items AS oi ON o.id = oi.order_id
    INNER JOIN product_variants AS pv ON oi.product_variant_id = pv.id
    INNER JOIN products AS p ON pv.product_id = p.id
    GROUP BY o.customer_id
),
metricas_clientes AS (
    SELECT
        f.customer_id,
        f.faturamento_total,
        f.frequencia,
        f.ticket_medio,
        d.diversidade_categorias
    FROM faturamento_por_cliente AS f
    INNER JOIN diversidade_por_cliente AS d ON f.customer_id = d.customer_id
),
top10_fieis AS (
    SELECT
        customer_id,
        faturamento_total,
        frequencia,
        ticket_medio,
        diversidade_categorias,
        ROW_NUMBER() OVER (ORDER BY ticket_medio DESC, customer_id ASC) AS ranking
    FROM metricas_clientes
    WHERE diversidade_categorias >= 13
)
SELECT ranking, customer_id, faturamento_total, frequencia, ticket_medio, diversidade_categorias
FROM top10_fieis
WHERE ranking <= 10
ORDER BY ranking;

-- Parte 2: Categoria Líder em Volume de Itens para o Top 10 Clientes Fiéis
WITH top10_ids AS (
    SELECT customer_id
    FROM (
        SELECT
            f.customer_id,
            ROW_NUMBER() OVER (
                ORDER BY (f.faturamento_total / f.frequencia) DESC, f.customer_id ASC
            ) AS ranking
        FROM (
            SELECT customer_id, SUM(total) AS faturamento_total, COUNT(DISTINCT id) AS frequencia
            FROM orders GROUP BY customer_id
        ) f
        INNER JOIN (
            SELECT o.customer_id, COUNT(DISTINCT p.category_id) AS diversidade
            FROM orders o
            JOIN order_items oi ON o.id = oi.order_id
            JOIN product_variants pv ON oi.product_variant_id = pv.id
            JOIN products p ON pv.product_id = p.id
            GROUP BY o.customer_id
        ) d ON f.customer_id = d.customer_id
        WHERE d.diversidade >= 13
    ) ranked
    WHERE ranking <= 10
)
SELECT
    c.id                                                        AS category_id,
    c.name                                                      AS category_name,
    SUM(oi.quantity)                                            AS total_unidades_compradas
FROM orders AS o
INNER JOIN top10_ids AS t ON o.customer_id = t.customer_id
INNER JOIN order_items AS oi ON o.id = oi.order_id
INNER JOIN product_variants AS pv ON oi.product_variant_id = pv.id
INNER JOIN products AS p ON pv.product_id = p.id
INNER JOIN categories AS c ON p.category_id = c.id
GROUP BY c.id, c.name
ORDER BY total_unidades_compradas DESC;
```

**Resultados Oficiais:**
- **Top 1 Cliente Fiel:** `Customer #22` (Ticket Médio: **R$ 41.839,94** | Faturamento: R$ 1.087.838,44 | 26 pedidos | 14 categorias).
- **Categoria Líder dos VIPs:** **"Hélices"** (**492 unidades compradas**).

---

### 📌 Campo: Questão 4.2 — Explicação Técnica
**Tipo:** Caixa de Texto Longo  
**Conteúdo para Envio:**

```
Metodologia e Arquitetura da Consulta SQL de Clientes Fiéis:

1. Arquitetura de CTEs e Prevenção de Dupla Contagem:
O cálculo do faturamento total e do ticket médio foi isolado na CTE `faturamento_por_cliente` operando exclusivamente na granularidade da tabela `orders` (sem join com itens). A diversidade de categorias foi calculada separadamente na CTE `diversidade_por_cliente` através da junção `orders` -> `order_items` -> `product_variants` -> `products`. Essa segregação impede que o valor total de cada pedido seja multiplicado pelo número de itens contidos no carrinho.

2. Filtro de Diversidade Mínima:
Utilizamos a agregação `COUNT(DISTINCT p.category_id)` por cliente na CTE de diversidade. Na filtragem de elite, aplicamos `WHERE diversidade_categorias >= 13`, garantindo que apenas clientes que compraram em praticamente todas as 14/15 categorias do mix náutico fossem classificados como fiéis.

3. Escopo Estrito dos Top 10 e Categoria Líder:
Utilizamos a função de janela `ROW_NUMBER() OVER (ORDER BY ticket_medio DESC, customer_id ASC)` para ordenar estritamente os clientes elegíveis. Em seguida, isolamos os IDs do Top 10 na CTE `top10_ids` e realizamos a agregação de `SUM(oi.quantity)` cruzando com `categories`. A categoria "Hélices" destacou-se como a líder isolada com 492 unidades compradas pelo grupo VIP.
```

---

# 📅 Questão 5 — Dimensão de Calendário (Vendas Lojas Físicas POS)

### 📌 Campo: Questão 5.1 — Código SQL
**Tipo:** Entrada de Texto / Código SQL  
**Conteúdo para Envio:**

```sql
-- =============================================================================
-- QUESTÃO 5.1 — VENDAS EM LOJAS FÍSICAS (POS) E DIMENSÃO DE CALENDÁRIO
-- Desafio LH Nautical — Lighthouse 2026 (Indicium AI)
-- Autor: Luciano Silva de Arruda
-- =============================================================================

WITH RECURSIVE limites_datas AS (
    SELECT
        MIN(DATE(placed_at)) AS data_inicio,
        MAX(DATE(placed_at)) AS data_fim
    FROM orders
),
dimensao_calendario AS (
    SELECT
        d::DATE                                                 AS data_calendario,
        EXTRACT(ISODOW FROM d)::INTEGER                         AS dia_semana_num,
        CASE EXTRACT(ISODOW FROM d)::INTEGER
            WHEN 1 THEN 'Segunda-feira'
            WHEN 2 THEN 'Terça-feira'
            WHEN 3 THEN 'Quarta-feira'
            WHEN 4 THEN 'Quinta-feira'
            WHEN 5 THEN 'Sexta-feira'
            WHEN 6 THEN 'Sábado'
            WHEN 7 THEN 'Domingo'
        END                                                     AS dia_semana_nome
    FROM limites_datas,
    GENERATE_SERIES(data_inicio, data_fim, INTERVAL '1 day') AS d
),
vendas_pos_diarias AS (
    SELECT
        DATE(placed_at)                                         AS data_venda,
        SUM(total)                                              AS total_vendas_dia
    FROM orders
    WHERE channel = 'pos'
    GROUP BY DATE(placed_at)
),
calendario_com_vendas AS (
    SELECT
        c.data_calendario,
        c.dia_semana_num,
        c.dia_semana_nome,
        COALESCE(v.total_vendas_dia, 0.0)                      AS valor_venda_final
    FROM dimensao_calendario AS c
    LEFT JOIN vendas_pos_diarias AS v
        ON c.data_calendario = v.data_venda
)
SELECT
    dia_semana_num,
    dia_semana_nome,
    COUNT(*)                                                    AS total_dias_no_periodo,
    ROUND(SUM(valor_venda_final), 2)                           AS faturamento_acumulado,
    ROUND(AVG(valor_venda_final), 2)                           AS media_vendas_diaria
FROM calendario_com_vendas
GROUP BY dia_semana_num, dia_semana_nome
ORDER BY media_vendas_diaria ASC;
```

**Resultado Oficial:**
- **Pior Dia da Semana:** **Quinta-feira** (Média de **R$ 157.154,32 / dia** | Faturamento acumulado de R$ 57.361.328,54 em 365 quintas-feiras).

---

### 📌 Campo: Questão 5.2 — Explicação Técnica
**Tipo:** Caixa de Texto Longo  
**Conteúdo para Envio:**

```
Diagnóstico da Dimensão de Calendário e Correção do Viés de Sobrevivência:

1. Necessidade da Dimensão de Calendário:
Em um banco de dados transacional, a tabela `orders` registra apenas os dias em que houve vendas. Em dias nos quais as lojas físicas estiveram abertas mas venderam zero (ou fecharam por motivos operacionais), não há linhas gravadas no banco. Se calcularmos a média agrupando diretamente por dia da semana (`GROUP BY dia_semana`), o denominador será apenas a contagem de dias com vendas, ignorando os dias zerados e inflando artificialmente as médias (viés de sobrevivência). A geração de uma dimensão de calendário contínua (com `GENERATE_SERIES` cobrindo 2020 a 2026) e o uso de `LEFT JOIN` com `COALESCE(vendas, 0.0)` garantem que o denominador reflita a totalidade de dias do período.

2. Impacto nos Resultados e Recomendação ao Sr. Almir:
A análise corrigida desmistifica a intuição empírica de fechar lojas aos domingos. O Domingo apresenta uma média real robusta de R$ 161.038,25/dia (impulsionado pelo movimento náutico e turismo de fins de semana). O verdadeiro pior dia operacional da LH Nautical é a Quinta-feira, com a menor média semanal de R$ 157.154,32/dia. Portanto, a recomendação executiva é não fechar as lojas aos domingos, mas sim enxugar a escala de funcionários às quintas-feiras e reforçar os turnos de quarta e sexta-feira.
```

---

# 📈 Questão 6 — Previsão de Demanda (Série Temporal Baseline)

### 📌 Campo: Questão 6.1 — Código Python
**Tipo:** Upload de Arquivo / Código Python  
**Arquivo:** `src/4_modelo_demanda.py`  
**Conteúdo para Envio:**

```python
#!/usr/bin/env python3
"""
===============================================================================
DESAFIO LH NAUTICAL — QUESTÃO 6: PREVISÃO DE DEMANDA MENSAL (BÚSSOLA 702)
Autor: Luciano Silva de Arruda
Programa: Lighthouse 2026 (Indicium AI)
===============================================================================
"""

import pandas as pd
import numpy as np
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent.parent
RAW_DIR = PROJECT_ROOT / "data" / "raw"

df_orders = pd.read_csv(RAW_DIR / "orders.csv")
df_items = pd.read_csv(RAW_DIR / "order_items.csv")
df_variants = pd.read_csv(RAW_DIR / "product_variants.csv")
df_products = pd.read_csv(RAW_DIR / "products.csv")

# 1. Filtrar o produto Bússola de Bordo 702
prod_ids = df_products[df_products["name"] == "Bússola de Bordo 702"]["id"].tolist()
variant_ids = df_variants[df_variants["product_id"].isin(prod_ids)]["id"].tolist()

# 2. Junção relacional
df_vendas = (
    df_orders[["id", "placed_at"]].rename(columns={"id": "order_id"})
    .merge(df_items[df_items["product_variant_id"].isin(variant_ids)], on="order_id")
)
df_vendas["ano_mes"] = pd.to_datetime(df_vendas["placed_at"]).dt.to_period("M")
df_mensal = df_vendas.groupby("ano_mes")["quantity"].sum().reset_index()

# 3. Série temporal contínua
all_months = pd.period_range(start=df_vendas["ano_mes"].min(), end=df_vendas["ano_mes"].max(), freq="M")
df_serie = pd.DataFrame({"ano_mes": all_months}).merge(df_mensal, on="ano_mes", how="left").fillna(0)

# 4. Média Móvel 3M sem vazamento de dados (shift 1)
df_serie["previsao"] = df_serie["quantity"].shift(1).rolling(3).mean()

# 5. Avaliação no 1º Tri/2026
teste_tri = df_serie[df_serie["ano_mes"].isin([
    pd.Period("2026-01", "M"), pd.Period("2026-02", "M"), pd.Period("2026-03", "M")
])].copy()

soma_prevista_exata = teste_tri["previsao"].sum()
soma_prevista_inteira = round(soma_prevista_exata)
mae = np.mean(np.abs(teste_tri["quantity"] - teste_tri["previsao"]))

print(f"Previsão 1º Tri/2026: {soma_prevista_inteira} unidades (Exato: {soma_prevista_exata:.2f})")
print(f"MAE: {mae:.2f} unidades/mês")
```

---

### 📌 Campo: Questão 6.2 — Validação (Valor Numérico)
**Tipo:** Caixa de Entrada Numérica / Texto Curto  
**Conteúdo para Envio:**

```
149
```

*(Detalhamento: Janeiro/2026: 38,67 un + Fevereiro/2026: 53,67 un + Março/2026: 56,33 un = 148,67 $\rightarrow$ 149 unidades).*

---

### 📌 Campo: Questão 6.3 — Explicação Técnica
**Tipo:** Caixa de Texto Longo  
**Conteúdo para Envio:**

```
Construção do Modelo de Demanda e Avaliação Crítica:

1. Construção da Série Temporal e Média Móvel 3M:
Unificamos o histórico transacional da "Bússola de Bordo 702" (472 itens transacionados) agregando as vendas em granularidade mensal. Preenchemos eventuais meses sem vendas com 0 e calculamos o modelo baseline pela média móvel dos 3 meses imediatamente anteriores: M_t = (Y_{t-1} + Y_{t-2} + Y_{t-3}) / 3.

2. Prevenção de Vazamento de Dados (Data Leakage):
Para assegurar que a previsão do mês t utilize estritamente dados conhecidos até o mês t-1, aplicamos rigorosamente a operação `shift(1)` antes do cálculo da média móvel `.rolling(3).mean()`. Isso garante que as vendas reais do próprio mês de teste não façam parte de sua previsão.

3. Resultados no 1º Trimestre de 2026 e Impacto do MAE:
A previsão acumulada para o 1º Tri/2026 totalizou 149 unidades (Jan: 38,67 un, Fev: 53,67 un, Mar: 56,33 un) frente a 207 unidades reais, resultando em um Erro Médio Absoluto (MAE) de 19,44 unidades/mês. Com o preço médio unitário praticado de R$ 2.122,22, o MAE representa uma incerteza financeira de R$ 41.265,44/mês em estoque.

4. Limitações e Sugestões do Autor:
A Média Móvel 3M apresenta atraso estrutural (lag), pois ao prever o pico de verão de Janeiro (79 un reais), ela calcula a média da primavera anterior (out/nov/dez), prevendo apenas 39 un. Como evolução, sugere-se implementar modelos autoregressivos com componente sazonal anual explícito (SARIMA ou Prophet com lag de 12 meses), disparando ordens de compra a fornecedores em Outubro com 60 dias de antecedência.
```

---

# 🤖 Questão 7 — Sistema de Recomendação (Similaridade de Cosseno)

### 📌 Campo: Questão 7.1 — Código Python
**Tipo:** Upload de Arquivo / Código Python  
**Arquivo:** `src/5_sistema_recomendacao.py`  
**Conteúdo para Envio:**

```python
#!/usr/bin/env python3
"""
===============================================================================
DESAFIO LH NAUTICAL — QUESTÃO 7: SISTEMA DE RECOMENDAÇÃO ITEM-ITEM
Autor: Luciano Silva de Arruda
Programa: Lighthouse 2026 (Indicium AI)
===============================================================================
"""

import pandas as pd
from pathlib import Path
from sklearn.metrics.pairwise import cosine_similarity

PROJECT_ROOT = Path(__file__).resolve().parent.parent
RAW_DIR = PROJECT_ROOT / "data" / "raw"

df_orders = pd.read_csv(RAW_DIR / "orders.csv")
df_items = pd.read_csv(RAW_DIR / "order_items.csv")
df_variants = pd.read_csv(RAW_DIR / "product_variants.csv")
df_products = pd.read_csv(RAW_DIR / "products.csv")

# 1. Cruzamento para mapear Cliente × Produto
df_cust_prod = (
    df_orders[["id", "customer_id"]].rename(columns={"id": "order_id"})
    .merge(df_items[["order_id", "product_variant_id"]], on="order_id")
    .merge(df_variants[["id", "product_id"]].rename(columns={"id": "product_variant_id"}), on="product_variant_id")
    .merge(df_products[["id", "name"]].rename(columns={"id": "product_id", "name": "product_name"}), on="product_id")
)[["customer_id", "product_name"]].drop_duplicates()

# 2. Matriz binária de incidência (Cliente × Produto)
matriz_binaria = pd.crosstab(
    index=df_cust_prod["customer_id"],
    columns=df_cust_prod["product_name"]
).map(lambda x: 1 if x > 0 else 0)

# 3. Similaridade de Cosseno Item-Item (Transposta: Produto × Produto)
matriz_produtos = matriz_binaria.T
sim_matrix = cosine_similarity(matriz_produtos.values)
df_sim = pd.DataFrame(sim_matrix, index=matriz_produtos.index, columns=matriz_produtos.index)

# 4. Recomendações para 'Motor de Popa 1949'
target = "Motor de Popa 1949"
ranking = df_sim[target].drop(index=target).sort_values(ascending=False).head(5)

print(f"Top Recomendações para '{target}':")
for prod, score in ranking.items():
    print(f"  {prod:<35} | Similaridade: {score:.4f}")
```

---

### 📌 Campo: Questão 7.2 — Validação de Texto
**Tipo:** Caixa de Entrada de Texto  
**Conteúdo para Envio:**

```
Motor de Popa 5331
```

*(Nota técnica: Na base bruta sem filtros de sanitização, o item com maior score de cosseno é o ruído de cadastro `'asdf'` com score 0.2789. Expurgando esse item teste, o produto comercial legítimo líder absoluto é o **`Motor de Popa 5331`** com similaridade de **0.2566**).*

---

### 📌 Campo: Questão 7.3 — Explicação Técnica
**Tipo:** Caixa de Texto Longo  
**Conteúdo para Envio:**

```
Metodologia do Sistema de Recomendação por Similaridade de Cosseno:

1. Estruturação da Matriz Binária Cliente × Produto:
Construímos uma matriz esparsa de incidência binária (2.000 clientes × 496 produtos) onde cada célula M_{u,i} = 1 se o cliente u realizou ao menos uma compra do produto i no histórico, e 0 caso contrário. A abordagem binária é ideal para focar no padrão de coocorrência de compras entre clientes, mitigando distorções de clientes que compraram grandes volumes de uma única vez.

2. Interpretação da Similaridade de Cosseno:
A similaridade de cosseno calcula o cosseno do ângulo entre os vetores de cada par de produtos no espaço multidimensional de clientes: cos(u, v) = (u . v) / (||u|| * ||v||). O resultado varia de 0 (nenhum cliente em comum) a 1 (perfil de clientes idêntico). Para o "Motor de Popa 1949", o produto comercial de maior afinidade é o "Motor de Popa 5331" (0.2566), seguido por itens de amarração como "Cabo Náutico 2105" (0.2562) e "Vela Mestra 1913" (0.2558).

3. Limitações Técnicas e Ação no E-commerce:
(a) Cold-Start: Produtos novos sem histórico de compras possuem vetor zerado e não são recomendados. Recomenda-se modelo híbrido combinando filtragem colaborativa com metadados de categoria e marca;
(b) Vulnerabilidade a Ruídos: A base bruta continha o produto teste 'asdf' liderando com score 0.2789, evidenciando a necessidade de sanitização cadastral contínua no Data Warehouse antes do deploy em produção.
```

---

# 📎 Campo 20 — Material Complementar (Dashboard / Relatório)

### 📌 Campo: Espaço para adicionar arquivos (PDFs, Pbix, CSVs...)
**Tipo:** Upload de Arquivo / Anexo  
**Arquivos Prontos para Anexo:**
1. **Relatório Técnico & Executivo Final (PDF Compilado):**  
   📄 [`lh_nautical_relatorio/main.pdf`](file:///home/lucenfort/Workspace/lh_nautical/lh_nautical_relatorio/main.pdf) *(13 páginas completas com gráficos de 300 DPI, DER, KPIs e planos de ação)*.
2. **Dashboard Interativo em Streamlit:**  
   💻 [`lh_nautical_final/dashboard/app.py`](file:///home/lucenfort/Workspace/lh_nautical/lh_nautical_final/dashboard/app.py) *(Executável via `streamlit run dashboard/app.py`)*.
3. **Notebook Jupyter Executado com Saídas Pré-renderizadas:**  
   📓 [`lh_nautical_final/notebooks/resolucao_lh_nautical.ipynb`](file:///home/lucenfort/Workspace/lh_nautical/lh_nautical_final/notebooks/resolucao_lh_nautical.ipynb).
