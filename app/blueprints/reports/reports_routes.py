from flask import Blueprint, jsonify, request, send_file
from flask_jwt_extended import jwt_required

from app.models.municipio import Municipio
from .apuracao_rat_reports import relatorio_rat_resumo_pdf


bp = Blueprint("reports", __name__)


@bp.post("/apuracao/pdf")
@jwt_required()
def relatorio_apuracao_pdf():
    payload = request.get_json(silent=True) or {}
    resultado = payload.get("resultado", payload)
    cnpj = payload.get("cnpj")
    municipio = payload.get("municipio") or payload.get("municipio_nome")
    if not municipio and cnpj:
        municipio_obj = Municipio.query.filter_by(cnpj=cnpj).first()
        municipio = municipio_obj.nome if municipio_obj else None

    try:
        pdf = relatorio_rat_resumo_pdf(resultado, cnpj=cnpj, municipio=municipio)
    except ValueError as error:
        return jsonify({"error": str(error)}), 400

    return send_file(
        pdf,
        mimetype="application/pdf",
        as_attachment=True,
        download_name="relatorio_apuracao_sat_gilrat.pdf",
    )