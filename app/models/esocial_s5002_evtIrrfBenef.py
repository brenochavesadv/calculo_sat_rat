from run import db

class ESocialS5002EvtIrrfBenef(db.Model):
    """
    Evento S-5002 – Informações complementares das contribuições sociais.
    Contém dados de FPAS, CNAE, FAP e alíquotas de RAT.
    """
    __tablename__ = "esocial_s5002_evt_irrf_benef"

    id = db.Column(db.Integer, primary_key=True)

    evtIrrfBenefId = db.Column(db.String(36), nullable=False, comment="Identificador do evento", unique=True)
    perApur = db.Column(db.String(7), nullable=False, comment="Período de apuração no formato AAAA-MM")
    tpInsc = db.Column(db.String(2), comment="Tipo de inscrição do contribuinte (1 = CNPJ, 2 = CPF)")
    nrInsc = db.Column(db.String(14), comment="Número de inscrição (CNPJ ou CPF)")
    nrRecArqBase = db.Column(db.String(23), nullable=False, comment="Número do recibo do arquivo base ao qual o evento se refere")
    substituido = db.Column(db.Boolean, comment="Arquivo foi substituido por outro mais recente: S=Sim, N=Não")

    # beneficiary/payment specific fields (extracted from evtIrrfBenef/dmDev)
    cpfBenef = db.Column(db.String(11), comment="CPF do beneficiário")
    perRef = db.Column(db.String(7), comment="Período de referência (AAAA-MM)")
    ideDmDev = db.Column(db.String(64), comment="Identificador do demonstrativo de pagamento")
    tpPgto = db.Column(db.String(4), comment="Tipo de pagamento")
    dtPgto = db.Column(db.Date, comment="Data de pagamento")
    codCateg = db.Column(db.String(5), comment="Código da categoria do beneficiário")

    # aggregated IR values found in dmDev/infoIR
    infoIR = db.Column(db.Text, comment="map com valor total dos infoIR encontrados no dmDev")
    arquivo_origem = db.Column(db.String(255), comment="Nome do arquivo de origem do qual o registro foi importado")

    __table_args__ = (
        db.Index('ix_esocial_s5002_nrInsc_cpf_dtPgto', 'nrInsc', 'cpfBenef', 'dtPgto'),
        db.Index('ix_esocial_s5002_nrRecArqBase', 'nrRecArqBase')
    )
