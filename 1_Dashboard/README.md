# 📊 Dashboard Executivo - LH Nautical

**Desenvolvido por:** Luciano Silva de Arruda  
**Programa:** Lighthouse (Indicium AI)  

---

## 🖥️ Como Visualizar o Dashboard Interativo

O dashboard executivo foi construído em **HTML5/CSS Glassmorphism** utilizando **Chart.js** para visualizações responsivas e de altíssimo padrão estético.

### Opções de Abertura:
1. **Diretamente no Navegador (Recomendado):**
   * Dê um duplo clique no arquivo `dashboard_lh_nautical.html` ou abra pelo navegador (Chrome, Firefox, Edge, Safari).
   * Caminho local: `/var/home/lucenfort/Workspace/lh_nautical/1_Dashboard/dashboard_lh_nautical.html`

2. **Servidor HTTP Local via Python:**
   ```bash
   cd 1_Dashboard
   python3 -m http.server 8000
   ```
   Acesse no navegador em: `http://localhost:8000/dashboard_lh_nautical.html`

---

## 📌 Conteúdo do Dashboard
- **Cards de KPIs Financeiros:** Receita Bruta, Lucro Líquido, Devoluções e Ticket Médio.
- **Gráfico de Vendas Médias por Dia da Semana (Questão 6):** Média real com imputação de R$ 0 para dias sem venda.
- **Tabela de Produtos Ofensores (Questão 4):** Produtos com menores margens operacionais (%).
- **Gráfico de Top Clientes VIP (Questão 5):** Clientes com maior margem de lucro acumulada.
- **Gráfico de Previsão de Demanda (Demand Forecasting):** Projeção de faturamento para os próximos 7 dias.
- **Caixas de Insights para a Diretoria:** Recomendações personalizadas para Gabriel Santos (Tech Lead), Marina Costa (Negócios) e Sr. Almir (Fundador).
