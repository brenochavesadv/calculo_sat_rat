from io import BytesIO

from reportlab.lib import colors
from reportlab.lib.enums import TA_CENTER
from reportlab.lib.pagesizes import A4, landscape
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import mm
from reportlab.platypus import Paragraph, SimpleDocTemplate, Spacer, Table, TableStyle


def _number(value):
    try:
        return float(value or 0)
    except (TypeError, ValueError):
        return 0.0


def _money(value, decimals=2):
    return f"R$ {_number(value):,.{decimals}f}".replace(",", "X").replace(".", ",").replace("X", ".")


def _percent(value,decimals=4):
    return f"{_number(value):.{decimals}f}%".replace(",", "X").replace(".", ",").replace("X", ".")


def relatorio_rat_resumo_pdf(resultado, cnpj=None, municipio=None):
    """Gera um PDF em memória com o resultado de ``calcula_cs``."""
    if not isinstance(resultado, dict):
        raise ValueError("O resultado da apuração deve ser um dicionário")

    linhas = resultado.get("por_competencia") or []
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

    total_periodo = resultado.get("total_rat_periodo", 0.0)
    total_periodo_corrigido = resultado.get("total_rat_periodo_corrigido", 0.0)
    dif_periodo = total_periodo - total_periodo_corrigido 

    resumo = [
        f"Total Apurado: {_money(total_periodo)}",
        f"Total Corrigido: {_money(total_periodo_corrigido)}",
        f"Diferença: {_money(dif_periodo)}"
        ]
    resumo_tabela = Table([resumo], colWidths=[60 * mm, 60 * mm, 60 * mm])
    resumo_tabela.setStyle(
        TableStyle(
            [
                ("BACKGROUND", (0, 0), (-1, -1), colors.HexColor("#e8f1f5")),
                ("BOX", (0, 0), (-1, -1), 0.5, colors.HexColor("#55717d")),
                ("FONTNAME", (0, 0), (-1, -1), "Helvetica-Bold"),
                ("PADDING", (0, 0), (-1, -1), 6),
            ]
        )
    )
    elementos.extend([resumo_tabela, Spacer(1, 6 * mm)])

    dados = [[
        "Competência",
        "Base Apurada",
        "RAT aplicado",
        "FAP",
        "Vl.Apurado",
        "RAT Corrigido",
        "FAP Corrigido",
        "Vl.Corrigido",
        "Saldo",
    ]]
    for linha in linhas:
        base_apurada = linha.get("soma_basesCp", 0.0)
        aliq_rat = linha.get("aliq_rat")
        fap = linha.get("fap")
        aliq_rat_ajustada = linha.get("aliq_rat_ajustada")/100
        vl_apurado = base_apurada * aliq_rat_ajustada
        aliq_rat_corrigida = linha.get("aliq_rat_corrigida")
        fap_devido = linha.get("fap_devido")
        aliq_rat_corrigida_ajustada = linha.get("aliq_rat_corrigida_ajustada")/100
        vl_corrigido = base_apurada * aliq_rat_corrigida_ajustada
        dif = vl_apurado - vl_corrigido
        
        dados.append([
            linha.get("competencia", ""),
            _money(base_apurada),
            _percent(aliq_rat, decimals=2),
            _money(fap, decimals=4),
            _money(vl_apurado),
            _percent(aliq_rat_corrigida, decimals=2),
            _money(fap_devido, decimals=4),
            _money(vl_corrigido),
            _money(dif),
        ])

    tabela = Table(dados, repeatRows=1)
    tabela.setStyle(
        TableStyle(
            [
                ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#234b59")),
                ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),
                ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
                ("GRID", (0, 0), (-1, -1), 0.35, colors.HexColor("#9aaeb5")),
                ("ROWBACKGROUNDS", (0, 1), (-1, -1), [colors.white, colors.HexColor("#f1f5f6")]),
                ("ALIGN", (1, 1), (-1, -1), "RIGHT"),
                ("PADDING", (0, 0), (-1, -1), 5),
            ]
        )
    )
    elementos.append(tabela)
    documento.build(elementos)
    buffer.seek(0)
    return buffer