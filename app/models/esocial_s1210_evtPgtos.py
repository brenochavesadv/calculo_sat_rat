from run import db

class ESocialS1210EvtPgtos(db.Model):
    """
    Evento S-1210 – Pagamentos de Rendimentos do Trabalho.
    Conforme leiaute eSocial S-1.3 (rev. 26.08.2025).
    """

    __tablename__ = "esocial_s1210_evt_pgtos"

    id = db.Column(db.Integer, primary_key=True)
    evtPgtosId = db.Column(db.String(36), nullable=False, comment="Identificador do evento", unique=True)
    substituido = db.Column(db.Boolean, comment="Arquivo foi substituido por outro mais recente: S=Sim, N=Não")
    perApur = db.Column(db.String(7), nullable=False, comment="Período de Apuração no formato AAAA-MM")
    tpInsc = db.Column(db.String(2), comment="Tipo de inscrição do declarante (1=CNPJ,2=CPF)")
    nrInsc = db.Column(db.String(14), comment="Número de inscrição do declarante (CNPJ/CPF)")
    indRetif = db.Column(db.String(1), comment="Indicador de retificação do evento (0=Original,1=Retificação)")
    procEmi = db.Column(db.String(1), nullable=False, comment="Processo de emissão (1=Aplicativo, 2=Webservice)")
    cpfBenef = db.Column(db.String(11), nullable=False, comment="CPF do beneficiário do pagamento")
    
    # Grupo infoPgto
    tpPgto = db.Column(db.String(2), comment="Tipo de pagamento (1=Folha, 2=Rescisão, 3=13º, 4=Outros)")
    perRef = db.Column(db.String(7), comment="Período de referência do pagamento (AAAA-MM)")
    ideDmDev = db.Column(db.String(30), comment="Identificador do demonstrativo de pagamento")
    vrLiq = db.Column(db.Numeric(14,2), comment="Valor líquido pago ao beneficiário")
    dtPgto = db.Column(db.Date, comment="Data de pagamento")

    arquivo_origem = db.Column(db.String(255), comment="Nome do arquivo de origem do qual o registro foi importado")
    
    __table_args__ = (
        db.Index('ix_esocial_s1210_nrInsc_cpf_dtPgto', 'nrInsc', 'cpfBenef', 'dtPgto'),
    )