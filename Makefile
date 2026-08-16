# =============================================================================
# MAKEFILE — AUTOMATION & MLOPS PIPELINE
# Desafio LH Nautical — Lighthouse 2026 (Indicium AI)
# Autor: Luciano Silva de Arruda
# =============================================================================

.PHONY: all audit schema load models charts test dashboard clean help

all: audit schema load models charts test
	@echo "🎉 Pipeline executado com 100% de sucesso!"

help:
	@echo "Comandos disponíveis:"
	@echo "  make all        - Executa o pipeline completo de ponta a ponta"
	@echo "  make audit      - Executa a auditoria dos dados e análise exploratória"
	@echo "  make schema     - Gera o schema DDL PostgreSQL em Python puro"
	@echo "  make load       - Ingestão das tabelas no Data Warehouse"
	@echo "  make models     - Executa o modelo de demanda e motor de recomendação"
	@echo "  make charts     - Gera os 7 gráficos oficiais em 300 DPI"
	@echo "  make test       - Roda a suíte de testes automatizados com pytest"
	@echo "  make dashboard  - Inicia o Dashboard interativo Streamlit"
	@echo "  make clean      - Limpa arquivos temporários e caches de teste"

audit:
	@echo "▶ Executando auditoria e EDA..."
	python3 src/0_eda_orders.py

schema:
	@echo "▶ Gerando schema DDL PostgreSQL em Python puro..."
	python3 src/1_gerar_schema.py

load:
	@echo "▶ Ingerindo dados no Data Warehouse..."
	python3 src/2_carregar_dados.py

models:
	@echo "▶ Treinando e executando modelos analíticos..."
	python3 src/4_modelo_demanda.py
	python3 src/5_sistema_recomendacao.py

charts:
	@echo "▶ Gerando os 7 gráficos analíticos e os 2 diagramas arquiteturais (300 DPI)..."
	python3 src/gerar_todos_graficos.py
	python3 src/gerar_diagramas_sql.py

test:
	@echo "▶ Executando suíte de testes unitários..."
	pytest -v

dashboard:
	@echo "▶ Iniciando Dashboard Streamlit..."
	streamlit run dashboard/app.py

clean:
	@echo "▶ Limpando caches temporários..."
	rm -rf .pytest_cache tests/__pycache__ src/__pycache__
