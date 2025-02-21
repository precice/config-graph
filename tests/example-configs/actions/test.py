import networkx as nx

from precice_config_graph import graph, xml_processing
from precice_config_graph import nodes as n
from precice_config_graph.edges import Edge
from precice_config_graph.nodes import DataType, Direction, TimingType, CouplingSchemeType

xml = xml_processing.parse_file("tests/example-configs/actions/precice-config.xml")
G_actual = graph.get_graph(xml)


G_expected = nx.Graph()

# Data
n_color = n.DataNode("Color", DataType.SCALAR)


# Generator
n_generator_mesh = n.MeshNode("Generator-Mesh", [n_color])

n_generator_participant = n.ParticipantNode("Generator", provide_meshes=[n_generator_mesh])

n_generator_write_data = n.WriteDataNode(n_generator_participant, n_color, n_generator_mesh)
n_generator_participant.write_data.append(n_generator_write_data)

G_expected.add_edge(n_generator_mesh, n_color, attr=Edge.USE_DATA)

G_expected.add_edge(n_generator_mesh, n_generator_participant, attr=Edge.PROVIDE_MESH__PARTICIPANT_PROVIDES)

G_expected.add_edge(n_generator_write_data, n_generator_participant, attr=Edge.WRITE_DATA__PARTICIPANT__BELONGS_TO)
G_expected.add_edge(n_generator_write_data, n_generator_mesh, attr=Edge.WRITE_DATA__WRITES_TO_MESH)
G_expected.add_edge(n_generator_write_data, n_color, attr=Edge.WRITE_DATA__WRITES_TO_DATA)


# Propagator
n_propagator_mesh = n.MeshNode("Propagator-Mesh", [n_color])

n_propagator_participant = n.ParticipantNode("Propagator", provide_meshes=[n_propagator_mesh])

n_propagator_receive_mesh = n.ReceiveMeshNode(
    n_propagator_participant, from_participant=n_generator_participant, mesh=n_generator_mesh
)

n_mapping = n.MappingNode(
    n_propagator_participant, Direction.READ, from_mesh=n_generator_mesh, to_mesh=n_propagator_mesh
)
n_propagator_participant.mappings.append(n_mapping)

n_read_data = n.ReadDataNode(n_propagator_participant, data=n_color, mesh=n_propagator_mesh)
n_propagator_participant.read_data.append(n_read_data)

n_action = n.ActionNode(
    n_propagator_participant, mesh=n_propagator_mesh, timing=TimingType.WRITE_MAPPING_POST, target_data=n_color,
    source_data=[],
)
n_propagator_participant.actions.append(n_action)

G_expected.add_edge(n_propagator_mesh, n_color, attr=Edge.USE_DATA)

G_expected.add_edge(n_propagator_mesh, n_propagator_participant, attr=Edge.PROVIDE_MESH__PARTICIPANT_PROVIDES)

G_expected.add_edge(n_propagator_receive_mesh, n_propagator_participant, attr=Edge.RECEIVE_MESH__PARTICIPANT__BELONGS_TO)
G_expected.add_edge(n_propagator_receive_mesh, n_generator_participant, attr=Edge.RECEIVE_MESH__PARTICIPANT_RECEIVED_FROM)
G_expected.add_edge(n_propagator_receive_mesh, n_generator_mesh, attr=Edge.RECEIVE_MESH__MESH)

G_expected.add_edge(n_mapping, n_propagator_participant, attr=Edge.MAPPING__PARTICIPANT__BELONGS_TO)
G_expected.add_edge(n_mapping, n_generator_mesh, attr=Edge.MAPPING__FROM_MESH)
G_expected.add_edge(n_mapping, n_propagator_mesh, attr=Edge.MAPPING__TO_MESH)

G_expected.add_edge(n_read_data, n_propagator_participant, attr=Edge.READ_DATA__PARTICIPANT__BELONGS_TO)
G_expected.add_edge(n_read_data, n_color, attr=Edge.READ_DATA__DATA_READ_BY)
G_expected.add_edge(n_read_data, n_propagator_mesh, attr=Edge.READ_DATA__MESH_READ_BY)

G_expected.add_edge(n_action, n_propagator_participant, attr=Edge.ACTION__PARTICIPANT__BELONGS_TO)
G_expected.add_edge(n_action, n_propagator_mesh, attr=Edge.ACTION__MESH)
G_expected.add_edge(n_action, n_color, attr=Edge.ACTION__TARGET_DATA)


# M2N Sockets edge
G_expected.add_edge(n_generator_participant, n_propagator_participant, attr=Edge.SOCKET)

# Couping scheme
n_coupling_scheme = n.CouplingSchemeNode(
    CouplingSchemeType.SERIAL_EXPLICIT, first_participant=n_generator_participant,
    second_participant=n_propagator_participant, exchanges=[]
)

n_exchange = n.ExchangeNode(
    coupling_scheme=n_coupling_scheme, data=n_color, mesh=n_generator_mesh, from_participant=n_generator_participant,
    to_participant=n_propagator_participant,
)
n_coupling_scheme.exchanges.append(n_exchange)

G_expected.add_edge(n_coupling_scheme, n_generator_participant, attr=Edge.COUPLING_SCHEME__PARTICIPANT_FIRST)
G_expected.add_edge(n_coupling_scheme, n_propagator_participant, attr=Edge.COUPLING_SCHEME__PARTICIPANT_SECOND)

G_expected.add_edge(n_exchange, n_coupling_scheme, attr=Edge.EXCHANGE__COUPLING_SCHEME__BELONGS_TO)
G_expected.add_edge(n_exchange, n_color, attr=Edge.EXCHANGE__DATA)
G_expected.add_edge(n_exchange, n_generator_mesh, attr=Edge.EXCHANGE__MESH)
G_expected.add_edge(n_exchange, n_generator_participant, attr=Edge.EXCHANGE__PARTICIPANT_EXCHANGED_BY)
G_expected.add_edge(n_exchange, n_propagator_participant, attr=Edge.EXCHANGE__EXCHANGES_TO)


assert nx.is_isomorphic(G_expected, G_actual),\
    f"Graphs did not match: {nx.to_dict_of_dicts(G_actual)}, {nx.to_dict_of_dicts(G_expected)}"
