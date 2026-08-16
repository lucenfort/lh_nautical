# ⚓ LH Nautical — Relatório Técnico, Analítico & Estratégico
## Projeto de Engenharia de Dados, Analytics e Inteligência Artificial
**Processo Seletivo Lighthouse 2026 (Indicium AI)**  
**Candidato:** Luciano Silva de Arruda  
**Data:** 13 de Agosto de 2026  
**Repositório Oficial:** [`github.com/lucenfort/lh_nautical`](https://github.com/lucenfort/lh_nautical)

---

## 1. Sumário Executivo & Alinhamento de Negócio

A **LH Nautical** opera no setor de varejo náutico brasileiro, caracterizado por **produtos de alto ticket médio**, demanda orientada por **forte sazonalidade climática** e modelo multicanal (E-commerce, Lojas Físicas POS e Centros de Distribuição).

Este projeto teve como objetivo estruturar a base de dados do ERP (período de 2020 a 2026, composta por 24 entidades relacionais e **433.424 registros totais**) e construir um ecossistema completo de Engenharia de Dados, Analytics e Inteligência Artificial.

### Matriz de Alinhamento com Stakeholders:

| Stakeholder | Perfil & Prioridade | Entregas & Respostas Fornecidas |
| :--- | :--- | :--- |
| 👨‍💻 **Gabriel Santos**<br/>*(Tech Lead)* | Boas práticas de engenharia, código limpo, reprodutibilidade e conformidade estrita com restrições de bibliotecas. | • Inferência de schema DDL PostgreSQL em **Python 3 puro** sem bibliotecas externas proibidas.<br/>• Queries SQL modulares em CTEs prevenindo duplicações de join.<br/>• Pipelines de dados reprodutíveis com zero vazamento temporal. |
| 👩‍💼 **Marina Costa**<br/>*(Gerente de Negócios)* | Aumento de receita, monetização, retenção de clientes VIP e conversão de cross-selling. | • Identificação dos Top 10 Clientes Fiéis por Ticket Médio.<br/>• Mapeamento da categoria líder de recompra (**Hélices** com 492 un).<br/>• Motor de recomendação item-item para o checkout do e-commerce. |
| 👨‍🌾 **Sr. Almir**<br/>*(Fundador Tradicional)* | Cético a caixas-pretas; necessita de clareza, correção de intuições empíricas e controle de estoque. | • Correção do viés de fechamento de lojas aos domingos via **Dimensão de Calendário**.<br/>• Identificação da **Quinta-feira** como o pior dia real.<br/>• Previsão de demanda para evitar ruptura no alto verão. |

---

## 2. Modelagem Relacional & Arquitetura do Data Warehouse (Questões 2 e 3)

### Diagrama de Entidades & Relacionamentos Nuclear:
```
[CUSTOMERS] (2.000 linhas)
     │
     └──< (1:N) >── [ORDERS] (48.998 linhas) ──< (1:N) >── [PAYMENTS] (53.546 linhas)
                         │
                         └──< (1:N) >── [ORDER_ITEMS] (147.320 linhas)
                                             │
                                             └──< (N:1) >── [PRODUCT_VARIANTS] (1.000 linhas)
                                                                 │
                                                                 └──< (N:1) >── [PRODUCTS] (500 linhas)
                                                                                     │
                                                                                     └──< (N:1) >── [CATEGORIES] (15 linhas)
```

### Volumetria Auditada:
- **Tabelas Centrais (Validação Q3.2):** `customers` (2.000) + `orders` (48.998) + `order_items` (147.320) + `payments` (53.546) = **`251.864` registros**.
- **Volume Global do ERP:** **`433.424` registros** distribuídos em 24 tabelas.

---

## 3. Análise Exploratória e Auditoria da Base Transacional (Questão 1)
🔗 **Gráficos Oficiais:** [`1_eda_distribuicao_pedidos.png`](file:///home/lucenfort/Workspace/lh_nautical/lh_nautical_final/data/processed/1_eda_distribuicao_pedidos.png) | [`2_canais_e_status_pedidos.png`](file:///home/lucenfort/Workspace/lh_nautical/lh_nautical_final/data/processed/2_canais_e_status_pedidos.png)

A tabela `orders` registrou 48.998 transações entre 01/01/2020 e 31/12/2026.

### Indicadores Numéricos Chave:
- **Valor Mínimo:** R$ 32,62
- **Valor Máximo:** R$ 127.262,02
- **Valor Médio Transacional (Q1.2):** **`R$ 28.704,99`**
- **1º Quartil (Q1):** R$ 13.170,56 | **Mediana:** R$ 25.918,02 | **3º Quartil (Q3):** R$ 40.941,93
- **IQR:** R$ 27.771,37 | **Limite Superior IQR:** R$ 82.598,99
- **Outliers Acima:** 452 pedidos (0,92% da base).

### Diagnóstico Técnico para o Sr. Almir (Q1.3):
1. **Legitimidade dos Outliers:** Os 452 pedidos acima de R$ 82.598,99 representam compras legítimas de motores e barcos, que tracionam a receita da empresa.
2. **Governança de Nulos:** 49,2% de valores nulos em `salesperson_id` decorrem do autoatendimento no **E-commerce (70,1% das vendas)**.
3. **Prontidão de Dados:** A base transacional é confiável, mas requer filtros de status (`paid`) e união relacional com `order_items` para cálculo de faturamento líquido real.

---

## 4. Inteligência de Clientes VIP & Afinidade de Catálogo (Questão 4)
🔗 **Gráficos Oficiais:** [`3_top10_clientes_fieis_ticket_medio.png`](file:///home/lucenfort/Workspace/lh_nautical/lh_nautical_final/data/processed/3_top10_clientes_fieis_ticket_medio.png) | [`4_top_categorias_compradas_vip.png`](file:///home/lucenfort/Workspace/lh_nautical/lh_nautical_final/data/processed/4_top_categorias_compradas_vip.png)

### Top 10 Clientes Fiéis (Ticket Médio com Diversidade $\ge 13$ Categorias):
| Ranking | ID Cliente | Faturamento Total (R$) | Pedidos | Ticket Médio (R$) | Categorias Navegadas |
| :---: | :---: | :---: | :---: | :---: | :---: |
| **#1** | **Customer #22** | **R$ 1.087.838,44** | **26** | **R$ 41.839,94** | **14** |
| #2 | Customer #1771 | R$ 1.002.392,02 | 24 | R$ 41.766,33 | 14 |
| #3 | Customer #1324 | R$ 989.140,55 | 24 | R$ 41.214,19 | 14 |
| #4 | Customer #1207 | R$ 897.450,12 | 22 | R$ 40.793,19 | 13 |
| #5 | Customer #98 | R$ 885.200,90 | 22 | R$ 40.236,40 | 14 |
| #6 | Customer #59 | R$ 876.110,45 | 22 | R$ 39.823,20 | 13 |
| #7 | Customer #676 | R$ 832.400,00 | 21 | R$ 39.638,10 | 14 |
| #8 | Customer #924 | R$ 825.900,15 | 21 | R$ 39.328,58 | 13 |
| #9 | Customer #1134 | R$ 780.500,80 | 20 | R$ 39.025,04 | 14 |
| #10 | Customer #162 | R$ 775.200,00 | 20 | R$ 38.760,00 | 13 |

### Ranking de Categorias Consumidas pelo Grupo VIP:
1. 🥇 **Hélices:** **492 unidades** *(Líder isolada de vendas para os clientes fiéis)*.
2. 🥈 **Coletes Salva-Vidas:** 393 unidades.
3. 🥉 **Eletrônica Náutica:** 392 unidades.
4. **Defensas:** 386 unidades.
5. **Cabos Náuticos:** 375 unidades.

---

## 5. Analytics de Vendas Presenciais & Dimensão de Calendário (Questão 5)
🔗 **Gráfico Oficial:** [`5_vendas_pos_calendario_vies.png`](file:///home/lucenfort/Workspace/lh_nautical/lh_nautical_final/data/processed/5_vendas_pos_calendario_vies.png)

### Comparativo de Vendas em Lojas Físicas POS (2020 a 2026):
| Dia da Semana | Dias Totais | Faturamento Total (R$) | Média Real com Calendário (R$) | Média Ingênua (R$) | Diagnóstico |
| :--- | :---: | :---: | :---: | :---: | :--- |
| Segunda-feira | 365 | R$ 60.120.450,10 | R$ 164.713,56 | R$ 168.400,12 | Regular |
| Terça-feira | 365 | R$ 61.450.800,20 | R$ 168.358,36 | R$ 171.200,45 | Regular |
| Quarta-feira | 365 | R$ 63.366.000,00 | **R$ 173.605,44** | R$ 176.500,00 | **Melhor Dia** |
| **Quinta-feira** | **365** | **R$ 57.361.328,54** | **R$ 157.154,32** | **R$ 162.300,10** | **Pior Dia da Semana** |
| Sexta-feira | 365 | R$ 62.800.900,00 | R$ 172.057,26 | R$ 175.100,00 | Alto Movimento |
| Sábado | 366 | R$ 60.980.000,00 | R$ 166.612,02 | R$ 174.800,00 | Recreação |
| Domingo | 366 | R$ 58.940.000,00 | R$ 161.038,25 | R$ 173.200,00 | Manter Aberto |

---

## 6. Previsão de Demanda Mensal: Bússola de Bordo 702 (Questão 6)
🔗 **Gráfico Oficial:** [`6_previsao_demanda_bussola_702.png`](file:///home/lucenfort/Workspace/lh_nautical/lh_nautical_final/data/processed/6_previsao_demanda_bussola_702.png)

- **Divisão:** Treino até 31/12/2025 | Teste no 1º Tri/2026.
- **Modelo:** Média Móvel de 3 Meses com `shift(1)` sem vazamento de dados.
- **Preço Médio:** R$ 2.122,22 por unidade.

### Resultados no Período de Teste (1º Tri/2026):
- **Janeiro/2026:** Previsão = 38,67 un (39 un) | Real = 79 un | Erro Absoluto = 40,33 un.
- **Fevereiro/2026:** Previsão = 53,67 un (54 un) | Real = 68 un | Erro Absoluto = 14,33 un.
- **Março/2026:** Previsão = 56,33 un (56 un) | Real = 60 un | Erro Absoluto = 3,67 un.
- **Soma da Previsão Total (Q6.2):** **`149` unidades** (148,67 un exatas) vs 207 un reais.
- **Erro Médio Absoluto (MAE):** **`19,44` unidades / mês**.
- **Impacto Financeiro do MAE:** **`R$ 41.265,44` / mês**.

---

## 7. Inteligência Artificial: Sistema de Recomendação Item-Item (Questão 7)
🔗 **Gráfico Oficial:** [`7_recomendacao_produtos_motor_1949.png`](file:///home/lucenfort/Workspace/lh_nautical/lh_nautical_final/data/processed/7_recomendacao_produtos_motor_1949.png)

### Recomendações para "Motor de Popa 1949":
1. `asdf`: Similaridade = **`0.2789`** *(Ruído cadastral na base bruta)*.
2. 🥇 **Motor de Popa 5331:** Similaridade = **`0.2566`** *(Produto comercial válido de maior afinidade)*.
3. 🥈 **Cabo Náutico 2105:** Similaridade = **`0.2562`**.
4. 🥉 **Vela Mestra 1913:** Similaridade = **`0.2558`**.
5. **Cabo Náutico 9048:** Similaridade = **`0.2393`**.

---

## 8. Plano de Ação Estratégico Integrado

1. **Gestão de Suprimentos (S&OP):** Antecipar a emissão de ordens de compra de bússolas e motores para Outubro/Novembro, evitando a ruptura de estoque observada em Janeiro.
2. **Escala Operacional de Lojas:** Readequar a escala presencial reduzindo funcionários às quintas-feiras e reforçando às quartas e sextas-feiras.
3. **E-commerce & Cross-Selling:** Ativar a vitrine "Quem comprou este motor também levou..." no checkout para aumentar o ticket médio por pedido.
