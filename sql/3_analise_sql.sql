-- =============================================================================
-- LH NAUTICAL — QUERIES ANALÍTICAS DE NEGÓCIO (SQL POSTGRESQL 16)
-- Autor: Luciano Silva de Arruda
-- Projeto: LH Nautical — Plataforma de Engenharia de Dados & Analytics
-- =============================================================================

-- =============================================================================
-- 1. ANÁLISE DE CLIENTES DE ALTA FIDELIDADE (TOP 10 TICKET MÉDIO + CATEGORIA LÍDER)
-- =============================================================================
-- Premissas:
--   - Faturamento Total: SUM(total) no nível de pedidos (orders)
--   - Frequência: COUNT(DISTINCT order_id) no nível de pedidos
--   - Ticket Médio: Faturamento Total / Frequência
--   - Diversidade: COUNT(DISTINCT category_id) >= 13
--   - Desempate: customer_id ASC
-- =============================================================================

-- Parte 1: Top 10 Clientes Fiéis por Ticket Médio
WITH faturamento_por_cliente AS (
    -- Faturamento e frequência calculados diretamente na tabela `orders`
    -- (sem join com itens, evitando multiplicação indevida de faturamento)
    SELECT
        customer_id,
        SUM(total)                                              AS faturamento_total,
        COUNT(DISTINCT id)                                      AS frequencia,
        ROUND(SUM(total) / COUNT(DISTINCT id), 2)              AS ticket_medio
    FROM orders
    GROUP BY customer_id
),

diversidade_por_cliente AS (
    -- Contagem de categorias distintas compradas por cliente
    SELECT
        o.customer_id,
        COUNT(DISTINCT p.category_id)                           AS diversidade_categorias
    FROM orders AS o
    INNER JOIN order_items AS oi
        ON o.id = oi.order_id
    INNER JOIN product_variants AS pv
        ON oi.product_variant_id = pv.id
    INNER JOIN products AS p
        ON pv.product_id = p.id
    GROUP BY o.customer_id
),

metricas_clientes AS (
    -- Combina faturamento com diversidade
    SELECT
        f.customer_id,
        f.faturamento_total,
        f.frequencia,
        f.ticket_medio,
        d.diversidade_categorias
    FROM faturamento_por_cliente AS f
    INNER JOIN diversidade_por_cliente AS d
        ON f.customer_id = d.customer_id
),

top10_fieis AS (
    -- Filtra clientes com diversidade >= 13 e aplica ordenação de desempate
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


-- Parte 2: Categoria Líder em Volume de Compras para os Top 10 Clientes
WITH faturamento_por_cliente AS (
    SELECT
        customer_id,
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
    INNER JOIN order_items AS oi
        ON o.id = oi.order_id
    INNER JOIN product_variants AS pv
        ON oi.product_variant_id = pv.id
    INNER JOIN products AS p
        ON pv.product_id = p.id
    GROUP BY o.customer_id
),

metricas_clientes AS (
    SELECT
        f.customer_id,
        f.ticket_medio,
        d.diversidade_categorias
    FROM faturamento_por_cliente AS f
    INNER JOIN diversidade_por_cliente AS d
        ON f.customer_id = d.customer_id
),

top10_fieis AS (
    SELECT
        customer_id,
        ROW_NUMBER() OVER (
            ORDER BY ticket_medio DESC, customer_id ASC
        ) AS ranking
    FROM metricas_clientes
    WHERE diversidade_categorias >= 13
),

top10_ids AS (
    SELECT customer_id FROM top10_fieis WHERE ranking <= 10
),

base_itens_top10 AS (
    SELECT
        oi.quantity          AS quantity,
        p.category_id        AS category_id,
        c.name               AS category_name
    FROM orders AS o
    INNER JOIN top10_ids AS t
        ON o.customer_id = t.customer_id
    INNER JOIN order_items AS oi
        ON o.id = oi.order_id
    INNER JOIN product_variants AS pv
        ON oi.product_variant_id = pv.id
    INNER JOIN products AS p
        ON pv.product_id = p.id
    INNER JOIN categories AS c
        ON p.category_id = c.id
),

categoria_compras AS (
    SELECT
        category_name,
        category_id,
        SUM(quantity)   AS total_quantidade
    FROM base_itens_top10
    GROUP BY category_name, category_id
)

SELECT
    category_name,
    category_id,
    total_quantidade,
    RANK() OVER (ORDER BY total_quantidade DESC) AS ranking_categoria
FROM categoria_compras
ORDER BY total_quantidade DESC;


-- =============================================================================
-- 2. DIMENSÃO DE CALENDÁRIO & PERFORMANCE DE LOJAS FÍSICAS (POS)
-- =============================================================================
-- Premissas:
--   - Intervalo temporal completo da tabela orders
--   - Canal exclusivo de lojas físicas (channel = 'pos')
--   - Lojas abertas todos os dias (dias sem vendas = R$ 0,00)
--   - Nomes dos dias em português
-- =============================================================================

WITH intervalo_datas AS (
    SELECT
        MIN(placed_at::DATE) AS data_inicio,
        MAX(placed_at::DATE) AS data_fim
    FROM orders
),

calendario AS (
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
    SELECT
        placed_at::DATE       AS data_venda,
        SUM(total)            AS total_vendas
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
    LEFT JOIN vendas_pos_diarias AS vpd
        ON cal.data_calendario = vpd.data_venda
)

SELECT
    dia_semana_pt                           AS dia_da_semana,
    COUNT(*)                                AS total_dias,
    ROUND(SUM(total_vendas), 2)            AS soma_vendas,
    ROUND(AVG(total_vendas), 2)            AS media_vendas
FROM calendario_com_vendas
GROUP BY dia_semana_pt, numero_dia_semana
ORDER BY numero_dia_semana;
