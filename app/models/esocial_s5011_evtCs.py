from app.app import db

class ESocialS5011EvtCs(db.Model):
    """
    Evento S-5011 – Informações Consolidadas por Contribuinte.
    Conforme leiaute eSocial S-1.3 (rev. 26.08.2025)
    """

    __tablename__ = "esocial_s5011_evt_cs"

    Id = db.Column(db.Integer, primary_key=True)
    evtCsId = db.Column(db.String(36), nullable=False, comment="Identificador do evento", unique=True)

    # ideEvento
    nrRecArqBase = db.Column(db.String(23), nullable=False, comment="Número do recibo do arquivo base ao qual o evento se refere")
    substituido = db.Column(db.Boolean, comment="Arquivo foi substituido por outro mais recente: S=Sim, N=Não")
    perApur = db.Column(db.String(7), nullable=False, comment="Período de apuração (AAAA-MM)")
    indApuracao = db.Column(db.String(1), comment="Indicativo de apuração: 1=Mensal, 2=Anual (13º)")
    tpInsc = db.Column(db.String(2), comment="Tipo de inscrição (1=CNPJ, 2=CPF)")
    nrInsc = db.Column(db.String(14), comment="Número de inscrição do contribuinte")
    
    # ideEstab
    tpInscEstab = db.Column(db.String(2), comment="Tipo de inscrição do estabelecimento (1=CNPJ, 2=CAEPF, 3=CNO)")
    nrInscEstab = db.Column(db.String(14), comment="Número de inscrição do estabelecimento (CNPJ/CAEPF/CNO)")
    cnaePrep = db.Column(db.String(7), comment="CNAE preponderante do estabelecimento")
    aliqRat = db.Column(db.Numeric(5,4), comment="Alíquota RAT aplicável ao estabelecimento")
    fap = db.Column(db.Numeric(5,4), comment="Fator Acidentário de Prevenção (FAP) aplicado")
    aliqRatAjust = db.Column(db.Numeric(5,4), comment="Alíquota RAT ajustada (RAT × FAP)")
    codLotacao = db.Column(db.String(20), comment="Código da lotação tributária")
    codFPAS = db.Column(db.String(6), comment="Código FPAS aplicável")
    codTerceiro = db.Column(db.String(6), comment="Código de terceiros (INSS/entidades) conforme Tabela 04")

    # valores consolidados
    vlrCpSeg = db.Column(db.Numeric(14,2), comment="Valor da contribuição dos segurados")
    vlrSalFamilia = db.Column(db.Numeric(14,2), comment="Valor de salário-família dedutível")
    vlrSalMatern = db.Column(db.Numeric(14,2), comment="Valor de salário-maternidade dedutível")
    vlrTotalApur = db.Column(db.Numeric(14,2), comment="Valor total apurado de contribuição devida")
   
    # infoRecRet
    indExistInfo = db.Column(db.String(1), comment="Indicador de existência de informações retidas (S/N)")

    arquivo_origem = db.Column(db.String(255), comment="Nome do arquivo de origem do qual o registro foi importado")

    bases_remun = db.relationship("ESocialS5011EvtCsBasesRemun", backref="evt_cs", lazy=True)
    info_cr_contrib = db.relationship("ESocialS5011EvtCsInfoCrContrib", backref="evt_cs", lazy=True)

    __table_args__ = (
        db.Index('ix_esocial_s5011_nrInsc_perApur', 'nrInsc', 'perApur'),
        db.Index('ix_esocial_s5011_nrRecArqBase', 'nrRecArqBase'),
    )