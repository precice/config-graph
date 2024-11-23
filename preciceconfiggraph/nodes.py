class ParticipantNode:
    def __init__(self, name, write_data, read_data, receive_mesh, provide_mesh, mapping):
        self.name = name
        self.write_data = write_data
        self.read_data = read_data
        self.receive_mesh = receive_mesh
        self.provide_mesh = provide_mesh
        self.mapping = mapping


class MeshNode:
    def __init__(self, name, use_data, write_data):
        self.name = name
        self.use_data = use_data
        self.write_data = write_data


class CouplingNode:
    def __init__(self, name, first_participant, second_participant, data, mesh, from_participant, to_participant):
        self.name = name
        self.first_participant = first_participant
        self.second_participant = second_participant
        self.data = data
        self.mesh = mesh
        self.from_participant = from_participant
        self.to_participant = to_participant


class DataNode:
    def __init__(self, name):
        self.name = name


class MappingNode:
    def __init__(self, name, parent, direction, from_participant, to_participant):
        self.name = name
        self.parent = parent
        self.direction = direction
        self.from_participant = from_participant
        self.to_participant = to_participant


class WriteDataNode:
    def __init__(self, participant, data, mesh):
        self.participant = participant
        self.data = data
        self.mesh = mesh


class ReadDataNode:
    def __init__(self, participant, data, mesh):
        self.participant = participant
        self.data = data
        self.mesh = mesh


class ExchangeNode:
    def __init__(self, coupling_scheme, data, from_participant, to_participant):
        self.coupling_scheme = coupling_scheme
        self.data = data
        self.from_participant = from_participant
        self.to_participant = to_participant
