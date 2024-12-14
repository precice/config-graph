import sys

from precice_config_graph import graph as g
from precice_config_graph.xml_processing import parse_file

if __name__ == "__main__":
    if len(sys.argv) < 2:
        sys.exit("No file path provided. Please provide the path to the config you wish to be visualized.")
    file_path = sys.argv[1]

    root = parse_file(file_path)
    G = g.get_graph(root)

    g.print_graph(G)
