from run import db


class ESocialS1298EvtReabreEvPer(db.Model):
    """
    Evento S-1298 – Reabertura dos Eventos Periódicos.
    Conforme leiaute eSocial S-1.3 (rev. 26.08.2025).
    """

    __tablename__ = "esocial_s1298_evt_reabre_ev_per"

    id = db.Column(db.Integer, primary_key=True)
    evtReabreEvPerId = db.Column(db.String(36), nullable=False, comment="Identificador do evento", unique=True)

    indApuracao = db.Column(db.String(1), nullable=False, comment="Indicativo de apuração (1=Mensal, 2=Anual/13º)")
    perApur = db.Column(db.String(7), nullable=False, comment="Período de apuração no formato AAAA-MM ou AAAA")
    indGuia = db.Column(db.String(1), comment="Indicativo de guia, quando informado")
    tpAmb = db.Column(db.String(1), nullable=False, comment="Ambiente do evento")
    procEmi = db.Column(db.String(1), nullable=False, comment="Processo de emissão")
    verProc = db.Column(db.String(20), nullable=False, comment="Versão do processo emissor")

    tpInsc = db.Column(db.String(2), nullable=False, comment="Tipo de inscrição do empregador (1=CNPJ, 2=CPF)")
    nrInsc = db.Column(db.String(14), nullable=False, comment="Número de inscrição do empregador")

    arquivo_origem = db.Column(db.String(255), comment="Nome do arquivo de origem do qual o registro foi importado")

    __table_args__ = (
        db.Index('ix_esocial_s1298_nrInsc_perApur', 'nrInsc', 'perApur'),
    )