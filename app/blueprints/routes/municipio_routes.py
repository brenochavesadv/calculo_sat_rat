from flask import Blueprint
from flask_jwt_extended import jwt_required
from app import db
from app.models.municipio import Municipio

bp = Blueprint("municipios", __name__)

@bp.get('/list')
@jwt_required()
def list_municipios():
    # Return a JSON list of municipios to populate UI controls
    ms = Municipio.query.order_by(Municipio.nome).all()
    out = []
    for m in ms:
        out.append({
            'id': m.id,
            'nome': m.nome,
            'uf': m.uf,
            'cod_ibge': m.cod_ibge,
            'cnpj': m.cnpj
        })
    return {'municipios': out}
