class Node:
    def __init__(self, name):
        self.name = name


class ParticipantNode(Node):
    # TODO new attribute socket-connected participant?
    def __init__(self, name, write_data, read_data, receive_mesh, provide_mesh, mapping):
        self.name = name
        self.write_data = write_data
        self.read_data = read_data
        self.receive_mesh = receive_mesh
        self.provide_mesh = provide_mesh
        self.mapping = mapping


class MeshNode(Node):
    # TODO dimensions attribute?
    def __init__(self, name, use_data, write_data):
        self.name = name
        self.use_data = use_data
        self.write_data = write_data


class CouplingNode(Node):
    def __init__(self, name, first_participant, second_participant, data, mesh, from_participant, to_participant):
        self.name = name
        self.first_participant = first_participant
        self.second_participant = second_participant
        self.data = data
        self.mesh = mesh
        self.from_participant = from_participant
        self.to_participant = to_participant


class DataNode(Node):
    # TODO used_by_participants as array? used_by_mesh also array? used_by_mapping also array?
    #  used_by_coupling/exchange
    def __init__(self, name):
        self.name = name


class MappingNode(Node):
    def __init__(self, name, direction, from_participant, to_participant):
        self.name = name
        self.direction = direction
        self.from_participant = from_participant
        self.to_participant = to_participant


class WriteDataNode(Node):
    # TODO is name needed here? name or data, one is redundant
    def __init__(self, name, participant, data, mesh):
        self.name = name
        self.participant = participant
        self.data = data
        self.mesh = mesh

class ReadDataNode(Node):
    # TODO is name needed here? name or data, one is redundant
    def __init__(self, name, participant, data, mesh):
        self.name = name
        self.participant = participant
        self.data = data
        self.mesh = mesh

class ExchangeNode(Node):
    # TODO is name needed here? name or data, one is redundant
    def __init__(self, name, coupling_scheme, data, from_participant, to_participant ):
        self.name = name
        self.coupling_scheme = coupling_scheme
        self.data = data
        self.from_participant = from_participant
        self.to_participant = to_participant
