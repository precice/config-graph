"""
This graph is intended for the preCICE logical-checker https://github.com/precice-forschungsprojekt/config-checker.

You can find documentation under README.md, docs/Nodes.md and docs/Edges.md.

This graph was developed by Simon Wazynski, Alexander Hutter and Orlando Ackermann as part of https://github.com/precice-forschungsprojekt.
"""

# use lxml instead of built-in, since it allows ignoring undefined namespaces.
# preCICE configs use tag names like `data:scalar`, which are like namespaces.
from lxml import etree

def parse_file(path: str) -> etree._Element:
    parser = etree.XMLParser(recover=True, remove_comments=True)
    tree = etree.fromstring(open(path, "rb").read(), parser)
    return tree