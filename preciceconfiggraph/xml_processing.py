# use lxml instead of built-in, since it allows ignoring undefined namespaces.
# PreCICE configs use tag names like `data:scalar`, which are like namespaces.
from lxml import etree

def parse_file(path: str) -> etree._Element:
    parser = etree.XMLParser(recover=True, remove_comments=True)
    tree = etree.fromstring(open(path, "rb").read(), parser)
    return tree