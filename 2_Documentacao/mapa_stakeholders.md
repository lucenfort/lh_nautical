# Mapa de Stakeholders - Desafio LH Nautical

**Elaborado por:** Luciano Silva de Arruda  
**Programa:** Lighthouse (Indicium AI)  
**Projeto:** Case LH Nautical (Análise de Dados, Engenharia e IA)

---

## 👥 Matriz de Alinhamento com a Diretoria

Para garantir o sucesso estratégico da entrega, cada seção e artefato técnico foi desenhado considerando as prioridades, dores e focos de cada stakeholder:

### 1. ⚙️ Gabriel Santos (Tech Lead)
* **Perfil:** Foco total em Arquitetura de Dados, Qualidade de Código, Performance e Boas Práticas.
* **Dores:** Códigos desorganizados, ausência de tratamento de tipos, queries SQL sem estrutura limpa, falta de controle de integridade referencial.
* **Respostas do Projeto:**
  * Script de ingestão (`1_ingestao_e_limpeza.py`) componentizado e tipado para DuckDB e SQLite.
  * Consultas SQL (`2_analise_e_sql.sql`) estruturadas exclusivamente com CTEs (`WITH ... AS`), documentadas e padronizadas em ANSI SQL.
  * Modelo relacional limpo e documentado via Diagrama ER (DER).
  * 0% de duplicação em chaves primárias e garantia de conversão explícita de tipos.

### 2. 📈 Marina Costa (Gerente de Negócios)
* **Perfil:** Foco em Lucratividade, Margens, Retorno sobre Investimento (ROI) e Ações de Marketing/Vendas.
* **Dores:** Ausência de visão clara de margem líquida (custos vs. receita), devoluções comendo margem, falta de direcionamento para cross-sell/up-sell.
* **Respostas do Projeto:**
  * Identificação precisa dos produtos ofensores (Questão 4) calculando custo de mercadoria (COGS) + devoluções.
  * Segmentação e ranqueamento de clientes VIP por Lucro Acumulado e matriz RFM (Questão 5).
  * Sistema de Recomendação Apriori (Market Basket Analysis em `3_modelagem_preditiva.py`) destacando combinações de maior Lift para a próxima campanha.

### 3. 🛡️ Sr. Almir (Fundador)
* **Perfil:** Foco em Consistência Histórica, Segurança de Estoque, Clareza e Aversão a Riscos.
* **Dores:** Desconfiança de "caixas-pretas" de ML, medo de rupturas de estoque no armazém ou excesso de capital imobilizado, jargões técnicos excessivos.
* **Respostas do Projeto:**
  * Apresentação visual limpa, acessível e sem jargões no Dashboard Executivo (`dashboard_lh_nautical.html`).
  * Cálculo correto de Vendas Médias por Dia da Semana (Questão 6) garantindo imputação de R$ 0 em dias sem faturamento para não inflar médias.
  * Modelo de Previsão de Demanda (Demand Forecasting em Ridge/Moving Average) com tradução financeira direta: *"Previsão de 7 dias = R$ 7.23M em vendas, exigindo R$ 4.34M em estoque"*.

---
*Assinado: Luciano Silva de Arruda*
