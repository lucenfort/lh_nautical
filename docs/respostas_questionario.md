# 📋 Guia Oficial de Respostas para o Questionário Seletivo
## Processo Seletivo Lighthouse 2026 (Indicium AI) — Desafio LH Nautical
**Candidato:** Luciano Silva de Arruda  
**Data:** 13 de Agosto de 2026

---

## 📌 Orientações de Preenchimento
Este documento contém o gabarito textual e técnico exato para submissão nos campos de texto da plataforma do processo seletivo da Indicium AI.

---

### 🔹 QUESTÃO 1 — EDA na Tabela `orders`

#### **Campo 1.1 — Código SQL da Análise Exploratória (EDA):**
```sql
-- =============================================================================
-- QUESTÃO 1.1 — EDA na Tabela `orders` (Dados Brutos, Sem Tratamento)
-- Desafio LH Nautical — Processo Seletivo Lighthouse 2026 (Indicium AI)
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

#### **Campo 1.2 — Valor Médio da Coluna `total`:**
```text
28704.99
```

#### **Campo 1.3 — Diagnóstico Técnico para o Sr. Almir:**
```text
Com base na análise exploratória conduzida sobre os dados brutos da tabela orders (48.998 registros transacionados entre 2020 e 2026), apresento o seguinte diagnóstico técnico:

1. Outliers na Coluna 'total': O valor dos pedidos varia de R$ 32,62 a R$ 127.262,02, com valor médio de R$ 28.704,99. Pelo método estatístico do Intervalo Interquartil (IQR: R$ 27.771,37; Q3: R$ 40.941,93; Limite Superior: R$ 82.598,99), foram identificados 452 registros acima do limite superior (0,92% da base). No contexto de varejo náutico (venda de embarcações, motores de popa de alta potência e eletrônicos de navegação), esses valores extremos são legítimos de negócio e não anomalias de digitação, refletindo transações de alto ticket que tracionam o faturamento da companhia.

2. Qualidade dos Dados & Nulos: Identificou-se que a coluna 'salesperson_id' possui 24.131 valores nulos (49,2% da base). Esse volume de nulos não representa corrupção de dados, mas decorre do modelo operacional da empresa: 70,1% das compras ocorrem no canal 'ecommerce' (autoatendimento digital sem vendedor associado), enquanto o canal físico 'pos' (29,9%) preenche o identificador do vendedor. O campo 'status' inclui pedidos pagos (70,1%), confirmados (15,0%), cancelados (9,9%) e rascunhos/draft (5,0%).

3. Prontidão para Análise e Decisões: A tabela é plenamente confiável como registro histórico e transacional bruto, mas NÃO está pronta para análises financeiras diretas sem segregação de status (excluindo cancelamentos e rascunhos). Para cálculo de faturamento líquido real e margens operacionais, é indispensável a integração relacional com as tabelas 'order_items' (itens) e 'payments' (liquidação financeira).
```

---

### 🔹 QUESTÃO 2 — Modelagem Relacional & Schema DDL PostgreSQL (Python Puro)

#### **Campo 2.1 — Código Python para Geração do `schema.sql`:**
```python
"""
Script de inferência estatística de tipos e geração do schema.sql para PostgreSQL 16.
Desenvolvido estritamente em Python 3 puro utilizando apenas a biblioteca padrão (csv, os, re, datetime, pathlib).
Em conformidade rigorosa com a restrição do edital (PROIBIDO pandas/polars/dask).
"""
import csv
import re
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent.parent
RAW_DIR = PROJECT_ROOT / "data" / "raw"
SQL_DIR = PROJECT_ROOT / "sql"
SCHEMA_OUTPUT = SQL_DIR / "schema.sql"
MAX_SAMPLE_ROWS = 5000

def inferir_tipo_valor(valor: str) -> str:
    val = valor.strip()
    if val == "" or val.lower() in ("null", "none", "na", "n/a"):
        return "NULL"
    if val.lower() in ("true", "false", "t", "f"):
        return "BOOLEAN"
    if re.match(r"^-?\d+$", val):
        if len(val) > 18:
            return "VARCHAR"
        num = int(val)
        return "INTEGER" if -2147483648 <= num <= 2147483647 else "BIGINT"
    if re.match(r"^-?\d+\.\d+$", val):
        return "NUMERIC"
    if re.match(r"^\d{4}-\d{2}-\d{2}\s+\d{2}:\d{2}:\d{2}", val):
        return "TIMESTAMP"
    if re.match(r"^\d{4}-\d{2}-\d{2}$", val):
        return "DATE"
    return "VARCHAR"

def resolver_tipo_coluna(tipos_encontrados: list, comprimento_max: int) -> str:
    tipos_efetivos = [t for t in tipos_encontrados if t != "NULL"]
    if not tipos_efetivos:
        return f"VARCHAR({max(comprimento_max, 50)})"
    tipos_set = set(tipos_efetivos)
    if len(tipos_set) == 1:
        tipo = tipos_set.pop()
        return f"VARCHAR({max(50, ((comprimento_max // 50) + 1) * 50)})" if tipo == "VARCHAR" else tipo
    if "VARCHAR" in tipos_set:
        return f"VARCHAR({max(50, ((comprimento_max // 50) + 1) * 50)})"
    if "TIMESTAMP" in tipos_set and "DATE" in tipos_set:
        return "TIMESTAMP"
    if tipos_set <= {"INTEGER", "BIGINT", "NUMERIC"}:
        return "NUMERIC" if "NUMERIC" in tipos_set else ("BIGINT" if "BIGINT" in tipos_set else "INTEGER")
    return f"VARCHAR({max(50, ((comprimento_max // 50) + 1) * 50)})"

def analisar_csv(filepath: Path, max_sample=MAX_SAMPLE_ROWS) -> list:
    with open(filepath, "r", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        headers = reader.fieldnames if reader.fieldnames else []
        if not headers:
            return []
        tipos_col = {col: [] for col in headers}
        len_col = {col: 0 for col in headers}
        for count, row in enumerate(reader):
            if count >= max_sample:
                break
            for col in headers:
                val = row.get(col, "").strip()
                tipos_col[col].append(inferir_tipo_valor(val))
                if len(val) > len_col[col]:
                    len_col[col] = len(val)
    return [(col, resolver_tipo_coluna(tipos_col[col], len_col[col])) for col in headers]

def gerar_create_table(nome_tabela: str, colunas: list) -> str:
    linhas_colunas = [f"    {col:<30} {tipo}" for col, tipo in colunas]
    corpo = ",\n".join(linhas_colunas)
    return f"DROP TABLE IF EXISTS {nome_tabela} CASCADE;\n\nCREATE TABLE {nome_tabela} (\n{corpo}\n);\n"
```

#### **Campo 2.2 — Amostra do Arquivo `schema.sql` Gerado:**
```sql
-- DDL para PostgreSQL 16 gerado para as 24 tabelas da base LH Nautical

DROP TABLE IF EXISTS orders CASCADE;
CREATE TABLE orders (
    id                             INTEGER,
    order_number                   VARCHAR(50),
    channel                        VARCHAR(50),
    customer_id                    INTEGER,
    salesperson_id                 INTEGER,
    location_id                    INTEGER,
    status                         VARCHAR(50),
    subtotal                       NUMERIC,
    discount_amount                NUMERIC,
    total                          NUMERIC,
    placed_at                      TIMESTAMP,
    created_at                     TIMESTAMP,
    updated_at                     TIMESTAMP
);

DROP TABLE IF EXISTS order_items CASCADE;
CREATE TABLE order_items (
    id                             INTEGER,
    order_id                       INTEGER,
    product_variant_id             INTEGER,
    quantity                       INTEGER,
    unit_price                     NUMERIC,
    icms_rate                      NUMERIC,
    ipi_rate                       NUMERIC,
    line_total                     NUMERIC
);
```

---

### 🔹 QUESTÃO 3 — Ingestão & Validação de Volume

#### **Campo 3.1 — Procedimento de Carga dos Dados:**
```sql
-- Carga dos 24 arquivos CSV no PostgreSQL via comando COPY nativo
\copy customers FROM 'data/raw/customers.csv' WITH (FORMAT csv, HEADER true, DELIMITER ',');
\copy orders FROM 'data/raw/orders.csv' WITH (FORMAT csv, HEADER true, DELIMITER ',');
\copy order_items FROM 'data/raw/order_items.csv' WITH (FORMAT csv, HEADER true, DELIMITER ',');
\copy payments FROM 'data/raw/payments.csv' WITH (FORMAT csv, HEADER true, DELIMITER ',');
```

#### **Campo 3.2 — Soma Total de Linhas (`customers + orders + order_items + payments`):**
```text
251864
```
*(Detalhamento: customers: 2.000 + orders: 48.998 + order_items: 147.320 + payments: 53.546 = 251.864 linhas)*.

---

### 🔹 QUESTÃO 4 — Análise de Clientes Fiéis & Categoria Líder

#### **Campo 4.1 — Código SQL com CTEs:**
```sql
-- =============================================================================
-- QUESTÃO 4.1 — Top 10 Clientes Fiéis e Categoria Líder em Volume
-- =============================================================================

-- PARTE 1: Top 10 Clientes Fiéis (Ticket Médio com Diversidade >= 13 Categorias)
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
        ROW_NUMBER() OVER (
            ORDER BY ticket_medio DESC, customer_id ASC
        ) AS ranking
    FROM metricas_clientes
    WHERE diversidade_categorias >= 13
)
SELECT
    ranking,
    customer_id,
    faturamento_total,
    frequencia,
    ticket_medio,
    diversidade_categorias
FROM top10_fieis
WHERE ranking <= 10
ORDER BY ranking;

-- PARTE 2: Categoria Líder em Volume de Vendas para o Top 10
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
    SELECT f.customer_id, f.ticket_medio, d.diversidade_categorias
    FROM faturamento_por_cliente AS f
    INNER JOIN diversidade_por_cliente AS d ON f.customer_id = d.customer_id
),
top10_fieis AS (
    SELECT customer_id, ROW_NUMBER() OVER (ORDER BY ticket_medio DESC, customer_id ASC) AS ranking
    FROM metricas_clientes
    WHERE diversidade_categorias >= 13
),
top10_ids AS (
    SELECT customer_id FROM top10_fieis WHERE ranking <= 10
),
base_itens_top10 AS (
    SELECT
        oi.quantity,
        p.category_id,
        c.name AS category_name
    FROM orders AS o
    INNER JOIN top10_ids AS t ON o.customer_id = t.customer_id
    INNER JOIN order_items AS oi ON o.id = oi.order_id
    INNER JOIN product_variants AS pv ON oi.product_variant_id = pv.id
    INNER JOIN products AS p ON pv.product_id = p.id
    INNER JOIN categories AS c ON p.category_id = c.id
)
SELECT
    RANK() OVER (ORDER BY SUM(quantity) DESC) AS ranking,
    category_name,
    category_id,
    SUM(quantity)                             AS total_quantidade
FROM base_itens_top10
GROUP BY category_name, category_id
ORDER BY total_quantidade DESC;
```

#### **Campo 4.2 — Explicação da Estrutura SQL & Conclusões de Negócio:**
```text
1. Estrutura e Isolamento de Granularidade: A consulta foi construída em CTEs modulares. O faturamento total e o ticket médio foram calculados exclusivamente no nível da tabela 'orders' (CTE faturamento_por_cliente), sem realizar join prévio com itens. A diversidade de categorias foi calculada separadamente agregando produtos por cliente (CTE diversidade_por_cliente). Essa separação técnica é fundamental para evitar a multiplicação indevida de valores totais (efeito de fanning por join 1:N).

2. Resultados do Top 10 Clientes Fiéis: O cliente líder é o Customer #22 (Faturamento: R$ 1.087.838,44; Frequência: 26 pedidos; Ticket Médio: R$ 41.839,94; 14 categorias distintas). O ranking completo é composto pelos clientes: #22, #1771, #1324, #1207, #98, #59, #676, #924, #1134 e #162.

3. Categoria Líder em Volume: A categoria com maior volume de unidades consumidas pelo Top 10 Clientes Fiéis é "Hélices", somando 492 unidades adquiridas, seguida por Coletes Salva-Vidas (393 un), Eletrônica Náutica (392 un) e Defensas (386 un). Isso comprova que clientes VIP realizam manutenção contínua e reposição frequente de propulsão e segurança, sugerindo a criação de programas de recompra automática e pacotes de revisão náutica.
```

---

### 🔹 QUESTÃO 5 — Dimensão Temporal & Vendas em Lojas Físicas (POS)

#### **Campo 5.1 — Código SQL com Dimensão de Calendário:**
```sql
-- =============================================================================
-- QUESTÃO 5.1 — Vendas Médias POS por Dia da Semana (Correção do Viés)
-- =============================================================================

WITH intervalo_datas AS (
    SELECT MIN(placed_at::DATE) AS data_inicio, MAX(placed_at::DATE) AS data_fim FROM orders
),
calendario AS (
    SELECT dia::DATE AS data_calendario
    FROM intervalo_datas,
         GENERATE_SERIES(intervalo_datas.data_inicio, intervalo_datas.data_fim, INTERVAL '1 day') AS dia
),
calendario_com_dia_semana AS (
    SELECT
        data_calendario,
        EXTRACT(ISODOW FROM data_calendario) AS numero_dia_semana,
        CASE EXTRACT(ISODOW FROM data_calendario)
            WHEN 1 THEN 'Segunda-feira'
            WHEN 2 THEN 'Terça-feira'
            WHEN 3 THEN 'Quarta-feira'
            WHEN 4 THEN 'Quinta-feira'
            WHEN 5 THEN 'Sexta-feira'
            WHEN 6 THEN 'Sábado'
            WHEN 7 THEN 'Domingo'
        END AS dia_semana_pt
    FROM calendario
),
vendas_pos_diarias AS (
    SELECT placed_at::DATE AS data_venda, SUM(total) AS total_vendas
    FROM orders
    WHERE channel = 'pos'
    GROUP BY placed_at::DATE
),
calendario_com_vendas AS (
    SELECT
        cal.data_calendario,
        cal.numero_dia_semana,
        cal.dia_semana_pt,
        COALESCE(vpd.total_vendas, 0) AS total_vendas
    FROM calendario_com_dia_semana AS cal
    LEFT JOIN vendas_pos_diarias AS vpd ON cal.data_calendario = vpd.data_venda
)
SELECT
    dia_semana_pt                           AS dia_da_semana,
    COUNT(*)                                AS total_dias,
    ROUND(SUM(total_vendas), 2)            AS soma_vendas,
    ROUND(AVG(total_vendas), 2)            AS media_vendas
FROM calendario_com_vendas
GROUP BY dia_semana_pt, numero_dia_semana
ORDER BY numero_dia_semana;
```

#### **Campo 5.2 — Justificativa do Calendário & Recomendações Operacionais:**
```text
1. Eliminação do Viés de Sobrevivência: Se calcularmos a média agrupando diretamente a tabela 'orders', o banco divide o faturamento apenas pelos dias em que houve pelo menos 1 venda registrada. Dias em que as lojas físicas estiveram abertas mas venderam R$ 0,00 deixam de existir na agregação, reduzindo o denominador e inflando a média artificialmente. A dimensão contínua de calendário com LEFT JOIN e COALESCE(total, 0) garante que todos os dias do período histórico entrem no cômputo da média real.

2. Resultado e Pior Dia de Vendas: A análise revela que a Quinta-feira é o pior dia da semana em lojas físicas, apresentando a menor média diária de vendas (R$ 157.154,32 / dia, com faturamento total de R$ 57.361.328,54 em 365 quintas-feiras). Em contrapartida, a Quarta-feira lidera as vendas com média de R$ 173.605,44 / dia.

3. Recomendação Estratégica para o Sr. Almir: Em vez de cogitar o fechamento no Domingo (que tem movimento relevante no varejo náutico), a diretoria deve readequar a escala de atendentes reduzindo o quadro nas quintas-feiras e reforçando a equipe nas quartas e sextas-feiras, além de criar campanhas promocionais de 'Quinta Náutica' para elevar o fluxo presencial.
```

---

### 🔹 QUESTÃO 6 — Previsão de Demanda Mensal (Bússola de Bordo 702)

#### **Campo 6.1 — Código Python do Modelo Preditivo:**
```python
# =============================================================================
# QUESTÃO 6.1 — Previsão de Demanda Mensal: Bússola de Bordo 702 (Média Móvel 3M)
# =============================================================================
import pandas as pd
from pathlib import Path

RAW_DIR = Path("data/raw")
df_orders = pd.read_csv(RAW_DIR / "orders.csv")
df_items = pd.read_csv(RAW_DIR / "order_items.csv")
df_variants = pd.read_csv(RAW_DIR / "product_variants.csv")
df_products = pd.read_csv(RAW_DIR / "products.csv")

# Unificação de dados
prod_bussola = df_products[df_products["name"] == "Bússola de Bordo 702"]["id"].tolist()
variants_bussola = df_variants[df_variants["product_id"].isin(prod_bussola)]["id"].tolist()

df_bussola = (
    df_orders[["id", "placed_at"]].rename(columns={"id": "order_id"})
    .merge(df_items[df_items["product_variant_id"].isin(variants_bussola)], on="order_id")
)
df_bussola["placed_at"] = pd.to_datetime(df_bussola["placed_at"])
df_bussola["ano_mes"] = df_bussola["placed_at"].dt.to_period("M")
preco_medio = df_bussola["unit_price"].mean()

# Agregação contínua
df_mensal = df_bussola.groupby("ano_mes")["quantity"].sum().reset_index()
all_months = pd.period_range(start=df_bussola["ano_mes"].min(), end=df_bussola["ano_mes"].max(), freq="M")
df_serie = pd.DataFrame({"ano_mes": all_months}).merge(df_mensal, on="ano_mes", how="left").fillna(0)
df_serie["quantity"] = df_serie["quantity"].astype(int)

# Média Móvel de 3 Meses com shift(1) para isolamento estrito contra data leakage
df_serie["previsao_3m"] = df_serie["quantity"].shift(1).rolling(window=3).mean()

# Avaliação no Período de Teste (1º Tri/2026)
teste_mask = (df_serie["ano_mes"] >= pd.Period("2026-01", freq="M")) & (df_serie["ano_mes"] <= pd.Period("2026-03", freq="M"))
df_teste = df_serie[teste_mask].copy()
df_teste["erro_absoluto"] = (df_teste["quantity"] - df_teste["previsao_3m"]).abs()

soma_previsao_inteira = int(round(df_teste["previsao_3m"].sum()))
mae_unidades = df_teste["erro_absoluto"].mean()
mae_financeiro = mae_unidades * preco_medio
```

#### **Campo 6.2 — Soma Total da Previsão para o 1º Tri/2026:**
```text
149
```
*(Detalhamento: Janeiro: 38,67 un; Fevereiro: 53,67 un; Março: 56,33 un. Soma exata = 148,67 un -> Arredondamento para 149 unidades)*.

#### **Campo 6.3 — Análise de Desempenho, MAE e Limitações:**
```text
1. Avaliação de Desempenho do Modelo: No 1º Trimestre de 2026, a previsão somou 149 unidades (Janeiro: 39 un, Fevereiro: 54 un, Março: 56 un) frente a 207 unidades efetivamente vendidas. O Erro Médio Absoluto (MAE) foi de 19,44 unidades/mês.

2. Tradução Financeira para a Gestão de Estoque: Considerando o preço médio de venda praticado de R$ 2.122,22 por unidade, o erro médio absoluto de 19,44 unidades equivale a uma incerteza financeira de R$ 41.265,44 por mês em valor de estoque imobilizado ou receita em risco de ruptura.

3. Limitações Metodológicas da Média Móvel: Por ser um modelo autorregressivo não ponderado de curto prazo, a média móvel de 3 meses reage com atraso (lag) a choques de sazonalidade. Em Janeiro (pico de verão náutico), as vendas saltaram para 79 unidades, enquanto a média móvel previu apenas 39 unidades (pois utilizou a média da primavera de 2025). 

4. Sugestão Técnica do Autor / Próximos Passos: Recomenda-se a evolução do pipeline para modelos de séries temporais com componente sazonal explícito de 12 meses (como SARIMA ou Prophet), que aprendem o padrão histórico de que todo Janeiro apresenta picos de demanda, permitindo programar ordens de compra junto aos fornecedores com 60 dias de antecedência.
```

---

### 🔹 QUESTÃO 7 — Sistema de Recomendação por Similaridade de Cosseno

#### **Campo 7.1 — Código Python do Sistema de Recomendação:**
```python
# =============================================================================
# QUESTÃO 7.1 — Sistema de Recomendação Item-Item (Cosine Similarity)
# =============================================================================
import pandas as pd
from sklearn.metrics.pairwise import cosine_similarity
from pathlib import Path

RAW_DIR = Path("data/raw")
df_orders = pd.read_csv(RAW_DIR / "orders.csv")
df_items = pd.read_csv(RAW_DIR / "order_items.csv")
df_variants = pd.read_csv(RAW_DIR / "product_variants.csv")
df_products = pd.read_csv(RAW_DIR / "products.csv")

# Unificação de compras cliente x produto
df_cust_prod = (
    df_orders[["id", "customer_id"]].rename(columns={"id": "order_id"})
    .merge(df_items[["order_id", "product_variant_id"]], on="order_id")
    .merge(df_variants[["id", "product_id"]].rename(columns={"id": "product_variant_id"}), on="product_variant_id")
    .merge(df_products[["id", "name"]].rename(columns={"id": "product_id", "name": "product_name"}), on="product_id")
)[["customer_id", "product_name"]].drop_duplicates()

# Matriz de Incidência Binária (2.000 clientes x 496 produtos)
matriz_bin = pd.crosstab(index=df_cust_prod["customer_id"], columns=df_cust_prod["product_name"]).map(lambda x: 1 if x > 0 else 0)

# Similaridade de Cosseno Produto x Produto
matriz_prod = matriz_bin.T
sim_matrix = cosine_similarity(matriz_prod.values)
df_sim = pd.DataFrame(sim_matrix, index=matriz_prod.index, columns=matriz_prod.index)

# Top 5 para 'Motor de Popa 1949'
target_prod = "Motor de Popa 1949"
ranking = df_sim[target_prod].drop(index=target_prod).sort_values(ascending=False).head(5)
```

#### **Campo 7.2 — Produto com Maior Similaridade ao 'Motor de Popa 1949':**
```text
Motor de Popa 5331
```
*(Nota técnica: Na base bruta sem sanitização cadastral, o item com maior valor numérico é 'asdf' com similaridade 0.2789. Desconsiderando o ruído de cadastro e analisando o catálogo de produtos válidos, o produto com maior similaridade é 'Motor de Popa 5331' com similaridade de cosseno de 0.2566).*

#### **Campo 7.3 — Vantagens, Limitações e Aplicação no E-commerce:**
```text
1. Fundamentação Matemática: A similaridade de cosseno calcula o cosseno do ângulo formado entre dois vetores de compradores no espaço n-dimensional (2.000 clientes). A matriz binária elimina a distorção gerada por clientes que compram volumes atípicos de uma só vez, medindo estritamente a afinidade de compra conjunta entre pares de produtos.

2. Vantagens do Método: Alta eficiência computacional, facilidade de implementação e capacidade de gerar recomendações de cross-selling instantâneas para a vitrine 'Quem comprou este produto também levou...' no checkout do e-commerce.

3. Limitações & Problema de Cold-Start: O modelo é dependente de histórico transacional prévio. Produtos recém-cadastrados no catálogo com zero compras possuem vetor zerado e nunca são recomendados (Cold-Start de itens). Além disso, como demonstrado na base bruta, algoritmos colaborativos são sensíveis a ruídos de cadastro (como o produto 'asdf'), exigindo higienização prévia de dados cadastrais.

4. Sugestão Técnica de Aplicação: Ativar o motor de recomendação no carrinho do e-commerce associando compras de motores de popa a cabos náuticos, velas e kits de hélice compatíveis, elevando a conversão de cross-selling e o ticket médio por pedido.
```

---

### 🔹 CAMPO 20 — Envio do Link do Dashboard e Materiais Complementares

```text
Prezados membros da banca avaliadora da Indicium AI,

Submeto a entrega oficial do Desafio LH Nautical contendo o ecossistema completo de Engenharia de Dados, Analytics e Inteligência Artificial:

1. Repositório Oficial no GitHub:
   https://github.com/lucenfort/lh_nautical

2. Dashboard Interativo Web (Streamlit):
   - Aplicação analítica executiva desenvolvida em Python + Streamlit + Plotly.
   - Código-fonte disponível no diretório: dashboard/app.py
   - Instruções completas para execução local e deploy no arquivo dashboard/README.md

3. Jupyter Notebook Oficial Executado:
   - Arquivo: notebooks/resolucao_lh_nautical.ipynb (contendo todas as análises, gráficos pré-renderizados e DDL relacional em Python puro).

4. Relatório Executivo e Técnico em PDF:
   - Arquivo consolidado disponível no diretório: relatorios/Relatorio_Executivo_LH_Nautical.pdf

Agradeço a oportunidade e permaneço à disposição para as etapas subsequentes do processo seletivo.

Atenciosamente,
Luciano Silva de Arruda
```
