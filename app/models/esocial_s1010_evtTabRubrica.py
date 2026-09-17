from run import db

class ESocialS1010EvtTabRubrica(db.Model):
    """
    Evento S-1010 – Tabela de Rubricas
    Conforme leiaute eSocial v. S-1.3 (rev. 26.08.2025)
    """

    __tablename__ = "esocial_s1010_evt_tab_rubrica"

    id = db.Column(db.Integer, primary_key=True)
    evtTabRubricaId = db.Column(db.String(36), unique=True, index=True, nullable=False, comment="Identificador único do evento")
    substituido = db.Column(db.Boolean, comment="Arquivo foi substituido por outro mais recente: S=Sim, N=Não")
    # <ideEmpregador>
    tpInsc = db.Column(db.String(2), comment="Tipo de inscrição do declarante (1=CNPJ,2=CPF)")
    nrInsc = db.Column(db.String(14), comment="Número de inscrição do declarante (CNPJ/CPF)")
    # <infoRubrica><inclusao><ideRubrica>
    codRubr = db.Column(db.String(30), comment="Código da rubrica")
    ideTabRubr = db.Column(db.String(8), comment="Identificador da rubrica na tabela do empregador")
    iniValidIncl = db.Column(db.String(7), comment="Data de início de validade da inclusão da rubrica")
    # <infoRubrica><inclusao><dadosRubrica>
    dscRubr = db.Column(db.String(100), comment="Descrição da rubrica")
    natRubr = db.Column(db.String(4), comment="Natureza da rubrica" )
    tpRubr = db.Column(db.String(1), comment="Tipo da rubrica")
    codIncCP = db.Column(db.String(2), comment="Código de incidência na contribuição previdenciária")
    codIncIRRF = db.Column(db.String(4), comment="Código de incidência no Imposto de Renda")
    codIncFGTS = db.Column(db.String(2), comment="Código de incidência no FGTS")
    codIncCPRP = db.Column(db.String(2), comment="Código de incidência na contribuição para o PIS/PASEP")
    tetoRemun = db.Column(db.String(1), comment="Teto de remuneração para incidência da rubrica")
    
    arquivo_origem = db.Column(db.String(255), comment="Nome do arquivo de origem do qual o registro foi importado.")

    __table_args__ = (
        db.Index('ix_esocial_s1010_evt_tab_rubrica', 'evtTabRubricaId'),
    )
