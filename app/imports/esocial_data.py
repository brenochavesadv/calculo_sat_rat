import os
import re
from lxml import etree
import logging

logger = logging.getLogger(__name__) 

def esocial_data(
    tipo_xml: str,
    xml_content: str | bytes,
):

    # -------------------------
    # PARSE XML
    # -------------------------
    # secure parser
    parser = etree.XMLParser(remove_blank_text=True, resolve_entities=False, load_dtd=False, no_network=True)
    xml_tree = etree.fromstring(xml_content, parser)
    ns_uri = None

    #print("Parsing XML to detect namespace...")

    # Prefer an event-scoped <eSocial> namespace when the XML is wrapped in retornoProcessamento.
    ns_prefix = "http://www.esocial.gov.br/schema/evt/"
    for node in xml_tree.iter():
        if etree.QName(node).localname == "evento":
            for child in node.iter():
                q = etree.QName(child)
                if q.localname == "eSocial" and q.namespace and q.namespace.startswith(ns_prefix):
                    ns_uri = q.namespace
                    break
            if ns_uri is not None:
                break

    # Fallback: accept direct eSocial event XMLs without the retornoProcessamento wrapper.
    if ns_uri is None:
        for child in xml_tree.iter():
            q = etree.QName(child)
            if q.localname == "eSocial" and q.namespace and q.namespace.startswith(ns_prefix):
                ns_uri = q.namespace
                break

    if ns_uri is None:
        return {"data": "", "ok": False, "error": "Não foi possível identificar o namespace do XML.", "details": "Nenhum elemento eSocial de evento foi encontrado."}

    proj_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
    #print(f"🔎 Projeto root: {proj_root}")

    version_map = {
        'v_S_01_00_00': os.path.join(proj_root, 'esocial_xsd', 'vs01_00_00_nt07', f'{tipo_xml}.xsd'),
        'v_S_01_01_00': os.path.join(proj_root, 'esocial_xsd', 'vs01_01_00_nt02', f'{tipo_xml}.xsd'),
        'v_S_01_02_00': os.path.join(proj_root, 'esocial_xsd', 'vs01_02_00_nt04', f'{tipo_xml}.xsd'),
        'v_S_01_03_00': os.path.join(proj_root, 'esocial_xsd', 'vs01_03_00-2', f'{tipo_xml}.xsd'),
    }

    version_match = re.search(r'v_S_01_(?:00_00|01_00|02_00|03_00)(?:-\d+)?$', ns_uri)
    if version_match:
        normalized_version = version_match.group(0).split('-', 1)[0]
        xsd_version = version_map.get(normalized_version)
    else:
        xsd_version = None

    if not xsd_version:
        return {"data": "","ok": False, "error": "xsd_version_not_found", "ns_uri": ns_uri}

    if not os.path.exists(xsd_version):
        return {"data": "", "ok": False, "error": "xsd_path_not_found", "ns_uri": ns_uri, "xsd_attempted": xsd_version}

    # extract eSocial from XML to validate
    esocial_data = None
    ns_evt = "http://www.esocial.gov.br/schema/evt"
    for node in xml_tree.iter():
        q = etree.QName(node)
        if q.localname == "eSocial" and q.namespace and q.namespace.startswith(ns_evt):
            esocial_data = etree.ElementTree(etree.fromstring(etree.tostring(node)))
            break

    if esocial_data is None:
        return {"data": "", "ok": False, "error": "eSocial_data_not_found", "details": "Nenhum nó eSocial correspondente ao namespace do evento foi encontrado."}

    # VALIDATE XML AGAINST XSD
    with open(xsd_version, "rb") as f:
        xsd_doc = etree.parse(f)

    schema = etree.XMLSchema(xsd_doc)
    # debug: show which XSD path and namespace we're validating against
    logger.debug("validating namespace %s against XSD: %s", ns_uri, xsd_version)
    is_valid = schema.validate(esocial_data)

    if not is_valid:
        print("❌ XML inválido!")
        for err in schema.error_log:
            print(f"Linha {err.line}: {err.message}")
        # on schema validation fail:
        return {"ok": False, "error": "schema_validation_failed", "xsd_attempted": xsd_version, "details": [{"line": err.line, "message": err.message} for err in schema.error_log]}

    # retorna o conteudo do evento eSocial como bytes
    return {"data": etree.tostring(esocial_data, encoding='utf-8')}