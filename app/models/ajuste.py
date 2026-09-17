from app.app import db
from app.models.base import TimestampMixin
class Ajuste(db.Model, TimestampMixin):
    __tablename__ = "ajustes"
    id = db.Column(db.Integer, primary_key=True)
    codigo_ibge_municipio = db.Column(db.Integer)  # código IBGE do município
    per_apur = db.Column(db.String(7), index=True)
    cpf_trab = db.Column(db.String(11), index=True)
    tp_valor = db.Column(db.String(20))
    vr_cp_seg = db.Column(db.Float)
