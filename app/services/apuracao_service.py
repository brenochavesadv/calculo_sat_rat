from app.app import db
from app.models.esocial_s1005_evtTabEstab import ESocialS1005EvtTabEstab
from app.models.esocial_s5011_evtCs import ESocialS5011EvtCs
from app.models.esocial_s5011_evtCs_bases_remun import ESocialS5011EvtCsBasesRemun
from app.models.esocial_s5011_evtCs_info_cr_contrib import ESocialS5011EvtCsInfoCrContrib
from app.models.esocial_s1005_evtTabEstab import ESocialS1005EvtTabEstab
from app.models.calcula_cs import CalculaCs
from app.models.base_apurada import BaseApurada
from app.models.contribuicao import Contribuicao
from app.models.ajuste import Ajuste
from app.models.selic_mensal_4390 import SelicMensal4390
from app.models.municipio import Municipio
from datetime import date, datetime


def _normalize_comp(c):
    """Accept MM-AAAA or YYYY-MM and normalize to YYYY-MM."""
    val = (c or '').strip()
    parts = val.split('-')
    if len(parts) != 2:
        raise ValueError('Formato de competência inválido')
    a, b = parts[0], parts[1]
    if len(a) == 2 and len(b) == 4:
        mm = int(a)
        yyyy = int(b)
    elif len(a) == 4 and len(b) == 2:
        yyyy = int(a)
        mm = int(b)
    else:
        raise ValueError('Formato de competência inválido')
    if mm < 1 or mm > 12:
        raise ValueError('Mês da competência inválido')
    return f"{yyyy:04d}-{mm:02d}"

def apurar_rat(comp_ini, comp_fim, cnpj, aliquota):
    comp_ini_norm = _normalize_comp(comp_ini)
    comp_fim_norm = _normalize_comp(comp_fim)

    """     # chamar a SelicService para atualizar a tabela SelicMensal
        from app.services.selic_4390_service import fetch_and_upsert_selic_from_bacen
        try:
            fetch_and_upsert_selic_from_bacen()
        except Exception:
            # Do not fail the whole apuracao if SELIC refresh has transient errors.
            pass
    """
    # keep API contract and return the computed result
    return calcula_cs(comp_ini=comp_ini_norm, comp_fim=comp_fim_norm, cnpj=cnpj, aliq_rat_corrigida=aliquota)

def _parse_comp(c): 
    y, m = c.split('-')
    return datetime(int(y), int(m), 1)

def _fmt_comp(d: date): return f"{d.year:04d}-{d.month:02d}"

def _end_of_month(d):
    from calendar import monthrange
    return datetime(d.year, d.month, monthrange(d.year, d.month)[1])

def _vigente(est, comp):
    ref_ini = datetime.strptime(comp + "-01", "%Y-%m-%d").date()
    ref_fim = _end_of_month(datetime.strptime(comp + "-01", "%Y-%m-%d")).date()
    inicio = getattr(est, "iniValidEstab", getattr(est, "dt_inicio", None))
    fim = getattr(est, "fimValidEstab", getattr(est, "dt_fim", None))
    return (inicio <= ref_fim) and (fim is None or fim >= ref_ini)

def calcula_cs(comp_ini, comp_fim, cnpj=None, aliq_rat_corrigida=0, fap_corrigido=0):
    """ calcula o RAT e GIL-RAT para o período informado, com os dados do CNPJ e alíquota fornecidos, retornando um dicionário com os resultados """

    if aliq_rat_corrigida < 1:
        raise ValueError("A alíquota RAT corrigida deve ser fornecida e não pode ser menor que 1.")

    if fap_corrigido < 0:
        raise ValueError("O FAP corrigido deve ser fornecido e não pode ser negativo.")

    mes_fim = _parse_comp(comp_fim)
    mes_ini = _parse_comp(comp_ini)
    comps = []
    cur = mes_ini
    
    while cur <= mes_fim:
        comps.append(_fmt_comp(cur))
        cur = datetime(cur.year + (cur.month==12), (cur.month % 12) + 1, 1)

    nr_insc = cnpj[0:8]  # pegar os 8 primeiros dígitos do CNPJ para buscar estabelecimentos
    estab_data = ESocialS1005EvtTabEstab.query.filter(ESocialS1005EvtTabEstab.nrInsc==nr_insc).all() 

    relatorio = {}
    total_rat_periodo = 0.0
    total_rat_periodo_corrigido = 0.0

    for comp in comps:
        soma_bases_cp = 0.0
        total_vlr_cr = 0.0
        aliq_rat = 0.0
        fap = 0.0
        fap_devido = 0
        aliq_rat_ajustada = 0.0
        aliq_rat_corrigida_ajustada = 0.0
        bases_remun_por_comp = []
        info_cr_por_comp = []

        for estab in estab_data:
            
            if not _vigente(estab, comp):
                continue

            selected_evt_cs = (
                ESocialS5011EvtCs.query
                #.join(ESocialS5011EvtCs.bases_remun)
                #.join(ESocialS5011EvtCs.info_cr_contrib)
                .filter(
                    ESocialS5011EvtCs.perApur == comp,
                    ESocialS5011EvtCs.nrInsc== estab.nrInsc,
                )
                .order_by(ESocialS5011EvtCs.evtCsId.desc()) # se houver mais de um evento para a mesma competência, pegar o último evento inserido no DB
                .first()
            )

            if selected_evt_cs is None:
                continue

            aliq_rat = float(selected_evt_cs.aliqRat)
            fap = float(selected_evt_cs.fap)
            aliq_rat_ajustada = float(selected_evt_cs.aliqRatAjust)
            fap_devido = fap_corrigido if (fap_corrigido > 0) else fap
            aliq_rat_corrigida_ajustada = aliq_rat_corrigida * fap_devido            

            for bases_remun in selected_evt_cs.bases_remun:
                bases_remun_por_comp.append({
                    "indIncid": bases_remun.indIncid,
                    "codCateg": bases_remun.codCateg,
                    "vrBcCp00": float(bases_remun.vrBcCp00 or 0.0),
                    "vrBcCp15": float(bases_remun.vrBcCp15 or 0.0),
                    "vrBcCp20": float(bases_remun.vrBcCp20 or 0.0),
                    "vrBcCp25": float(bases_remun.vrBcCp25 or 0.0),
                    "vrSuspBcCp00": float(bases_remun.vrSuspBcCp00 or 0.0),
                    "vrSuspBcCp15": float(bases_remun.vrSuspBcCp15 or 0.0),
                    "vrSuspBcCp20": float(bases_remun.vrSuspBcCp20 or 0.0),
                    "vrSuspBcCp25": float(bases_remun.vrSuspBcCp25 or 0.0),
                    "vrDescSest": float(bases_remun.vrDescSest or 0.0),
                    "vrCalcSest": float(bases_remun.vrCalcSest or 0.0),
                    "vrDescSenat": float(bases_remun.vrDescSenat or 0.0),
                    "vrCalcSenat": float(bases_remun.vrCalcSenat or 0.0),
                    "vrSalFam": float(bases_remun.vrSalFam or 0.0),
                    "vrSalMat": float(bases_remun.vrSalMat or 0.0),
                })
                soma_bases_cp += (
                    float(bases_remun.vrBcCp00 or 0.0)
                    + float(bases_remun.vrBcCp15 or 0.0)
                    + float(bases_remun.vrBcCp20 or 0.0)
                    + float(bases_remun.vrBcCp25 or 0.0)
                )

            for info_cr in selected_evt_cs.info_cr_contrib:
                info_cr_por_comp.append({
                    "tpCR": info_cr.tpCR,
                    "vrCR": float(info_cr.vrCR or 0.0),
                    "vrCRSusp": float(info_cr.vrCRSusp or 0.0),
                })

                if info_cr.tpCR == 164601:  # cód. receita GIL-RAT
                    total_vlr_cr += float(info_cr.vrCR or 0.0)

        relatorio[comp] = {
            "competencia": comp,
            "aliq_rat": aliq_rat,
            "fap": fap,
            "aliq_rat_ajustada": aliq_rat_ajustada,
            "aliq_rat_corrigida": aliq_rat_corrigida,
            "fap_devido": fap_devido,
            "aliq_rat_corrigida_ajustada": aliq_rat_corrigida_ajustada,
            "bases_remun": bases_remun_por_comp,
            "info_cr_contrib": info_cr_por_comp,
            "soma_basesCp": soma_bases_cp,
            "rat_corrigido_devido": soma_bases_cp * aliq_rat_corrigida_ajustada/100,
            "vlr_cr_total": total_vlr_cr,
        }

        total_rat_periodo += total_vlr_cr
        total_rat_periodo_corrigido += relatorio[comp]["rat_corrigido_devido"]

        
    return {
        "total_rat_periodo_corrigido": total_rat_periodo_corrigido,
        "total_rat_periodo": total_rat_periodo,
        "por_competencia": list(relatorio.values())
        }
