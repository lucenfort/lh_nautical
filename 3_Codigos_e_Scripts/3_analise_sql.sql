-- =============================================================================
-- DESAFIO LH NAUTICAL — QUESTÃO 4 + QUESTÃO 5: ANALYTICS SQL
-- Autor: Luciano Silva de Arruda
-- Programa: Lighthouse 2026 (Indicium AI)
-- Banco: PostgreSQL 16 (lhnautical)
-- =============================================================================

-- =============================================================================
-- QUESTÃO 4 — ANÁLISE DE CLIENTES FIÉIS (TOP 10 TICKET MÉDIO + CATEGORIA LÍDER)
-- =============================================================================
-- Premissas:
--   - Faturamento Total: SUM(total) por customer_id
--   - Frequência: COUNT(DISTINCT order_id) por customer_id
--   - Ticket Médio: Faturamento Total / Frequência
--   - Diversidade: COUNT(DISTINCT category_id) >= 13
--   - Desempate: customer_id ASC
--
-- Cadeia de relacionamentos para alcançar a categoria:
--   orders.id → order_items.order_id
--   order_items.product_variant_id → product_variants.id
--   product_variants.product_id → products.id
--   products.category_id → categories.id
-- =============================================================================

-- ---------------------------------------------------------------------------
-- Q4.1 — PARTE 1: Top 10 Clientes Fiéis por Ticket Médio (diversidade >= 13)
-- ---------------------------------------------------------------------------
WITH base_pedidos AS (
    -- CTE 1 (Staging): Junção das tabelas transacionais com dimensão de produto
    -- Conecta pedidos aos itens, variantes, produtos e categorias
    SELECT
        o.id                        AS order_id,
        o.customer_id               AS customer_id,
        o.total                     AS order_total,
        oi.id                       AS order_item_id,
        oi.quantity                 AS quantity,
        oi.line_total               AS line_total,
        pv.id                       AS product_variant_id,
        pv.product_id               AS product_id,
        p.name                      AS product_name,
        p.category_id               AS category_id,
        c.name                      AS category_name
    FROM orders AS o
    INNER JOIN order_items AS oi
        ON o.id = oi.order_id
    INNER JOIN product_variants AS pv
        ON oi.product_variant_id = pv.id
    INNER JOIN products AS p
        ON pv.product_id = p.id
    INNER JOIN categories AS c
        ON p.category_id = c.id
),

metricas_clientes AS (
    -- CTE 2 (Intermediate): Calcula métricas de fidelidade por cliente
    -- Faturamento, Frequência, Ticket Médio e Diversidade de Categorias
    SELECT
        customer_id,
        SUM(order_total)                                        AS faturamento_total,
        COUNT(DISTINCT order_id)                                AS frequencia,
        ROUND(SUM(order_total) / COUNT(DISTINCT order_id), 2)  AS ticket_medio,
        COUNT(DISTINCT category_id)                             AS diversidade_categorias
    FROM base_pedidos
    GROUP BY customer_id
),

top10_fieis AS (
    -- CTE 3 (Marts): Filtra clientes com diversidade >= 13 e ranqueia Top 10
    -- Desempate por customer_id ASC (conforme premissa obrigatória)
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

-- Resultado Q4.1: Top 10 Clientes Fiéis
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


-- ---------------------------------------------------------------------------
-- Q4.1 — PARTE 2: Categoria Líder (maior SUM(quantity) entre os Top 10)
-- ---------------------------------------------------------------------------
WITH base_pedidos AS (
    SELECT
        o.id                        AS order_id,
        o.customer_id               AS customer_id,
        o.total                     AS order_total,
        oi.quantity                 AS quantity,
        pv.product_id               AS product_id,
        p.category_id               AS category_id,
        c.name                      AS category_name
    FROM orders AS o
    INNER JOIN order_items AS oi
        ON o.id = oi.order_id
    INNER JOIN product_variants AS pv
        ON oi.product_variant_id = pv.id
    INNER JOIN products AS p
        ON pv.product_id = p.id
    INNER JOIN categories AS c
        ON p.category_id = c.id
),

metricas_clientes AS (
    SELECT
        customer_id,
        SUM(order_total)                                        AS faturamento_total,
        COUNT(DISTINCT order_id)                                AS frequencia,
        ROUND(SUM(order_total) / COUNT(DISTINCT order_id), 2)  AS ticket_medio,
        COUNT(DISTINCT category_id)                             AS diversidade_categorias
    FROM base_pedidos
    GROUP BY customer_id
),

top10_fieis AS (
    SELECT
        customer_id,
        ticket_medio,
        diversidade_categorias,
        ROW_NUMBER() OVER (
            ORDER BY ticket_medio DESC, customer_id ASC
        ) AS ranking
    FROM metricas_clientes
    WHERE diversidade_categorias >= 13
),

-- Filtra apenas os Top 10 clientes
top10_ids AS (
    SELECT customer_id
    FROM top10_fieis
    WHERE ranking <= 10
),

-- Calcula a quantidade total de itens por categoria para os Top 10
categoria_compras AS (
    SELECT
        bp.category_name,
        bp.category_id,
        SUM(bp.quantity)   AS total_quantidade
    FROM base_pedidos AS bp
    INNER JOIN top10_ids AS t
        ON bp.customer_id = t.customer_id
    GROUP BY bp.category_name, bp.category_id
)

-- Resultado: Ranking de categorias por quantidade vendida aos Top 10
SELECT
    category_name,
    category_id,
    total_quantidade,
    RANK() OVER (ORDER BY total_quantidade DESC) AS ranking_categoria
FROM categoria_compras
ORDER BY total_quantidade DESC;


-- =============================================================================
-- QUESTÃO 5 — DIMENSÃO DE CALENDÁRIO + MÉDIA POS POR DIA DA SEMANA
-- =============================================================================
-- Premissas:
--   - Período: MIN(placed_at) até MAX(placed_at) da tabela orders
--   - Loja: apenas channel = 'pos' (lojas físicas)
--   - A loja esteve aberta em TODOS os dias do período (inclusive fins de semana)
--   - Dias sem venda = valor R$ 0,00 (não ignorar)
--   - Dias da semana em português: Segunda-feira, Terça-feira, etc.
--   - Vendas diárias = SUM(total) por dia
--   - Média = total_vendas_dia_semana / total_dias_semana
-- =============================================================================

WITH intervalo_datas AS (
    -- CTE 1: Identifica o período completo de análise
    SELECT
        MIN(placed_at::DATE) AS data_inicio,
        MAX(placed_at::DATE) AS data_fim
    FROM orders
),

calendario AS (
    -- CTE 2: Gera a série temporal completa de datas (dimensão de calendário)
    SELECT
        dia::DATE AS data_calendario
    FROM intervalo_datas,
         GENERATE_SERIES(
             intervalo_datas.data_inicio,
             intervalo_datas.data_fim,
             INTERVAL '1 day'
         ) AS dia
),

calendario_com_dia_semana AS (
    -- CTE 3: Adiciona o nome do dia da semana em português
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
    -- CTE 4: Soma de vendas POS por dia (apenas lojas físicas)
    SELECT
        placed_at::DATE       AS data_venda,
        SUM(total)            AS total_vendas
    FROM orders
    WHERE channel = 'pos'
    GROUP BY placed_at::DATE
),

calendario_com_vendas AS (
    -- CTE 5: LEFT JOIN do calendário com vendas, preenchendo dias sem venda com 0
    SELECT
        cal.data_calendario,
        cal.numero_dia_semana,
        cal.dia_semana_pt,
        COALESCE(vpd.total_vendas, 0) AS total_vendas
    FROM calendario_com_dia_semana AS cal
    LEFT JOIN vendas_pos_diarias AS vpd
        ON cal.data_calendario = vpd.data_venda
)

-- Resultado Q5.1: Média de vendas por dia da semana (com dias zerados)
SELECT
    dia_semana_pt                           AS dia_da_semana,
    COUNT(*)                                AS total_dias,
    ROUND(SUM(total_vendas), 2)            AS soma_vendas,
    ROUND(AVG(total_vendas), 2)            AS media_vendas
FROM calendario_com_vendas
GROUP BY dia_semana_pt, numero_dia_semana
ORDER BY numero_dia_semana;
