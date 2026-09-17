from xml.etree import ElementTree as etree
from models.esocial_s5001_evtBasesTrab import ESocialS5001EvtBasesTrab
import json
import logging
from .esocial_data import esocial_data

logger = logging.getLogger(__name__)

def import_s5001_evtBasesTrab(
    xml_content: str | bytes,
    source_file: str = None,
    municipio_cnpj: str = None,
) -> dict:
    
    xml_data = esocial_data(tipo_xml='evtBasesTrab', xml_content=xml_content)
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

    # find the inner evtBasesTrab element (namespace-agnostic)
    evt = root.find('.//{*}evtBasesTrab')
    if evt is None:
        return {"sucess": False, "error": "eSocial_data_not_found"}

    def find_text(parent, tag):
        if parent is None:
            return None
        node = parent.find('.//{*}%s' % tag)
        if node is None or node.text is None:
            return None
        return node.text.strip()

    evtBasesTrabId = evt.get('Id')
    perApur = find_text(evt, 'perApur')
    # ideEmpregador
    ideEmp = evt.find('.//{*}ideEmpregador')
    nrInsc = find_text(ideEmp, 'nrInsc')

    #print(f"ℹ️ evtBasesTrab: {json.dumps(evtBasesTrab, indent=2, ensure_ascii=False)}")
    
    # Ensure nrInsc exists and, if a municipio_cnpj filter was provided, compare prefix safely.
    if not nrInsc:
        return {"ok": True, "inserted": 0, "skipped": 1, "skipped_details": "nrInsc não informado no evento."}

    if municipio_cnpj:
        # compare first 8 digits of municipio CNPJ when available
        mun_prefix = municipio_cnpj[:8] if isinstance(municipio_cnpj, str) and len(municipio_cnpj) >= 8 else municipio_cnpj
        if nrInsc != mun_prefix:
            return {"sucess": False, "error": "nrInsc não corresponde ao município fornecido."}

    from run import db

    if ESocialS5001EvtBasesTrab.query.filter_by(evtBasesTrabId=evtBasesTrabId).first():
        from models.import_skip import ImportSkip
        details = {"evtBasesTrabId": evtBasesTrabId, "nrInsc": nrInsc, "perApur": perApur, "arquivo_origem": source_file}
        skip = ImportSkip(event_type='S-5001 evtBasesTrab', nrInsc=nrInsc, cpf=None, perApur=perApur or None, arquivo_origem=source_file, details=str(details))
        db.session.add(skip)
        db.session.commit()
        return {"sucess": False, "error": "evtBasesTrabId already exists", "details": [details]}

    # ideTrabalhador
    ideTrabalhador = evt.find('.//{*}ideTrabalhador')

    # infoCp -> ideEstabLot -> infoCategIncid (may repeat)
    infoCp = evt.find('.//{*}infoCp')
    ideEstabLot = infoCp.find('.//{*}ideEstabLot') if infoCp is not None else None
    infoCategIncid_list = []
    if ideEstabLot is not None:
        infoCategIncid_list = ideEstabLot.findall('.//{*}infoCategIncid')

    # Aggregate infoBaseCS entries across all infoCategIncid entries.
    infoBaseCs_parts = []
    for categ in infoCategIncid_list:
        if categ is None:
            continue
        for ib in categ.findall('.//{*}infoBaseCS'):
            tpValor = find_text(ib, 'tpValor')
            valor = find_text(ib, 'valor')
            infoBaseCs_parts.append(f"{tpValor}:{valor}")

    infoBaseCs = ",".join([p for p in infoBaseCs_parts if p])

    first_infoCateg = infoCategIncid_list[0] if infoCategIncid_list else None

    #print("infoCategIncid:", infoCategIncid)

    # safe retrieval helpers (use etree-based find_text)
    tpInsc_val = find_text(ideEmp, 'tpInsc')
    cpfTrab_val = find_text(ideTrabalhador, 'cpfTrab')
    nrInscLotacao_val = find_text(ideEstabLot, 'nrInsc')
    codLotacao_val = find_text(ideEstabLot, 'codLotacao')
    codCBO_val = find_text(ideTrabalhador, 'codCBO')

    rec = ESocialS5001EvtBasesTrab(
        evtBasesTrabId = evtBasesTrabId or None,
        substituido = False,
        perApur = perApur or None,
        tpInsc = tpInsc_val or None,
        nrInsc = nrInsc or None,
        cpfTrab = cpfTrab_val or None,
        matricula = find_text(first_infoCateg, "matricula") or None,
        codCBO = codCBO_val or None,
        nrInscLotacao = nrInscLotacao_val or None,
        codLotacao = codLotacao_val or None,
        codCateg = find_text(first_infoCateg, "codCateg") or None,      
        infoBaseCs = infoBaseCs or None,
        arquivo_origem = source_file or None,
    )

    db.session.add(rec)
    db.session.commit()
    return {"sucess": True, "inserted": 1, "skipped": 0, "skipped_details": []}



