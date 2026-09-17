from app.app import db
from app.models.base import TimestampMixin
class Rubrica(db.Model, TimestampMixin):
    __tablename__ = "rubricas"
    id = db.Column(db.Integer, primary_key=True)
    cod_rubr = db.Column(db.String(50), unique=True, nullable=False)
    nat_rubr = db.Column(db.String(10))
    cod_inccp = db.Column(db.String(5))
