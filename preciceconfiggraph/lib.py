# use lxml instead of built-in, since it allows ignoring undefined namespaces.
# PreCICE configs use tag names like `data:scalar`, which are like namespaces.
from lxml import etree
from graph import getGraph
import matplotlib.pyplot as plt
import networkx as nx


# TODO class Graph:
# TODO class Node:
# TODO class Edge:

def parseFile(path: str) -> etree._Element:
    parser = etree.XMLParser(recover=True, remove_comments=True)
    tree = etree.fromstring(open(path, "rb").read(), parser)
    return tree


def color_for_node(value: str):
    if value.startswith("Data \n "):
        return [1, 0.3, 0]
    if value.startswith("Mesh \n "):
        return [0.9, 0.6, 0]
    if value.startswith("Participant \n "):
        return [0.3, 0.6, 1.0]
    if value.startswith("Exchange \n "):
        return [0.9, 0.9, 0.9]
    if value.startswith("Coupling Scheme \n "):
        return [0.7, 0.7, 0.7]
    if value.startswith("Write-Data \n ") or value.startswith("Read-Data \n "):
        return [0.7, 0, 1.0]
    if value.startswith("Mapping \n "):
        return [0.1, 0.7, 0.1]
    else:
        return [0, 0, 0]


def size_for_node(value: str):
    if value.startswith("Participant \n "):
        return 800
    if value.startswith("Data \n ") or value.startswith("Mesh \n "):
        return 600
    else:
        return 300


if __name__ == "__main__":
    root = parseFile("test/example-configs/simple-good/precice-config.xml")
    G = getGraph(root)

    node_colors = [color_for_node(n) for n in G.nodes()]
    node_sizes = [size_for_node(n) for n in G.nodes()]
    nx.draw(G, with_labels=True, arrows=True, pos=nx.spring_layout(G), node_color=node_colors, node_size=node_sizes)
    plt.show()