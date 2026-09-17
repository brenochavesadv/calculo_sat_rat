from run import db

class ESocialS1202EvtRmnRPPS(db.Model):
    """
    Evento S-1202 – Remuneração de servidor vinculado a Regime Próprio de Previdência Social (RPPS)
    Conforme leiaute eSocial S-1.3 (rev. 26.08.2025)
    """
    __tablename__ = "esocial_s1202_evt_rmn_rpps"

    id = db.Column(db.Integer, primary_key=True)
    evtRmnRPPSId = db.Column(db.String(36), nullable=False, comment="Identificador do evento", unique=True)
    substituido = db.Column(db.Boolean, comment="Arquivo foi substituido por outro mais recente: S=Sim, N=Não")
    # <ideEvento>
    perApur = db.Column(db.String(7), nullable=False, comment="Período de Apuração no formato AAAA-MM")
    indRetif = db.Column(db.String(1), comment="Indicador de retificação do evento (0=Original,1=Retificação)")
    procEmi = db.Column(db.String(1), nullable=False, comment="Processo de emissão (1=Aplicativo, 2=Webservice)")
    # <ideEmpregador>
    tpInsc = db.Column(db.String(2), comment="Tipo de inscrição do declarante (1=CNPJ,2=CPF)")
    nrInsc = db.Column(db.String(14), comment="Número de inscrição do declarante (CNPJ/CPF)")
    # <ideTrabalhador>
    cpfTrab = db.Column(db.String(11), nullable=False, comment="CPF do beneficiário do pagamento")
    # <dmDev>
    ideDmDev = db.Column(db.String(36), comment="Identificador do Demonstrativo de Débito/Crédito")
    codCateg = db.Column(db.String(3), comment="Código da categoria do trabalhador conforme tabela do eSocial")
    # <dmDev><infoPerApur><ideEstab>
    tpInscEstab = db.Column(db.String(1), comment="Tipo de inscrição do estabelecimento (1=CNPJ,2=CPF)")
    nrInscEstab = db.Column(db.String(14), comment="Número de inscrição do estabelecimento (CNPJ/CPF)")
    # <dmDev><infoPerApur><ideEstab><remunPerApur>
    matricula = db.Column(db.String(30), comment="Matrícula do trabalhador no estabelecimento")
    itensRemun = db.Column(db.Text, comment="Itens de remuneração em formato JSON")

    arquivo_origem = db.Column(db.String(255), comment="Nome do arquivo de origem do qual o registro foi importado.")

    __table_args__ = (
        db.Index('ix_esocial_s1202_nrInsc_cpf_perApur', 'nrInsc', 'cpfTrab', 'perApur'),
    )