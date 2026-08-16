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
