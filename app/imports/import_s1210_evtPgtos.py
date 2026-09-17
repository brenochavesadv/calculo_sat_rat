from xml.etree import ElementTree as etree
from models.esocial_s1210_evtPgtos import ESocialS1210EvtPgtos
import json
import logging
from .esocial_data import esocial_data

logger = logging.getLogger(__name__)

def import_s1210_evtPgtos(
    xml_content: str | bytes,
    source_file: str = None,
    municipio_cnpj: str = None,
) -> dict:

    xml_data = esocial_data(tipo_xml='evtPgtos', xml_content=xml_content)
    if isinstance(xml_data, dict):
        xml_bytes = xml_data.get('data')
        if not isinstance(xml_bytes, (bytes, bytearray)):
            details = {k: v for k, v in xml_data.items() if k != 'data'}
            return {"sucess": False, "error": "esocial_data_failed", "details": details}
    else:
        return {"sucess": False, "error": "esocial_data_failed:EvtPgtos"}

    try:
        parser = etree.XMLParser(remove_blank_text=True, resolve_entities=False, load_dtd=False, no_network=True)
        root = etree.fromstring(xml_bytes, parser)
    except Exception as e:
        return {"sucess": False, "error": "xml_parse_failed", "details": str(e)}

    evt = root.find('.//{*}evtPgtos')
    if evt is None:
        return {"sucess": False, "error": "eSocial_data_not_found"}

    def find_text(parent, tag):
        if parent is None:
            return None
        node = parent.find('.//{*}%s' % tag)
        if node is None or node.text is None:
            return None
        return node.text.strip()

    evtPgtosId = evt.get('Id')
    nrInsc = find_text(evt.find('.//{*}ideEmpregador'), 'nrInsc')
    perApur = find_text(evt.find('.//{*}ideEvento'), 'perApur')

    #print(f"ℹ️ nrInsc: {nrInsc}, perApur: {perApur}")
    
    if not nrInsc or nrInsc != municipio_cnpj[:8]:
        return {"sucess": False, "error": "nrInsc não corresponde ao município fornecido."}

    from run import db

    if ESocialS1210EvtPgtos.query.filter_by(evtPgtosId=evtPgtosId).first():
        from models.import_skip import ImportSkip
        details = {"evtPgtosId": evtPgtosId, "nrInsc": nrInsc, "perApur": perApur, "arquivo_origem": source_file}
        skip = ImportSkip(event_type='S-1210 evtPgtos', nrInsc=nrInsc, cpf=None, perApur=perApur or None, arquivo_origem=source_file, details=str(details))
        db.session.add(skip)
        db.session.commit()
        return {"sucess": False, "error": "evtPgtosId already exists", "details": [details]}

    ideBenef = evt.find('.//{*}ideBenef')
    infoPgto = ideBenef.find('.//{*}infoPgto') if ideBenef is not None else None

    rec = ESocialS1210EvtPgtos(
        evtPgtosId = evtPgtosId or None,
        substituido = False,
        perApur = perApur or None,
    tpInsc = find_text(evt.find('.//{*}ideEmpregador'), 'tpInsc') or None,
    nrInsc = nrInsc or None,
    indRetif = find_text(evt.find('.//{*}ideEvento'), 'indRetif') or None,
    procEmi = find_text(evt.find('.//{*}ideEvento'), 'procEmi') or None,
    cpfBenef = find_text(ideBenef, 'cpfBenef') or None,
    tpPgto = find_text(infoPgto, 'tpPgto') or None,
    perRef = find_text(infoPgto, 'perRef') or None,
    ideDmDev = find_text(infoPgto, 'ideDmDev') or None,
    vrLiq = find_text(infoPgto, 'vrLiq') or None,
    dtPgto = find_text(infoPgto, 'dtPgto') or None,

        arquivo_origem = source_file or None,
    )

    db.session.add(rec)
    db.session.commit()
    return {"sucess": True, "inserted": 1, "skipped": 0, "skipped_details": []}



