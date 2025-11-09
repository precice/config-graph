# Nodes

This project builds a graph based on a precice-config.xml file. The nodes in the graph correspond to the specified XML
elements and tags.<br>
The documentation for preCICE's config tags can be read
at [preCICE XML reference](https://precice.org/configuration-XML-reference.html)

> [!NOTE]
> This graph is built for the [preCICE logic checker](https://github.com/precice-forschungsprojekt/config-checker). This
> means that there may be redundancies or “inconsistencies” in the building of the graph itself.

Here you will find a list with brief explanations of each node and its parameters.

## Participant

The participant is the center of the graph. It saves references to all connected meshes, written and read data,
mappings, and more.

- `name`: The name of the participant as specified by its tag `name=""`, used in the graph debugging view to identify
  the participant.
- `write_data`: A list of all data the participant writes. This links to `WriteData` nodes to allow further references.
- `read_data`: A list of all data the participant reads. This links to `ReadData` nodes to allow further references.
- `receive_meshes`: A list of all meshes the participant receives. This links to `ReceiveMesh` nodes to allow further
  references.
- `provide_meshes`: A list of all meshes the participant provides. This links to `Mesh` nodes to allow further
  references.
- `mappings`: A list of all mappings specified by the participant. This links to `Mapping` nodes to allow further
  references.
- `exports`: A list of all exports specified by the participant. This links to `Export` nodes to allow further
  references.
- `actions`: A list of all actions the participant specifies. This links to `Action` nodes to allow further references.
- `watchpoints`: A list of all watchpoints the participant specifies. This links to `Watchpoint` nodes to allow further
  references.
- `watch_integrals`: A list of all watch integrals the participant specifies. This links to `WatchIntegral` nodes to
  allow further references.
- `line`: The line number where the participant is defined in the config.xml.

## Mesh

Mesh nodes represent the XML elements mesh.

- `name`: The name of the mesh as specified by its tag `name=""`, used in the graph debugging view to identify the mesh.
- `use_data`: A list of all data used by the mesh. This links to `Data` nodes.
- `line`: The line number where the mesh is defined in the config.xml.

## ReceiveMesh

Receive mesh nodes are used to differentiate between meshes a participant provides, and meshes a participant receives.
They are also meshes, with the additional information of who they get received by.

- `participant`: The participant the mesh gets received by.
- `mesh`: The mesh that gets received.
- `from_participant`: The participant that provides the mesh.
- `api-access`: `True`, if the tag `api-access="true"` exists, otherwise `False`.
- `line`: The line number where the receive mesh is defined in the config.xml.

## CouplingScheme

A coupling-scheme node represents a coupling-scheme element of the XML file.

- `type`: The type of the coupling being used. Possible values are `serial-explicit`,`parallel-explicit`,
  `serial-implicit` and `parallel-implicit`.
- `first_participant`: The participant of the coupling-scheme that gets referred to as `first=“”`.
- `second_participant`: The participant of the coupling-scheme that gets referred to as `second=“”`.
- `exchanges`: A list of exchanges between the participants. This links to `Exchange` nodes for further references.
- `accelerations`: The acceleration node that will contain references to all data-accelerations of the coupling-scheme.
- `convergence_measures`: A list of convergence-measure. Defines the convergence criterion of certain data of a mesh in
  a coupling-scheme.
- `line`: The line number where the coupling-scheme is defined in the config.xml.

## MultiCouplingScheme

A multi-coupling-scheme node corresponds to a multi-coupling-scheme XML element. It is an extension of a regular
coupling-scheme to allow for more than two participants.

- `control_participant`: The key participant of the multi-coupling-scheme, which links to a regular `Participant` node.
- `participants`: A list of all participants taking part in the multi-coupling-scheme.
  This does _not_ include the control participant.
- `exchanges`: A list of all exchanges being used to exchange data in this multi-coupling-scheme.
- `accelerations`: The acceleration node that will contain references to all data-accelerations of the coupling-scheme.
- `convergence_measures`: A list of convergence-measure. Defines the convergence criterion of certain data of a mesh in
  a multi-coupling-scheme.
- `line`: The line number where the multi-coupling-scheme is defined in the config.xml.

## Data

A data node represents a data element of the XML file.

- `name`: The name of the data element as specified in `name=“”`, used in the graph debugging view to identify the data
  node.
- `data_type`: The type of the data node. Possible values are `scalar` and `vector`.
- `line`: The line number where the data is defined in the config.xml.

## Mapping

Mapping nodes correspond to XML subelements of participants, which specify how data gets mapped from one mesh to
another.

- `parent_participant`: This links to the participant that specifies the mapping.
- `direction`: This specifies the direction of the data mapping.
- `just-in-time`: A bool, which indicates, if the mapping is a "just-in-time"-mapping. A JIT mapping is missing either
  the `to` or `from` tag.
- `method`: The method of the mapping as specified by `<mapping:method .../>`.
- `constraint`: The constraint as specified in the `constraint=“”` tag.
- `from_mesh`: The mesh as specified in the `from=“”` tag, if any.
- `to_mesh`: The mesh as specified in the `to=“”` tag, if any.
- `line`: The line number where the mapping is defined in the config.xml.

## WriteData

A write-data node corresponds to a subelement of a participant, specifying which data he writes.

- `participant`: The participant this write-data element belongs to.
- `data`: The data that gets written.
- `mesh`: The mesh that the data gets written to.
- `line`: The line number where the write-data is defined in the config.xml.

## ReadData

A read-data node corresponds to a subelement of a participant, specifying which data he reads.

- `participant`: The participant this read-data element belongs to.
- `data`: The data that gets read.
- `mesh`: The mesh that the data gets read from.
- `line`: The line number where the read-data is defined in the config.xml.

## Exchange

An exchange node corresponds to a subelement of a coupling-scheme. It specifies how data gets exchanged between two
participants.

- `coupling_scheme`: The coupling-scheme this exchange belongs to.
- `data`: The data that gets exchanged.
- `mesh`: The mesh through which data gets exchanged.
- `from_participant`: The participant from whom the data originates.
- `to_participant`: The participant who will receive the data.
- `line`: The line number where the exchange is defined in the config.xml.

## Export

Export nodes are another way a user can receive data from a coupled simulation using preCICE.

- `participant`: The participant whose data gets exported.
- `format`: The format of the file export. Possible values are `vtk`,`vtu`,`vtp` and `csv`.
- `line`: The line number where the export is defined in the config.xml.

## Action

- `participant`: The participant specifying this action.
- `type`: The type of the action, as specified by `<action:…` …/>. Possible values are `multiply-by-area`,
  `divide-by-area`, `summation` and `python`.
- `mesh`: The mesh this action will operate on.
- `timing`: When this action will be executed. One value is `write-mapping-post`, the other `read-mapping-post`.
- `target_data`: The data that will be the output of this action.
- `source_data`: The data that is the input of this action.
- `line`: The line number where the action is defined in the config.xml.

## Watchpoint

Watchpoints are a way to keep track of data development at a specified location. They correspond to a subelement of
participants.

- `name`: The name of the watchpoint.
- `participant`: The participant who the watchpoint belongs to.
- `mesh`: The mesh which is observed.
- `line`: The line number where the watchpoint is defined in the config.xml.

## WatchIntegral

Watch-integrals are a way to keep track of data development in an entire mesh. They correspond to a subelement of
participants.

- `name`: The name of the watch-integral.
- `participant`: The participant who the watch-integral belongs to.
- `mesh`: The mesh which is observed.
- `line`: The line number where the watch-integral is defined in the config.xml.

## M2N

To let participants exchange information (physically), they have to be connected via an m2n node.

- `type`: The type of the m2n node. Possible values are `sockets`, `mpi` and `mpi-multiple-ports`.
- `acceptor`: The participant defined as `acceptor=...`.
- `connector`: The participant defined as `connector=...`.
- `line`: The line number where the m2n is defined in the config.xml.

## AccelerationData

A acceleration-data node corresponds to a subelement of a acceleration, specifying which data is accelerated.

- `acceleration`: The acceleration at which the acceleration data is accelerated.
- `data`: Which data is accelerated.
- `mesh`: In which mesh the data is accelerated.
- `line`: The line number where the acceleration-data is defined in the config.xml.

## Acceleration

Acceleration techniques are a way to stabilize and accelerate fixed-point iteration.
Data is accelerated in a mesh in an exchange in the same coupling scheme.

- `coupling_scheme`: The coupling-scheme who the acceleration belongs to.
- `type`: The type of the acceleration node. Possible values are `aitken`, `IQN-ILS`, `IQN-IMVJ` and `constant`.
- `data`: A list of acceleration-data that are accelerated with the same type.
- `line`: The line number where the acceleration is defined in the config.xml.

## ConvergenceMeasure

Defines the convergence criterion of certain data of a mesh in a coupling-scheme.

- `coupling_scheme`: The coupling-scheme who the convergence-measure belongs to.
- `type`: The type of the convergence-measure node. Possible values are `absolute`, `absolute-or-relative`, `relative`
  and `residual-relative`.
- `data`: Which data should converge by type.
- `mesh`: In which mesh the data is to be converged according to the type.
- `line`: The line number where the convergence-measure is defined in the config.xml.
