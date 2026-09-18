from datetime import datetime
from decimal import Decimal
from io import BytesIO

from reportlab.lib import colors
from reportlab.lib.enums import TA_CENTER
from reportlab.lib.pagesizes import A4, landscape
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import mm
from reportlab.platypus import Paragraph, SimpleDocTemplate, Spacer, Table, TableStyle
from app.services.selic_4390_service import Selic4390Service

def _number(value, decimals=2, money=False):
    try:
        number = float(value or 0)
    except (TypeError, ValueError):
        number = 0.0
    formatted = f"{number:,.{decimals}f}".replace(",", "X").replace(".", ",").replace("X", ".")
    return f"R$ {formatted}" if money else formatted


def _percent(value, decimals=4):
    return f"{_number(value, decimals)}%"


def relatorio_rat_resumo_pdf(
    resultado, cnpj=None, municipio=None, mes_inicial=None, mes_final=None
):
    """Gera um PDF em memória com o resultado de ``calcula_cs``."""
    if not isinstance(resultado, dict):
        raise ValueError("O resultado da apuração deve ser um dicionário")

    linhas = resultado.get("por_competencia") or []
    mes_inicial = mes_inicial or (linhas[0].get("competencia") if linhas else None)
    mes_final = mes_final or (linhas[-1].get("competencia") if linhas else None)
    if not mes_inicial:
        raise ValueError("A competência inicial é obrigatória para calcular a SELIC")
    if not mes_final:
        raise ValueError("A competência final é obrigatória para calcular a SELIC")

    mes_final = datetime.now().strftime("%Y-%m")
    selic_service = Selic4390Service()
    selic_service.check_selic_4390_exists(
        mes_inicial=mes_inicial,
        mes_final=mes_final
    )
    selic_values = selic_service.get_selic_4390(
        mes_inicial=mes_inicial, mes_final=mes_final
    )
    selic_acumulada = selic_service.calcular_selic_acumulada_RFB(
        values=selic_values, mes_final=mes_final
    )

    buffer = BytesIO()
    titulo = "Relatório de Apuração SAT/GILRAT"
    
    documento = SimpleDocTemplate(
        buffer,
        pagesize=landscape(A4),
        rightMargin=12 * mm,
        leftMargin=12 * mm,
        topMargin=12 * mm,
        bottomMargin=12 * mm,
        title=titulo,
        author="SAT/GILRAT",
    )
    estilos = getSampleStyleSheet()
    estilo_titulo = ParagraphStyle(
        "Titulo", parent=estilos["Title"], alignment=TA_CENTER, fontSize=16
    )
    elementos = [Paragraph("Chaves & Noronha Advogados Associados", estilos["Heading3"])]
    elementos.append(Paragraph(titulo, estilo_titulo))
    if cnpj:
        elementos.append(Paragraph(f"CNPJ: {cnpj} - {municipio}", estilos["Normal"]))
        elementos.append(Spacer(1, 3 * mm))

    table_style = TableStyle(
                [
                    ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#234b59")),
                    ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),
                    ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
                    ("ALIGN", (0, 0), (-1, 0), "CENTER"),
                    ("ALIGN", (0, 1), (-1, -1), "RIGHT"),
                    ("FONTSIZE", (0, 0), (-1, 0), 10),
                    ("FONTSIZE", (0, 1), (-1, -1), 8),
                    ("LEADING", (0, 0), (-1, 0), 12),
                    ("LEADING", (0, 1), (-1, -1), 9),
                    ("GRID", (0, 0), (-1, -1), 0.35, colors.HexColor("#9aaeb5")),
                    ("ROWBACKGROUNDS", (0, 1), (-1, -1), [colors.white, colors.HexColor("#f1f5f6")]),
                    ("PADDING", (0, 0), (-1, -1), 5),
                ]
            )

    dados = [[
        "Competência",
        "Base Apurada",
        "RAT Aplic.",
        "FAP",
        "Vl.Apurado",
        "RAT Corr.",
        "FAP Corr.",
        "Vl.Corrigido",
        "Crédito",
        "Selic Acum.",
        "Créd. Atz.",
        "Créd. Acum.",
    ]]
    
    cred_acum = 0.0
    
    for linha in linhas:
        competencia = linha.get("competencia")
        base_apurada = linha.get("soma_basesCp", 0.0)
        aliq_rat = linha.get("aliq_rat")
        fap = linha.get("fap")
        aliq_rat_ajustada = float(linha.get("aliq_rat_ajustada") or 0) / 100
        vl_apurado = base_apurada * aliq_rat_ajustada
        aliq_rat_corrigida = linha.get("aliq_rat_corrigida")
        fap_devido = linha.get("fap_devido")
        aliq_rat_corrigida_ajustada = float(linha.get("aliq_rat_corrigida_ajustada") or 0) / 100
        vl_corrigido = base_apurada * aliq_rat_corrigida_ajustada
        credito = vl_apurado - vl_corrigido
        selic = selic_acumulada.get(competencia, 0.00)
        cred_atz = credito * float(selic)/100 + credito
        cred_acum = cred_acum + cred_atz
        
        dados.append([
            competencia,
            _number(base_apurada, money=True),
            _percent(aliq_rat, decimals=2),
            _number(fap, decimals=4),
            _number(vl_apurado, money=True),
            _percent(aliq_rat_corrigida, decimals=2),
            _number(fap_devido, decimals=4),
            _number(vl_corrigido, money=True),
            _number(credito, money=True),
            _percent(selic, decimals=2),
            _number(cred_atz, money=True),
            _number(cred_acum, money=True),
        ])

    total_apurado = resultado.get("total_rat_periodo", 0.0)
    credito_apurado = total_apurado - resultado.get("total_rat_periodo_corrigido", 0.0)

    resumo = [
        f"Total Apurado: {_number(total_apurado, money=True)}",
        f"Indébito Apurado: {_number(credito_apurado, money=True)}",
        f"Indébito Atz.: {_number(cred_acum, money=True)}",
        ]

    resumo_tabela = Table([resumo], colWidths=[60 * mm, 60 * mm, 60 * mm])
    resumo_tabela.setStyle(table_style)
        
    elementos.extend([resumo_tabela, Spacer(1, 6 * mm)])

    tabela = Table(dados, repeatRows=1)
    tabela.setStyle(table_style)

    elementos.append(tabela)
    documento.build(elementos)
    buffer.seek(0)
    return buffer