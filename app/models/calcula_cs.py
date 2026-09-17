from app.app import db
from app.models.base import TimestampMixin

class CalculaCs(db.Model, TimestampMixin):
    __tablename__ = "calcula_cs"
    id = db.Column(db.Integer, primary_key=True)
    nrInsc = db.Column(db.String(14), nullable=False)  # número de inscrição do empregador
    per_apur = db.Column(db.String(7), index=True)
    vr_bc_consolidada = db.Column(db.Float, default=0.0, comment="Valor da base de cálculo consolidada somatorio basesRemun do S-5011")
    fap_aplicado = db.Column(db.Numeric(5,4), comment="FAP aplicado no s5011_evtCs") 
    aliq_rat_aplicada = db.Column(db.Numeric(5,4), comment="Alíquota RAT informada no s5011_evtCs") 
    aliq_rat_ajustada = db.Column(db.Numeric(5,4), comment="Alíquota RAT ajustada (RAT × FAP)") 
    fap_devido = db.Column(db.Numeric(5,4), comment="FAP devido")
    aliq_rat_corrigida = db.Column(db.Numeric(5,4), comment="Alíquota RAT corrigida")
    aliq_rat_corrigida_ajustada = db.Column(db.Numeric(5,4), comment="Alíquota RAT ajustada corrigida (RAT × FAP)")
    vl_total_apur_aplicado = db.Column(db.Numeric(14,2), comment="Valor total apurado de contribuição devida no s5011_evtCs")
    vl_total_apur_corrigido = db.Column(db.Numeric(14,2), comment="Valor total calculado conforme ajuste da aliquota ajustada")
    created_at = db.Column(db.DateTime, default=db.func.current_timestamp())


def codigo_de_receita(codigo, descricao):
    codigo_de_receita = {
        "113801": "CP patronal sobre a remuneração do segurado empregado ou trabalhador avulso, aliquota: 20",
        "164601": "CP GILRAT sobre a remuneração do segurado empregado ou trabalhador avulso Variável (RAT X FAP)",
        "113804": "CP patronal sobre a remuneração do segurado contribuinte individual (autônomos) 20",
        "114101": "CP para financiamento de aposentadoria especial sobre a remuneração do segurado empregado 6, 9 ou 12",
        "108201": "CP do segurado empregado e trabalhador avulso Variável",
        "109901": "CP do segurado contribuinte individual 11",
        "109902": "CP do segurado contribuinte individual 20",
        "116201": "Retenção INSS 11 ou 3,5",
        "114106": "Adicional de Retenção INSS 4, 3 ou 2",
        "121802": "SEST - Desconto do Transportador 1,5",
        "122102": "SENAT - Desconto do Transportador 1",
        "165601": "CP - Aquisição de Produção Rural de Pessoa Física 1,2",
        "164603": "CP GILRAT - Aquisição de Produção Rural de Pessoa Física 0,1",
        "121306": "SENAR - Aquisição de Produção Rural de Pessoa Física 0,2",
        "165604": "CP PAA - Aquisição de Produção Rural de Pessoa Física 1,2",
        "164608": "CP GILRAT PAA - Aquisição de Produção Rural de Pessoa Física 0,1",
    }

    return codigo_de_receita.get(codigo, descricao)