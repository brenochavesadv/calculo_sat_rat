from lxml import etree
from datetime import datetime
def parse_xml_bytes(xml_bytes): return etree.fromstring(xml_bytes)
def text(node, path, default=''):
    """Return text for a simple path.

    This helper first tries Element.find (fast) and if that returns None
    it builds an XPath expression that matches by local-name() so it works
    with elements that use default namespaces (common in eSocial XML).

    Examples of supported paths: './/ideEvento/perApur', './infoCpCalc/vrCpSeg'
    """
    # try fast path first
    try:
        el = node.find(path)
        if el is not None and el.text:
            return el.text.strip()
    except Exception:
        # some lxml nodes might raise when mixing API usages; fall through to xpath
        pass

    # Build a local-name() XPath fallback for namespaced documents
    try:
        xpath = None
        if path.startswith('.//'):
            parts = [p for p in path[3:].split('/') if p]
            xpath = './/' + '/'.join(['*[local-name()="%s"]' % p for p in parts])
        elif path.startswith('./'):
            parts = [p for p in path[2:].split('/') if p]
            xpath = './' + '/'.join(['*[local-name()="%s"]' % p for p in parts])
        else:
            parts = [p for p in path.split('/') if p and p != '.']
            xpath = '/'.join(['*[local-name()="%s"]' % p for p in parts])

        if xpath:
            res = node.xpath(xpath)
            if res:
                n = res[0]
                if hasattr(n, 'text') and n.text:
                    return n.text.strip()
    except Exception:
        pass

    return default

def to_float(s):
    if s is None: return 0.0
    return float(s)

def parse_date_iso(s):
    try: 
        return datetime.strptime(s, "%Y-%m-%d").date()
    except:
        try: return datetime.strptime(s, "%Y-%m").date().replace(day=1)
        except:
            try: return datetime.strptime(s, "%d/%m/%Y").date()
            except: return None
