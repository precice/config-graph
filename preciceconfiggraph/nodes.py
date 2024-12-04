from __future__ import annotations

from enum import Enum


class Direction(Enum):
    READ = "read"
    WRITE = "write"


class DataType(Enum):
    SCALAR = "scalar"
    VECTOR = "vector"


class ParticipantNode:
    def __init__(
        self, name: str,
        write_data: list[WriteDataNode] = None, read_data: list[ReadDataNode] = None,
        receive_meshes: list[ReceiveMeshNode] = None, provide_meshes: list[MeshNode] = None,
        mappings: list[MappingNode] = None
    ):
        self.name = name

        if write_data is None: self.write_data = []
        else: self.write_data = write_data

        if read_data is None: self.read_data = []
        else: self.read_data = read_data

        if receive_meshes is None: self.receive_meshes = []
        else: self.receive_meshes = receive_meshes

        if provide_meshes is None: self.provide_meshes = []
        else: self.provide_meshes = provide_meshes

        if mappings is None: self.mappings = []
        else: self.mappings = mappings


class MeshNode:
    def __init__(self, name: str, use_data: list[DataNode] = None, write_data: list[DataNode] = None):
        self.name = name

        if use_data is None: self.use_data = []
        else: self.use_data = use_data

        if write_data is None: self.write_data = []
        else: self.write_data = write_data


class ReceiveMeshNode:
    def __init__(self, participant: ParticipantNode, mesh: MeshNode, from_participant: ParticipantNode):
        self.participant = participant
        self.mesh = mesh
        self.from_participant = from_participant


class CouplingNode:
    def __init__(
        self,
        first_participant: ParticipantNode, second_participant: ParticipantNode,
        exchanges: list[ExchangeNode] = None
    ):
        self.first_participant = first_participant
        self.second_participant = second_participant

        if exchanges is None: self.exchanges = []
        else: self.exchanges = exchanges


class DataNode:
    def __init__(self, name: str, data_type: DataType):
        self.name = name
        self.data_type = data_type


class MappingNode:
    def __init__(self, parent_participant: ParticipantNode, direction: Direction,
                 from_mesh: MeshNode, to_mesh: MeshNode):
        self.parent_participant = parent_participant
        self.direction = direction
        self.from_mesh = from_mesh
        self.to_mesh = to_mesh


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
    def __init__(self, coupling_scheme: CouplingNode, data: DataNode, mesh: MeshNode, from_participant: ParticipantNode,
                 to_participant: ParticipantNode):
        self.coupling_scheme = coupling_scheme
        self.data = data
        self.mesh = mesh
        self.from_participant = from_participant
        self.to_participant = to_participant
