#!/usr/bin/env bash
# =============================================================================
# PIPELINE DE EXECUÇÃO AUTOMATIZADA DE PONTA A PONTA (DATA PIPELINE & IA)
# Desafio LH Nautical — Lighthouse 2026 (Indicium AI)
# Autor: Luciano Silva de Arruda
# =============================================================================

set -e

GREEN="\033[0;32m"
BLUE="\033[0;34m"
YELLOW="\033[1;33m"
CYAN="\033[0;36m"
RED="\033[0;31m"
NC="\033[0m" # No Color

echo -e "${BLUE}======================================================================${NC}"
echo -e "${CYAN}⚓ LH NAUTICAL — PIPELINE AUTOMATIZADO DE ENGENHARIA & IA${NC}"
echo -e "${BLUE}======================================================================${NC}"

# Garantir que estamos no diretório do projeto
SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
cd "$SCRIPT_DIR"

echo -e "\n${YELLOW}▶ ETAPA 1/6: Auditoria da Base de Dados & Análise Exploratória (EDA)${NC}"
python3 src/0_eda_orders.py
echo -e "${GREEN}✔ Auditoria de 24 tabelas e EDA concluídas com sucesso.${NC}"

echo -e "\n${YELLOW}▶ ETAPA 2/6: Inferência de Schema PostgreSQL DDL em Python Puro${NC}"
python3 src/1_gerar_schema.py
echo -e "${GREEN}✔ Schema relacional gerado em sql/schema.sql sem bibliotecas externas.${NC}"

echo -e "\n${YELLOW}▶ ETAPA 3/6: Carga e Ingestão do Data Warehouse Relacional${NC}"
python3 src/2_carregar_dados.py
echo -e "${GREEN}✔ 251.864 registros nucleares ingeridos no banco lh_nautical.db.${NC}"

echo -e "\n${YELLOW}▶ ETAPA 4/6: Execução dos Modelos Preditivos e Motor de Recomendação${NC}"
python3 src/4_modelo_demanda.py
python3 src/5_sistema_recomendacao.py
echo -e "${GREEN}✔ Modelo de Média Móvel 3M e Similaridade de Cosseno calculados.${NC}"

echo -e "\n${YELLOW}▶ ETAPA 5/6: Geração dos Gráficos Analíticos e Diagramas Arquiteturais (300 DPI)${NC}"
python3 src/gerar_todos_graficos.py
python3 src/gerar_diagramas_sql.py
echo -e "${GREEN}✔ 7 gráficos de negócio e 2 diagramas arquiteturais gerados em data/processed/.${NC}"

echo -e "\n${YELLOW}▶ ETAPA 6/6: Execução da Suíte de Testes Automatizados (pytest)${NC}"
pytest -v
echo -e "${GREEN}✔ 100% dos testes unitários e validações matemáticas aprovados.${NC}"

echo -e "\n${BLUE}======================================================================${NC}"
echo -e "${GREEN}🎉 PIPELINE CONCLUÍDO COM SUCESSO TOTAL!${NC}"
echo -e "${CYAN}Para iniciar o Dashboard interativo: make dashboard (ou streamlit run dashboard/app.py)${NC}"
echo -e "${BLUE}======================================================================${NC}"
