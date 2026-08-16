#!/usr/bin/env python3
"""
===============================================================================
GERADOR DE RELATÓRIO EXECUTIVO EM PDF — DESAFIO LH NAUTICAL (DOSSIÊ COMPLETO)
Processo Seletivo Lighthouse 2026 (Indicium AI)
Autor: Luciano Silva de Arruda
===============================================================================
"""

from pathlib import Path
import sys
from reportlab.lib.pagesizes import letter
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.platypus import (
    SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, Image, PageBreak, HRFlowable, KeepTogether
)
from reportlab.pdfgen import canvas

# Caminhos do Projeto
PROJECT_ROOT = Path(__file__).resolve().parent.parent
PROCESSED_DIR = PROJECT_ROOT / "data" / "processed"
RELATORIOS_DIR = PROJECT_ROOT / "relatorios"
RELATORIOS_DIR.mkdir(parents=True, exist_ok=True)
PDF_FILE = RELATORIOS_DIR / "Relatorio_Executivo_LH_Nautical.pdf"

# Paleta Náutica Corporativa
NAVY = colors.HexColor("#0B2545")
STEEL_BLUE = colors.HexColor("#134074")
LIGHT_BLUE = colors.HexColor("#38BDF8")
DARK_TEXT = colors.HexColor("#1E293B")
MUTED_TEXT = colors.HexColor("#64748B")
BG_CARD = colors.HexColor("#F8FAFC")
BORDER_CARD = colors.HexColor("#CBD5E1")
ACCENT_GREEN = colors.HexColor("#10B981")
ACCENT_RED = colors.HexColor("#EF4444")


class NumberedCanvas(canvas.Canvas):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._saved_page_states = []

    def showPage(self):
        self._saved_page_states.append(dict(self.__dict__))
        self._startPage()

    def save(self):
        num_pages = len(self._saved_page_states)
        for state in self._saved_page_states:
            self.__dict__.update(state)
            self.draw_page_decorations(num_pages)
            super().showPage()
        super().save()

    def draw_page_decorations(self, page_count):
        if self._pageNumber == 1:
            return  # Capa limpa
        
        self.saveState()
        self.setFont("Helvetica", 8)
        self.setFillColor(MUTED_TEXT)
        
        # Cabeçalho Superior
        self.drawString(54, 750, "LH NAUTICAL — RELATÓRIO EXECUTIVO DE INTELIGÊNCIA DE DADOS & IA")
        self.drawRightString(558, 750, "TURMA 10/2026 • INDICIUM AI")
        self.setStrokeColor(colors.HexColor("#E2E8F0"))
        self.setLineWidth(0.5)
        self.line(54, 744, 558, 744)
        
        # Rodapé
        self.line(54, 45, 558, 45)
        self.drawString(54, 32, "Programa Lighthouse 2026 (Indicium AI) | Trilha: Dados e Inteligência Artificial")
        self.drawRightString(558, 32, f"Página {self._pageNumber} de {page_count}")
        self.restoreState()


def construir_pdf():
    doc = SimpleDocTemplate(
        str(PDF_FILE),
        pagesize=letter,
        leftMargin=54,
        rightMargin=54,
        topMargin=54,
        bottomMargin=54
    )
    
    styles = getSampleStyleSheet()
    
    title_style = ParagraphStyle('CoverTitle', parent=styles['Normal'], fontName='Helvetica-Bold', fontSize=22, leading=26, textColor=NAVY, spaceAfter=4)
    subtitle_style = ParagraphStyle('CoverSubtitle', parent=styles['Normal'], fontName='Helvetica', fontSize=11, leading=15, textColor=STEEL_BLUE, spaceAfter=14)
    h1_style = ParagraphStyle('Header1', parent=styles['Heading1'], fontName='Helvetica-Bold', fontSize=12, leading=15, textColor=NAVY, spaceBefore=8, spaceAfter=4, keepWithNext=True)
    h2_style = ParagraphStyle('Header2', parent=styles['Heading2'], fontName='Helvetica-Bold', fontSize=9.5, leading=12.5, textColor=STEEL_BLUE, spaceBefore=5, spaceAfter=2, keepWithNext=True)
    body_style = ParagraphStyle('Body', parent=styles['BodyText'], fontName='Helvetica', fontSize=8.2, leading=11.5, textColor=DARK_TEXT, spaceAfter=4)
    code_style = ParagraphStyle('CodeBox', parent=styles['Normal'], fontName='Courier', fontSize=7.5, leading=9.5, textColor=NAVY)
    
    story = []
    
    # =========================================================================
    # PÁGINA 1: CAPA EXECUTIVA & SUMÁRIO DO PROJETO
    # =========================================================================
    story.append(Spacer(1, 20))
    story.append(Paragraph("⚓ LH NAUTICAL", title_style))
    story.append(Paragraph("Relatório Técnico, Estratégico e Arquitetura de Inteligência de Dados & IA", subtitle_style))
    story.append(HRFlowable(width="100%", thickness=2, color=LIGHT_BLUE, spaceBefore=0, spaceAfter=12))
    
    info_data = [
        [Paragraph("<b>Candidato:</b>", body_style), Paragraph("Luciano Silva de Arruda", body_style)],
        [Paragraph("<b>Processo Seletivo:</b>", body_style), Paragraph("Programa Lighthouse (Turma 10/2026) — Indicium AI", body_style)],
        [Paragraph("<b>Trilha de Especialização:</b>", body_style), Paragraph("Engenharia de Dados, Analytics & Inteligência Artificial", body_style)],
        [Paragraph("<b>Repositório Oficial Git:</b>", body_style), Paragraph("<u>github.com/lucenfort/lh_nautical</u>", body_style)],
        [Paragraph("<b>Dashboard Interativo:</b>", body_style), Paragraph("Streamlit Enterprise Platform (Aplicação Web Executiva)", body_style)],
    ]
    t_info = Table(info_data, colWidths=[140, 364])
    t_info.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,-1), BG_CARD),
        ('PADDING', (0,0), (-1,-1), 4),
        ('BOX', (0,0), (-1,-1), 1, BORDER_CARD),
        ('VALIGN', (0,0), (-1,-1), 'MIDDLE'),
    ]))
    story.append(t_info)
    story.append(Spacer(1, 10))
    
    story.append(Paragraph("<b>Resumo Executivo & Alinhamento com Stakeholders</b>", h2_style))
    story.append(Paragraph(
        "Este documento consolida o ecossistema analítico e preditivo desenvolvido para a <b>LH Nautical</b>, "
        "estruturando 24 entidades relacionais do ERP (433.424 registros totais de 2020 a 2026). A solução atende rigorosamente às "
        "três personas executivas do negócio: ao Tech Lead <b>Gabriel Santos</b>, com pipeline reprodutível, testes automatizados (100% no pytest) "
        "e DDL em Python puro nativo (Q2); à Gerente de Negócios <b>Marina Costa</b>, com inteligência de faturamento, cross-selling no checkout "
        "e retenção de clientes VIP; e ao Fundador <b>Sr. Almir</b>, eliminando vieses de sobrevivência com calendário contínuo e garantindo dimensionamento "
        "de estoque seguro para a temporada de verão.", body_style
    ))
    story.append(Spacer(1, 8))
    
    kpi_table_data = [
        [
            Paragraph("<b>Faturamento Bruto</b><br/><font size=9.5 color='#0B2545'><b>R$ 1,406 Bi</b></font><br/><font size=6.5 color='#64748B'>48.998 pedidos (2020-2026)</font>", body_style),
            Paragraph("<b>Ticket Médio Geral</b><br/><font size=9.5 color='#0B2545'><b>R$ 28.704,99</b></font><br/><font size=6.5 color='#64748B'>Base bruta auditada (Q1.2)</font>", body_style),
            Paragraph("<b>Top 1 Cliente VIP</b><br/><font size=9.5 color='#0B2545'><b>R$ 41.839,94</b></font><br/><font size=6.5 color='#64748B'>Cliente #22 (14 categorias)</font>", body_style),
            Paragraph("<b>Acurácia Demanda</b><br/><font size=9.5 color='#0B2545'><b>19,44 un/mês</b></font><br/><font size=6.5 color='#64748B'>MAE Bússola 702 (Q6)</font>", body_style),
        ]
    ]
    t_kpis = Table(kpi_table_data, colWidths=[126, 126, 126, 126])
    t_kpis.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,-1), colors.HexColor("#EFF6FF")),
        ('BOX', (0,0), (-1,-1), 1, colors.HexColor("#BFDBFE")),
        ('ALIGN', (0,0), (-1,-1), 'CENTER'),
        ('PADDING', (0,0), (-1,-1), 5),
    ]))
    story.append(t_kpis)
    story.append(Spacer(1, 10))

    story.append(Paragraph("<b>Destaques Técnicos da Solução Entregue</b>", h2_style))
    story.append(Paragraph(
        "• <b>Engenharia Pura Standard Lib:</b> Script DDL de inferência em Python 3.12 puro (zero dependência de pandas para schema), gerando PostgreSQL DDL idempotente.<br/>"
        "• <b>Pipeline Medallion & Qualidade:</b> Ingestão validada de 251.864 linhas nas 4 tabelas nucleares sem truncamento de tipos.<br/>"
        "• <b>Dashboard Interativo Streamlit:</b> Plataforma analítica executiva com 5 módulos dinâmicos e filtros reativos contextuais.<br/>"
        "• <b>Testes Automatizados CI/CD:</b> Suíte de testes unitários em <code>pytest</code> cobrindo integridade transacional, ausência de vazamento (*data leakage*) e propriedades matemáticas.",
        body_style
    ))
    story.append(PageBreak())
    
    # =========================================================================
    # PÁGINA 2: ARQUITETURA DO REPOSITÓRIO GIT & ENGENHARIA DE DADOS
    # =========================================================================
    story.append(Paragraph("1. Arquitetura do Repositório Git & Engenharia de Dados", h1_style))
    story.append(Paragraph(
        "O repositório do projeto foi estruturado seguindo as melhores práticas de Engenharia de Software e Data Ops corporativo. "
        "A organização garante total reprodutibilidade através de scripts desacoplados, documentação completa e testes automatizados.",
        body_style
    ))
    
    repo_table_data = [
        [Paragraph("<b>Diretório / Arquivo</b>", body_style), Paragraph("<b>Responsabilidade Técnica & Governança</b>", body_style)],
        [Paragraph("<code>src/1_gerar_schema.py</code>", code_style), Paragraph("Inferência de tipos e geração do <code>schema.sql</code> em <b>Python 3 nativo</b> (PostgreSQL DDL).", body_style)],
        [Paragraph("<code>src/2_carregar_dados.py</code>", code_style), Paragraph("Carga otimizada dos 24 CSVs com validação de <b>251.864 linhas</b> nas 4 tabelas centrais.", body_style)],
        [Paragraph("<code>dashboard/app.py</code>", code_style), Paragraph("Aplicação Streamlit com Design System corporativo, 5 módulos e filtros contextuais reativos.", body_style)],
        [Paragraph("<code>notebooks/*.ipynb</code>", code_style), Paragraph("Jupyter Notebook estruturado como pipeline analítico linear com saídas renderizadas.", body_style)],
        [Paragraph("<code>tests/test_*.py</code>", code_style), Paragraph("Suíte de testes automatizados via <b>pytest</b> (9 testes cobrindo integridade, schema e IA).", body_style)],
        [Paragraph("<code>run_pipeline.sh / Makefile</code>", code_style), Paragraph("Orquestrador end-to-end de execução do pipeline com um único comando.", body_style)],
    ]
    t_repo = Table(repo_table_data, colWidths=[150, 354])
    t_repo.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,0), colors.HexColor("#E2E8F0")),
        ('BACKGROUND', (0,1), (-1,-1), BG_CARD),
        ('GRID', (0,0), (-1,-1), 0.5, BORDER_CARD),
        ('PADDING', (0,0), (-1,-1), 3.5),
        ('VALIGN', (0,0), (-1,-1), 'MIDDLE'),
    ]))
    story.append(t_repo)
    story.append(Spacer(1, 6))

    story.append(Paragraph("<b>Arquitetura Medallion & DDL em Python Puro (Questões 2 e 3)</b>", h2_style))
    story.append(Paragraph(
        "Em estrita conformidade com as regras do edital (que proíbem o uso de pandas/polars para a Questão 2), o script <code>1_gerar_schema.py</code> "
        "utilizou exclusivamente os módulos nativos <code>csv</code>, <code>os</code>, <code>re</code> e <code>pathlib</code>. O algoritmo realiza "
        "amostragem determinística nos arquivos CSV, mapeando tipos de dados rigorosos (<code>INTEGER</code>, <code>NUMERIC(12,2)</code>, "
        "<code>TIMESTAMP</code>, <code>DATE</code>, <code>VARCHAR</code> e <code>BOOLEAN</code>), gerando comandos DDL idempotentes "
        "(<code>DROP TABLE IF EXISTS CASCADE</code> + <code>CREATE TABLE</code>).",
        body_style
    ))
    
    g_pipe = PROCESSED_DIR / "9_arquitetura_pipeline_sql.png"
    if g_pipe.exists():
        story.append(Image(str(g_pipe), width=490, height=140))
        story.append(Spacer(1, 4))
        
    story.append(Paragraph(
        "<b>Auditoria de Ingestão:</b> A soma das linhas das 4 tabelas centrais da transação náutica atingiu com precisão milimétrica o gabarito oficial de "
        "<b>251.864 registros</b> (<code>customers</code>: 2.000 + <code>orders</code>: 48.998 + <code>order_items</code>: 147.320 + <code>payments</code>: 53.546).",
        body_style
    ))
    story.append(PageBreak())

    # =========================================================================
    # PÁGINA 3: PAINEL INTERATIVO STREAMLIT
    # =========================================================================
    story.append(Paragraph("2. Plataforma Executiva de Analytics & IA — Dashboard Streamlit", h1_style))
    story.append(Paragraph(
        "Como <b>Plataforma de Decisão Executiva</b>, foi desenvolvida uma aplicação web interativa em <b>Streamlit</b> "
        "(<code>dashboard/app.py</code>) com Design System corporativo moderno, tipografia <i>Plus Jakarta Sans</i> e tema escuro executivo. "
        "O painel traduz os resultados das consultas SQL e dos modelos preditivos em ferramentas práticas de tomada de decisão.",
        body_style
    ))
    
    dash_modules_data = [
        [Paragraph("<b>Módulo Analítico</b>", body_style), Paragraph("<b>Funcionalidade, Controles & Valor de Negócio</b>", body_style)],
        [
            Paragraph("<b>1. Performance POS & Calendário</b>", body_style),
            Paragraph("Demonstração visual do <b>viés de sobrevivência</b> em lojas físicas. Compara a média real com dias zerados versus a média ingênua. Controles de Ano (2020 a 2026) e Canal (POS vs E-commerce).", body_style)
        ],
        [
            Paragraph("<b>2. Segmentação VIP & LTV</b>", body_style),
            Paragraph("Ranking dos Top 10 Clientes Fiéis e categorias âncora. Possui <b>Slider Interativo de Diversidade (5 a 15 categorias)</b>, permitindo simular a ampliação da base VIP a partir do corte oficial $\\ge 13$.", body_style)
        ],
        [
            Paragraph("<b>3. Demanda & Simulador de Estoque</b>", body_style),
            Paragraph("Série histórica e previsão da <i>Bússola 702</i>. <b>Seletor de Janela Temporal (2M, 3M oficial, 6M)</b> com recálculo do MAE em tempo real e <b>Slider de Buffer de Segurança (± un.)</b> para ordens de compra.", body_style)
        ],
        [
            Paragraph("<b>4. Motor de Recomendação</b>", body_style),
            Paragraph("Algoritmo Item-Item com Similaridade de Cosseno. Seletor de produto alvo, controle de Top-K recomendações e <b>Toggle de Higienização de Catálogo</b> (ocultação de ruídos de teste como 'asdf').", body_style)
        ],
        [
            Paragraph("<b>5. Gestão de Cancelamentos</b>", body_style),
            Paragraph("Auditoria de perdas financeiras (R$ 138,5M) com <b>Alternador de Métrica (Perda Financeira R$ vs Volume de Pedidos)</b> e status travado com badge de segurança em <code>cancelled</code>.", body_style)
        ],
    ]
    t_dash = Table(dash_modules_data, colWidths=[140, 364])
    t_dash.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,0), colors.HexColor("#E2E8F0")),
        ('BACKGROUND', (0,1), (-1,-1), BG_CARD),
        ('GRID', (0,0), (-1,-1), 0.5, BORDER_CARD),
        ('PADDING', (0,0), (-1,-1), 3.5),
        ('VALIGN', (0,0), (-1,-1), 'TOP'),
    ]))
    story.append(t_dash)
    story.append(Spacer(1, 6))

    story.append(Paragraph("<b>Guia Rápido de Execução Local do Dashboard</b>", h2_style))
    story.append(Paragraph(
        "A aplicação é 100% funcional e autônoma. Para executá-la no ambiente local:",
        body_style
    ))
    
    cmd_box_data = [
        [Paragraph(
            "<code>git clone https://github.com/lucenfort/lh_nautical.git<br/>"
            "cd lh_nautical<br/>"
            "python3 -m venv .venv && source .venv/bin/activate<br/>"
            "pip install -r requirements.txt<br/>"
            "streamlit run dashboard/app.py</code>",
            code_style
        )]
    ]
    t_cmd = Table(cmd_box_data, colWidths=[504])
    t_cmd.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,-1), colors.HexColor("#0B1224")),
        ('PADDING', (0,0), (-1,-1), 6),
        ('BOX', (0,0), (-1,-1), 1, STEEL_BLUE),
    ]))
    story.append(t_cmd)
    story.append(PageBreak())

    # =========================================================================
    # PÁGINA 4: AUDITORIA EDA & GOVERNANÇA TRANSACIONAL (QUESTÃO 1)
    # =========================================================================
    story.append(Paragraph("3. Auditoria da Base Transacional & EDA (Questão 1)", h1_style))
    story.append(Paragraph(
        "A Análise Exploratória de Dados sobre os 48.998 registros brutos da tabela <code>orders</code> (2020 a 2026) revelou que o valor "
        "médio exato da coluna <code>total</code> é de <b>R$ 28.704,99</b> (amplitude de R$ 32,62 a R$ 127.262,02).",
        body_style
    ))
    story.append(Paragraph(
        "<b>Detecção de Outliers via IQR:</b> Com primeiro quartil $Q_1 = R\\$ 1.954,12$ e terceiro quartil $Q_3 = R\\$ 34.212,07$ ($IQR = R\\$ 32.257,95$), "
        "o limite superior de corte foi calculado em $Q_3 + 1,5 \\times IQR = \\mathbf{R\\$ 82.598,99}$. Foram identificados <b>452 pedidos atípicos</b> (0,92% da base), "
        "os quais representam transações comerciais legítimas de motores de alta cilindrada e embarcações náuticas, devendo ser mantidos na base.",
        body_style
    ))
    
    g1_p = PROCESSED_DIR / "1_eda_distribuicao_pedidos.png"
    if g1_p.exists():
        story.append(Image(str(g1_p), width=490, height=185))
        story.append(Spacer(1, 4))
        
    story.append(Paragraph(
        "<b>Governança de Nulos e Prontidão da Base:</b> 49,2% dos pedidos possuem <code>salesperson_id</code> nulo. O cruzamento dimensional comprovou "
        "que isso não é falha de captura, mas sim característica de negócio: 70,1% das compras ocorrem no canal E-commerce (autoatendimento sem comissionamento). "
        "A base bruta é inapta para cômputo contábil direto sem o filtro <code>status = 'paid'</code>, que expurga 4.847 cancelamentos e 4.908 rascunhos.",
        body_style
    ))
    
    g2_p = PROCESSED_DIR / "2_canais_e_status_pedidos.png"
    if g2_p.exists():
        story.append(Image(str(g2_p), width=490, height=175))
        story.append(Spacer(1, 4))
        
    story.append(PageBreak())

    # =========================================================================
    # PÁGINA 5: MODELAGEM RELACIONAL & CLIENTES VIP (QUESTÃO 4)
    # =========================================================================
    story.append(Paragraph("4. Segmentação de Clientes VIP & Afinidade de Categorias (Questão 4)", h1_style))
    story.append(Paragraph(
        "<b>Prevenção do Efeito Fan-Out em SQL:</b> A consulta para apuração de clientes de alto valor exige separação rigorosa de grãos dimensionais. "
        "A junção prévia de <code>orders</code> com <code>order_items</code> duplica o faturamento de cada pedido pelo número de itens (inflação de até 300%). "
        "A arquitetura SQL desenvolvida utiliza Common Table Expressions (CTEs) isoladas: uma para agregar receita estritamente no grão de pedido e outra para "
        "contabilizar a diversidade de categorias no grão de produto.",
        body_style
    ))
    story.append(Paragraph(
        "<b>Top 10 Clientes Fiéis:</b> Aplicando o filtro de elite de diversidade ($\\ge 13$ categorias distintas) e ordenando por Ticket Médio, o líder absoluto é o "
        "<b>Customer #22 (Ticket Médio: R$ 41.839,94 | 26 pedidos | 14 categorias)</b>.",
        body_style
    ))
    
    g3_p = PROCESSED_DIR / "3_top10_clientes_fieis_ticket_medio.png"
    if g3_p.exists():
        story.append(Image(str(g3_p), width=490, height=185))
        story.append(Spacer(1, 4))
        
    story.append(Paragraph(
        "<b>Categoria Líder de Recompra:</b> Ao cruzar os itens adquiridos exclusivamente por esses 10 clientes de elite, a categoria <b>Hélices</b> lidera "
        "com folga, totalizando <b>492 unidades compradas</b> (seguida por Tintas e Âncoras), demonstrando que peças de propulsão e manutenção formam a âncora de retenção VIP.",
        body_style
    ))
    
    g4_p = PROCESSED_DIR / "4_top_categorias_compradas_vip.png"
    if g4_p.exists():
        story.append(Image(str(g4_p), width=490, height=185))
        story.append(Spacer(1, 4))
        
    story.append(PageBreak())

    # =========================================================================
    # PÁGINA 6: OPERAÇÃO DE LOJAS FÍSICAS & PREVISÃO DE DEMANDA (QUESTÕES 5 E 6)
    # =========================================================================
    story.append(Paragraph("5. Performance POS & Previsão de Demanda (Questões 5 e 6)", h1_style))
    story.append(Paragraph(
        "<b>Eliminação do Viés de Sobrevivência (Questão 5):</b> O agrupamento simples de vendas em lojas físicas (<code>channel = 'pos'</code>) ignora dias sem vendas, "
        "inflacionando artificialmente as médias diárias em 26,2%. Com a criação de uma <b>Dimensão de Calendário Contínua (2020 a 2026)</b> via <code>GENERATE_SERIES</code> "
        "e junção <code>LEFT JOIN</code> com <code>COALESCE(total, 0)</code>, comprovou-se que a <b>Quinta-feira</b> é o pior dia real (média de <b>R$ 157.154,32/dia</b>), "
        "enquanto a Quarta-feira lidera (R$ 173.605,44/dia).",
        body_style
    ))
    
    g5_p = PROCESSED_DIR / "5_vendas_pos_calendario_vies.png"
    if g5_p.exists():
        story.append(Image(str(g5_p), width=490, height=185))
        story.append(Spacer(1, 4))
        
    story.append(Paragraph(
        "<b>Previsão de Demanda & Anti-Leakage (Questão 6):</b> Modelagem da demanda mensal da <i>Bússola de Bordo 702</i>. Para prevenir o vazamento de dados (*data leakage*), "
        "a Média Móvel de 3 Meses utilizou defasagem obrigatória <code>shift(1)</code>. A previsão acumulada para o 1º Trimestre de 2026 totalizou <b>149 unidades</b> "
        "(Jan: 38,67 $\\rightarrow$ 39 un, Fev: 53,67 $\\rightarrow$ 54 un, Mar: 56,33 $\\rightarrow$ 56 un). O <b>MAE de 19,44 un/mês</b> (impacto de <b>R$ 41.265,44/mês</b>) "
        "evidencia o atraso do modelo em responder à sazonalidade de verão, justificando a criação de um buffer de segurança de estoque.",
        body_style
    ))
    
    g6_p = PROCESSED_DIR / "6_previsao_demanda_bussola_702.png"
    if g6_p.exists():
        story.append(Image(str(g6_p), width=490, height=185))
        story.append(Spacer(1, 4))
        
    story.append(PageBreak())

    # =========================================================================
    # PÁGINA 7: INTELIGÊNCIA ARTIFICIAL, AUDITORIA & MATRIZ ESTRATÉGICA (Q7 & SÍNTESE)
    # =========================================================================
    story.append(Paragraph("6. Inteligência Artificial, Cancelamentos & Matriz de Decisão", h1_style))
    story.append(Paragraph(
        "<b>Motor de Recomendação Item-Item (Questão 7):</b> Vetorização da matriz binária de incidência Cliente $\\times$ Produto ($2.000 \\times 496$) e cômputo da "
        "<b>Similaridade de Cosseno</b>. Para o <i>Motor de Popa 1949</i>, o item líder na base bruta é o ruído cadastral <code>asdf</code> (cosseno 0.2789), enquanto no catálogo "
        "comercial higienizado o produto de maior afinidade de compra conjunta é o <b>Motor de Popa 5331 (0.2566 | 25,66%)</b> seguido por <b>Cabo Náutico 2105 (0.2105 | 21,05%)</b>.",
        body_style
    ))
    
    g7_p = PROCESSED_DIR / "7_recomendacao_produtos_motor_1949.png"
    if g7_p.exists():
        story.append(Image(str(g7_p), width=490, height=175))
        story.append(Spacer(1, 4))
        
    story.append(Paragraph(
        "<b>Auditoria de Cancelamentos:</b> Identificados 4.847 pedidos cancelados (9,9% da base), representando <b>R$ 138,5 Milhões</b> em perda potencial de receita bruta "
        "(liderados pelas categorias Motores e Embarcações).",
        body_style
    ))
    story.append(Spacer(1, 4))

    story.append(Paragraph("<b>Matriz de Decisão Estratégica para Stakeholders</b>", h2_style))
    
    stakeholder_data = [
        [Paragraph("<b>Stakeholder</b>", body_style), Paragraph("<b>Foco de Decisão & Plano de Ação Estratégico</b>", body_style)],
        [
            Paragraph("👨‍💻 <b>Gabriel Santos</b><br/><font size=7 color='#64748B'>Tech Lead</font>", body_style),
            Paragraph("Homologar o pipeline Medallion automatizado com CI/CD, DDL PostgreSQL nativo em Python puro e regras de qualidade de dados na camada Silver para expurgar itens de teste ('asdf').", body_style)
        ],
        [
            Paragraph("👩‍💼 <b>Marina Costa</b><br/><font size=7 color='#64748B'>Gerente Negócios</font>", body_style),
            Paragraph("Ativar o motor de recomendação no checkout do e-commerce (+18% de conversão cruzada) e lançar programa de fidelidade corporativo ancorado na categoria Hélices para clientes de R$ 41k de ticket.", body_style)
        ],
        [
            Paragraph("👨‍🌾 <b>Sr. Almir</b><br/><font size=7 color='#64748B'>Fundador</font>", body_style),
            Paragraph("Reduzir a escala de atendentes presenciais nas quintas-feiras em favor dos fins de semana e autorizar ordem de compra antecipada em outubro com buffer de segurança de 19 unidades no verão.", body_style)
        ],
    ]
    t_stake = Table(stakeholder_data, colWidths=[120, 384])
    t_stake.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,0), colors.HexColor("#E2E8F0")),
        ('BACKGROUND', (0,1), (-1,-1), BG_CARD),
        ('GRID', (0,0), (-1,-1), 0.5, BORDER_CARD),
        ('PADDING', (0,0), (-1,-1), 3.5),
        ('VALIGN', (0,0), (-1,-1), 'TOP'),
    ]))
    story.append(t_stake)
    
    doc.build(story, canvasmaker=NumberedCanvas)
    print(f"✅ Relatório Executivo em PDF consolidado com sucesso em: {PDF_FILE}")


if __name__ == "__main__":
    construir_pdf()
