from run import db

class SelicMensal(db.Model):
    __tablename__ = "selic_mensal"
    competencia = db.Column(db.String(10), primary_key=True)
    taxa = db.Column(db.Float, nullable=False)
