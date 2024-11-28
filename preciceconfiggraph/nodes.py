from __future__ import annotations

from enum import Enum


class Direction(Enum):
    READ = "read"
    WRITE = "write"


class DataType(Enum):
    SCALAR = "scalar"
    VECTOR = "vector"


class ParticipantNode:
    def __init__(self, name: str, write_data: list[DataNode] = [], read_data: list[DataNode] = [], receive_meshes: list[ReceiveMeshNode] = [],
                 provide_meshes: list[MeshNode] = [], mappings: list[MappingNode] = []):
        self.name = name
        self.write_data = write_data
        self.read_data = read_data
        self.receive_meshes = receive_meshes
        self.provide_meshes = provide_meshes
        self.mappings = mappings


class MeshNode:
    def __init__(self, name: str, use_data: list[DataNode] = [], write_data: list[DataNode] = []):
        self.name = name
        self.use_data = use_data
        self.write_data = write_data


class ReceiveMeshNode:
    def __init__(self, participant: ParticipantNode, mesh: MeshNode, from_participant: ParticipantNode):
        self.participant = participant
        self.mesh = mesh
        self.from_participant = from_participant


class CouplingNode:
    def __init__(self, first_participant: ParticipantNode, second_participant: ParticipantNode,
                 exchanges: list[ExchangeNode] = []):
        self.first_participant = first_participant
        self.second_participant = second_participant
        self.exchanges = exchanges


class DataNode:
    def __init__(self, name: str, data_type: DataType):
        self.name = name
        self.data_type = data_type


class MappingNode:
    def __init__(self, parent_participant: ParticipantNode, direction: Direction,
                 from_participant: ParticipantNode, to_participant: ParticipantNode):
        self.parent_participant = parent_participant
        self.direction = direction
        self.from_participant = from_participant
        self.to_participant = to_participant


class WriteDataNode:
    def __init__(self, participant: ParticipantNode, data: DataNode, mesh: MeshNode):
        self.participant = participant
        self.data = data
        self.mesh = mesh


class ReadDataNode:
    def __init__(self, participant: ParticipantNode, data: DataNode, mesh: MeshNode):
        self.participant = participant
        self.data = data
        self.mesh = mesh


class ExchangeNode:
    def __init__(self, coupling_scheme: CouplingNode, data: DataNode, from_participant: ParticipantNode,
                 to_participant: ParticipantNode):
        self.coupling_scheme = coupling_scheme
        self.data = data
        self.from_participant = from_participant
        self.to_participant = to_participant
