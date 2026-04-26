import io
import textwrap
from pathlib import Path
import networkx as nx

from preciceconfigformat.cli import parseXML, PrettyPrinter

from precice_config_graph import nodes as n
from precice_config_graph import helper as h
from precice_config_graph.edges import Edge
from precice_config_graph.xml_processing import parse_file
from precice_config_graph.graph.builder import get_graph


def check_graph_equivalence(expected: nx.Graph, actual: nx.Graph, ignore_names: bool = False) -> bool:
    """
    Check if two graphs are equivalent, with the option to ignore names.
    This check is done by comparing the attributes of the nodes and edges of the graphs.
    If names are ignored, any attribute that is a reference to another node will be ignored,
    as it may contain a different name.
    :param expected: The expected graph.
    :param actual: The actual graph.
    :param ignore_names: A flag indicating whether to ignore names when comparing the graphs.
    :return: True if the graphs are equivalent, False otherwise.
    """

    def node_match(node_a: dict[str, str | int | list[str]], node_b: dict[str, str | int | list[str]]) -> bool:
        """
        Compare two nodes for equivalence based on their attributes.
        :param node_a: A node represented by a dict of attributes.
        :param node_b: A node represented by a dict of attributes.
        :return:
        """
        # If the nodes match completely, then they will also match if names are ignored
        if node_a == node_b:
            return True

        if not ignore_names:
            return False

        # Get the attributes of the nodes that are references to named nodes
        refs_a: set[str] = set(node_a.get("_ref_keys", []))
        refs_b: set[str] = set(node_b.get("_ref_keys", []))

        # Combine all known reference keys and the meta-key itself to be on the safe side
        all_refs: set[str] = refs_a.union(refs_b).union({"_ref_keys"})

        def transform_attributes(attributes: dict[str, str | int | list[str]], refs_to_transform: set[str]):
            """
            Transform the given attributes by manipulating attributes whose keys are contained in "refs_to_transform".
            :param attributes: The attributes to transform.
            :param refs_to_transform: The keys of attributes that should be transformed.
            :return: A dict of the updated attributes.
            """
            new_attributes: dict[str, str | int | list[str]] = {}
            for key, value in attributes.items():
                if key in refs_to_transform:
                    # The attribute is a list of named values. Store the count of values instead of the names.
                    if isinstance(value, list):
                        new_attributes[key] = len(value)
                    else:
                        # This key is a named value.
                        # Store "1" to assert that the value existed, but ignore the name
                        new_attributes[key] = 1
                # Keep other values
                else:
                    new_attributes[key] = value
            return new_attributes

        attributes_a: dict[str, str | int | list[str]] = transform_attributes(node_a, all_refs)
        attributes_b: dict[str, str | int | list[str]] = transform_attributes(node_b, all_refs)

        return attributes_a == attributes_b

    def edge_match(edge_a: dict[str, Edge], edge_b: dict[str, Edge]) -> bool:
        """
        Compare two edges for equivalence based on their attributes.
        Edges have only one attribute, namely their edge type.
        :param edge_a: An edge represented by a dict of its attributes.
        :param edge_b: An edge represented by a dict of its attributes.
        :return: True if the edges are equivalent, False otherwise.
        """
        return edge_a["attr"] == edge_b["attr"]

    return nx.is_isomorphic(expected, actual, node_match=node_match, edge_match=edge_match)


def check_config_equivalence(path_expected: str, path_actual: str, ignore_names: bool = False) -> bool:
    """
    Check if two precice-config.xml files are equivalent.
    This check is done for the graph structure, including nodes and edges.
    :param path_expected: Path to the precice-config.xml file with the expected results
    :param path_actual: Path to the precice-config.xml file with the actual results
    :param ignore_names: A flag indicating whether to ignore names when comparing the graphs.
    This is helpful when checking only for "isomorphism" or equivalent structure, not equivalent values.
    :return: True if the two configs are equivalent, False otherwise
    """
    file_expected = parse_file(path_expected)
    graph_expected: nx.Graph = get_graph(file_expected)
    file_actual = parse_file(path_actual)
    graph_actual: nx.Graph = get_graph(file_actual)
    return check_graph_equivalence(graph_expected, graph_actual, ignore_names=ignore_names)


def create_config_file(graph: nx.Graph, path: str = ".", filename: str = "precice-config.xml") -> None:
    """
    Create a formatted precice-config.xml file from a given graph.
    The file is saved to the specified path.
    :param graph: The graph to be converted to a precice-config.xml file.
    :param path: The path where the file should be saved. Defaults to the current directory.
    :param filename: The name of the file to be saved. Defaults to "precice-config.xml".
    """
    directory = Path(path)
    file_path: Path = directory / filename
    config_str: str = create_config_str(graph)
    with open(file_path, "w") as f:
        f.write(_format_config_string(config_str))


def create_config_str(graph: nx.Graph) -> str:
    """
    Create a formatted precice-config.xml string from a given graph.
    :param graph: The graph to be converted to a precice-config.xml file.
    :return: A string representing a preCICE configuration file.
    """
    config_str: str = _create_unformatted_config_str(_create_config_dict(graph))
    return _format_config_string(config_str)


def _create_unformatted_config_str(config_dict: dict[str, list[n.ParticipantNode |
                                                               n.DataNode | n.MeshNode |
                                                               n.CouplingSchemeNode |
                                                               n.MultiCouplingSchemeNode |
                                                               n.M2NNode]]) -> str:
    """
    Create a string representing a preCICE configuration file.
    This is done by iterating over the given dict and creating a string for each element.
    :param config_dict: A dict containing the configuration elements.
    :return: A string representing a preCICE configuration file.
    """
    # "Header" information
    config_str: str = (f"<?xml version=\"1.0\" encoding=\"UTF-8\" ?>\n"
                       f"<precice-configuration>\n"
                       f"{h.INDENT}<log>\n"
                       f"{h.INDENT}{h.INDENT}<sink\n"
                       f"{h.INDENT}{h.INDENT}{h.INDENT}format=\"---[precice] %ColorizedSeverity% %Message%\" />\n"
                       f"{h.INDENT}</log>\n\n")  # two newlines to separate the header from the content

    for data in config_dict["data"]:
        config_str += f"{h.INDENT}" + data.to_xml() + "\n"

    config_str += "\n"  # separate mesh from data

    mesh_str: str = ""
    for mesh in config_dict["meshes"]:
        mesh_str += f"{mesh.to_xml()}"
    config_str += textwrap.indent(mesh_str, h.INDENT)

    config_str += "\n"  # separate mesh from participants

    participant_str: str = ""
    for participant in config_dict["participants"]:
        participant_str += f"{participant.to_xml()}"
    config_str += textwrap.indent(participant_str, h.INDENT)

    config_str += "\n"  # separate participants from m2ns

    for m2n in config_dict["m2n"]:
        config_str += f"{h.INDENT}{m2n.to_xml()}"

    config_str += "\n"  # separate m2ns from coupling-schemes

    coupling_scheme_str: str = ""
    for coupling_scheme in config_dict["coupling-schemes"]:
        coupling_scheme_str += f"{coupling_scheme.to_xml()}"
    config_str += textwrap.indent(coupling_scheme_str, h.INDENT)

    config_str += f"\n</precice-configuration>"
    return config_str


def _create_config_dict(graph: nx.Graph) -> dict[str, list[n.ParticipantNode |
                                                           n.DataNode | n.MeshNode |
                                                           n.CouplingSchemeNode |
                                                           n.MultiCouplingSchemeNode |
                                                           n.M2NNode]]:
    """
    Create a dict containing only the "major" elements of the given graph;
    i.e., the data, participants, meshes, coupling-schemes, and m2n nodes.
    :param graph: The graph representing the configuration.
    :return: A dict containing the configuration elements.
    """
    config_dict: dict[str, list[n.ParticipantNode
                                | n.DataNode
                                | n.MeshNode
                                | n.CouplingSchemeNode
                                | n.MultiCouplingSchemeNode
                                | n.M2NNode]] = {
        "data": [],
        "participants": [],
        "meshes": [],
        "coupling-schemes": [],
        "m2n": [],
    }
    for node in graph.nodes():
        if isinstance(node, n.ParticipantNode):
            config_dict["participants"].append(node)
        elif isinstance(node, n.MeshNode):
            config_dict["meshes"].append(node)
        elif isinstance(node, n.DataNode):
            config_dict["data"].append(node)
        elif isinstance(node, n.CouplingSchemeNode):
            config_dict["coupling-schemes"].append(node)
        elif isinstance(node, n.MultiCouplingSchemeNode):
            config_dict["coupling-schemes"].append(node)
        elif isinstance(node, n.M2NNode):
            config_dict["m2n"].append(node)
        # Other nodes can be ignored
        # This also filters out any unknown types
    return config_dict


def _format_config_string(xml_string: str) -> str:
    """
    Format the given XML string using the precice-config-format library.
    :param xml_string: An XML string to be formatted, represeting a precice-config.xml file.
    :return: The formatted XML string.
    """
    xml_bytes = xml_string.encode("utf-8")

    xml_tree = parseXML(xml_bytes)

    buffer = io.StringIO()

    # Assign the stream to the buffer
    printer = PrettyPrinter(stream=buffer)
    printer.printRoot(xml_tree)

    return buffer.getvalue()
