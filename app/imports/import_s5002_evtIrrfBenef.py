from xml.etree import ElementTree as etree
from models.esocial_s5002_evtIrrfBenef import ESocialS5002EvtIrrfBenef
import json
import logging
from .esocial_data import esocial_data

logger = logging.getLogger(__name__)

def import_s5002_evtIrrfBenef(
    xml_content: str | bytes,
    source_file: str = None,
    municipio_cnpj: str = None,
) -> dict:

    xml_data = esocial_data(tipo_xml='evtIrrfBenef', xml_content=xml_content)
    if isinstance(xml_data, dict):
        xml_bytes = xml_data.get('data')
        # If helper returned an error or no data, propagate a helpful failure
        if not isinstance(xml_bytes, (bytes, bytearray)):
            # try to include diagnostic info from esocial_data result
            details = {k: v for k, v in xml_data.items() if k != 'data'}
            return {"sucess": False, "error": "esocial_data_failed", "details": details}
    else:
        return {"sucess": False, "error": "esocial_data_failed"}

    try:
        parser = etree.XMLParser(remove_blank_text=True, resolve_entities=False, load_dtd=False, no_network=True)
        root = etree.fromstring(xml_bytes, parser)
    except Exception as e:
        return {"sucess": False, "error": "xml_parse_failed", "details": str(e)}

    # find the inner evtIrrfBenef element (namespace-agnostic)
    evt = root.find('.//{*}evtIrrfBenef')
    if evt is None:
        return {"sucess": False, "error": "eSocial_data_not_found"}

    def find_text(parent, tag):
        if parent is None:
            return None
        node = parent.find('.//{*}%s' % tag)
        if node is None or node.text is None:
            return None
        return node.text.strip()

    evtIrrfBenefId = evt.get('Id')
    ideEmp = evt.find('.//{*}ideEmpregador')
    nrInsc = find_text(ideEmp, 'nrInsc')
    ideEvento = evt.find('.//{*}ideEvento')
    perApur = find_text(ideEvento, 'perApur')

    #print(f"ℹ️ evtIrrfBenefId: {json.dumps(evtIrrfBenef, indent=2, ensure_ascii=False)}")

    # Ensure nrInsc exists and, if a municipio_cnpj filter was provided, compare prefix safely.
    if not nrInsc:
        return {"sucess": False, "error": "nrInsc não informado no evento."}

    if municipio_cnpj:
        mun_prefix = municipio_cnpj[:8] if isinstance(municipio_cnpj, str) and len(municipio_cnpj) >= 8 else municipio_cnpj
        if nrInsc != mun_prefix:
            return {"sucess": False, "error": "nrInsc não corresponde ao município fornecido."}

    from run import db

    if ESocialS5002EvtIrrfBenef.query.filter_by(evtIrrfBenefId=evtIrrfBenefId).first():
        from models.import_skip import ImportSkip
        details = {"evtIrrfBenefId": evtIrrfBenefId, "nrInsc": nrInsc, "perApur": perApur, "arquivo_origem": source_file}
        skip = ImportSkip(event_type='S-5002 evtIrrfBenef', nrInsc=nrInsc, cpf=None, perApur=perApur or None, arquivo_origem=source_file, details=str(details))
        db.session.add(skip)
        db.session.commit()
        return {"sucess": False, "error": "evtIrrfBenefId already exists", "details": [details]}
    
    ideTrabalhador = evt.find('.//{*}ideTrabalhador')
    dmDev = ideTrabalhador.find('.//{*}dmDev') if ideTrabalhador is not None else None

    infoIR_items = []
    if dmDev is not None:
        for info in dmDev.findall('.//{*}infoIR'):
            # collect child elements of infoIR as a dict
            parts = {}
            for child in info:
                tag = child.tag.rsplit('}', 1)[-1] if '}' in child.tag else child.tag
                if child.text and child.text.strip():
                    parts[tag] = child.text.strip()
            if parts:
                infoIR_items.append(parts)
            else:
                # fallback to textual content
                txt = info.text.strip() if info.text else ''
                if txt:
                    infoIR_items.append(txt)

    infoIR = json.dumps(infoIR_items, ensure_ascii=False) if infoIR_items else None

    rec = ESocialS5002EvtIrrfBenef(
        perApur=perApur or None,
        nrInsc=nrInsc or None,
        tpInsc=find_text(ideEmp, 'tpInsc') or None,
        evtIrrfBenefId=evtIrrfBenefId or None,
        nrRecArqBase=find_text(ideEvento, 'nrRecArqBase') or None,
        substituido = False,
        cpfBenef = find_text(ideTrabalhador, 'cpfBenef') or None,
        perRef = find_text(dmDev, 'perRef') or None,
        ideDmDev = find_text(dmDev, 'ideDmDev') or None,
        tpPgto = find_text(dmDev, 'tpPgto') or None,
        dtPgto = find_text(dmDev, 'dtPgto') or None,
        codCateg = find_text(dmDev, 'codCateg') or None,
        infoIR = infoIR or None,
        arquivo_origem=source_file or None,
    )

    db.session.add(rec)
    db.session.commit()
    return {"sucess": True, "inserted": 1, "skipped": 0, "skipped_details": []}



