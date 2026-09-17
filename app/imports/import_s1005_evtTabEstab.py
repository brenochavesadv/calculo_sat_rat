from xml.etree import ElementTree as etree
from models.esocial_s1005_evtTabEstab import ESocialS1005EvtTabEstab
import json
import logging
from .esocial_data import esocial_data
from services.xml_parser import parse_date_iso

logger = logging.getLogger(__name__)

def import_s1005_evtTabEstab(
    xml_content: str | bytes,
    source_file: str = None,
    municipio_cnpj: str = None,
) -> dict:

    xml_data = esocial_data(tipo_xml='evtTabEstab', xml_content=xml_content)
    if isinstance(xml_data, dict):
        xml_bytes = xml_data.get('data')
        if not isinstance(xml_bytes, (bytes, bytearray)):
            details = {k: v for k, v in xml_data.items() if k != 'data'}
            return {'sucess': False, "error": "esocial_data_failed", "details": details}
    else:
        return {'sucess': False, "error": "esocial_data_failed:EvtTabEstab"}

    try:
        parser = etree.XMLParser()
        root = etree.fromstring(xml_bytes, parser)
    except Exception as e:
        return {'sucess': False, "error": "xml_parse_failed", "details": str(e)}

    # find inner evtTabEstab
    evt = root.find('.//{*}evtTabEstab')
    if evt is None:
        return {'sucess': False, "error": "eSocial_data_not_found"}

    def find_text(parent, tag):
        if parent is None:
            return None
        node = parent.find('.//{*}%s' % tag)
        if node is None or node.text is None:
            return None
        return node.text.strip()

    evtTabEstabId = evt.get('Id')
    ideEmpregador = evt.find('.//{*}ideEmpregador')
    nrInsc = find_text(ideEmpregador, 'nrInsc')

    from run import db

    if ESocialS1005EvtTabEstab.query.filter_by(evtTabEstabId=evtTabEstabId).first():
        from models.import_skip import ImportSkip
        details = {"evtTabEstabId": evtTabEstabId, "nrInsc": nrInsc, "arquivo_origem": source_file}
        skip = ImportSkip(event_type='S-1005 evtTabEstab', nrInsc=nrInsc, cpf=None, arquivo_origem=source_file, details=str(details))
        db.session.add(skip)
        db.session.commit()
        return {'sucess': False, "error": "evtTabEstabId already exists", "details": [details]}

    # tolerate two shapes: <infoEstab><inclusao><ideEstab>... or <infoEstab><ideEstab>...
    ideEstab = evt.find('.//{*}infoEstab//{*}inclusao//{*}ideEstab')
    if ideEstab is None:
        ideEstab = evt.find('.//{*}infoEstab//{*}ideEstab')
    dadosEstab = evt.find('.//{*}infoEstab//{*}inclusao//{*}dadosEstab')
    if dadosEstab is None:
        dadosEstab = evt.find('.//{*}infoEstab//{*}dadosEstab')
    aliqGilrat = dadosEstab.find('.//{*}aliqGilrat') if dadosEstab is not None else None
    procAdmJurRat = aliqGilrat.find('.//{*}procAdmJurRat') if aliqGilrat is not None else None
    procAdmJurFap = aliqGilrat.find('.//{*}procAdmJurFap') if aliqGilrat is not None else None
    aliqRatValue = find_text(aliqGilrat, 'aliqRat') if aliqGilrat is not None else None

    rec = ESocialS1005EvtTabEstab(
        evtTabEstabId = evtTabEstabId or None,
    nrInsc = nrInsc or None,
    tpInsc = find_text(ideEmpregador, 'tpInsc') or None,
    tpInscEstab = find_text(ideEstab, 'tpInsc') or None,
    nrInscEstab = find_text(ideEstab, 'nrInsc') or None,
    iniValidEstab = parse_date_iso(find_text(ideEstab, 'iniValid') or '') if find_text(ideEstab, 'iniValid') else None,
    fimValidEstab = parse_date_iso(find_text(ideEstab, 'fimValid') or '') if find_text(ideEstab, 'fimValid') else None,
    cnaePrep = find_text(dadosEstab, 'cnaePrep') or None,
    cnpjResp = find_text(dadosEstab, 'cnpjResp') or None,
    aliqRat = aliqRatValue,
    fap = find_text(aliqGilrat, 'fap') if aliqGilrat is not None else None,
    tpProcRat = find_text(procAdmJurRat, 'tpProc') if procAdmJurRat is not None else None,
    nrProcRat = find_text(procAdmJurRat, 'nrProc') if procAdmJurRat is not None else None,
    codSuspRat = find_text(procAdmJurRat, 'codSusp') if procAdmJurRat is not None else None,
    tpProcFap = find_text(procAdmJurFap, 'tpProc') if procAdmJurFap is not None else None,
    nrProcFap = find_text(procAdmJurFap, 'nrProc') if procAdmJurFap is not None else None,
    codSuspFap = find_text(procAdmJurFap, 'codSusp') if procAdmJurFap is not None else None,

        arquivo_origem = source_file or None,
    )

    db.session.add(rec)
    db.session.commit()
    return {'sucess': True, "inserted": 1, "skipped": 0, "skipped_details": []}