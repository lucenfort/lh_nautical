-- =============================================================================
-- LH NAUTICAL — DIMENSÃO DE CALENDÁRIO & MÉDIA DE VENDAS LOJAS FÍSICAS (POS)
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


-- =============================================================================
-- VERSÃO ALTERNATIVA PORTÁTIL (ANSI SQL / SQLITE / DUCKDB / SNOWFLAKE)
-- Utiliza CTE Recursiva (WITH RECURSIVE) para motores sem GENERATE_SERIES:
-- =============================================================================
/*
WITH RECURSIVE intervalo(dt_inicio, dt_fim) AS (
    SELECT MIN(DATE(placed_at)), MAX(DATE(placed_at)) FROM orders
),
calendario_rec(data_calendario) AS (
    SELECT dt_inicio FROM intervalo
    UNION ALL
    SELECT DATE(data_calendario, '+1 day')
    FROM calendario_rec, intervalo
    WHERE data_calendario < dt_fim
),
vendas_pos AS (
    SELECT DATE(placed_at) AS dt_venda, SUM(total) AS total_vendas
    FROM orders WHERE channel = 'pos' GROUP BY DATE(placed_at)
)
SELECT
    CASE STRFTIME('%w', c.data_calendario)
        WHEN '1' THEN 'Segunda-feira'
        WHEN '2' THEN 'Terça-feira'
        WHEN '3' THEN 'Quarta-feira'
        WHEN '4' THEN 'Quinta-feira'
        WHEN '5' THEN 'Sexta-feira'
        WHEN '6' THEN 'Sábado'
        WHEN '0' THEN 'Domingo'
    END AS dia_da_semana,
    COUNT(*) AS total_dias,
    ROUND(SUM(COALESCE(v.total_vendas, 0)), 2) AS soma_vendas,
    ROUND(AVG(COALESCE(v.total_vendas, 0)), 2) AS media_vendas
FROM calendario_rec c
LEFT JOIN vendas_pos v ON c.data_calendario = v.dt_venda
GROUP BY dia_da_semana
ORDER BY AVG(COALESCE(v.total_vendas, 0)) ASC;
*/
