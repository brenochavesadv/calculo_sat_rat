from run import db

class ESocialS1005EvtTabEstab(db.Model):
    """
    Evento S-1005 – Tabela de Estabelecimentos, Obras ou Unidades de Órgãos Públicos.
    Conforme leiaute eSocial S-1.3 (rev. 26.08.2025)
    """

    __tablename__ = "esocial_s1005_evt_tab_estab"

    id = db.Column(db.Integer, primary_key=True)

    evtTabEstabId = db.Column(db.String(36), unique=True, index=True, nullable=False, comment="Identificador único do evento")
    substituido = db.Column(db.Boolean, comment="Arquivo foi substituido por outro")
    #<ideEmpregador> 
    tpInsc = db.Column(db.String(1), comment="Tipo de inscrição do empregador (1=CNPJ, 2=CPF)")
    nrInsc = db.Column(db.String(14), comment="Número de inscrição do empregador (CNPJ/CPF)")
    #<infoEstab><inclusao><ideEstab>
    tpInscEstab = db.Column(db.String(1), comment="Tipo de inscrição do estabelecimento (1=CNPJ, 2=CPF)")
    nrInscEstab = db.Column(db.String(14), comment="Número de inscrição do estabelecimento (CNPJ/CPF)")
    iniValidEstab = db.Column(db.Date, comment="Data de início da validade do cadastro do estabelecimento")
    fimValidEstab = db.Column(db.Date, comment="Data de fim da validade do cadastro do estabelecimento")
    #<infoEstab><inclusao><dadosEstab>
    cnaePrep = db.Column(db.String(7), comment="Código CNAE da atividade preponderante do estabelecimento")
    cnpjResp = db.Column(db.String(14), comment="CNPJ do responsável pelo estabelecimento")
    #<infoEstab><inclusao><dadosEstab><aliqGilrat>
    aliqRat = db.Column(db.String(1), comment="Alíquota do RAT")
    fap = db.Column(db.String(4), comment="Fator Acidentário de Prevenção (FAP)")
    #<infoEstab><inclusao><dadosEstab><aliqGilrat><procAdmJurRat>
    tpProcRat = db.Column(db.String(1), comment="Tipo de processo administrativo ou judicial do RAT")
    nrProcRat = db.Column(db.String(21), comment="Número do processo administrativo ou judicial do RAT")
    codSuspRat = db.Column(db.String(14), comment="Código de suspensão do RAT")
    #<infoEstab><inclusao><dadosEstab><aliqGilrat><procAdmJurFap>
    tpProcFap = db.Column(db.String(1), comment="Tipo de processo administrativo ou judicial do FAP")
    nrProcFap = db.Column(db.String(21), comment="Número do processo administrativo ou judicial do FAP")
    codSuspFap = db.Column(db.String(14), comment="Código de suspensão do FAP")

    arquivo_origem = db.Column(db.String(255), comment="Nome do arquivo de origem do qual o registro foi importado")
