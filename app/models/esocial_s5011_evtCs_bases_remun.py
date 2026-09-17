from run import db


TABELA_01_CATEGORIAS_TRABALHADORES = {
    "101": "Empregado - Geral, inclusive o empregado público da administração direta ou indireta contratado pela CLT",
    "102": "Empregado - Trabalhador rural por pequeno prazo da Lei 11.718/2008",
    "103": "Empregado - Aprendiz",
    "104": "Empregado - Doméstico",
    "105": "Empregado - Contrato a termo firmado nos termos da Lei 9.601/1998",
    "106": "Trabalhador temporário - Contrato nos termos da Lei 6.019/1974",
    "107": "Empregado - Contrato de trabalho Verde e Amarelo - sem acordo para antecipação mensal da multa rescisória do FGTS",
    "108": "Empregado - Contrato de trabalho Verde e Amarelo - com acordo para antecipação mensal da multa rescisória do FGTS",
    "111": "Empregado - Contrato de trabalho intermitente",
    "201": "Trabalhador avulso portuário",
    "202": "Trabalhador avulso não portuário",
    "301": "Servidor público titular de cargo efetivo, magistrado, ministro de Tribunal de Contas, conselheiro de Tribunal de Contas e membro do Ministério Público",
    "302": "Servidor público ocupante de cargo exclusivo em comissão",
    "303": "Exercente de mandato eletivo",
    "304": "Servidor público exercente de mandato eletivo, inclusive com exercício de cargo em comissão",
    "305": "Servidor público indicado para conselho ou órgão deliberativo, na condição de representante do governo, órgão ou entidade da administração pública",
    "306": "Servidor público contratado por tempo determinado, sujeito a regime administrativo especial definido em lei própria",
    "307": "Militar",
    "308": "Conscrito",
    "309": "Agente público - Outros",
    "310": "Servidor público eventual",
    "311": "Ministros, juízes, procuradores, promotores ou oficiais de justiça à disposição da Justiça Eleitoral",
    "312": "Auxiliar local",
    "313": "Servidor público exercente de atividade de instrutoria, capacitação, treinamento, curso ou concurso, ou convocado para pareceres técnicos ou depoimentos",
    "401": "Dirigente sindical - Informação prestada pelo sindicato",
    "410": "Trabalhador cedido/exercício em outro órgão/juiz auxiliar - Informação prestada pelo cessionário/destino",
    "501": "Dirigente sindical - Segurado especial",
    "701": "Contribuinte individual - Autônomo em geral, exceto se enquadrado em uma das demais categorias de contribuinte individual",
    "711": "Contribuinte individual - Transportador autônomo de passageiros",
    "712": "Contribuinte individual - Transportador autônomo de carga",
    "721": "Contribuinte individual - Diretor não empregado, com FGTS",
    "722": "Contribuinte individual - Diretor não empregado, sem FGTS",
    "723": "Contribuinte individual - Empresário, sócio e membro de conselho de administração ou fiscal",
    "731": "Contribuinte individual - Cooperado que presta serviços por intermédio de cooperativa de trabalho",
    "734": "Contribuinte individual - Transportador cooperado que presta serviços por intermédio de cooperativa de trabalho",
    "738": "Contribuinte individual - Cooperado filiado a cooperativa de produção",
    "741": "Contribuinte individual - Microempreendedor individual",
    "751": "Contribuinte individual - Magistrado classista temporário da Justiça do Trabalho ou da Justiça Eleitoral que seja aposentado de qualquer regime previdenciário",
    "761": "Contribuinte individual - Associado eleito para direção de cooperativa, associação ou entidade de classe de qualquer natureza ou finalidade, bem como o síndico ou administrador eleito para exercer atividade de direção condominial, desde que recebam remuneração",
    "771": "Contribuinte individual - Membro de conselho tutelar, nos termos da Lei 8.069/1990",
    "781": "Ministro de confissão religiosa ou membro de vida consagrada, de congregação ou de ordem religiosa",
    "901": "Estagiário",
    "902": "Médico residente ou residente em área profissional de saúde",
    "903": "Bolsista",
    "904": "Participante de curso de formação, como etapa de concurso público, sem vínculo de emprego/estatutário",
    "906": "Beneficiário do Programa Nacional de Prestação de Serviço Civil Voluntário",
}


class ESocialS5011EvtCsBasesRemun(db.Model):
    """
    Evento S-5011 – Bases de cálculo por categoria.
    Uma linha por ocorrência de basesRemun.
    """

    __tablename__ = "esocial_s5011_evt_cs_bases_remun"

    id = db.Column(db.Integer, primary_key=True)
    evtCsId = db.Column(
        db.String(36),
        db.ForeignKey("esocial_s5011_evt_cs.evtCsId"),
        nullable=False,
        index=True,
        comment="Identificador do evento S-5011",
    )

    tpInscEstab = db.Column(db.String(2), comment="Tipo de inscrição do estabelecimento")
    nrInscEstab = db.Column(db.String(14), comment="Número de inscrição do estabelecimento")

    indIncid = db.Column(db.String(1), comment="Indicativo de incidência")
    codCateg = db.Column(db.String(5), comment="Código da categoria do trabalhador")

    vrBcCp00 = db.Column(db.Numeric(14, 2), comment="Base de cálculo da contribuição previdenciária sobre remuneração")
    vrBcCp15 = db.Column(db.Numeric(14, 2), comment="Base de cálculo adicional após 15 anos")
    vrBcCp20 = db.Column(db.Numeric(14, 2), comment="Base de cálculo adicional após 20 anos")
    vrBcCp25 = db.Column(db.Numeric(14, 2), comment="Base de cálculo adicional após 25 anos")
    vrSuspBcCp00 = db.Column(db.Numeric(14, 2), comment="BC com incidência suspensa")
    vrSuspBcCp15 = db.Column(db.Numeric(14, 2), comment="BC suspensa após 15 anos")
    vrSuspBcCp20 = db.Column(db.Numeric(14, 2), comment="BC suspensa após 20 anos")
    vrSuspBcCp25 = db.Column(db.Numeric(14, 2), comment="BC suspensa após 25 anos")
    vrDescSest = db.Column(db.Numeric(14, 2), comment="Valor descontado para SEST")
    vrCalcSest = db.Column(db.Numeric(14, 2), comment="Valor calculado para SEST")
    vrDescSenat = db.Column(db.Numeric(14, 2), comment="Valor descontado para SENAT")
    vrCalcSenat = db.Column(db.Numeric(14, 2), comment="Valor calculado para SENAT")
    vrSalFam = db.Column(db.Numeric(14, 2), comment="Valor total do salário-família")
    vrSalMat = db.Column(db.Numeric(14, 2), comment="Valor total do salário-maternidade")

    arquivo_origem = db.Column(db.String(255), comment="Nome do arquivo de origem do qual o registro foi importado")

    __table_args__ = (
        db.Index('ix_esocial_s5011_bases_remun_evt_estab', 'evtCsId', 'nrInscEstab', 'codCateg'),
    )

    def codigo_categoria(self):
        """
        Retorna o código da categoria do trabalhador.
        """

        return TABELA_01_CATEGORIAS_TRABALHADORES.get(str(self.codCateg), self.codCateg)