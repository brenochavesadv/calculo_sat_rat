from app.app import db
from app.models.base import TimestampMixin
class BaseApurada(db.Model, TimestampMixin):
    __tablename__ = "bases_apuradas"
    id = db.Column(db.Integer, primary_key=True)
    nrInsc = db.Column(db.String(14), nullable=False)  # número de inscrição do empregador
    per_apur = db.Column(db.String(7), index=True)
    cpf_trab = db.Column(db.String(11), index=True)
    vr_bc_cp00 = db.Column(db.Float, default=0.0)
    vr_rat = db.Column(db.Float)
    cnpj = db.Column(db.String(14), index=True)
