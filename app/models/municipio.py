from app.app import db
from app.models.base import TimestampMixin
class Municipio(db.Model, TimestampMixin):
    __tablename__ = "municipios"
    id = db.Column(db.Integer, primary_key=True)
    nome = db.Column(db.String(120), index=True)
    uf = db.Column(db.String(2), index=True)
    cod_ibge = db.Column(db.Integer, unique=True, index=True)
    cod_siafi = db.Column(db.Integer, unique=True, index=True)
    cnpj = db.Column(db.String(14), unique=True, index=True)
