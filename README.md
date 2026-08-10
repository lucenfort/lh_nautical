# ⚓ Desafio LH Nautical - Estrutura do Projeto

**Desenvolvedor:** Luciano Silva de Arruda  
**Programa:** Lighthouse (Indicium AI)  

---

## 🎯 Sobre este Repositório

Este repositório contém a resolução técnica completa, modularizada e reproduzível desenvolvida para o **Desafio LH Nautical**, integrante do processo seletivo do **Programa Lighthouse (Indicium AI)**.

---

## 📜 Créditos e Isenção de Responsabilidade

> **📌 Nota de Propriedade Intelectual & Créditos:**  
> Este projeto foi desenvolvido por **Luciano Silva de Arruda** como solução técnica para o Desafio Prático do **Programa Lighthouse 2026** promovido pela **Indicium AI** ([https://indicium.ai](https://indicium.ai)).  
> Todos os direitos sobre os datasets brutos (`data/raw/`) e sobre a formulação dos estudos de caso pertencem originalmente à **Indicium AI**. A disponibilização dos arquivos neste repositório tem fins exclusivamente educacionais, de portfólio e de avaliação pública da resolução técnica.

---

## 📁 Estrutura de Diretórios e Arquivos

```
lh_nautical/
├── README.md                              # Documentação principal e guia de desenvolvimento
├── requirements.txt                        # Arquivo para dependências do projeto Python
├── 1_Dashboard/                            # Camada de Visualização Executiva
│   ├── dashboard_lh_nautical.html          # Template HTML do Dashboard Executivo
│   └── README.md                           # Instruções para configuração e exibição do Dashboard
├── 2_Documentacao/                         # Documentação e Relatórios
│   ├── relatorio_tecnico_executivo.md      # Modelo de Relatório Técnico/Executivo
│   ├── der_modelo_dados.mermaid            # Diagrama Entidade-Relacionamento (DER)
│   └── mapa_stakeholders.md                # Diretrizes de alinhamento com a diretoria
├── 3_Codigos_e_Scripts/                    # Scripts de Desenvolvimento
│   ├── 1_ingestao_e_limpeza.py             # Script para ingestão, tratamento e carga no BD
│   ├── 2_analise_e_sql.sql                 # Queries SQL para respostas de negócio (Q4, Q5, Q6)
│   └── 3_modelagem_preditiva.py            # Scripts de Ciência de Dados e IA (Demanda & Recomendações)
└── data/                                   # Diretório de Armazenamento de Dados
    ├── raw/                                # Arquivos CSV brutos (extraídos de 1-lh_nautical_csv.zip)
    └── processed/                          # Diretório reservado para o banco de dados gerado (.db)
```

---

## 🛠️ Passo a Passo para Desenvolvimento

1. **Instalação das Dependências:**
   Adicione as bibliotecas necessárias em `requirements.txt` e instale no ambiente virtual:
   ```bash
   python3 -m venv .venv
   source .venv/bin/activate
   pip install -r requirements.txt
   ```

2. **Ingestão e Tratamento de Dados:**
   Implemente a lógica de leitura dos CSVs da pasta `data/raw/` e geração da base tratada em `3_Codigos_e_Scripts/1_ingestao_e_limpeza.py`.

3. **Consultas SQL e Analytics:**
   Desenvolva as queries em `3_Codigos_e_Scripts/2_analise_e_sql.sql` utilizando CTEs (`WITH ... AS`).

4. **Modelagem Preditiva (IA):**
   Crie os modelos em `3_Codigos_e_Scripts/3_modelagem_preditiva.py`.

5. **Preenchimento dos Relatórios e Dashboard:**
   Preencha `2_Documentacao/relatorio_tecnico_executivo.md` e monte as visualizações em `1_Dashboard/dashboard_lh_nautical.html`.
