# 📊 Dicionário de Gráficos Oficiais, Evidências e Interpretações
## Desafio LH Nautical — Processo Seletivo Lighthouse 2026 (Indicium AI)
**Candidato:** Luciano Silva de Arruda  
**Data:** 13 de Agosto de 2026  
**Diretório de Imagens (300 DPI):** [`lh_nautical_final/data/processed/`](file:///home/lucenfort/Workspace/desafio_lh_nautical/lh_nautical_final/data/processed)

---

## 🧭 Sumário das Evidências Visuais Oficiais

Todos os gráficos foram estruturados individualmente no mais alto padrão visual corporativo e editorial:
- **Design Limpo e Focado:** 1 objetivo analítico por gráfico, sem divisões apertadas.
- **Legendas Seguras:** Posicionadas no canto superior esquerdo ou direito sem cobrir dados ou títulos.
- **Tipografia & Eixos:** Margens amplas, labels monetárias e numéricas legíveis em 300 DPI.

---

### 📈 1. Distribuição do Valor dos Pedidos e Limites do IQR (Questão 1 — EDA)
🔗 **Arquivo:** [`1_eda_distribuicao_pedidos.png`](file:///home/lucenfort/Workspace/desafio_lh_nautical/lh_nautical_final/data/processed/1_eda_distribuicao_pedidos.png)

![Distribuição dos Pedidos](file:///home/lucenfort/Workspace/desafio_lh_nautical/lh_nautical_final/data/processed/1_eda_distribuicao_pedidos.png)

#### 🔬 Descrição Técnica:
- Histograma de frequência do valor total dos 48.998 pedidos da tabela `orders` (2020 a 2026).
- **Linha Tracejada Azul:** Média Geral dos Pedidos = **R$ 28.704,99** (Gabarito da Q1.2).
- **Linha Contínua Verde:** Mediana = **R$ 25.918,02**.
- **Linha Pontilhada Vermelha:** Limite Superior do Intervalo Interquartil = **R$ 82.598,99** ($Q_1 = \text{R\$}~13.170,56$; $Q_3 = \text{R\$}~40.941,93$; $IQR = \text{R\$}~27.771,37$).
- **Identificação de Outliers:** 452 pedidos acima do limite superior (0,92% da base).

#### 💡 Diagnóstico Técnico para o Sr. Almir (Q1.3):
- No setor de varejo náutico, embarcações e motores de popa de alta cilindrada custam naturalmente acima de R$ 80.000,00, comprovando que esses valores representam vendas reais de alto valor comercial, e não erros cadastrais.

---

### 🌐 2. Composição por Canal de Venda e Status Operacional (Questão 1 — EDA)
🔗 **Arquivo:** [`2_canais_e_status_pedidos.png`](file:///home/lucenfort/Workspace/desafio_lh_nautical/lh_nautical_final/data/processed/2_canais_e_status_pedidos.png)

![Canais e Status dos Pedidos](file:///home/lucenfort/Workspace/desafio_lh_nautical/lh_nautical_final/data/processed/2_canais_e_status_pedidos.png)

#### 🔬 Descrição Técnica:
- **Painel Esquerdo (Canais de Venda):** Participação do **E-commerce (34.342 pedidos | 70,1%)** e das **Lojas Físicas POS (14.656 pedidos | 29,9%)**.
- **Painel Direito (Status dos Pedidos):** Distribuição operacional das transações: **Pago (34.365 | 70,1%)**, **Confirmado (7.335 | 15,0%)**, **Cancelado (4.847 | 9,9%)** e **Rascunho (2.451 | 5,0%)**.

#### 💡 Interpretação de Negócio & Governança (Q1.3):
- 49,2% de valores nulos em `salesperson_id` ocorrem devido ao autoatendimento no E-commerce (70,1%). É indispensável filtrar pedidos pagos (`paid`) para cômputo da receita líquida real.

---

### 👑 3. Top 10 Clientes Fiéis por Ticket Médio (Questão 4 — Clientes VIP)
🔗 **Arquivo:** [`3_top10_clientes_fieis_ticket_medio.png`](file:///home/lucenfort/Workspace/desafio_lh_nautical/lh_nautical_final/data/processed/3_top10_clientes_fieis_ticket_medio.png)

![Top 10 Clientes Fiéis](file:///home/lucenfort/Workspace/desafio_lh_nautical/lh_nautical_final/data/processed/3_top10_clientes_fieis_ticket_medio.png)

#### 🔬 Descrição Técnica:
- Ranking horizontal dos clientes com compras em **13 ou mais categorias distintas**, ordenado pelo **Ticket Médio** decrescente (cálculo isolado em nível de pedido `orders` sem duplicações de join).
- Destaque em vermelho para o **Customer #22**, líder absoluto com **Ticket Médio de R$ 41.839,94** (Faturamento de R$ 1.087.838,44 em 26 pedidos e 14 categorias navegadas).

#### 💡 Estratégia Comercial para Marina Costa (Q4.2):
- Criar o programa de fidelidade náutica VIP com benefícios de revisão preventiva e atendimento concierge exclusivo.

---

### 📦 4. Categorias Mais Compradas pelo Grupo VIP (Questão 4 — Mix de Produtos)
🔗 **Arquivo:** [`4_top_categorias_compradas_vip.png`](file:///home/lucenfort/Workspace/desafio_lh_nautical/lh_nautical_final/data/processed/4_top_categorias_compradas_vip.png)

![Categorias Mais Compradas VIP](file:///home/lucenfort/Workspace/desafio_lh_nautical/lh_nautical_final/data/processed/4_top_categorias_compradas_vip.png)

#### 🔬 Descrição Técnica:
- Soma do volume de unidades compradas pelo grupo dos 10 clientes mais fiéis.
- Destaque em azul marinho para a categoria **"Hélices"**, líder isolada com **492 unidades**, seguida por *Coletes Salva-Vidas* (393 un), *Eletrônica Náutica* (392 un), *Defensas* (386 un) e *Cabos Náuticos* (375 un).

#### 💡 Decisão de Suprimentos & Estoque:
- Hélices sofrem desgaste contínuo por cavitação e impactos aquáticos. Manter estoque de segurança elevado e kits de substituição programada.

---

### 📅 5. Vendas em Lojas Físicas POS & Correção de Calendário (Questão 5)
🔗 **Arquivo:** [`5_vendas_pos_calendario_vies.png`](file:///home/lucenfort/Workspace/desafio_lh_nautical/lh_nautical_final/data/processed/5_vendas_pos_calendario_vies.png)

![Vendas POS e Dimensão Calendário](file:///home/lucenfort/Workspace/desafio_lh_nautical/lh_nautical_final/data/processed/5_vendas_pos_calendario_vies.png)

#### 🔬 Descrição Técnica:
- **Barras Azuis (Média Real com Calendário):** Faturamento diário médio via `LEFT JOIN` com uma **Dimensão de Calendário Contínua (2020 a 2026)**, imputando R$ 0,00 via `COALESCE` para dias sem vendas.
- **Barras Vermelhas (Média Ingênua):** Cálculo que descarta dias zerados (*viés de sobrevivência*).

#### 💡 Diagnóstico Operacional para o Sr. Almir (Q5.2):
- **Pior Dia Real:** A **Quinta-feira** tem a menor média real da semana (**R$ 157.154,32 / dia** | R$ 57,36 Mi totais em 365 quintas-feiras).
- **Melhor Dia Real:** A **Quarta-feira** lidera as vendas com **R$ 173.605,44 / dia**.
- **Decisão:** Não fechar aos domingos (faturamento sólido de R$ 161.038,25/dia). O ajuste correto é enxugar a escala de funcionários às quintas-feiras.

---

### 📈 6. Previsão Mensal de Demanda: Bússola de Bordo 702 (Questão 6)
🔗 **Arquivo:** [`6_previsao_demanda_bussola_702.png`](file:///home/lucenfort/Workspace/desafio_lh_nautical/lh_nautical_final/data/processed/6_previsao_demanda_bussola_702.png)

![Previsão Demanda Bússola 702](file:///home/lucenfort/Workspace/desafio_lh_nautical/lh_nautical_final/data/processed/6_previsao_demanda_bussola_702.png)

#### 🔬 Descrição Técnica:
- **Barras Azuis:** Vendas reais mensais da *Bússola de Bordo 702* (Jun/2024 a Mar/2026).
- **Linha Vermelha com Pontos:** Curva do modelo de **Média Móvel de 3 Meses com `shift(1)`** (sem vazamento temporal).
- **Área Sombreada:** Período de Teste oficial do 1º Trimestre de 2026.
- **Legenda Posicionada à Esquerda:** Permite a visualização perfeita de todas as barras e picos sazonais de verão.
- **Validação Numérica:**
  - Janeiro/2026: Real = 79 un | Previsão = 38,67 un (39 un)
  - Fevereiro/2026: Real = 68 un | Previsão = 53,67 un (54 un)
  - Março/2026: Real = 60 un | Previsão = 56,33 un (56 un)
  - **Soma da Previsão Total (Q6.2):** **149 unidades** (148,67 un exatas) vs 207 un reais.
  - **Métrica de Erro (MAE):** **19,44 unidades / mês**.
  - **Impacto Financeiro:** **R$ 41.265,44 / mês** em valor de estoque (Preço médio: R$ 2.122,22/un).

---

### 🤖 7. Ranking de Similaridade de Cosseno para o Motor de Popa 1949 (Questão 7 — Recomendação)
🔗 **Arquivo:** [`7_recomendacao_produtos_motor_1949.png`](file:///home/lucenfort/Workspace/desafio_lh_nautical/lh_nautical_final/data/processed/7_recomendacao_produtos_motor_1949.png)

![Recomendação de Produtos](file:///home/lucenfort/Workspace/desafio_lh_nautical/lh_nautical_final/data/processed/7_recomendacao_produtos_motor_1949.png)

#### 🔬 Descrição Técnica:
- Similaridade de Cosseno calculada sobre a matriz binária transposta de incidência ($2.000 \times 496$).
- Destaque em vermelho para o ruído cadastral `asdf` (**0.2789** na base bruta) e destaque em azul para o produto comercial legítimo líder **Motor de Popa 5331 (0.2566 | 25,66%)** (Gabarito da Q7.2).

#### 💡 Estratégia de E-commerce (Q7.3):
- Recomendar produtos de mesma categoria funcional (motorização de maior potência) e itens complementares de navegação e atracação (*cross-selling*).

---

### 🗄️ 8. Diagrama de Entidade-Relacionamento (DER) — Data Warehouse (Questões 2 e 3)
🔗 **Arquivo:** [`8_diagrama_entidade_relacionamento.png`](file:///home/lucenfort/Workspace/desafio_lh_nautical/lh_nautical_final/data/processed/8_diagrama_entidade_relacionamento.png)

![Diagrama de Entidade Relacionamento](file:///home/lucenfort/Workspace/desafio_lh_nautical/lh_nautical_final/data/processed/8_diagrama_entidade_relacionamento.png)

#### 🔬 Descrição Técnica:
- Mapeamento relacional e dimensional do Data Warehouse da LH Nautical (24 tabelas | 433.424 registros totais).
- **Tabelas Fato (Azul Escuro):** `orders`, `order_items`, `payments` (249.864 transações operacionais).
- **Tabelas Dimensão (Azul Ciano / Teal):** `customers`, `product_variants`, `products`, `categories`, `employees`.
- Indicação formal de Chaves Primárias `[PK]`, Chaves Estrangeiras `[FK]` e cardinalidade ($1:N$).

---

### 🔄 9. Arquitetura de Linhagem de Dados & Pipeline SQL (Data Lineage)
🔗 **Arquivo:** [`9_arquitetura_pipeline_sql.png`](file:///home/lucenfort/Workspace/desafio_lh_nautical/lh_nautical_final/data/processed/9_arquitetura_pipeline_sql.png)

![Linhagem do Pipeline SQL](file:///home/lucenfort/Workspace/desafio_lh_nautical/lh_nautical_final/data/processed/9_arquitetura_pipeline_sql.png)

#### 🔬 Descrição Técnica:
- **Camada Bronze (Raw):** 24 arquivos CSV brutos e scripts de auditoria/EDA.
- **Camada Silver (Schema & Ingestão):** `1_gerar_schema.py` (Python puro) + `sql/schema.sql` (PostgreSQL DDL) + `2_carregar_dados.py`.
- **Camada Gold (CTEs Analíticas):** Modelagem de Clientes Fiéis (Q4) e Dimensão de Calendário Contínuo com `GENERATE_SERIES` (Q5).
- **Camada de Inteligência & IA:** Modelo de Demanda (Q6 Média Móvel 3M sem leakage) e Motor de Recomendação (Q7 Cosseno Item-Item).
