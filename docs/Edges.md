# Edges

This project builds a graph based on a precice-config.xml file. The nodes in the graph correspond to the specified xml
elements and tags.<br>
The documentation for preCICE's config tags can be read
at [preCICE XML reference](https://precice.org/configuration-xml-reference.html).<br>
The edges mainly add redundancies to allow future checks to be less complex.

> [!NOTE]
> This graph is built for the [preCICE logic checker](https://github.com/precice-forschungsprojekt/config-checker). This
> means that there may redundancies or “inconsistencies” in the building of the graph itself.

Edges are modeled as an enum. The “type” of the edge is important for the checker;
for the graph the type defines a label for the edge.

Here you will find a list with brief explanations of each edge.
As the graph is undirected, the `to` and `from` entries correspond only to the reading direction of the edge's `label`.

- `type`: The type of the edge.
- `from`: The type of the origin-node.
- `to`: The type of the destination-node.
- `label`: The label as shown in the debugging view of the graph. If this is missing, then the edge does not have a
  label.

## Receive-mesh - mesh

This edge connects a receive-mesh node and the mesh that it actually refers to.

- `type`: RECEIVE_MESH__MESH
- `from`: ReceiveMesh
- `to`: Mesh
- `label`:

## Participant - Receive-mesh

This edge connects a participant and a receive-mesh node. The participant is the one who the mesh is received from (the
participant who provides the mesh. In the context of a receive-mesh node, the receive-mesh gets received from this
participant).

- `type`: RECEIVE_MESH__PARTICIPANT_RECEIVED_FROM
- `from`: Participant
- `to`: ReceiveMesh
- `label`: received from

## Receive-mesh - participant

This edge connects a receive-mesh node and a participant who receives the mesh and defined the <receive-mesh .../> tag.

- `type`: RECEIVE_MESH__PARTICIPANT__BELONGS_TO
- `from`: ReceiveMesh
- `to`: Participant
- `label`: belongs to

## Participant - mesh

This edge connects a participant and the meshes that it provides.

- `type`: PROVIDE_MESH__PARTICIPANT_PROVIDES
- `from`: Participant
- `to`: Mesh
- `label`: provides

## Mapping - mesh

This edge connects a mapping and the to-mesh of it.

- `type`: MAPPING__TO_MESH
- `from`: Mapping
- `to`: Mesh
- `label`: to

## Mapping - mesh

This edge connects a mapping and the from-mesh of it.

- `type`: MAPPING__FROM_MESH
- `from`: Mapping
- `to`: Mesh
- `label`: from

## Mapping - participant

This edge connects a mapping and the participant it is part of.

- `type`: MAPPING__PARTICIPANT__BELONGS_TO
- `from`: Mapping
- `to`: Participant
- `label`: belongs to

## Participant - exchange

This edge connects a participant with an exchange. This edge is to identify the "from" participant.

- `type`: EXCHANGE__EXCHANGED_FROM
- `from`: Participant
- `to`: Exchange
- `label`: from

## Exchange - participant

This edge connects an exchange with a participant. This edge specifically connects to the "to" participant of the
exchange.

- `type`: EXCHANGE__EXCHANGES_TO
- `from`: Exchange
- `to`: Participant
- `label`: to

## Exchange - data

This edge connects data with exchanges using its data. This edge is undirected.

- `type`: EXCHANGE__DATA
- `from/to`: Exchange
- `to/from`: Data
- `label`:

## Exchange - mesh

This edge connects exchange nodes with the mesh that is being used in the exchange.

- `type`: EXCHANGE__MESH
- `from/to`: Exchange
- `to/from`: Mesh
- `label`:

## Coupling-scheme - exchange

This edge connects a coupling scheme with its exchanges.

- `type`: EXCHANGE__COUPLING_SCHEME__BELONGS_TO
- `from`: Exchange
- `to`: Coupling-scheme
- `label`: belongs to

## Coupling-scheme - acceleration

This edge connects a coupling scheme with its accelerations.

- `type`: ACCELERATION__COUPLING_SCHEME__BELONGS_TO
- `from`: Acceleration
- `to`: Coupling-scheme
- `label`: belongs to

## Acceleration-data - data

This edge connects a data with an acceleration-data.

- `type`: ACCELERATION_DATA__DATA
- `from`: Acceleration-data
- `to`: Data
- `label`: data

## Acceleration-data - mesh

This edge connects a mesh with an acceleration-data.

- `type`: ACCELERATION_DATA__MESH
- `from`: Acceleration-data
- `to`: Mesh
- `label`: mesh

## Acceleration - acceleration-data

This edge connects a acceleration with its acceleration-datas.

- `type`: ACCELERATION_DATA__ACCELERATION__BELONGS_TO
- `from`: Acceleration-data
- `to`: Acceleration
- `label`: accelerates

## Coupling-scheme - convergence-measure

This edge connects a coupling scheme with its convergence-measures.

- `type`: CONVERGENCE_MEASURE__COUPLING_SCHEME__BELONGS_TO
- `from`: Convergence-measure
- `to`: Coupling-scheme
- `label`: belongs to

## Convergence-measure - data

This edge connects a data with a convergence-measure.

- `type`: CONVERGENCE_MEASURE__DATA
- `from`: Convergence-measure
- `to`: Data
- `label`: data

## Convergence-measure - mesh

This edge connects a mesh with an convergence-measure.

- `type`: CONVERGENCE_MEASURE__MESH
- `from`: Convergence-measure
- `to`: Mesh
- `label`: mesh

## M2N - participant

This edge connects the "acceptor" participant and its m2n node.

- `type`: M2N__PARTICIPANT_ACCEPTOR
- `from`: M2N
- `to`: Participant
- `label`: acceptor

## M2N - participant

This edge connects the "connector" participant and its m2n node.

- `type`: M2N__PARTICIPANT_CONNECTOR
- `from`: M2N
- `to`: Participant
- `label`: connector

## Coupling-scheme - participant

This edge connects a coupling-scheme with its "first" participant.

- `type`: COUPLING_SCHEME__PARTICIPANT_FIRST
- `from/to`: CouplingScheme
- `to/from`: Participant
- `label`: first

## Coupling-scheme - participant

This edge connects a coupling-scheme with its "second" participant.

- `type`: COUPLING_SCHEME__PARTICIPANT_SECOND
- `from/to`: CouplingScheme
- `to/from`: Participant
- `label`: second

## Mesh - data

This edge connects a mesh to the data it uses.

- `type`: USE_DATA
- `from`: Mesh
- `to`: Data
- `label`: uses

## Write-data - data

This edge connects a write-data node to the data it writes.

- `type`: WRITE_DATA__WRITES_TO_DATA
- `from`: WriteData
- `to`: Data
- `label`: writes to

## Write-data - mesh

This edge connects a write-data node with the mesh it is written to.

- `type`: WRITE_DATA__WRITES_TO_MESH
- `from`: WriteData
- `to`: Mesh
- `label`: writes to

## Write-data - participant

This edge connects a write-data node with the participant who specified it.

- `type`: WRITE_DATA__PARTICIPANT__BELONGS_TO
- `from`: WriteData
- `to`: Participant
- `label`: belongs to

## Data - read-data

This edge connects a data node to read-data nodes who read it.

- `type`: READ_DATA__DATA_READ_BY
- `from`: Data
- `to`: ReadData
- `label`: read by

## Mesh - read-data

This edge connects a mesh to its read-data node.

- `type`: READ_DATA__MESH_READ_BY
- `from`: Mesh
- `to`: ReadData
- `label`: read by

## Read-data - participant

This edge connects a read-data node to the participant specifying it.

- `type`: READ_DATA__PARTICIPANT__BELONGS_TO
- `from`: ReadData
- `to`: Participant
- `label`: belongs to

## Export - participant

This edge connects an export node to the participant who specified it.

- `type`: EXPORT__PARTICIPANT__BELONGS_TO
- `from`: Export
- `to`: Participant
- `label`: belongs to

## Multi-coupling-scheme - participant

This edge connects a multi-coupling-scheme with its "control" participant.

- `type`: MULTI_COUPLING_SCHEME__PARTICIPANT_CONTROL
- `from`: MultiCouplingScheme
- `to`: Participant
- `label`: control

## Multi-coupling-scheme - participant

This edge connects a multi-coupling-scheme with its _regular_ participants.

- `type`: MULTI_COUPLING_SCHEME__PARTICIPANT
- `from`: MultiCouplingScheme
- `to`: Participant
- `label`: participant

## Action - participant

This edge connects an action node to the participant who specified it.

- `type`: ACTION__PARTICIPANT__BELONGS_TO
- `from`: Action
- `to`: Participant
- `label`: belongs to

## Action - mesh

This edge connects an action node to the mesh the action gets performed on.

- `type`: ACTION_MESH
- `from`: Action
- `to`: Mesh
- `label`: mesh

## Action - data

This edge connects an action node with the data node that is involved in the operation.

- `type`: ACTION__TARGET_DATA
- `from`: Action
- `to`: Data
- `label`: target data

## Action - data

This edge connects an action node with the data node that is involved in the operation.

- `type`: ACTION__SOURCE_DATA
- `from`: Action
- `to`: Data
- `label`: source data

## Watchpoint - participant

This edge connects a watchpoint node to the participant specifying it.

- `type`: WATCH_POINT__PARTICIPANT__BELONGS_TO
- `from`: Watchpoint
- `to`: Participant
- `label`: belongs to

## Watchpoint - mesh

This edge connects a watchpoint node to the mesh it is watching.

- `type`: WATCH_POINT__MESH
- `from`: Watchpoint
- `to`: Mesh
- `label`: mesh

## Watch-integral - participant

This edge connects a watch-integral node to the participant specifying it.

- `type`: WATCH_INTEGRAL__PARTICIPANT__BELONGS_TO
- `from`: WatchIntegral
- `to`: Participant
- `label`: belongs to

## Watch-integral - mesh

This edge connects a watch-integral node to the mesh it is watching.

- `type`: WATCH_INTEGRAL__MESH
- `from`: WatchIntegral
- `to`: Mesh
- `label`: mesh