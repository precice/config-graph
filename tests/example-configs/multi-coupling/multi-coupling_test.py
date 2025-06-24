import networkx as nx

from precice_config_graph import graph, xml_processing
from precice_config_graph import nodes as n
from precice_config_graph.edges import Edge
from precice_config_graph.nodes import (
    DataType,
    Direction,
    M2NType,
    MappingMethod,
    MappingConstraint,
)


def test_graph():
    xml = xml_processing.parse_file(
        "tests/example-configs/multi-coupling/precice-config.xml"
    )
    G_actual = graph.get_graph(xml)

    edges = []

    # Data
    n_data_forces1 = n.DataNode("Forces1", DataType.VECTOR)
    n_data_forces2 = n.DataNode("Forces2", DataType.VECTOR)
    n_data_forces3 = n.DataNode("Forces3", DataType.VECTOR)
    n_data_displacements1 = n.DataNode("Displacements1", DataType.VECTOR)
    n_data_displacements2 = n.DataNode("Displacements2", DataType.VECTOR)
    n_data_displacements3 = n.DataNode("Displacements3", DataType.VECTOR)

    # Meshes
    n_mesh_nastin1 = n.MeshNode("NASTIN_Mesh1", [n_data_forces1])
    n_mesh_solidz1 = n.MeshNode("SOLIDZ_Mesh1", [n_data_displacements1, n_data_forces1])
    n_mesh_nastin2 = n.MeshNode("NASTIN_Mesh2", [n_data_forces2])
    n_mesh_solidz2 = n.MeshNode("SOLIDZ_Mesh2", [n_data_displacements2, n_data_forces2])
    n_mesh_nastin3 = n.MeshNode("NASTIN_Mesh3", [n_data_forces3])
    n_mesh_solidz3 = n.MeshNode("SOLIDZ_Mesh3", [n_data_displacements3, n_data_forces3])

    meshes = [
        n_mesh_nastin1,
        n_mesh_solidz1,
        n_mesh_nastin2,
        n_mesh_solidz2,
        n_mesh_nastin3,
        n_mesh_solidz3,
    ]
    for mesh in meshes:
        edges += [(mesh, data, Edge.USE_DATA) for data in mesh.use_data]

    # SOLIDZ participants
    n_participant_solizd1 = n.ParticipantNode(
        "SOLIDZ1", provide_meshes=[n_mesh_solidz1]
    )
    n_participant_solizd1.write_data = [
        n.WriteDataNode(
            data=n_data_displacements1,
            mesh=n_mesh_solidz1,
            participant=n_participant_solizd1,
        )
    ]
    n_participant_solizd1.read_data = [
        n.ReadDataNode(
            data=n_data_forces1, mesh=n_mesh_solidz1, participant=n_participant_solizd1
        )
    ]

    n_participant_solizd2 = n.ParticipantNode(
        "SOLIDZ2", provide_meshes=[n_mesh_solidz2]
    )
    n_participant_solizd2.write_data = [
        n.WriteDataNode(
            data=n_data_displacements2,
            mesh=n_mesh_solidz2,
            participant=n_participant_solizd2,
        )
    ]
    n_participant_solizd2.read_data = [
        n.ReadDataNode(
            data=n_data_forces2, mesh=n_mesh_solidz2, participant=n_participant_solizd2
        )
    ]

    n_participant_solizd3 = n.ParticipantNode(
        "SOLIDZ3", provide_meshes=[n_mesh_solidz3]
    )
    n_participant_solizd3.write_data = [
        n.WriteDataNode(
            data=n_data_displacements3,
            mesh=n_mesh_solidz3,
            participant=n_participant_solizd3,
        )
    ]
    n_participant_solizd3.read_data = [
        n.ReadDataNode(
            data=n_data_forces3, mesh=n_mesh_solidz3, participant=n_participant_solizd3
        )
    ]

    # NASTIN participant
    n_participant_nastin = n.ParticipantNode(
        "NASTIN",
        provide_meshes=[n_mesh_nastin1, n_mesh_nastin2, n_mesh_nastin3],
    )

    edges += [
        (n_participant_nastin, mesh, Edge.PROVIDE_MESH__PARTICIPANT_PROVIDES)
        for mesh in n_participant_nastin.provide_meshes
    ]

    n_participant_nastin.receive_meshes = [
        n.ReceiveMeshNode(
            mesh=mesh,
            from_participant=from_participant,
            participant=n_participant_nastin,
            api_access=False,
        )
        for (mesh, from_participant) in [
            (n_mesh_solidz1, n_participant_solizd1),
            (n_mesh_solidz2, n_participant_solizd2),
            (n_mesh_solidz3, n_participant_solizd3),
        ]
    ]
    n_participant_nastin.write_data = [
        n.WriteDataNode(data=data, mesh=mesh, participant=n_participant_nastin)
        for (mesh, data) in [
            (n_mesh_nastin1, n_data_forces1),
            (n_mesh_nastin2, n_data_forces2),
            (n_mesh_nastin3, n_data_forces3),
        ]
    ]
    n_participant_nastin.mappings = [
        n.MappingNode(
            parent_participant=n_participant_nastin,
            direction=Direction.WRITE,
            just_in_time=False,
            method=MappingMethod.NEAREST_NEIGHBOR,
            constraint=MappingConstraint.CONSERVATIVE,
            from_mesh=from_mesh,
            to_mesh=to_mesh,
        )
        for (from_mesh, to_mesh) in [
            (n_mesh_nastin1, n_mesh_solidz1),
            (n_mesh_nastin2, n_mesh_solidz2),
            (n_mesh_nastin3, n_mesh_solidz3),
        ]
    ]

    participants = [
        n_participant_solizd1,
        n_participant_solizd2,
        n_participant_solizd3,
        n_participant_nastin,
    ]

    edges += [
        (participant, mesh, Edge.PROVIDE_MESH__PARTICIPANT_PROVIDES)
        for participant in participants
        for mesh in participant.provide_meshes
    ]

    edges += (
        [
            (read_data, participant, Edge.READ_DATA__PARTICIPANT__BELONGS_TO)
            for participant in participants
            for read_data in participant.read_data
        ]
        + [
            (read_data, read_data.data, Edge.READ_DATA__DATA_READ_BY)
            for participant in participants
            for read_data in participant.read_data
        ]
        + [
            (read_data, read_data.mesh, Edge.READ_DATA__MESH_READ_BY)
            for participant in participants
            for read_data in participant.read_data
        ]
    )

    edges += (
        [
            (
                receive_mesh,
                n_participant_nastin,
                Edge.RECEIVE_MESH__PARTICIPANT__BELONGS_TO,
            )
            for participant in participants
            for receive_mesh in participant.receive_meshes
        ]
        + [
            (receive_mesh, receive_mesh.mesh, Edge.RECEIVE_MESH__MESH)
            for participant in participants
            for receive_mesh in participant.receive_meshes
        ]
        + [
            (
                receive_mesh,
                receive_mesh.from_participant,
                Edge.RECEIVE_MESH__PARTICIPANT_RECEIVED_FROM,
            )
            for participant in participants
            for receive_mesh in participant.receive_meshes
        ]
    )

    edges += (
        [
            (write_data, participant, Edge.WRITE_DATA__PARTICIPANT__BELONGS_TO)
            for participant in participants
            for write_data in participant.write_data
        ]
        + [
            (write_data, write_data.data, Edge.WRITE_DATA__WRITES_TO_DATA)
            for participant in participants
            for write_data in participant.write_data
        ]
        + [
            (write_data, write_data.mesh, Edge.WRITE_DATA__WRITES_TO_MESH)
            for participant in participants
            for write_data in participant.write_data
        ]
    )

    edges += (
        [
            (mapping, n_participant_nastin, Edge.MAPPING__PARTICIPANT__BELONGS_TO)
            for participant in participants
            for mapping in participant.mappings
        ]
        + [
            (mapping, mapping.from_mesh, Edge.MAPPING__FROM_MESH)
            for participant in participants
            for mapping in participant.mappings
        ]
        + [
            (mapping, mapping.to_mesh, Edge.MAPPING__TO_MESH)
            for participant in participants
            for mapping in participant.mappings
        ]
    )

    # M2N nodes
    m2n_nastin_solidz1 = n.M2NNode(
        M2NType.SOCKETS, n_participant_nastin, n_participant_solizd1
    )
    m2n_nastin_solidz2 = n.M2NNode(
        M2NType.SOCKETS, n_participant_nastin, n_participant_solizd2
    )
    m2n_nastin_solidz3 = n.M2NNode(
        M2NType.SOCKETS, n_participant_nastin, n_participant_solizd3
    )

    edges += [
        (m2n_nastin_solidz1, n_participant_nastin, Edge.M2N__PARTICIPANT_ACCEPTOR),
        (m2n_nastin_solidz1, n_participant_solizd1, Edge.M2N__PARTICIPANT_CONNECTOR),
    ]
    edges += [
        (m2n_nastin_solidz2, n_participant_nastin, Edge.M2N__PARTICIPANT_ACCEPTOR),
        (m2n_nastin_solidz2, n_participant_solizd2, Edge.M2N__PARTICIPANT_CONNECTOR),
    ]
    edges += [
        (m2n_nastin_solidz3, n_participant_nastin, Edge.M2N__PARTICIPANT_ACCEPTOR),
        (m2n_nastin_solidz3, n_participant_solizd3, Edge.M2N__PARTICIPANT_CONNECTOR),
    ]

    # Couping scheme
    n_coupling_scheme = n.MultiCouplingSchemeNode(
        participants=[
            n_participant_solizd1,
            n_participant_solizd2,
            n_participant_nastin,
            n_participant_solizd3,
        ],
        control_participant=n_participant_nastin,
    )

    edges += [
        (n_coupling_scheme, participant, Edge.MULTI_COUPLING_SCHEME__PARTICIPANT)
        for participant in n_coupling_scheme.participants
    ] + [
        (
            n_coupling_scheme,
            n_participant_nastin,
            Edge.MULTI_COUPLING_SCHEME__PARTICIPANT__CONTROL,
        )
    ]

    n_exchange_forces1 = n.ExchangeNode(
        coupling_scheme=n_coupling_scheme,
        data=n_data_forces1,
        mesh=n_mesh_solidz1,
        from_participant=n_participant_nastin,
        to_participant=n_participant_solizd1,
    )
    n_exchange_forces2 = n.ExchangeNode(
        coupling_scheme=n_coupling_scheme,
        data=n_data_forces2,
        mesh=n_mesh_solidz2,
        from_participant=n_participant_nastin,
        to_participant=n_participant_solizd2,
    )
    n_exchange_forces3 = n.ExchangeNode(
        coupling_scheme=n_coupling_scheme,
        data=n_data_forces3,
        mesh=n_mesh_solidz3,
        from_participant=n_participant_nastin,
        to_participant=n_participant_solizd3,
    )
    n_exchange_displacements1 = n.ExchangeNode(
        coupling_scheme=n_coupling_scheme,
        data=n_data_displacements1,
        mesh=n_mesh_solidz1,
        from_participant=n_participant_solizd1,
        to_participant=n_participant_nastin,
    )
    n_exchange_displacements2 = n.ExchangeNode(
        coupling_scheme=n_coupling_scheme,
        data=n_data_displacements2,
        mesh=n_mesh_solidz2,
        from_participant=n_participant_solizd2,
        to_participant=n_participant_nastin,
    )
    n_exchange_displacements3 = n.ExchangeNode(
        coupling_scheme=n_coupling_scheme,
        data=n_data_displacements3,
        mesh=n_mesh_solidz3,
        from_participant=n_participant_solizd3,
        to_participant=n_participant_nastin,
    )
    exchanges = [
        n_exchange_forces1,
        n_exchange_forces2,
        n_exchange_forces3,
        n_exchange_displacements1,
        n_exchange_displacements2,
        n_exchange_displacements3,
    ]
    n_coupling_scheme.exchanges = exchanges

    edges += (
        [
            (exchange, n_coupling_scheme, Edge.EXCHANGE__COUPLING_SCHEME__BELONGS_TO)
            for exchange in exchanges
        ]
        + [(exchange, exchange.data, Edge.EXCHANGE__DATA) for exchange in exchanges]
        + [(exchange, exchange.mesh, Edge.EXCHANGE__MESH) for exchange in exchanges]
        + [
            (exchange, exchange.from_participant, Edge.EXCHANGE__EXCHANGED_FROM)
            for exchange in exchanges
        ]
        + [
            (exchange, exchange.to_participant, Edge.EXCHANGE__EXCHANGES_TO)
            for exchange in exchanges
        ]
    )

    acceleration = n.AccelerationNode(n_coupling_scheme, n.AccelerationType.IQN_ILS)
    n_coupling_scheme.accelerations.append(acceleration)
    acceleration_data1 = n.AccelerationDataNode(
        acceleration, n_data_forces1, n_mesh_solidz1
    )
    acceleration_data2 = n.AccelerationDataNode(
        acceleration, n_data_forces2, n_mesh_solidz2
    )
    acceleration_data3 = n.AccelerationDataNode(
        acceleration, n_data_forces3, n_mesh_solidz3
    )
    acceleration.data.append(acceleration_data1)
    acceleration.data.append(acceleration_data2)
    acceleration.data.append(acceleration_data3)

    edges += (
        [
            (
                acceleration,
                acceleration.coupling_scheme,
                Edge.ACCELERATION__COUPLING_SCHEME__BELONGS_TO,
            )
        ]
        + [
            (
                data_node,
                data_node.acceleration,
                Edge.ACCELERATION_DATA__ACCELERATION__BELONGS_TO,
            )
            for data_node in acceleration.data
        ]
        + [
            (data_node, data_node.data, Edge.ACCELERATION_DATA__DATA)
            for data_node in acceleration.data
        ]
        + [
            (data_node, data_node.mesh, Edge.ACCELERATION_DATA__MESH)
            for data_node in acceleration.data
        ]
    )

    convergence_measures = [
        n.ConvergenceMeasureNode(
            n_coupling_scheme,
            n.ConvergenceMeasureType.RELATIVE,
            n_data_displacements1,
            n_mesh_solidz1,
        ),
        n.ConvergenceMeasureNode(
            n_coupling_scheme,
            n.ConvergenceMeasureType.RELATIVE,
            n_data_displacements2,
            n_mesh_solidz2,
        ),
        n.ConvergenceMeasureNode(
            n_coupling_scheme,
            n.ConvergenceMeasureType.RELATIVE,
            n_data_displacements3,
            n_mesh_solidz3,
        ),
        n.ConvergenceMeasureNode(
            n_coupling_scheme,
            n.ConvergenceMeasureType.RELATIVE,
            n_data_forces1,
            n_mesh_solidz1,
        ),
        n.ConvergenceMeasureNode(
            n_coupling_scheme,
            n.ConvergenceMeasureType.RELATIVE,
            n_data_forces2,
            n_mesh_solidz2,
        ),
        n.ConvergenceMeasureNode(
            n_coupling_scheme,
            n.ConvergenceMeasureType.RELATIVE,
            n_data_forces3,
            n_mesh_solidz3,
        ),
    ]

    edges += (
        [
            (
                convergence_measure,
                convergence_measure.coupling_scheme,
                Edge.CONVERGENCE_MEASURE__COUPLING_SCHEME__BELONGS_TO,
            )
            for convergence_measure in convergence_measures
        ]
        + [
            (
                convergence_measure,
                convergence_measure.data,
                Edge.CONVERGENCE_MEASURE__DATA,
            )
            for convergence_measure in convergence_measures
        ]
        + [
            (
                convergence_measure,
                convergence_measure.mesh,
                Edge.CONVERGENCE_MEASURE__MESH,
            )
            for convergence_measure in convergence_measures
        ]
    )

    G_expected = nx.Graph()
    for (node_a, node_b, attr) in edges:
        G_expected.add_edge(node_a, node_b, attr=attr)

    def node_match(node_a, node_b):
        return node_a == node_b

    def edge_match(edge_a, edge_b):
        return edge_a["attr"] == edge_b["attr"]

    assert nx.is_isomorphic(
        G_expected, G_actual, node_match=node_match, edge_match=edge_match
    ), (
        f"Graphs did not match. Some stats: Expected: (num nodes: {len(G_expected.nodes)}, num edges: {len(G_expected.edges)}), "
        + f"Actual: (num nodes: {len(G_actual.nodes)}, num edges: {len(G_actual.edges)})"
    )

    print("\nGraphs are isomorphic.")
