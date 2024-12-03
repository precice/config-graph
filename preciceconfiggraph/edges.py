from enum import Enum


class Edge(Enum):
    RECEIVE_MESH = "receive-mesh"
    PROVIDE_MESH = "provide-mesh"

    MAPPING = "mapping"
    EXCHANGE = "exchange"
    SOCKET = "socket"
    COUPLING_SCHEME = "coupling-scheme"

    USE_DATA = "use-data"
    WRITE_DATA = "write-data"
    READ_DATA = "read-data"
