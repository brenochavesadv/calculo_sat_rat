from app.app import db
from app.models.base import TimestampMixin
class Contribuicao(db.Model, TimestampMixin):
    __tablename__ = "contribuicoes"
    id = db.Column(db.Integer, primary_key=True)
    codigo_ibge_municipio = db.Column(db.Integer)  # código IBGE do município
    per_apur = db.Column(db.String(7), index=True)
    cpf_trab = db.Column(db.String(11), index=True)
    vr_cp_seg = db.Column(db.Float)
    vr_rat = db.Column(db.Float)
    vr_senar = db.Column(db.Float)
