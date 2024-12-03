from lxml import etree
import networkx as nx
import matplotlib.pyplot as plt

import nodes as n


def get_graph(root: etree._Element) -> nx.DiGraph:
    assert root.tag == "precice-configuration" # TODO: Make this an error?
    
    # Taken from config-visualizer. Modified to also return postfix.
    def find_all_with_prefix(e: etree._Element, prefix: str):
        for child in e.iterchildren():
            if child.tag.startswith(prefix):
                postfix = child.tag[child.tag.find(":") + 1 :]
                yield child, postfix


    # FIND NODES

    # Keep track of these types of nodes, since we cannot construct them on demand when referenced,
    # since the reference does not contain relevant data.
    data_nodes: dict[str, n.DataNode] = {}
    mesh_nodes: dict[str, n.MeshNode] = {}
    participant_nodes: dict[str, n.ParticipantNode] = {}
    write_data_nodes: list[n.WriteDataNode] = []
    read_data_nodes: list[n.ReadDataNode] = []
    receive_mesh_nodes: list[n.ReceiveMeshNode] = []
    coupling_nodes: list[n.CouplingNode] = []
    mapping_nodes: list[n.MappingNode] = []
    exchange_nodes: list[n.ExchangeNode] = []
    socket_edges: list[(n.ParticipantNode, n.ParticipantNode)] = []

    # Data items – <data:… />
    for (data_el, kind) in find_all_with_prefix(root, "data"):
        # TODO: Error on unknown kind
        name = data_el.attrib['name'] # TODO: Error on not found
        node = n.DataNode(name, n.DataType(kind))
        data_nodes[name] = node


    # Meshes – <mesh />
    for mesh_el in root.findall("mesh"):
        name = mesh_el.attrib['name'] # TODO: Error on not found
        mesh = n.MeshNode(name)

        # Data usages – <use-data />: Will be mapped to edges
        for use_data in mesh_el.findall("use-data"):
            data_name = use_data.attrib['name'] # TODO: Error on not found
            data_node = data_nodes[data_name] # TODO: Raise custom error if data not found
            mesh.use_data.append(data_node)
        
        # Now that mesh_node is completely built, add it to our dictionary
        mesh_nodes[name] = mesh


    # Participants – <participant />
    for participant_el in root.findall("participant"):
        name = participant_el.attrib['name'] # TODO: Error on not found
        participant = n.ParticipantNode(name)

        # Provide- and Receive-Mesh
        # <provide-mesh />
        for provide_mesh_el in participant_el.findall("provide-mesh"):
            mesh_name = provide_mesh_el.attrib['name'] # TODO: Error on not found
            participant.provide_meshes.append(mesh_nodes[mesh_name]) # TODO: Raise custom error if mesh not found
        
        # Read and write data
        # <write-data />
        for write_data_el in participant_el.findall("write-data"):
            data_name = write_data_el.attrib['name'] # TODO: Error on not found
            data = data_nodes[data_name] # TODO: Raise custom error if data not found
            mesh_name = write_data_el.attrib['mesh'] # TODO: Error on not found
            mesh = mesh_nodes[mesh_name] # TODO: Raise custom error if mesh not found

            write_data = n.WriteDataNode(participant, data, mesh)
            participant.write_data.append(write_data)
            write_data_nodes.append(write_data)

        # <read-data />
        # TODO: Refactor to reduce code duplication
        for read_data_el in participant_el.findall("read-data"):
            data_name = read_data_el.attrib['name'] # TODO: Error on not found
            data = data_nodes[data_name] # TODO: Raise custom error if data not found
            mesh_name = read_data_el.attrib['mesh'] # TODO: Error on not found
            mesh = mesh_nodes[mesh_name] # TODO: Raise custom error if mesh not found

            read_data = n.ReadDataNode(participant, data, mesh)
            participant.read_data.append(read_data)
            read_data_nodes.append(read_data)
        
        # Mapping
        for (mapping_el, kind) in find_all_with_prefix(participant_el, "mapping"):
            direction = mapping_el.attrib['direction'] # TODO: Error on not found
            from_mesh_name = mapping_el.attrib['from'] # TODO: Error on not found
            from_mesh = mesh_nodes[from_mesh_name] # TODO: Raise custom error if mesh not found
            to_mesh_name = mapping_el.attrib['to'] # TODO: Error on not found
            to_mesh = mesh_nodes[to_mesh_name] # TODO: Raise custom error if mesh not found

            mapping = n.MappingNode(participant, n.Direction(direction), from_mesh, to_mesh)
            participant.mappings.append(mapping)
            mapping_nodes.append(mapping)

        # Now that participant_node is completely built, add it and children to the graph and our dictionary
        participant_nodes[name] = participant
    
    # Receive Mesh Participants
    # This can't be done in the participants loop, since it references participants which might not yet be created
    # <participant />
    for participant_el in root.findall("participant"):
        name = participant_el.attrib['name'] # TODO: Error on not found
        participant = participant_nodes[name] # This should not fail, because we created participants before

        # <receive-mesh />
        for receive_mesh_el in participant_el.findall("receive-mesh"):
            mesh_name = receive_mesh_el.attrib['name'] # TODO: Error on not found
            mesh = mesh_nodes[mesh_name] # TODO: Raise custom error if mesh not found

            from_participant_name = receive_mesh_el.attrib['from'] # TODO: Error on not found
            from_participant = participant_nodes[from_participant_name] # TODO: Raise custom error if participant not found

            receive_mesh = n.ReceiveMeshNode(participant, mesh, from_participant)
            participant.receive_meshes.append(receive_mesh)
            receive_mesh_nodes.append(receive_mesh)


    # Coupling Scheme – <coupling-scheme:… />
    for (coupling_scheme_el, kind) in find_all_with_prefix(root, "coupling-scheme"):
        # <participants />
        participants = coupling_scheme_el.find("participants") # TODO: Error on multiple participants tags
        first_participant_name = participants.attrib['first'] # TODO: Error on not found
        first_participant = participant_nodes[first_participant_name] # TODO: Raise custom error if participant not found
        second_participant_name = participants.attrib['second'] # TODO: Error on not found
        second_participant = participant_nodes[second_participant_name] # TODO: Raise custom error if participant not found

        coupling_scheme = n.CouplingNode(first_participant, second_participant)

        # Exchanges – <exchange />
        for exchange_el in coupling_scheme_el.findall("exchange"):
            data_name = exchange_el.attrib['data'] # TODO: Error on not found
            data = data_nodes[data_name] # TODO: Raise custom error if data not found
            mesh_name = exchange_el.attrib['mesh'] # TODO: Error on not found
            mesh = mesh_nodes[mesh_name] # TODO: Raise custom error if mesh not found
            from_participant_name = exchange_el.attrib['from'] # TODO: Error on not found and different from first or second participant
            from_participant = participant_nodes[from_participant_name] # TODO: Raise custom error if participant not found
            to_participant_name = exchange_el.attrib['to'] # TODO: Error on not found and different from first or second participant
            to_participant = participant_nodes[to_participant_name] # TODO: Raise custom error if participant not found

            exchange = n.ExchangeNode(coupling_scheme, data, from_participant, to_participant)
            coupling_scheme.exchanges.append(exchange)
            exchange_nodes.append(exchange)
        
        coupling_nodes.append(coupling_scheme)


    # M2N – <m2n:… />
    for (m2n, kind) in find_all_with_prefix(root, "m2n"):
        match kind:
            case "sockets":
                acceptor_name = m2n.attrib['acceptor'] # TODO: Error on not found
                acceptor = participant_nodes[acceptor_name] # TODO: Raise custom error if participant not found
                connector_name = m2n.attrib['connector'] # TODO: Error on not found
                connector = participant_nodes[connector_name] # TODO: Raise custom error if participant not found
                socket_edges.append((acceptor, connector))
            case "mpi":
                # TODO: Implement MPI
                raise NotImplementedError("MPI M2N type is not implemented")
            case _:
                raise ValueError("Unknown m2n type")


    # BUILD GRAPH

    G = nx.DiGraph()

    for data in data_nodes.values(): G.add_node(data)

    for mesh in mesh_nodes.values():
        G.add_node(mesh)
        for data in mesh.use_data: G.add_edge(data, mesh)
        for data in mesh.write_data: G.add_edge(mesh, data)
    
    for participant in participant_nodes.values():
        G.add_node(participant)
        for mesh in participant.provide_meshes: G.add_edge(participant, mesh)
        # Use data and write data, as well as receive mesh nodes are added later
    
    for read_data in read_data_nodes:
        G.add_node(read_data)
        G.add_edge(read_data.data, read_data)
        G.add_edge(read_data.mesh, read_data)
        G.add_edge(read_data.participant, read_data)
        G.add_edge(read_data, read_data.participant)

    for write_data in read_data_nodes:
        G.add_node(write_data)
        G.add_edge(write_data, write_data.data)
        G.add_edge(write_data, write_data.mesh)
        G.add_edge(write_data.participant, write_data)
        G.add_edge(write_data, write_data.participant)
    
    for receive_mesh in receive_mesh_nodes:
        G.add_node(receive_mesh)
        G.add_edge(receive_mesh.from_participant, receive_mesh)
        G.add_edge(receive_mesh.mesh, receive_mesh)
        G.add_edge(receive_mesh, receive_mesh.participant)
    
    for mapping in mapping_nodes:
        G.add_node(mapping)
        G.add_edge(mapping, mapping.to_mesh)
        G.add_edge(mapping.from_mesh, mapping)
        G.add_edge(mapping, mapping.parent_participant)
        G.add_edge(mapping.parent_participant, mapping)
    
    for coupling in coupling_nodes:
        G.add_node(coupling)
        # Edges to and from exchanges will be added by exchange nodes
        G.add_edge(coupling.first_participant, coupling)
        G.add_edge(coupling, coupling.first_participant)
        G.add_edge(coupling.second_participant, coupling)
        G.add_edge(coupling, coupling.second_participant)
    
    for exchange in exchange_nodes:
        G.add_node(exchange)
        G.add_edge(exchange.from_participant, exchange)
        G.add_edge(exchange, exchange.to_participant)
        G.add_edge(data, exchange)
        G.add_edge(exchange, data)
        G.add_edge(exchange, exchange.coupling_scheme)
        G.add_edge(exchange.coupling_scheme, exchange)
    
    for (acceptor, connector) in socket_edges:
        G.add_edge(acceptor, connector)

    return G

def print_graph(graph: nx.DiGraph):
    def color_for_node(node):
        match node:
            case n.DataNode():
                return [1, 0.3, 0]
            case n.ReadDataNode() | n.WriteDataNode():
                return [1, 0.5, 0.5]
            case n.MeshNode():
                return [0.9, 0.6, 0]
            case n.ReceiveMeshNode():
                return [0.95, 0.75, 0]
            case n.ParticipantNode():
                return [0.3, 0.6, 1.0]
            case n.ExchangeNode():
                return [0.9, 0.9, 0.9]
            case n.CouplingNode():
                return [0.7, 0.7, 0.7]
            case n.WriteDataNode():
                return [0.7, 0, 1.0]
            case n.MappingNode():
                return [0.1, 0.7, 0.1]
            case _:
                return [0.5, 0.5, 0.5]

    def size_for_node(node):
        match node:
            case n.ParticipantNode():
                return 800
            case n.DataNode(), n.MeshNode():
                return 600
            case _:
                return 300

    node_colors = [color_for_node(n) for n in graph.nodes()]
    node_sizes = [size_for_node(n) for n in graph.nodes()]
    node_labels = dict()
    for node in graph.nodes():
        match node:
            case n.ParticipantNode() | n.MeshNode() | n.DataNode():
                node_labels[node] = node.name
            case n.CouplingNode():
                node_labels[node] = "Coupling"
            case n.ExchangeNode():
                node_labels[node] = "Exchange"
            case n.MappingNode():
                node_labels[node] = f"Mapping ({node.direction})"
            case n.WriteDataNode():
                node_labels[node] = f"Write {node.data.name}"
            case n.ReadDataNode():
                node_labels[node] = f"Read {node.data.name}"
            case n.ReceiveMeshNode():
                node_labels[node] = f"Receive {node.mesh.name}"
            case _:
                node_labels[node] = ""

    nx.draw(graph, with_labels=True, arrows=True, pos=nx.spring_layout(graph), node_color=node_colors, node_size=node_sizes, labels=node_labels)
    plt.show()
