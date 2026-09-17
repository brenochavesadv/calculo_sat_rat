from app.app import db
from app.models.base import TimestampMixin
class Estabelecimento(db.Model, TimestampMixin):
    __tablename__ = "estabelecimentos"
    id = db.Column(db.Integer, primary_key=True)
    cnpj_completo = db.Column(db.String(14), index=True, nullable=False)
    cod_lotacao = db.Column(db.String(50), default="DEFAULT")
    cnae = db.Column(db.String(10))
    rat_informado = db.Column(db.Integer, default=2)
    fap = db.Column(db.Float, default=1.0)
    dt_inicio = db.Column(db.Date, nullable=False)
    dt_fim = db.Column(db.Date, nullable=True)
    municipio_id = db.Column(db.Integer, db.ForeignKey("municipios.id"), nullable=True)
    municipio = db.relationship("Municipio", backref="estabelecimentos")
