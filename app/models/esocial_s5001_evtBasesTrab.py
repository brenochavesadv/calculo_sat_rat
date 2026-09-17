from run import db

class ESocialS5001EvtBasesTrab(db.Model):
    """
    Evento S-5001 – Informações das contribuições sociais por trabalhador.
    Relacionado ao evento S-1200 (remuneração).
    """
    __tablename__ = "esocial_s5001_evt_bases_trab"

    id = db.Column(db.Integer, primary_key=True)
    evtBasesTrabId = db.Column(db.String(36), nullable=False, comment="Identificador do evento", unique=True)
    substituido = db.Column(db.Boolean, comment="Arquivo foi substituido por outro mais recente: S=Sim, N=Não")
    perApur = db.Column(db.String(7), nullable=False, comment="Período de Apuração no formato AAAA-MM")
    tpInsc = db.Column(db.String(2), comment="Tipo de inscrição do declarante (1=CNPJ,2=CPF)")
    nrInsc = db.Column(db.String(14), comment="Número de inscrição do declarante (CNPJ/CPF)")
    cpfTrab = db.Column(db.String(11), nullable=False, comment="CPF do trabalhador")
    matricula = db.Column(db.String(30), comment="Matrícula do trabalhador no empregador")
    codCBO = db.Column(db.String(6), comment="Código Brasileiro de Ocupação do trabalhador")
    nrInscLotacao = db.Column(db.String(14), comment="Inscrição da lotação tributária conforme evento S-1020")
    codLotacao = db.Column(db.String(20), comment="Código da lotação tributária conforme tabela 10 do eSocial")
    codCateg = db.Column(db.String(5), comment="Categoria do trabalhador (Tabela 1 do eSocial)")
    infoBaseCs = db.Column(db.Text, comment="Informações da base de cálculo da contribuição previdenciária")
    arquivo_origem = db.Column(db.String(255), comment="Nome do arquivo de origem do qual o registro foi importado")