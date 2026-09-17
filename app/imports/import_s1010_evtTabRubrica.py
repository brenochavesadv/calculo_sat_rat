from xml.etree import ElementTree as etree
from models.esocial_s1010_evtTabRubrica import ESocialS1010EvtTabRubrica
import json
import logging
from .esocial_data import esocial_data

logger = logging.getLogger(__name__)

def import_s1010_evtTabRubrica(
    xml_content: str | bytes,
    source_file: str = None,
    municipio_cnpj: str = None,
) -> dict:

    xml_data = esocial_data(tipo_xml='evtTabRubrica', xml_content=xml_content)
    if isinstance(xml_data, dict):
        xml_bytes = xml_data.get('data')
        if not isinstance(xml_bytes, (bytes, bytearray)):
            details = {k: v for k, v in xml_data.items() if k != 'data'}
            return {"sucess": False, "error": "esocial_data_failed", "details": details}
    else:
        return {"sucess": False, "error": "esocial_data_failed:EvtTabRubrica"}

    try:
        parser = etree.XMLParser(remove_blank_text=True, resolve_entities=False, load_dtd=False, no_network=True)
        root = etree.fromstring(xml_bytes, parser)
    except Exception as e:
        return {"sucess": False, "error": "xml_parse_failed", "details": str(e)}

    evt = root.find('.//{*}evtTabRubrica')
    if evt is None:
        return {"sucess": False, "error": "eSocial_data_not_found"}

    def find_text(parent, tag):
        if parent is None:
            return None
        node = parent.find('.//{*}%s' % tag)
        if node is None or node.text is None:
            return None
        return node.text.strip()

    evtTabRubricaId = evt.get('Id')

    from run import db

    if ESocialS1010EvtTabRubrica.query.filter_by(evtTabRubricaId=evtTabRubricaId).first():
        from models.import_skip import ImportSkip
        details = {"evtTabRubricaId": evtTabRubricaId, "nrInsc": nrInsc, "arquivo_origem": source_file}
        skip = ImportSkip(event_type='S-1010 evtTabRubrica', nrInsc=nrInsc, cpf=None, arquivo_origem=source_file, details=str(details))
        db.session.add(skip)
        db.session.commit()
        return {"sucess": False, "error": "evtTabRubricaId already exists", "details": [details]}

    ideEmpregador = evt.find('.//{*}ideEmpregador')
    nrInsc = find_text(ideEmpregador, 'nrInsc')
    # tolerate either <infoRubrica><inclusao><ideRubrica>... or <infoRubrica><ideRubrica>...
    ideRubrica = evt.find('.//{*}infoRubrica//{*}inclusao//{*}ideRubrica')
    if ideRubrica is None:
        ideRubrica = evt.find('.//{*}infoRubrica//{*}ideRubrica')
    dadosRubrica = evt.find('.//{*}infoRubrica//{*}inclusao//{*}dadosRubrica')
    if dadosRubrica is None:
        dadosRubrica = evt.find('.//{*}infoRubrica//{*}dadosRubrica')

    rec = ESocialS1010EvtTabRubrica(
        evtTabRubricaId = evtTabRubricaId or None,
        substituido = False,
    tpInsc = find_text(ideEmpregador, 'tpInsc') or None,
    nrInsc = nrInsc or None,
    codRubr = find_text(ideRubrica, 'codRubr') or None,
    ideTabRubr = find_text(ideRubrica, 'ideTabRubr') or None,
    iniValidIncl = find_text(ideRubrica, 'iniValid') or None,
    dscRubr = find_text(dadosRubrica, 'dscRubr') or None,
    natRubr = find_text(dadosRubrica, 'natRubr') or None,
    tpRubr = find_text(dadosRubrica, 'tpRubr') or None,
    codIncCP = find_text(dadosRubrica, 'codIncCP') or None,
    codIncIRRF = find_text(dadosRubrica, 'codIncIRRF') or None,
    codIncFGTS = find_text(dadosRubrica, 'codIncFGTS') or None,
    codIncCPRP = find_text(dadosRubrica, 'codIncCPRP') or None,
    tetoRemun = find_text(dadosRubrica, 'tetoRemun') or None,

        arquivo_origem = source_file or None,
    )

    db.session.add(rec)
    db.session.commit()
    return {"sucess": True, "inserted": 1, "skipped": 0, "skipped_details": []}