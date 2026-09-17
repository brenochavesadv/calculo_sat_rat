from xml.etree import ElementTree as etree
from models.esocial_s1298_evtReabreEvPer import ESocialS1298EvtReabreEvPer
import logging
from .esocial_data import esocial_data

logger = logging.getLogger(__name__)


def import_s1298_evtReabreEvPer(
    xml_content: str | bytes,
    source_file: str = None,
    municipio_cnpj: str = None,
) -> dict:

    xml_data = esocial_data(tipo_xml='evtReabreEvPer', xml_content=xml_content)
    if isinstance(xml_data, dict):
        xml_bytes = xml_data.get('data')
        if not isinstance(xml_bytes, (bytes, bytearray)):
            details = {k: v for k, v in xml_data.items() if k != 'data'}
            return {"sucess": False, "error": f"esocial_data_failed:{xml_data.get('error', 'unknown')}", "details": details}
    else:
        return {"sucess": False, "error": "esocial_data_failed:EvtReabreEvPer"}

    try:
        parser = etree.XMLParser(remove_blank_text=True, resolve_entities=False, load_dtd=False, no_network=True)
        root = etree.fromstring(xml_bytes, parser)
    except Exception as e:
        return {"sucess": False, "error": "xml_parse_failed", "details": str(e)}

    evt = root.find('.//{*}evtReabreEvPer')
    if evt is None:
        return {"sucess": False, "error": "eSocial_data_not_found"}

    def find_text(parent, tag):
        if parent is None:
            return None
        node = parent.find('.//{*}%s' % tag)
        if node is None or node.text is None:
            return None
        return node.text.strip()

    evtReabreEvPerId = evt.get('Id')
    ide_evento = evt.find('.//{*}ideEvento')
    ide_empregador = evt.find('.//{*}ideEmpregador')
    nrInsc = find_text(ide_empregador, 'nrInsc')
    perApur = find_text(ide_evento, 'perApur')

    if not nrInsc or not municipio_cnpj or nrInsc != municipio_cnpj[:8]:
        return {"sucess": False, "error": "nrInsc não corresponde ao município fornecido."}

    from run import db

    if ESocialS1298EvtReabreEvPer.query.filter_by(evtReabreEvPerId=evtReabreEvPerId).first():
        from models.import_skip import ImportSkip
        details = {"evtReabreEvPerId": evtReabreEvPerId, "nrInsc": nrInsc, "perApur": perApur, "arquivo_origem": source_file}
        skip = ImportSkip(event_type='S-1298 evtReabreEvPer', nrInsc=nrInsc, cpf=None, perApur=perApur or None, arquivo_origem=source_file, details=str(details))
        db.session.add(skip)
        db.session.commit()
        return {"sucess": False, "error": "evtReabreEvPerId already exists", "details": [details]}

    rec = ESocialS1298EvtReabreEvPer(
        evtReabreEvPerId=evtReabreEvPerId or None,
        indApuracao=find_text(ide_evento, 'indApuracao') or None,
        perApur=perApur or None,
        indGuia=find_text(ide_evento, 'indGuia') or None,
        tpAmb=find_text(ide_evento, 'tpAmb') or None,
        procEmi=find_text(ide_evento, 'procEmi') or None,
        verProc=find_text(ide_evento, 'verProc') or None,
        tpInsc=find_text(ide_empregador, 'tpInsc') or None,
        nrInsc=nrInsc or None,
        arquivo_origem=source_file or None,
    )

    db.session.add(rec)
    db.session.commit()
    return {"sucess": True, "inserted": 1, "skipped": 0, "skipped_details": []}



