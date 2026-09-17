from run import db

class ESocialS5011EvtCsInfoCrContrib(db.Model):
    """
    Evento S-5011 – Bases de cálculo por categoria.
    Uma linha por ocorrência de InfoCRContrib.
    """

    __tablename__ = "esocial_s5011_evt_cs_info_cr_contrib"

    id = db.Column(db.Integer, primary_key=True)
    evtCsId = db.Column(
        db.String(36),
        db.ForeignKey("esocial_s5011_evt_cs.evtCsId"),
        nullable=False,
        index=True,
        comment="Identificador do evento S-5011",
    )
    tpCR = db.Column(db.Integer, comment="Código de Receita")
    """
    tpCR - Código de Receita
    CR relativo a contribuições sociais devidas à Previdência Social e a Outras Entidades e Fundos (Terceiros), 
    conforme legislação em vigor na competência. Validacao: Deve ser um código válido, compatível com a classificação
    tributária do contribuinte e com as informações prestadas nos demais eventos.
    """
    vrCR = db.Column(db.Numeric(14, 2), comment="Valor do crédito")
    """
    vrCR = Valor correspondente ao CR apurado. Validação: Deve ser apurado de acordo com a legislação em vigor na competência.
    Deve ser maior que 0 (zero).
    """
    vrCRSusp = db.Column(db.Numeric(14, 2), comment="Valor do tributo com exigibilidade suspensa.")
    arquivo_origem = db.Column(db.String(255), comment="Nome do arquivo de origem do qual o registro foi importado")

    __table_args__ = (
        db.Index('ix_esocial_s5011_info_cr_contrib_evt_tpcr', 'evtCsId', 'tpCR'),
    )