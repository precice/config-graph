from lxml import etree
import networkx as nx

# Taken from config-visualizer. Modified to also return postfix.
def findAllWithPrefix(e: etree._Element, prefix: str):
    for child in e.iterchildren():
        if child.tag.startswith(prefix):
            postfix = child.tag[child.tag.find(":") + 1 :]
            yield (child, postfix)


def getGraph(root: etree._Element) -> nx.DiGraph:
    assert root.tag == "precice-configuration" # TODO: Make this an error?

    G = nx.DiGraph()


    # Data items – <data:… />
    for (elem, kind) in findAllWithPrefix(root, "data"):
        # TODO: Error on unknown kind
        name = elem.attrib['name'] # TODO: Error on not found
        G.add_node(f"Data \n {name}")


    # Meshes – <mesh />
    for mesh in root.findall("mesh"):
        name = mesh.attrib['name'] # TODO: Error on not found
        mesh_node = f"Mesh \n {name}"
        G.add_node(mesh_node)

        # Data usages – <use-data />: Will be mapped to edges
        for use_data in mesh.findall("use-data"):
            data_name = use_data.attrib['name'] # TODO: Error on not found
            data_node = f"Data \n {data_name}"

            # Mesh -> Data
            G.add_edge(mesh_node, data_node) # TODO: Raise error if data not found


    # Participants – <participant />
    for participant in root.findall("participant"):
        name = participant.attrib['name'] # TODO: Error on not found
        participant_node = f"Participant \n {name}"
        G.add_node(participant_node)

        # Provide- and Receive-Mesh
        # <provide-mesh />
        for provide_mesh in participant.findall("provide-mesh"):
            mesh_name = provide_mesh.attrib['name'] # TODO: Error on not found
            mesh_node = f"Mesh \n {mesh_name}"
            G.add_edge(participant_node, mesh_node) # TODO: Raise error if mesh is not found
        # <receive-mesh />
        for receive_mesh in participant.findall("receive-mesh"):
            mesh_name = receive_mesh.attrib['name'] # TODO: Error on not found
            mesh_node = f"Mesh \n {mesh_name}"
            # TODO: Make this a node and add an edge to `from` participant
            G.add_edge(mesh_node, participant_node) # TODO: Raise error if mesh is not found
        
        # Read and write data
        # <write-data />
        for write_data in participant.findall("write-data"):
            data_name = write_data.attrib['name'] # TODO: Error on not found
            data_node = f"Data \n {data_name}"
            mesh_name = write_data.attrib['mesh'] # TODO: Error on not found
            mesh_node = f"Mesh \n {mesh_name}"

            write_data_node = f"Write-Data \n {name} {data_name} {mesh_name}"

            G.add_edge(participant_node, write_data_node)
            G.add_edge(write_data_node, participant_node)
            G.add_edge(write_data_node, mesh_node)
            G.add_edge(write_data_node, data_node)
        # <read-data />
        # TODO: Refactor to reduce code duplication
        for read_data in participant.findall("read-data"):
            data_name = read_data.attrib['name'] # TODO: Error on not found
            data_node = f"Data \n {data_name}"
            mesh_name = read_data.attrib['mesh'] # TODO: Error on not found
            mesh_node = f"Mesh \n {mesh_name}"

            read_data_node = f"Read-Data \n {name} {data_name} {mesh_name}"

            G.add_edge(participant_node, read_data_node)
            G.add_edge(read_data_node, participant_node)
            G.add_edge(mesh_node, read_data_node)
            G.add_edge(data_node, read_data_node)
        
        # Mapping
        for (mapping, kind) in findAllWithPrefix(participant, "mapping"):
            direction = mapping.attrib['direction'] # TODO: Error on not found
            from_mesh = mapping.attrib['from'] # TODO: Error on not found
            from_mesh_node = f"Mesh \n {from_mesh}"
            to_mesh = mapping.attrib['to'] # TODO: Error on not found
            to_mesh_node = f"Mesh \n {to_mesh}"

            mapping_node = f"Mapping \n {name} {direction} {from_mesh} {to_mesh}"

            G.add_edge(participant_node, mapping_node)
            G.add_edge(mapping_node, participant_node)
            G.add_edge(from_mesh_node, mapping_node) # TODO: Raise error if mesh is not found
            G.add_edge(mapping_node, to_mesh_node) # TODO: Raise error if mesh is not found


    # Coupling Scheme – <coupling-scheme:… />
    for (coupling_scheme, kind) in findAllWithPrefix(root, "coupling-scheme"):
        # <participants />
        participants = coupling_scheme.find("participants") # TODO: Error on multiple participants tags
        first_participant = participants.attrib['first'] # TODO: Error on not found
        first_participant_node = f"Participant \n {first_participant}"
        second_participant = participants.attrib['second'] # TODO: Error on not found
        second_participant_node = f"Participant \n {second_participant}"

        cs_node = f"Coupling Scheme \n {first_participant} {second_participant}"

        G.add_edge(first_participant_node, cs_node) # TODO: Raise error if participant is not found
        G.add_edge(cs_node, first_participant_node)
        G.add_edge(second_participant_node, cs_node) # TODO: Raise error if participant is not found
        G.add_edge(cs_node, second_participant_node)

        # Exchanges – <exchange />
        for exchange in coupling_scheme.findall("exchange"):
            data = exchange.attrib['data'] # TODO: Error on not found
            data_node = f"Data \n {data}"
            mesh = exchange.attrib['mesh'] # TODO: Error on not found
            mesh_node = f"Mesh \n {mesh}"
            from_participant = exchange.attrib['from'] # TODO: Error on not found and different from first or second participant
            from_participant_mesh = f"Participant \n {from_participant}"
            to_participant = exchange.attrib['to'] # TODO: Error on not found and different from first or second participant
            to_participant_mesh = f"Participant \n {to_participant}"

            exchange_node = f"Exchange \n {from_participant} {to_participant}" # TODO: Make this unique

            G.add_edge(exchange_node, cs_node)
            G.add_edge(cs_node, exchange_node)
            G.add_edge(exchange_node, data_node)
            G.add_edge(data_node, exchange_node)
            G.add_edge(exchange_node, mesh_node)
            G.add_edge(mesh_node, exchange_node)
            G.add_edge(from_participant_mesh, exchange_node)
            G.add_edge(exchange_node, to_participant_mesh)

    # M2N – <m2n:… />
    for (m2n, kind) in findAllWithPrefix(root, "m2n"):
        match kind:
            case "sockets":
                acceptor = m2n.attrib['acceptor'] # TODO: Error on not found
                acceptor_node = f"Participant \n {acceptor}"
                connector = m2n.attrib['connector'] # TODO: Error on not found
                connector_node = f"Participant \n {connector}"

                G.add_edge(acceptor_node, connector_node) # TODO: Raise error if participants are not found
            case "mpi":
                # TODO: Implement MPI
                raise NotImplementedError("MPI M2N type is not implemented")
            case _:
                raise ValueError("Unknown m2n type")


    return G
