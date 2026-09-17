from models.esocial_s5011_evtCs import ESocialS5011EvtCs
from models.esocial_s5011_evtCs_bases_remun import ESocialS5011EvtCsBasesRemun
from models.esocial_s5011_evtCs_info_cr_contrib import ESocialS5011EvtCsInfoCrContrib
import json
import logging
from .esocial_data import esocial_data
from xml.etree import ElementTree as etree

logger = logging.getLogger(__name__)

def import_s5011_evtCs(
    xml_content: str | bytes,
    source_file: str = None,
    municipio_cnpj: str = None,
) -> dict:

    # Note: event type for this importer is evtCS
    xml_data = esocial_data(tipo_xml='evtCS', xml_content=xml_content)
    if isinstance(xml_data, dict):
        xml_bytes = xml_data.get('data')
        if not isinstance(xml_bytes, (bytes, bytearray)):
            details = {k: v for k, v in xml_data.items() if k != 'data'}
            return {"sucess": False, "error": "esocial_data_failed", "details": details}
    else:
        return {"sucess": False, "error": "esocial_data_failed"}

    try:
        parser = etree.XMLParser(remove_blank_text=True, resolve_entities=False, load_dtd=False, no_network=True)
        root = etree.fromstring(xml_bytes, parser)
    except Exception as e:
        return {"sucess": False, "error": "xml_parse_failed", "details": str(e)}

    evt = root.find('.//{*}evtCS')
    if evt is None:
        return {"sucess": False, "error": "eSocial_data_not_found"}

    def find_text(parent, tag):
        if parent is None:
            return None
        node = parent.find('.//{*}%s' % tag)
        if node is None or node.text is None:
            return None
        return node.text.strip()

    evtCsId = evt.get('Id')
    nrInsc = find_text(evt.find('.//{*}ideEmpregador'), 'nrInsc')
    perApur = find_text(evt.find('.//{*}ideEvento'), 'perApur')

    #print(f"ℹ️ nrInsc: {nrInsc}, perApur: {perApur}")
    
    if not nrInsc or nrInsc != municipio_cnpj[:8]:
        return {"sucess": False, "error": "nrInsc não corresponde ao município fornecido."}

    from run import db

    if ESocialS5011EvtCs.query.filter_by(evtCsId=evtCsId).first():
        from models.import_skip import ImportSkip
        details = {"nrInsc": nrInsc, "perApur": perApur, "arquivo_origem": source_file}
        skip = ImportSkip(event_type='S-5011', nrInsc=nrInsc, cpf=None, perApur=perApur or None, arquivo_origem=source_file, details=str(details))
        db.session.add(skip)
        db.session.commit()
        return {"sucess": False, "error": "evtCsId already exists", "details": [details]}

    info_cs = evt.find('.//{*}infoCS')
    ide_estab_nodes = info_cs.findall('.//{*}ideEstab') if info_cs is not None else []
    first_ide_estab = ide_estab_nodes[0] if ide_estab_nodes else None
    ide_estab = first_ide_estab
    info_estab = first_ide_estab.find('.//{*}infoEstab') if first_ide_estab is not None else None
    ide_lotacao = first_ide_estab.find('.//{*}ideLotacao') if first_ide_estab is not None else None
    info_cr_contrib = info_cs.findall('.//{*}infoCRContrib') if info_cs is not None else []

    rec = ESocialS5011EvtCs(

            evtCsId=evtCsId or None,
            perApur=perApur or None,
            nrInsc=nrInsc or None,

            nrRecArqBase=find_text(info_cs, 'nrRecArqBase') or None,
            substituido=False,
            indApuracao=find_text(evt.find('.//{*}ideEvento'), 'indApuracao') or None,
            tpInsc=find_text(evt.find('.//{*}ideEmpregador'), 'tpInsc') or None,
            tpInscEstab=find_text(ide_estab, 'tpInsc') or None,

            nrInscEstab=find_text(ide_estab, 'nrInsc') or None,

            cnaePrep=find_text(info_estab, 'cnaePrep') or None,
            aliqRat=find_text(info_estab, 'aliqRat') or None,
            fap=find_text(info_estab, 'fap') or None,
            aliqRatAjust=find_text(info_estab, 'aliqRatAjust') or None,

            codLotacao=find_text(ide_lotacao, 'codLotacao') or None,
            codFPAS=find_text(ide_lotacao, 'fpas') or None,
            codTerceiro=find_text(ide_lotacao, 'codTercs') or None,

            vlrCpSeg=find_text(info_cs.find('.//{*}infoCPSeg') if info_cs is not None else None, 'vrCpSeg') or None,

            vlrSalFamilia=None,
            vlrSalMatern=None,
            vlrTotalApur=None,
            indExistInfo=None,
            arquivo_origem=source_file or None,
        )

    db.session.add(rec)
    db.session.flush()

    for ide_estab in ide_estab_nodes:
        bases_remun_nodes = ide_estab.findall('.//{*}basesRemun')
        for bases_remun in bases_remun_nodes:
            bases_cp = bases_remun.find('.//{*}basesCp')
            child = ESocialS5011EvtCsBasesRemun(
                evtCsId=evtCsId or None,
                tpInscEstab=find_text(ide_estab, 'tpInsc') or None,
                nrInscEstab=find_text(ide_estab, 'nrInsc') or None,
                indIncid=find_text(bases_remun, 'indIncid') or None,
                codCateg=find_text(bases_remun, 'codCateg') or None,
                vrBcCp00=find_text(bases_cp, 'vrBcCp00') or None,
                vrBcCp15=find_text(bases_cp, 'vrBcCp15') or None,
                vrBcCp20=find_text(bases_cp, 'vrBcCp20') or None,
                vrBcCp25=find_text(bases_cp, 'vrBcCp25') or None,
                vrSuspBcCp00=find_text(bases_cp, 'vrSuspBcCp00') or None,
                vrSuspBcCp15=find_text(bases_cp, 'vrSuspBcCp15') or None,
                vrSuspBcCp20=find_text(bases_cp, 'vrSuspBcCp20') or None,
                vrSuspBcCp25=find_text(bases_cp, 'vrSuspBcCp25') or None,
                vrDescSest=find_text(bases_cp, 'vrDescSest') or None,
                vrCalcSest=find_text(bases_cp, 'vrCalcSest') or None,
                vrDescSenat=find_text(bases_cp, 'vrDescSenat') or None,
                vrCalcSenat=find_text(bases_cp, 'vrCalcSenat') or None,
                vrSalFam=find_text(bases_cp, 'vrSalFam') or None,
                vrSalMat=find_text(bases_cp, 'vrSalMat') or None,
                arquivo_origem=source_file or None,
            )
            db.session.add(child)
    
    for info_cr_node in info_cr_contrib:
        child = ESocialS5011EvtCsInfoCrContrib(
            evtCsId=evtCsId or None,
            tpCR=find_text(info_cr_node, 'tpCR') or find_text(info_cr_node, 'tpCR') or None,
            vrCR=find_text(info_cr_node, 'vrCR') or find_text(info_cr_node, 'vrCR') or None,
            vrCRSusp=find_text(info_cr_node, 'vrCrSusp') or find_text(info_cr_node, 'vrCRSusp') or None,
            arquivo_origem=source_file or None,
        )
        db.session.add(child)

    db.session.commit()
    
    return {"sucess": True, "inserted": 1, "skipped": 0, "skipped_details": []}



