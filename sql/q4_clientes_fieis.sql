-- =============================================================================
-- LH NAUTICAL — SEGMENTAÇÃO DE CLIENTES FIÉIS (TOP 10 TICKET MÉDIO)
-- =============================================================================

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
