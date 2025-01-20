"""
This graph is intended for the preCICE logical-checker https://github.com/precice-forschungsprojekt/config-checker.

You can find documentation under README.md, docs/Nodes.md and docs/Edges.md.

This graph was developed by Simon Wazynski, Alexander Hutter and Orlando Ackermann as part of https://github.com/precice-forschungsprojekt.
"""

from enum import Enum

class Edge(Enum):
    # mesh --received-by-> receive-mesh
    RECEIVE_MESH__MESH_RECEIVED_BY = "receive-mesh_mesh-received-by"
    # participant (from) --received-by-> receive-mesh
    RECEIVE_MESH__PARTICIPANT_RECEIVED_BY = "receive-mesh_participant-received-by"
    # The connection between receive-mesh and participant it is part of
    RECEIVE_MESH__CHILD_OF = "receive-mesh_child-of"

    # participant --provides-> mesh
    PROVIDE_MESH__PARTICIPANT_PROVIDES = "provide-mesh_participant-provides"

    # mapping --to-> mesh
    MAPPING__TO_MESH = "mapping_to-mesh"
    # mesh --mapped-by-> mapping
    MAPPING__FROM_MESH = "mapping_from-mesh"
    # The connection between mapping and participant it is part of
    MAPPING__PARTICIPANT_PARENT_OF = "mapping_participant-parent-of"
    MAPPING__CHILD_OF = "mapping_child-of"

    # participant (from) --exchanged_by--> exchange
    EXCHANGE__PARTICIPANT_EXCHANGED_BY = "exchange_participant-exchanged-by"
    # exchange --exchanges-to--> participant (to)
    EXCHANGE__EXCHANGES_TO = "exchange_exchanges-to"
    # exchange <--> data
    EXCHANGE__DATA = "exchange_data"
    # exchange <--> mesh
    EXCHANGE__MESH = "exchange_mesh"
    # The connection between exchange and coupling scheme it is part of
    EXCHANGE__CHILD_OF = "exchange_child-of"
    EXCHANGE__COUPLING_SCHEME_PARENT_OF = "exchange_coupling-scheme-parent-of"

    # participant (connector) -> participant (acceptor)
    SOCKET = "socket"

    # participant (first) <--> coupling-scheme
    COUPLING_SCHEME__PARTICIPANT_FIRST = "coupling-scheme_participant-first"
    # participant (second) <--> coupling-scheme
    COUPLING_SCHEME__PARTICIPANT_SECOND = "coupling-scheme_participant-second"

    # mesh --"uses"--> data
    USE_DATA = "use-data"

    # write-data --writes-to-> data
    WRITE_DATA__WRITES_TO_DATA = "write-data_writes-to-data"
    # write-data --writes-to-> mesh
    WRITE_DATA__WRITES_TO_MESH = "write-data_writes-to-mesh"
    # The connection between write-data and participant it is part of
    WRITE_DATA__PARTICIPANT_PARENT_OF = "write-data_participant-parent-of"
    WRITE_DATA__CHILD_OF = "write-data_child-of"

    # data --read-by-> read-data
    READ_DATA__DATA_READ_BY = "read-data_data-read-by"
    # mesh --read-by-> read-data
    READ_DATA__MESH_READ_BY = "read-data_mesh-read-by"
    # The connection between read-data and participant it is part of
    READ_DATA__PARTICIPANT_PARENT_OF = "read-data_participant-parent-of"
    READ_DATA__CHILD_OF = "read-data_child-of"

    # connection between participant and export node
    EXPORT__CHILD_OF = "export_child-of"
    EXPORT__PARENT_PARTICIPANT_OF = "export_participant-parent-of"

    # multi coupling: control participant
    MULTI_COUPLING_SCHEME__PARTICIPANT_CONTROL = "multi-coupling-scheme_participant-control"
    # multi coupling: all participants (this includes regular ones, as well as control participants (they have two edges))
    MULTI_COUPLING_SCHEME__PARTICIPANT = "multi-coupling-scheme_participant"

    # connection between actions and its members
    ACTION_PARTICIPANT = "action_participant"
    ACTION_MESH = "action_mesh"
    ACTION_TARGET_DATA = "action_target-data"
    ACTION_SOURCE_DATA = "action_source-data"

    # connection between watchpoints/-integrals and their participants / meshes
    WATCH_POINT_PARTICIPANT = "watch-point_participant"
    WATCH_POINT_MESH = "watch-point_mesh"

    WATCH_INTEGRAL_PARTICIPANT = "watch-integral_participant"
    WATCH_INTEGRAL_MESH = "watch-integral_mesh"

