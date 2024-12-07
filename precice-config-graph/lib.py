from . import graph as g
from .xml_processing import parse_file


if __name__ == "__main__":
    root = parse_file("test/example-configs/simple-good/precice-config.xml")
    G = g.get_graph(root)
    g.print_graph(G)