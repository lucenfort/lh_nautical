# 📄 Relatório Técnico e Executivo: Desafio LH Nautical

**Autor:** Luciano Silva de Arruda  
**Programa:** Processo Seletivo Lighthouse 2026 (Indicium AI) — Trilha Dados & IA  
**Empresa:** LH Nautical  
**Data:** 10 de Agosto de 2026  
**Banco de Dados:** PostgreSQL 16 (`lhnautical`)  

---

## 📑 Sumário Executivo

Este relatório consolida a execução técnica, analítica e estratégica desenvolvida para o **Desafio LH Nautical**. A jornada de dados abrangeu desde a auditoria e ingestão dos 24 arquivos CSV brutos (433.424 registros) até o desenvolvimento de análises exploratórias, modelagem relacional DDL em PostgreSQL (sem bibliotecas de terceiros), consultas analíticas com CTEs para identificação de clientes fiéis e correção do viés de sazonalidade via dimensão de calendário.

---

## 1. 🔍 Questão 1 — Análise Exploratória (EDA na Tabela `orders`)

### 1.1 Cenário & Objetivo
Avaliar a qualidade e confiabilidade inicial da base transacional bruta de vendas (`orders.csv`), respondendo às dúvidas da diretoria sobre volume, distribuição e presença de inconsistências antes de qualquer modelagem.

### 1.2 Metodologia & Script
Desenvolvido o script `lh_nautical/3_Codigos_e_Scripts/0_eda_orders.py` utilizando Python 3 puro (biblioteca padrão `csv`), sem aplicar limpezas ou tratamentos prévios aos dados.

```sql
-- Consulta SQL equivalente para a Q1.1
SELECT
    COUNT(*)                                  AS total_linhas,
    MIN(created_at)                           AS data_minima,
    MAX(created_at)                           AS data_maxima,
    MIN(total)                                AS valor_minimo,
    MAX(total)                                AS valor_maximo,
    ROUND(AVG(total), 2)                      AS valor_medio
FROM orders;
```

### 1.3 Resultados e Métricas Chave (Q1.1 & Q1.2)
- **Volume Total:** 48.998 linhas | 13 colunas
- **Intervalo Temporal (`created_at`):** `2020-01-01 01:19:28` a `2026-12-31 23:43:09` (cobertura de 7 anos)
- **Valor Mínimo (`total`):** R$ 32,62
- **Valor Máximo (`total`):** R$ 127.262,02
- **✅ VALOR MÉDIO REGISTRADO (`total` — Q1.2):** **R$ 28.704,99**

### 1.4 Diagnóstico de Confiabilidade (Q1.3)
1. **Outliers:** O método do Intervalo Interquartil ($Q1 = \text{R\$ 13.170,56}$, $Q3 = \text{R\$ 40.941,93}$, $IQR = \text{R\$ 27.771,37}$) identificou 452 registros acima do limite superior ($\text{R\$ 82.598,99}$). Não há faturamento negativo nem zerado. Esses outliers representam $0,9\%$ da base e correspondem a compras corporativas legítimas de embarcações e motores náuticos de alto valor.
2. **Qualidade dos Dados & Nulos:** A coluna `salesperson_id` possui $49,2\%$ de nulos ($24.131$ registros), explicados pelo canal e-commerce ($70,1\%$ das vendas totais), que opera sem vendedor físico. Todas as outras 12 colunas possuem $0\%$ de nulos.
3. **Recomendação para Análises Futuras:** A tabela não está pronta para consumo direto sem tratamentos. É necessário filtrar pedidos cancelados (`status = 'cancelled'`) e rascunhos (`draft`), além de cruzar com `order_items` para itens e `payments` para validação de faturamento real.

---

## 📐 2. Questão 2 — Detecção de Schema e DDL PostgreSQL

### 2.1 Cenário & Restrição Tecnológica
Diante da impossibilidade de conexão direta com o ERP, o schema do PostgreSQL precisou ser construído a partir dos 24 CSVs brutos.
- **Premissa Inviolável:** Uso exclusivo de **Python 3 puro** (`csv`, `os`, `re`, `datetime`). **Proibido o uso de `pandas`, `polars` ou `dask`**.

### 2.2 Script de Inferência de Tipos (`1_gerar_schema.py`)
Criado o script `lh_nautical/3_Codigos_e_Scripts/1_gerar_schema.py` que amostra até 5.000 linhas por CSV e infere automaticamente os tipos PostgreSQL:
- Inteiros de 32-bit: `INTEGER`
- Inteiros de 64-bit: `BIGINT`
- Chaves numéricas $> 18$ dígitos (ex: Chave NFe de 44 dígitos): `VARCHAR(50)`
- Valores decimais: `NUMERIC`
- Caracteres de data/hora: `TIMESTAMP` / `DATE`
- Valores booleanos: `BOOLEAN`
- Texto genérico: `VARCHAR(50)` ou `VARCHAR(100)`

### 2.3 Resultado (`schema.sql` — Q2.1 & Q2.2)
Gerado o arquivo `lh_nautical/3_Codigos_e_Scripts/schema.sql` contendo 24 comandos `CREATE TABLE` com `DROP TABLE IF EXISTS CASCADE` para idempotência total.

---

## 📥 3. Questão 3 — Ingestão e Carga Bruta no PostgreSQL

### 3.1 Script de Ingestão (`2_carregar_dados.py`)
Desenvolvido o script `lh_nautical/3_Codigos_e_Scripts/2_carregar_dados.py` utilizando `psycopg2` e `COPY ... FROM STDIN WITH CSV HEADER` para alta performance de carga sem realizar tratamentos (preservando nulos e caracteres originais).

### 3.2 Validação da Soma de Linhas (Q3.2)
```sql
SELECT
    (SELECT COUNT(*) FROM customers)   +  --   2.000
    (SELECT COUNT(*) FROM orders)      +  --  48.998
    (SELECT COUNT(*) FROM order_items)  +  -- 147.320
    (SELECT COUNT(*) FROM payments)        --  53.546
    AS total_linhas_acumulado;
```
- **✅ SOMA TOTAL ACUMULADA (Q3.2):** **251.864 linhas**
- **Total geral carregado (24 tabelas):** **433.424 linhas** com $100\%$ de sucesso.

---

## 👑 4. Questão 4 — Análise de Clientes Fiéis e Categoria Líder

### 4.1 Cenário & Regras de Negócio
Mapear clientes de alta fidelidade que possuem gasto médio elevado por transação e navegam por diversas categorias da loja (mínimo de 13 categorias distintas).

### 4.2 Consulta SQL (`3_analise_sql.sql` — Q4.1)
```sql
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
    INNER JOIN order_items AS oi ON o.id = oi.order_id
    INNER JOIN product_variants AS pv ON oi.product_variant_id = pv.id
    INNER JOIN products AS p ON pv.product_id = p.id
    INNER JOIN categories AS c ON p.category_id = c.id
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
```

### 4.3 Resultados do Ranking Top 10 Clientes Fiéis
| Ranking | Customer ID | Faturamento Total | Frequência | Ticket Médio | Diversidade Categorias |
|:---:|:---:|:---:|:---:|:---:|:---:|
| 🥇 1 | 1477 | R$ 3.834.485,79 | 22 pedidos | **R$ 174.294,81** | 14 |
| 🥈 2 | 1691 | R$ 3.453.998,50 | 20 pedidos | **R$ 172.699,93** | 14 |
| 🥉 3 | 929 | R$ 4.473.415,16 | 26 pedidos | **R$ 172.054,43** | 14 |
| 4 | 1067 | R$ 4.610.578,75 | 27 pedidos | **R$ 170.762,18** | 14 |
| 5 | 1505 | R$ 2.554.093,77 | 15 pedidos | **R$ 170.272,92** | 14 |
| 6 | 300 | R$ 3.348.742,37 | 20 pedidos | **R$ 167.437,12** | 14 |
| 7 | 568 | R$ 3.484.219,20 | 21 pedidos | **R$ 165.915,20** | 14 |
| 8 | 1116 | R$ 2.638.008,13 | 16 pedidos | **R$ 164.875,51** | 14 |
| 9 | 177 | R$ 5.212.191,17 | 32 pedidos | **R$ 162.880,97** | 14 |
| 10 | 1470 | R$ 4.218.169,21 | 26 pedidos | **R$ 162.237,28** | 14 |

### 4.4 Categoria Líder em Vendas para o Grupo Top 10 (Q4.1 Parte 2)
- 🏆 **CATEGORIA LÍDER:** **Hélices** (Category ID 8) com **561 itens comprados**.
- 2º Lugar: **Coletes Salva-Vidas** (370 itens)
- 3º Lugar: **Pesca** (365 itens)

### 4.5 Explicação Técnica (Q4.2)
1. **Cadeia de Chaves:** `orders.id` $\rightarrow$ `order_items.order_id` $\rightarrow$ `order_items.product_variant_id` $\rightarrow$ `product_variants.id` $\rightarrow$ `product_variants.product_id` $\rightarrow$ `products.id` $\rightarrow$ `products.category_id` $\rightarrow$ `categories.id`.
2. **Filtro de Diversidade:** `COUNT(DISTINCT category_id) >= 13` aplicado na cláusula `WHERE` das métricas agregadas.
3. **Escopo do Top 10:** Uso de `ROW_NUMBER() OVER (ORDER BY ticket_medio DESC, customer_id ASC)` e `INNER JOIN` da CTE de IDs elegíveis com os itens consumidos.

---

## 📅 5. Questão 5 — Dimensão de Calendário e Sazonalidade POS

### 5.1 Cenário & Erro do Estagiário
Identificar o pior dia da semana em média de vendas nas lojas físicas (`channel = 'pos'`). O estagiário agrupou a tabela `orders` diretamente, ignorando dias em que a loja abriu mas vendeu zero.

### 5.2 Consulta SQL (`3_analise_sql.sql` — Q5.1)
```sql
WITH intervalo_datas AS (
    SELECT MIN(placed_at::DATE) AS data_inicio, MAX(placed_at::DATE) AS data_fim FROM orders
),
calendario AS (
    SELECT dia::DATE AS data_calendario
    FROM intervalo_datas, GENERATE_SERIES(intervalo_datas.data_inicio, intervalo_datas.data_fim, INTERVAL '1 day') AS dia
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
    SELECT placed_at::DATE AS data_venda, SUM(total) AS total_vendas FROM orders WHERE channel = 'pos' GROUP BY placed_at::DATE
),
calendario_com_vendas AS (
    SELECT
        cal.data_calendario, cal.numero_dia_semana, cal.dia_semana_pt,
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

### 5.3 Resultados das Vendas Médias por Dia da Semana (POS)
| Dia da Semana | Dias Totais | Soma Total de Vendas | Média Diária Real | Posição |
|:---|:---:|:---:|:---:|:---:|
| Quarta-feira | 366 | R$ 63.539.589,22 | **R$ 173.605,44** | 🥇 1º (Melhor) |
| Sexta-feira | 365 | R$ 62.120.694,25 | **R$ 170.193,68** | 🥈 2º |
| Terça-feira | 365 | R$ 60.633.373,26 | **R$ 166.118,83** | 🥉 3º |
| Sábado | 365 | R$ 60.173.268,58 | **R$ 164.858,27** | 4º |
| Segunda-feira | 365 | R$ 57.758.021,43 | **R$ 158.241,15** | 5º |
| Domingo | 365 | R$ 57.529.887,95 | **R$ 157.616,13** | 6º |
| **Quinta-feira** | **366** | **R$ 57.518.480,61** | **R$ 157.154,32** | 🔻 **7º (PIOR DIA)** |

### 5.4 Explicação Técnica (Q5.2)
1. **Por que usar tabela de datas (calendário):** A tabela `orders` registra apenas transações ocorridas. Dias em que a loja esteve aberta mas vendeu R$ 0 não possuem linhas em `orders`. Sem o calendário, o `COUNT(dias)` no denominador desconsidera os dias zerados, criando viés de sobrevivência.
2. **Impacto nos resultados:** Ao aplicar o `LEFT JOIN` com o calendário completo e tratar `NULL` como R$ 0,00 via `COALESCE`, revelou-se que a **Quinta-feira** (e não o Domingo) possui a pior média real de vendas nas lojas físicas (R$ 157.154,32 / dia).

---

## 🤖 6. Questão 7 — Sistema de Recomendação (Similaridade de Cosseno)

### 6.1 Cenário & Objetivo Estratégico
A Sra. Marina identificou que clientes que compram embarcações e motores náuticos de alto valor frequentemente esquecem de adicionar itens de proteção e suporte (como defensas e cabos) no momento do checkout. O objetivo foi construir um motor de recomendação baseado em filtragem colaborativa item-item por similaridade de cosseno, identificando os produtos de maior afinidade para o item de referência **"Motor de Popa 1949"**.

### 6.2 Metodologia & Arquitetura do Script (`5_sistema_recomendacao.py`)
Desenvolvido o script `lh_nautical/3_Codigos_e_Scripts/5_sistema_recomendacao.py` em Python 3 (`pandas`, `numpy`, `sklearn`):
1. **Modelagem de Dados:** Junção relacional `orders` $\rightarrow$ `order_items` $\rightarrow$ `product_variants` $\rightarrow$ `products`.
2. **Matriz de Interação Binária ($2.000 \times 496$):** $2.000$ clientes em linhas e $496$ produtos em colunas. Células binarizadas em $1$ (presença de compra) ou $0$ (ausência), desconsiderando volume para focar na incidência de consumo.
3. **Cálculo da Matrix de Cosseno ($496 \times 496$):** Medição do cosseno do ângulo entre vetores de 2.000 dimensões:
   $$\text{Cosine Similarity}(A, B) = \frac{A \cdot B}{\|A\| \|B\|}$$
4. **Ranking Decrescente:** Seleção dos 5 produtos mais similares (excluindo o próprio item alvo).

### 6.3 Resultados Numéricos e Diagnóstico do Ranking (Produto Alvo: "Motor de Popa 1949")
| Ranking | Produto Recomendado | Similaridade Cosseno | Diagnóstico de Dados / Categoria de Negócio |
|:---:|:---|:---:|:---|
| **1** | `asdf` | **0.2789** | ⚠️ **Ruído nos Dados Brutos** (Cadastro de teste em `products.csv`, IDs 187 e 342). |
| **2** | **`Motor de Popa 5331`** | **0.2566** | 🏆 **Top 1 Produto Válido de Negócio** (Mesma categoria/Linha paralela). |
| **3** | `Cabo Náutico 2105` | **0.2562** | ⚓ **Venda Cruzada (Cross-Selling)**: Cabo de alta resistência para ancoragem. |
| **4** | `Vela Mestra 1913` | **0.2558** | ⛵ **Venda Cruzada (Cross-Selling)**: Propulsão auxiliar para veleiros. |
| **5** | `Defensa Náutica 3153` | **0.2529** | 🛡️ **Venda Cruzada Perfeita**: Proteção lateral de atracação (solução da Marina!). |

### 6.4 Resposta Oficial para o Questionário (Q7.2)
- **Cenário 1 (Dataset Bruto, sem filtros):** `'asdf'` (Similaridade Cosseno: **0.2789**)
- **Cenário 2 (Catálogo Higienizado / Produto Válido):** `'Motor de Popa 5331'` (Similaridade Cosseno: **0.2566**)

### 6.5 Análise Técnica & Insights de Negócio para o E-commerce (Q7.3)
1. **Sensibilidade do Modelo a Ruídos no Catálogo:** O aparecimento do registro `'asdf'` em 1º lugar demonstra empiricamente que algoritmos de filtragem colaborativa puramente matemáticos amplificam inconsistências de dados cadastrais. Em um ambiente de produção, é essencial sanitizar o catálogo de produtos antes de alimentar o modelo de recomendação.
2. **Estratégia de Regras de Negócio (Cross-Category vs. Same-Category):** Embora `Motor de Popa 5331` apresente a maior similaridade válida (0,2566), a exibição de outro motor de popa na vitrine do checkout é pouco efetiva para o consumidor final (que dificilmente comprará dois motores de popa na mesma sessão). A recomendação executiva para a LH Nautical é forçar a exibição de produtos complementares de categorias distintas — como **`Cabo Náutico 2105`** (0,2562) e **`Defensa Náutica 3153`** (0,2529) —, resolvendo diretamente o problema de *cross-selling* identificado pela Marina.
3. **Limitação de Cold-Start:** Produtos recém-lançados ou com poucas compras possuem vetores predominantemente zerados na matriz binária, resultando em similaridade próxima de $0$. Para contornar essa limitação, recomenda-se combinar a filtragem colaborativa com recomendação baseada em conteúdo (atributos de produto, categoria e NCM).

---

## 📈 7. Questão 6 — Previsão de Demanda ("Bússola de Bordo 702")

### 7.1 Cenário & Necessidade de Negócio
O Sr. Almir e a equipe de suprimentos enfrentavam desabastecimento de itens críticos em alta temporada (como coletes salva-vidas) e excesso de estoque empacado em outros (como âncoras). O objetivo foi construir um modelo baseline preditivo para estimar as vendas mensais do produto **"Bússola de Bordo 702"** no 1º trimestre de 2026 (`01/01/2026` a `31/03/2026`) com base nos dados históricos até `31/12/2025`.

### 7.2 Metodologia & Algoritmo (`4_modelo_demanda.py`)
Desenvolvido o script `lh_nautical/3_Codigos_e_Scripts/4_modelo_demanda.py` em Python 3 (`pandas`, `numpy`):
1. **Unificação Temporal:** Junção relacional `orders` $\rightarrow$ `order_items` $\rightarrow$ `product_variants` $\rightarrow$ `products` para o produto id correspondente à "Bússola de Bordo 702".
2. **Série Temporal Contínua:** Agregação mensal (`SUM(quantity)`) cobrindo 2020 a 2026.
3. **Média Móvel de 3 Meses (Rolling 3M) sem Data Leakage:** Aplicação de `shift(1).rolling(3).mean()`, garantindo que a previsão do mês $t$ dependa exclusivamente de $t-1, t-2, t-3$.
4. **Métrica de Erro MAE:** Avaliação da acurácia pela Média do Erro Absoluto:
   $$\text{MAE} = \frac{1}{n} \sum_{i=1}^{n} |Y_i - \hat{Y}_i|$$
5. **Tradução Financeira do Erro:** Conversão do MAE em Reais (R\$) multiplicando pela média de preço unitário ($R\$ 2.122,22$).

### 7.3 Resultados Preditivos do 1º Trimestre de 2026 (Período de Teste)
| Mês/Ano | Vendas Reais ($Y$) | Previsão 3M ($\hat{Y}$) | Previsão Inteira | Erro Absoluto ($|Y - \hat{Y}|$) |
|:---:|:---:|:---:|:---:|:---:|
| 2026-01 | **79 un** | 38,67 un | 39 un | 40,33 un |
| 2026-02 | **68 un** | 53,67 un | 54 un | 14,33 un |
| 2026-03 | **60 un** | 56,33 un | 56 un | 3,67 un |
| **TOTAL 1º TRI** | **207 un** | **148,67 un** | **149 un** | **MAE = 19,44 un/mês** |

### 7.4 Resposta Oficial para o Questionário (Q6.2) & Análise de Limitações (Q6.3)
- **✅ SOMA TOTAL DA PREVISÃO ARREDONDADA (Q6.2):** **149 unidades** (Previsão acumulada: 148,67 unidades).
- **Métrica MAE em Unidades:** **19,44 unidades / mês**.
- **MAE Financeiro Traduzido:** **R$ 41.265,44 / mês** em risco de desabastecimento.
- **Análise de Limitação:** O modelo de Média Móvel apresenta **atraso (*lag*) em picos sazonais**. Em janeiro/2026, com o início do verão, as vendas reais saltaram para 79 unidades, mas o modelo previa apenas 39 unidades (baseando-se no fim do ano anterior). Recomendação para produção: implementar modelos sazonais avançados (SARIMA, Prophet ou XGBoost com *lag 12*).

---

## 🎨 8. Próximas Etapas a Implementar

1. **Dashboard Executivo Náutico (`1_Dashboard/`):** Desenvolvimento da interface interativa com indicadores de faturamento, perfil de clientes fiéis, calendário POS e vitrine preditiva.
2. **Auditoria de Dados Final & Empacotamento:** Revisão final de todos os arquivos, conferência das respostas no rascunho `questionario.md` e preparação dos artefatos para entrega no Campo 20.


