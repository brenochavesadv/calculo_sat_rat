from xml.etree import ElementTree as etree
from models.esocial_s1200_evtRemun import ESocialS1200EvtRemun
import json
import logging
from .esocial_data import esocial_data

logger = logging.getLogger(__name__)

def import_s1200_evtRemun(
    xml_content: str | bytes,
    source_file: str = None,
    municipio_cnpj: str = None,
) -> dict:

    xml_data = esocial_data(tipo_xml='evtRemun', xml_content=xml_content)
    if isinstance(xml_data, dict):
        xml_bytes = xml_data.get('data')
        if not isinstance(xml_bytes, (bytes, bytearray)):
            details = {k: v for k, v in xml_data.items() if k != 'data'}
            return {"sucess": False, "error": "esocial_data_failed", "details": details}
    else:
        return {"sucess": False, "error": "esocial_data_failed:EvtRemun"}

    try:
        parser = etree.XMLParser(remove_blank_text=True, resolve_entities=False, load_dtd=False, no_network=True)
        root = etree.fromstring(xml_bytes, parser)
    except Exception as e:
        return {"sucess": False, "error": "xml_parse_failed", "details": str(e)}

    evt = root.find('.//{*}evtRemun')
    if evt is None:
        return {"sucess": False, "error": "eSocial_data_not_found"}

    def find_text(parent, tag):
        if parent is None:
            return None
        node = parent.find('.//{*}%s' % tag)
        if node is None or node.text is None:
            return None
        return node.text.strip()

    evtRemunId = evt.get('Id')
    perApur = find_text(evt, 'perApur')
    ideEmpregador = evt.find('.//{*}ideEmpregador')
    nrInsc = find_text(ideEmpregador, 'nrInsc')
    
    #print(f"ℹ️ nrInsc: {nrInsc}, perApur: {perApur}")
    
    if not nrInsc or nrInsc != municipio_cnpj[:8]:
        return {"sucess": False, "error": "nrInsc não corresponde ao município fornecido."}

    from run import db

    if ESocialS1200EvtRemun.query.filter_by(evtRemunId=evtRemunId).first():
        from models.import_skip import ImportSkip
        details = {"evtRemunId": evtRemunId, "nrInsc": nrInsc, "perApur": perApur, "arquivo_origem": source_file}
        skip = ImportSkip(event_type='S-1200 evtRemun', nrInsc=nrInsc, cpf=None, perApur=perApur or None, arquivo_origem=source_file, details=str(details))
        db.session.add(skip)
        db.session.commit()
        return {"sucess": False, "error": "evtRemunId already exists", "details": [details]}

    dmDev = evt.find('.//{*}dmDev')
    ideEstabLot = dmDev.find('.//{*}infoPerApur//{*}ideEstabLot') if dmDev is not None else None
    remunPerApur = ideEstabLot.find('.//{*}remunPerApur') if ideEstabLot is not None else None
    itensRemun_parts = []
    if remunPerApur is not None:
        # collect textual children under remunPerApur (e.g., multiple itensRemun entries)
        for item in remunPerApur.findall('.//*'):
            if item is not remunPerApur and item.text and item.text.strip():
                itensRemun_parts.append(item.text.strip())
    itensRemun = ','.join(itensRemun_parts)

    rec = ESocialS1200EvtRemun(
        evtRemunId = evtRemunId or None,
        substituido = False,
        perApur = perApur or None,
    indRetif = find_text(evt.find('.//{*}ideEvento'), 'indRetif') or None,
    indApuracao = find_text(evt.find('.//{*}ideEvento'), 'indApuracao') or None,
    procEmi = find_text(evt.find('.//{*}ideEvento'), 'procEmi') or None,
    tpInsc = find_text(ideEmpregador, 'tpInsc') or None,
    nrInsc = nrInsc or None,
    cpfTrab = find_text(evt.find('.//{*}ideTrabalhador'), 'cpfTrab') or None,
    ideDmDev = find_text(dmDev, 'ideDmDev') or None,
    codCateg = find_text(dmDev, 'codCateg') or None,
    tpInscEstab = find_text(ideEstabLot, 'tpInsc') or None,
    nrInscEstab = find_text(ideEstabLot, 'nrInsc') or None,
    matricula = find_text(remunPerApur, 'matricula') or None,
    itensRemun = itensRemun,

        arquivo_origem = source_file or None,
    )

    db.session.add(rec)
    db.session.commit()
    return {"sucess": True, "inserted": 1, "skipped": 0, "skipped_details": []}