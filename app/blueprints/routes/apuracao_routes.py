from flask import Blueprint, request, jsonify, current_app
from flask_jwt_extended import jwt_required
from app.services.xml_parser import parse_xml_bytes, text
from app import db
import os
import uuid
from werkzeug.utils import secure_filename

# import tables for migrations
from app.models.esocial_s1005_evtTabEstab import ESocialS1005EvtTabEstab
from app.models.esocial_s1010_evtTabRubrica import ESocialS1010EvtTabRubrica
from app.models.esocial_s1200_evtRemun import ESocialS1200EvtRemun
from app.models.esocial_s1202_evtRmnRPPS import ESocialS1202EvtRmnRPPS
from app.models.esocial_s1210_evtPgtos import ESocialS1210EvtPgtos
from app.models.esocial_s5001_evtBasesTrab import ESocialS5001EvtBasesTrab
from app.models.esocial_s5002_evtIrrfBenef import ESocialS5002EvtIrrfBenef
from app.models.esocial_s5011_evtCs import ESocialS5011EvtCs
from app.models.import_skip import ImportSkip
from app.models.municipio import Municipio
from app.models.job import Job, JobFile
from app.services.apuracao_service import _normalize_comp, calcula_cs


bp = Blueprint("apuracao", __name__)

@bp.post('/calcularGilRat')
@jwt_required()
def calcular_gilrat():
    data = request.get_json(force=True) 
    comp_ini = data.get('comp_ini')
    comp_fim = data.get('comp_fim')
    cnpj = data.get('cnpj')
    aliquota = data.get('aliquota')

    # Validate input
    if not comp_ini or not comp_fim or not cnpj:
        return jsonify({"calcular_gilrat error": "comp_ini, comp_fim, and cnpj are required"}), 400

    if aliquota is None or not isinstance(aliquota, (int, float)) or aliquota < 0:
        return jsonify({"calcular_gilrat error": "aliquota is required"}), 400

    try:
        # A tela envia MM-AAAA, enquanto calcula_cs trabalha com YYYY-MM.
        comp_ini = _normalize_comp(comp_ini)
        comp_fim = _normalize_comp(comp_fim)
        resultado = calcula_cs(
            comp_ini=comp_ini,
            comp_fim=comp_fim,
            cnpj=cnpj,
            aliq_rat_corrigida=aliquota,
        )
        return jsonify({"resultado": resultado})
    except Exception as e:
        current_app.logger.error(f"Error calcular_gilrat calculating GIL-RAT: {str(e)}")
        return jsonify({"calcular_gilrat error": str(e)}), 500