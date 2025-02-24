import networkx as nx

from precice_config_graph import graph, xml_processing
from precice_config_graph import nodes as n
from precice_config_graph.edges import Edge
from precice_config_graph.nodes import DataType, Direction, CouplingSchemeType, M2NType

xml = xml_processing.parse_file("tests/example-configs/simple-good/precice-config.xml")
G_actual = graph.get_graph(xml)

edges = []

# Data
n_data_color = n.DataNode("Color", DataType.SCALAR)

# Meshes
n_mesh_generator = n.MeshNode("Generator-Mesh", [n_data_color])
n_mesh_propagator = n.MeshNode("Propagator-Mesh", [n_data_color])

# Participants
n_participant_generator = n.ParticipantNode("Generator", None, None, None,
                                            [n_mesh_generator], None, None, None,
                                            None, None)
n_participant_propagator = n.ParticipantNode("Propagator", None, None, None,
                                             [n_mesh_propagator], None, None, None,
                                             None, None)
# Write Data
n_write_data_generator_color_generator_mesh = n.WriteDataNode(n_participant_generator, n_data_color, n_mesh_generator)
n_participant_generator.write_data = [n_write_data_generator_color_generator_mesh]

# Read Data
n_read_data_propagator_color_propagator_mesh = n.ReadDataNode(n_participant_propagator, n_data_color, n_mesh_propagator)
n_participant_propagator.read_data = [n_read_data_propagator_color_propagator_mesh]

# Receive Mesh
n_receive_mesh_propagator_generator_mesh_generator = n.ReceiveMeshNode(n_participant_propagator, n_mesh_generator,
                                                                       n_participant_generator)
n_participant_propagator.receive_meshes = [n_receive_mesh_propagator_generator_mesh_generator]

# Mappings
n_mapping_propagator = n.MappingNode(n_participant_propagator, Direction.READ, n_mesh_generator, n_mesh_propagator)
n_participant_propagator.mapping = [n_mapping_propagator]

# Exchanges
n_exchange_color_generator_mesh_generator_propagator = n.ExchangeNode(None, n_data_color, n_mesh_generator,
                                                                      n_participant_generator, n_participant_propagator)

# Coupling Schemes
n_coupling_scheme_generator_propagator = n.CouplingSchemeNode(CouplingSchemeType.SERIAL_EXPLICIT,
                                                              n_participant_generator, n_participant_propagator,
                                                              [n_exchange_color_generator_mesh_generator_propagator])
n_exchange_color_generator_mesh_generator_propagator.coupling_scheme = n_coupling_scheme_generator_propagator

# m2n
n_m2n_generator_propagator = n.M2NNode(M2NType.SOCKETS, n_participant_generator, n_participant_propagator, )

# Edges in the order specified by docs/Edges.md

# Receive Mesh -- Participant
edges += [(n_participant_generator, n_receive_mesh_propagator_generator_mesh_generator,
           Edge.RECEIVE_MESH__PARTICIPANT_RECEIVED_FROM)]

# Receive-mesh -- mesh
edges += [(n_receive_mesh_propagator_generator_mesh_generator, n_mesh_generator, Edge.RECEIVE_MESH__MESH)]

# Receive-mesh -- participant
edges += [(n_receive_mesh_propagator_generator_mesh_generator, n_participant_propagator,
           Edge.RECEIVE_MESH__PARTICIPANT__BELONGS_TO)]

# Participant -- mesh
edges += [(n_participant_generator, n_mesh_generator, Edge.PROVIDE_MESH__PARTICIPANT_PROVIDES)]
edges += [(n_participant_propagator, n_mesh_propagator, Edge.PROVIDE_MESH__PARTICIPANT_PROVIDES)]

# Mapping -- mesh
edges += [(n_mapping_propagator, n_mesh_propagator, Edge.MAPPING__TO_MESH)]

# Mapping -- mesh
edges += [(n_mapping_propagator, n_mesh_generator, Edge.MAPPING__FROM_MESH)]

# Mapping -- participant
edges += [(n_mapping_propagator, n_participant_propagator, Edge.MAPPING__PARTICIPANT__BELONGS_TO)]

# Participant -- exchange
edges += [(n_participant_generator, n_exchange_color_generator_mesh_generator_propagator,
           Edge.EXCHANGE__PARTICIPANT_EXCHANGED_BY)]

# Exchange -- participant
edges += [(n_participant_propagator, n_exchange_color_generator_mesh_generator_propagator, Edge.EXCHANGE__EXCHANGES_TO)]

# Exchange -- data
edges += [(n_exchange_color_generator_mesh_generator_propagator, n_data_color, Edge.EXCHANGE__DATA)]

# Exchange -- mesh
edges += [(n_exchange_color_generator_mesh_generator_propagator, n_mesh_generator, Edge.EXCHANGE__MESH)]

# Coupling scheme -- exchange
edges += [(n_coupling_scheme_generator_propagator, n_exchange_color_generator_mesh_generator_propagator,
           Edge.EXCHANGE__COUPLING_SCHEME__BELONGS_TO)]

# M2N -- participant
edges += [(n_m2n_generator_propagator, n_participant_generator, Edge.M2N__PARTICIPANT_ACCEPTOR)]
edges += [(n_m2n_generator_propagator, n_participant_propagator, Edge.M2N__PARTICIPANT_CONNECTOR)]

# Coupling-scheme -- participant
edges += [(n_coupling_scheme_generator_propagator, n_participant_generator, Edge.COUPLING_SCHEME__PARTICIPANT_FIRST)]

# Coupling-scheme -- participant
edges += [(n_coupling_scheme_generator_propagator, n_participant_propagator, Edge.COUPLING_SCHEME__PARTICIPANT_SECOND)]

# Mesh -- data
edges += [(n_mesh_generator, n_data_color, Edge.USE_DATA)]
edges += [(n_mesh_propagator, n_data_color, Edge.USE_DATA)]

# Write-data -- data
edges += [(n_write_data_generator_color_generator_mesh, n_data_color, Edge.WRITE_DATA__WRITES_TO_DATA)]

# Write-data -- mesh
edges += [(n_write_data_generator_color_generator_mesh, n_mesh_generator, Edge.WRITE_DATA__WRITES_TO_MESH)]

# Write-data -- participant
edges += [(n_write_data_generator_color_generator_mesh, n_participant_generator,
           Edge.WRITE_DATA__PARTICIPANT__BELONGS_TO)]

# Data -- read-data
edges += [(n_data_color, n_read_data_propagator_color_propagator_mesh, Edge.READ_DATA__DATA_READ_BY)]

# Mesh -- read-data
edges += [(n_mesh_propagator, n_read_data_propagator_color_propagator_mesh, Edge.READ_DATA__MESH_READ_BY)]

# Participant -- read-data
edges += [(n_participant_propagator, n_read_data_propagator_color_propagator_mesh,
           Edge.READ_DATA__PARTICIPANT__BELONGS_TO)]

G_expected = nx.Graph()
for (node_a, node_b, attr) in edges:
    G_expected.add_edge(node_a, node_b, attr=attr)


# print(nx.to_dict_of_dicts(G_expected))
# print("------------------------")
# print(nx.to_dict_of_dicts(G_actual))
# graph.print_graph(G_actual)
# graph.print_graph(G_expected)

def node_match(node_a, node_b):
    return node_a == node_b


def edge_match(edge_a, edge_b):
    return edge_a['attr'] == edge_b['attr']


assert nx.is_isomorphic(G_expected, G_actual, node_match=node_match, edge_match=edge_match), \
    f"Graphs did not match. Some stats: Expected: (num nodes: {len(G_expected.nodes)}, num edges: {len(G_expected.edges)}), " \
    + f"Actual: (num nodes: {len(G_actual.nodes)}, num edges: {len(G_actual.edges)})"

print("\nGraphs are isomorphic.")
