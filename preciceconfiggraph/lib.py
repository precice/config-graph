# use lxml instead of built-in, since it allows ignoring undefined namespaces.
# PreCICE configs use tag names like `data:scalar`, which are like namespaces.
from lxml import etree
import graph as g


# TODO class Graph:
# TODO class Node:
# TODO class Edge:

def parseFile(path: str) -> etree._Element:
    parser = etree.XMLParser(recover=True, remove_comments=True)
    tree = etree.fromstring(open(path, "rb").read(), parser)
    return tree


if __name__ == "__main__":
    root = parseFile("test/example-configs/simple-good/precice-config.xml")
    G = g.getGraph(root)
    g.printGraph(G)