# 🧭 Guia de Avaliação & Execução — LH Nautical (Dados & IA)

**Programa Lighthouse 2026 (Indicium AI Academy)**  
**Candidato:** Luciano Silva de Arruda  
**Repositório Oficial:** [https://github.com/lucenfort/lh_nautical](https://github.com/lucenfort/lh_nautical)  

---

## 📌 1. Visão Geral da Entrega

Este pacote consolida a resolução completa do **Desafio Técnico LH Nautical**, cobrindo desde a auditoria transacional e engenharia de dados em baixo nível até a modelagem estatística preditiva, inteligência artificial aplicada e visualização executiva de dados.

### 🌟 Principais Artefatos Disponibilizados:
1. **Dashboard Interativo (Streamlit):** Interface analítica com 5 módulos executivos (`dashboard/app.py`).
2. **Relatório Executivo Oficial (PDF):** Documento formal com 16 páginas, 7 gráficos em 300 DPI e fundamentação teórica (`relatorios/Relatorio_Executivo_LH_Nautical.pdf`).
3. **Jupyter Notebook Comentado:** Caderno de dados 100% executado e documentado de ponta a ponta (`notebooks/analise_e_modelagem_lh_nautical.ipynb`).
4. **Scripts Modulares & Consultas SQL:** Implementação desacoplada das questões do desafio em `src/` e `sql/`.
5. **Suíte de Testes Automatizados:** 14 testes unitários e de integração no **Pytest** com 100% de aprovação (`tests/`).

---

## 🌳 2. Estrutura de Diretórios do Pacote `.zip`

```text
lh_nautical/
├── 📄 guia.md                            # Este manual de avaliação e execução rápida
├── 📄 README.md                          # Visão geral, arquitetura e contextualização de negócio
├── 📄 requirements.txt                   # Dependências do projeto com versões fixadas
├── 📄 Makefile                           # Automação de setup, testes, pipelines e dashboard
├── 📄 run_pipeline.sh                    # Script orquestrador Bash de execução completa
├── 📄 .gitignore                         # Higienização de arquivos de ambiente e cache
│
├── 📁 dashboard/                         # [Campo 20 — Material Obrigatório]
│   ├── 📄 app.py                         # Aplicação Streamlit com os 5 módulos executivos
│   └── 📄 README.md                      # Manual de uso e arquitetura da interface visual
│
├── 📁 relatorios/                        # [Material Complementar — Nível Executivo]
│   └── 📄 Relatorio_Executivo_LH_Nautical.pdf # Relatório Executivo Oficial (16 páginas em 300 DPI)
│
├── 📁 notebooks/                         # [Material Complementar — Data Science & Analytics]
│   └── 📄 analise_e_modelagem_lh_nautical.ipynb # Caderno Jupyter com análises e visualizações
│
├── 📁 src/                               # Scripts Python do Pipeline e Modelagem
│   ├── 📄 0_eda_orders.py                # Script de auditoria inicial dos CSVs brutos
│   ├── 📄 1_gerar_schema.py              # [Q2.1] Inferência DDL PostgreSQL (Python Puro Nativo)
│   ├── 📄 2_carregar_dados.py            # [Q3.1] Ingestão em lote e carga relacional (24 tabelas)
│   ├── 📄 4_modelo_demanda.py            # [Q6.1] Média Móvel 3M com shift(1) anti-leakage e MAE
│   ├── 📄 5_sistema_recomendacao.py      # [Q7.1] Motor de Recomendação Item-Item por Cosseno
│   ├── 📄 gerar_todos_graficos.py        # Compilador das 7 figuras em alta resolução 300 DPI
│   ├── 📄 gerar_diagramas_sql.py         # Gerador do diagrama de arquitetura do pipeline
│   ├── 📄 gerar_erd_graphviz.py          # Gerador do Diagrama de Entidade-Relacionamento
│   ├── 📄 gerar_notebook.py              # Compilador programático do Jupyter Notebook
│   └── 📄 gerar_relatorio_pdf.py         # Orquestrador de compilação
│
├── 📁 sql/                               # Consultas Analíticas e Definição de Schema
│   ├── 📄 schema.sql                     # [Q2.2] DDL PostgreSQL inferido das 24 tabelas
│   ├── 📄 3_analise_sql.sql              # Consolidação de todas as consultas analíticas
│   ├── 📄 q1_eda_orders.sql              # [Q1.1] Consulta de EDA na tabela orders
│   ├── 📄 q4_clientes_fieis.sql          # [Q4.1] CTEs de Clientes VIP e categoria líder
│   └── 📄 q5_calendario_pos.sql          # [Q5.1] Dimensão de Calendário Contínua e vendas POS
│
├── 📁 tests/                             # Suíte de Testes Automatizados (Pytest)
│   ├── 📄 conftest.py                    # Fixtures e configurações do Pytest
│   ├── 📄 test_schema_generation.py      # Teste de conformidade de bibliotecas nativas
│   ├── 📄 test_data_integrity.py         # Teste de volumetria (251.864 registros nucleares)
│   ├── 📄 test_models_and_analytics.py   # Teste das métricas dos modelos (MAE 19,44 e Cosseno)
│   └── 📄 test_dashboard.py              # Teste unitário e de integração do Dashboard
│
├── 📁 data/                              # Dados do Projeto
│   ├── 📁 raw/                           # Os 24 arquivos CSV brutos fornecidos do ERP
│   │   ├── addresses.csv, attributes.csv, brands.csv, categories.csv, customers.csv, ...
│   └── 📁 processed/                     # Figuras em 300 DPI e diagramas relacionais gerados
│
└── 📁 assets/
    └── 📄 banner.svg                     # Identidade visual e banner do projeto
```

---

## 🚀 3. Instruções Rápidas de Execução para os Avaliadores

O projeto é 100% autocontido e reproduzível em ambientes Linux, macOS e Windows.

### ⚙️ Passo 1: Preparação do Ambiente Virtual
No terminal, descompacte o arquivo `.zip` e acesse a pasta raiz:
```bash
# Criar e ativar o ambiente virtual Python (versão 3.10 ou superior recomendada)
python3 -m venv .venv
source .venv/bin/activate  # No Windows: .venv\Scripts\activate

# Instalar as dependências do projeto
pip install -r requirements.txt
```
*(Ou utilize o comando rápido: `make setup`)*

---

### 🧪 Passo 2: Executar a Suíte de Testes Automatizados
Para verificar a integridade do código, restrições do edital e validações matemáticas:
```bash
pytest -v
```
*(Ou utilize: `make test` — resultado esperado: **14 testes aprovados**)*

---

### ⚡ Passo 3: Executar o Pipeline de Dados Ponta a Ponta
Para reexecutar a inferência de schema, carga dos dados, modelos de IA e geração de gráficos:
```bash
bash run_pipeline.sh
```
*(Ou utilize: `make run`)*

---

### 📊 Passo 4: Inicializar o Dashboard Interativo (Streamlit)
Para abrir a interface visual interativa no navegador:
```bash
streamlit run dashboard/app.py
```
*(Ou utilize: `make dashboard`)*  
O dashboard será aberto automaticamente em `http://localhost:8501`.

---

## 🎯 4. Mapeamento dos Arquivos por Questão do Desafio

| Questão do Desafio | Descrição Técnica | Arquivo de Código | Saída / Validação |
| :--- | :--- | :--- | :--- |
| **Questão 1 (EDA)** | Análise exploratória sobre `orders.csv` | [`sql/q1_eda_orders.sql`](file:///home/lucenfort/Workspace/desafio_lh_nautical/lh_nautical/sql/q1_eda_orders.sql) | Média `28704.99`, 452 outliers em IQR e 49,2% de nulos explicados pelo E-commerce. |
| **Questão 2 (Schema)** | Inferência DDL PostgreSQL em **Python Puro** | [`src/1_gerar_schema.py`](file:///home/lucenfort/Workspace/desafio_lh_nautical/lh_nautical/src/1_gerar_schema.py) | Arquivo [`sql/schema.sql`](file:///home/lucenfort/Workspace/desafio_lh_nautical/lh_nautical/sql/schema.sql) com as 24 tabelas tipadas. |
| **Questão 3 (Carga)** | Ingestão e carga massiva dos 24 CSVs | [`src/2_carregar_dados.py`](file:///home/lucenfort/Workspace/desafio_lh_nautical/lh_nautical/src/2_carregar_dados.py) | Validação exata de **`251864` registros** somados nas 4 tabelas centrais. |
| **Questão 4 (Clientes VIP)** | CTEs de Ticket Médio e Diversidade $\ge 13$ | [`sql/q4_clientes_fieis.sql`](file:///home/lucenfort/Workspace/desafio_lh_nautical/lh_nautical/sql/q4_clientes_fieis.sql) | Top 1 Cliente \#22 (R\$ 41,8k) e Categoria **Hélices** líder (492 unidades). |
| **Questão 5 (Calendário POS)**| Dimensão de datas contínua (`GENERATE_SERIES`) | [`sql/q5_calendario_pos.sql`](file:///home/lucenfort/Workspace/desafio_lh_nautical/lh_nautical/sql/q5_calendario_pos.sql) | Prova do viés de sobrevivência: **Quinta-feira** é o pior dia real (R\$ 157.154,32). |
| **Questão 6 (Previsão)** | Média Móvel 3M com `shift(1)` sem leakage | [`src/4_modelo_demanda.py`](file:///home/lucenfort/Workspace/desafio_lh_nautical/lh_nautical/src/4_modelo_demanda.py) | Previsão no 1º Tri/2026: **`149` unidades** \| MAE: **19,44 un/mês**. |
| **Questão 7 (Recomendação)** | Filtragem Colaborativa Item-Item por Cosseno | [`src/5_sistema_recomendacao.py`](file:///home/lucenfort/Workspace/desafio_lh_nautical/lh_nautical/src/5_sistema_recomendacao.py) | Top 1 Bruto: `asdf` (0.2789) \| Top 1 Comercial: **Motor de Popa 5331** (0.2566). |
| **Campo 20 (Dashboard)** | Painel interativo com 5 visuais executivos | [`dashboard/app.py`](file:///home/lucenfort/Workspace/desafio_lh_nautical/lh_nautical/dashboard/app.py) | Interface web em Streamlit com simulação de estoque e motor interativo. |

---

## 🛡️ 5. Destaques de Governança & Boas Práticas de Engenharia

* **Restrição Estrita de Bibliotecas (Q2):** O script `1_gerar_schema.py` não importa `pandas`, `polars` ou `dask`. Foi desenvolvido exclusivamente com módulos da *standard library* (`csv`, `os`, `re`, `datetime`).
* **Prevenção do Efeito Fan-Out (Q4):** As agregações financeiras e a contagem de categorias foram separadas em CTEs com granularidades distintas, impedindo a triplicação indevida da receita em junções relacionais.
* **Blindagem Temporal Anti-Leakage (Q6):** Aplicação obrigatória de `shift(1)` antes do cálculo da média móvel, garantindo que previsões futuras utilizem estritamente dados anteriores.
* **Diagnóstico de Governança de Dados (Q7):** Identificação e tratamento de ruídos cadastrais de teste (`asdf`), com implementação de filtros na camada de analytics e no dashboard.
