from run import db

class SelicMensal4390(db.Model):
    __tablename__ = "selic_mensal_4390"
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    competencia = db.Column(db.String(10), nullable=False)
    taxa = db.Column(db.Float, nullable=False, default=0.0)
    updated_at = db.Column(db.DateTime, nullable=False, default=db.func.now())
