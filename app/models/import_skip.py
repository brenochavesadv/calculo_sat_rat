from run import db
from datetime import datetime


class ImportSkip(db.Model):
    """Log table for skipped imports (deduplication).

    Stores a concise record of why an import was skipped so it can be
    reviewed later.
    """

    __tablename__ = "import_skip"

    id = db.Column(db.Integer, primary_key=True)
    event_type = db.Column(db.String(25), nullable=False)
    nrInsc = db.Column(db.String(14), comment="Declarante/Empregador nrInsc (CNPJ/CPF)")
    cpf = db.Column(db.String(14), comment="CPF involved (worker/beneficiary)")
    perApur = db.Column(db.String(7), comment="Período de apuração (AAAA-MM)")
    dt = db.Column(db.Date, comment="Relevant date (e.g. dtAdm or dtPgto)")
    arquivo_origem = db.Column(db.String(255), comment="Source filename")
    details = db.Column(db.String(1024), comment="Optional free-text details / JSON")
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
