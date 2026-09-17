from app.app import db
from app.models.base import TimestampMixin
class Remuneracao(db.Model, TimestampMixin):
    __tablename__ = "remuneracoes"
    id = db.Column(db.Integer, primary_key=True)
    codigo_ibge_municipio = db.Column(db.Integer)  # código IBGE do município
    competencia = db.Column(db.String(7), index=True)
    cpf = db.Column(db.String(11))
    matricula = db.Column(db.String(50))
    nome = db.Column(db.String(150))
    cnpj_lotacao = db.Column(db.String(14), index=True)
    cod_lotacao = db.Column(db.String(50))
    base_previdenciaria = db.Column(db.Float, default=0.0)
