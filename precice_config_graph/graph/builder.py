import sys
from enum import Enum
import networkx as nx
from lxml import etree

from precice_config_graph import nodes as n
from precice_config_graph import helper as h
from precice_config_graph.edges import Edge
from precice_config_graph import enums as e
from precice_config_graph.xml_processing import convert_string_to_bool, parse_file

LINK_GRAPH_REPOSITORY: str = "'\033[1;36mhttps://github.com/precice/config-graph\033[0m'"


def get_graph(root: etree.Element) -> nx.Graph:
    assert root.tag == "precice-configuration"

    # Taken from config-visualizer. Modified to also return postfix.
    def find_all_with_prefix(e: etree.Element, prefix: str):
        for child in e.iterchildren():
            if child.tag.startswith(prefix):
                postfix = child.tag[child.tag.find(":") + 1:]
                yield child, postfix

    def find_all_with_postfix(e: etree.Element, postfix: str):
        for child in e.iterchildren():
            if child.tag.endswith(postfix):
                prefix: str = child.tag.removesuffix(postfix)
                yield child, prefix

    def error(message: str):
        sys.exit(
            "\033[1;31m[ERROR]\033[0m Exiting graph generation."
            + "\n"
            + message
            + "\nPlease run 'precice-tools check' (preCICE version <3.30) "
              "or 'precice-config-validate' (preCICE version ≥3.30) to check for syntax errors."
            + "\n\nIf you are sure this behaviour is incorrect, please leave a report at "
            + LINK_GRAPH_REPOSITORY
        )

    def error_missing_attribute(e: etree.Element, key: str):
        message: str = 'Missing attribute "' + key + '" for element "' + e.tag + '".'
        error(message)

    def get_enum_values(enum: Enum) -> list:
        return list(map(lambda x: x.value, enum._member_map_.values()))

    def list_to_string(values: list) -> str:
        string: str = ""
        size = len(values)
        for i in range(size - 2):
            string += f'"{values[i]}", '
        string += f'"{values[size - 2]}" or "{values[size - 1]}".'
        return string

    def error_unknown_type(e: etree.Element, type: str, enum: Enum, unknown_str: str = "type"):
        possible_types_list = get_enum_values(enum)
        possible_types = list_to_string(possible_types_list)
        message: str = (
                f'Unknown {unknown_str} "'
                + type
                + '" for element "'
                + e.tag
                + '".\nUse one of '
                + possible_types
        )
        error(message)

    def get_attribute(e: etree.Element, key: str):
        attribute = e.get(key)
        if not attribute:
            error_missing_attribute(e, key)
        return attribute

    # FIND NODES

    # Keep track of these types of nodes, since we cannot construct them on demand when referenced,
    # since the reference does not contain relevant data.
    data_nodes: dict[str, n.DataNode] = {}
    mesh_nodes: dict[str, n.MeshNode] = {}
    participant_nodes: dict[str, n.ParticipantNode] = {}
    write_data_nodes: list[n.WriteDataNode] = []
    read_data_nodes: list[n.ReadDataNode] = []
    receive_mesh_nodes: list[n.ReceiveMeshNode] = []
    coupling_nodes: list[n.CouplingSchemeNode] = []
    multi_coupling_nodes: list[n.MultiCouplingSchemeNode] = []
    mapping_nodes: list[n.MappingNode] = []
    export_nodes: list[n.ExportNode] = []
    exchange_nodes: list[n.ExchangeNode] = []
    acceleration_nodes: list[n.AccelerationNode] = []
    acceleration_data_nodes: list[n.AccelerationDataNode] = []
    convergence_measure_nodes: list[n.ConvergenceMeasureNode] = []
    action_nodes: list[n.ActionNode] = []
    m2n_nodes: list[n.M2NNode] = []
    watch_point_nodes: list[n.WatchPointNode] = []
    watch_integral_nodes: list[n.WatchIntegralNode] = []

    # Data items – <data:… />
    for (data_el, kind) in find_all_with_prefix(root, "data"):
        name = get_attribute(data_el, "name")
        try:
            type = e.DataType(kind)
        except ValueError:
            error_unknown_type(data_el, kind, e.DataType)
        line: int = data_el.sourceline
        node = n.DataNode(name, type, line=line)
        data_nodes[name] = node

    # Meshes – <mesh />
    for mesh_el in root.findall("mesh"):
        name = get_attribute(mesh_el, "name")
        line: int = mesh_el.sourceline

        dim_str = mesh_el.get("dimensions")
        mesh_dims = int(dim_str) if dim_str else 3

        mesh = n.MeshNode(name, dimensions=mesh_dims, line=line)

        # Data usages – <use-data />: Will be mapped to edges
        for use_data in mesh_el.findall("use-data"):
            data_name = get_attribute(use_data, "name")
            data_node = data_nodes[data_name]
            mesh.use_data.append(data_node)

        # Now that mesh_node is completely built, add it to our dictionary
        mesh_nodes[name] = mesh

    # Participants – <participant />
    for participant_el in root.findall("participant"):
        name = get_attribute(participant_el, "name")
        line: int = participant_el.sourceline
        participant = n.ParticipantNode(name, line=line)

        # Provide- and Receive-Mesh
        # <provide-mesh />
        for provide_mesh_el in participant_el.findall("provide-mesh"):
            mesh_name = get_attribute(provide_mesh_el, "name")
            participant.provide_meshes.append(mesh_nodes[mesh_name])

        # Read and write data
        # <write-data />
        for write_data_el in participant_el.findall("write-data"):
            data_name = get_attribute(write_data_el, "name")
            data = data_nodes[data_name]
            mesh_name = get_attribute(write_data_el, "mesh")
            mesh = mesh_nodes[mesh_name]
            line: int = write_data_el.sourceline

            write_data = n.WriteDataNode(participant, data, mesh, line=line)
            participant.write_data.append(write_data)
            write_data_nodes.append(write_data)

        # <read-data />
        # TODO: Refactor to reduce code duplication
        for read_data_el in participant_el.findall("read-data"):
            data_name = get_attribute(read_data_el, "name")
            data = data_nodes[data_name]
            mesh_name = get_attribute(read_data_el, "mesh")
            mesh = mesh_nodes[mesh_name]
            line: int = read_data_el.sourceline

            read_data = n.ReadDataNode(participant, data, mesh, line=line)
            participant.read_data.append(read_data)
            read_data_nodes.append(read_data)

        # Mapping
        for (mapping_el, kind) in find_all_with_prefix(participant_el, "mapping"):
            direction = get_attribute(mapping_el, "direction")
            # From mesh might not exist due to just-in-time mapping
            from_mesh_name = mapping_el.get("from")
            from_mesh = mesh_nodes[from_mesh_name] if from_mesh_name else None
            # From mesh might not exist due to just-in-time mapping
            to_mesh_name = mapping_el.get("to")
            to_mesh = mesh_nodes[to_mesh_name] if to_mesh_name else None

            try:
                method = e.MappingMethod(kind)
            except ValueError:
                error_unknown_type(mapping_el, kind, e.MappingMethod, unknown_str="method")
            constraint = e.MappingConstraint(get_attribute(mapping_el, "constraint"))

            if not from_mesh and not to_mesh:
                error_missing_attribute(mapping_el, 'from" or "to')
            just_in_time = not (from_mesh and to_mesh)
            line: int = mapping_el.sourceline

            # Optional attributes
            polynomial_str: str = mapping_el.get("polynomial", h.MAPPING_POLYNOMIAL)
            try:
                # If it is a string, it will try to convert it to MappingPolynomialType.
                # If it is already a MappingPolynomialType, nothing will happen.
                polynomial = e.MappingPolynomialType(polynomial_str)
            except ValueError:
                error_unknown_type(mapping_el, polynomial_str, e.MappingPolynomialType, unknown_str="polynomial")

            x_dead_str: str = mapping_el.get("x-dead")
            x_dead = convert_string_to_bool(x_dead_str) if x_dead_str else h.MAPPING_X_DEAD
            y_dead_str: str = mapping_el.get("y-dead")
            y_dead = convert_string_to_bool(y_dead_str) if y_dead_str else h.MAPPING_Y_DEAD
            z_dead_str: str = mapping_el.get("z-dead")
            z_dead = convert_string_to_bool(z_dead_str) if z_dead_str else h.MAPPING_Z_DEAD

            rtol_str = mapping_el.get("solver-rtol")
            rtol = float(rtol_str) if rtol_str else h.MAPPING_SOLVER_RTOL

            vertices_per_cluster_str: str = mapping_el.get("vertices-per-cluster")
            vertices_per_cluster = int(
                vertices_per_cluster_str) if vertices_per_cluster_str else h.MAPPING_VERTICES_PER_CLUSTER

            project_to_input_str = mapping_el.get("project-to-input")
            project_to_input = convert_string_to_bool(
                project_to_input_str) if project_to_input_str else h.MAPPING_PROJECT_TO_INPUT

            multiscale_type_str: str = mapping_el.get("multiscale-type", h.MAPPING_MULTISCALE_TYPE)
            try:
                multiscale_type = e.MappingMultiscaleType(multiscale_type_str)
            except ValueError:
                error_unknown_type(mapping_el, multiscale_type_str, e.MappingMultiscaleType)

            multiscale_axis_str: str = mapping_el.get("multiscale-axis", h.MAPPING_MULTISCALE_AXIS)
            try:
                multiscale_axis = e.MappingMultiscaleAxis(multiscale_axis_str)
            except ValueError:
                error_unknown_type(mapping_el, multiscale_axis_str, e.MappingMultiscaleAxis,
                                   unknown_str="multiscale-axis")

            multiscale_radius_str: str = mapping_el.get("multiscale-radius")
            multiscale_radius = float(multiscale_radius_str) if multiscale_radius_str else h.MAPPING_MULTISCALE_RADIUS

            basis_function: n.MappingBasisFunctionNode | None = None
            # There exists a maximum of one basis-function tag per mapping tag.
            for (basisfunction_el, bftype_str) in find_all_with_prefix(mapping_el, "basis-function"):
                try:
                    bftype = e.MappingBasisFunctionType(bftype_str)
                except ValueError:
                    error_unknown_type(basisfunction_el, bftype_str, e.MappingBasisFunctionType,
                                       unknown_str="basis-function")

                support_radius_str: str = basisfunction_el.get("support-radius")
                support_radius: float = float(
                    support_radius_str) if support_radius_str else h.MAPPING_BASIS_FUNCTION_SUPPORT_RADIUS

                shape_parameter_str: str = basisfunction_el.get("shape-parameter")
                shape_parameter: float = float(
                    shape_parameter_str) if shape_parameter_str else h.MAPPING_BASIS_FUNCTION_SHAPE_PARAMETER

                basis_function = n.MappingBasisFunctionNode(
                    bftype,
                    None,
                    support_radius,
                    shape_parameter
                )

            executor: n.MappingExecutorNode | None = None
            for (executor_el, etype) in find_all_with_prefix(mapping_el, "executor"):
                try:
                    etype = e.MappingExecutorType(etype)
                except ValueError:
                    error_unknown_type(executor_el, etype, e.MappingExecutorType, unknown_str="executor-type")

                gpu_device_id_str: str = executor_el.get("gpu-device-id")
                gpu_device_id = int(gpu_device_id_str) if gpu_device_id_str else h.MAPPING_EXECUTOR_GPU_DEVICE_ID

                n_threads_str: str = executor_el.get("n-threads")
                n_threads = int(n_threads_str) if n_threads_str else h.MAPPING_EXECUTOR_N_THREADS

                executor = n.MappingExecutorNode(
                    etype,
                    None,
                    gpu_device_id,
                    n_threads,
                )

            mapping = n.MappingNode(
                participant,
                e.Direction(direction),
                just_in_time,
                method,
                constraint,
                from_mesh,
                to_mesh,
                line=line,
                polynomial=polynomial,
                x_dead=x_dead,
                y_dead=y_dead,
                z_dead=z_dead,
                solver_rtol=rtol,
                vertices_per_cluster=vertices_per_cluster,
                project_to_input=project_to_input,
                multiscale_type=multiscale_type,
                multiscale_axis=multiscale_axis,
                multiscale_radius=multiscale_radius,
                basisfunction=basis_function,
                executor=executor,
            )

            if mapping.basisfunction:
                mapping.basisfunction.mapping = mapping

            if mapping.executor:
                mapping.executor.mapping = mapping

            participant.mappings.append(mapping)
            mapping_nodes.append(mapping)

        # Exports
        # <export:… />
        for (export_el, kind) in find_all_with_prefix(participant_el, "export"):
            try:
                type = e.ExportFormat(kind)
            except ValueError:
                error_unknown_type(export_el, kind, e.ExportFormat, unknown_str="export-format")
            line: int = export_el.sourceline

            directory = export_el.get("directory", h.EXPORT_DIRECTORY)

            export = n.ExportNode(participant, type, line=line, directory=directory)
            participant.exports.append(export)
            export_nodes.append(export)

        # Actions
        # <action:… />
        for (action_el, kind) in find_all_with_prefix(participant_el, "action"):
            mesh = mesh_nodes[get_attribute(action_el, "mesh")]
            timing = e.TimingType(get_attribute(action_el, "timing"))

            target_data = None
            if kind in ["multiply-by-area", "divide-by-area", "summation", "python"]:
                target_data_el = action_el.find("target-data")
                if target_data_el is not None:
                    target_data = data_nodes[get_attribute(target_data_el, "name")]

            source_data: list[n.DataNode] = []
            path_str: str = ""
            module_name: str = ""
            if kind in ["summation", "python"]:
                source_data_els = action_el.findall("source-data")
                for source_data_el in source_data_els:
                    source_data.append(
                        data_nodes[get_attribute(source_data_el, "name")]
                    )
                for path_str_el in action_el.findall("path"):
                    path_str: str = path_str_el.get("name", "")
                for module_name_el in action_el.findall("module"):
                    module_name: str = module_name_el.get("name", "")
            try:
                type = e.ActionType(kind)
            except ValueError:
                error_unknown_type(action_el, kind, e.ActionType, unknown_str="type")

            line: int = action_el.sourceline

            action = n.ActionNode(
                participant,
                type,
                mesh,
                timing,
                target_data,
                source_data,
                line=line,
                python_module_path=path_str,
                python_module_name=module_name
            )
            participant.actions.append(action)
            action_nodes.append(action)

        # Watch-Points
        # <watch-point />
        for watch_point_el in participant_el.findall("watch-point"):
            point_name = get_attribute(watch_point_el, "name")
            mesh = mesh_nodes[get_attribute(watch_point_el, "mesh")]
            line: int = watch_point_el.sourceline

            coordinate_str = watch_point_el.get("coordinate")
            coord_list: list[float] = []
            if coordinate_str:
                coord_list = [float(x) for x in coordinate_str.split(";")]

            watch_point = n.WatchPointNode(point_name, participant, mesh, line=line, coordinate=coord_list)
            watch_point_nodes.append(watch_point)
            participant.watchpoints.append(watch_point)

        # Watch-Integral
        # <watch-integral />
        for watch_integral_el in participant_el.findall("watch-integral"):
            integral_name = get_attribute(watch_integral_el, "name")
            mesh = mesh_nodes[get_attribute(watch_integral_el, "mesh")]
            line: int = watch_integral_el.sourceline

            scale_with_connectivity_str = watch_integral_el.get("scale-with-connectivity")
            scale_with_connectivity = convert_string_to_bool(
                scale_with_connectivity_str) if scale_with_connectivity_str else h.WATCH_INTEGRAL_SCALE_WITH_CONNECTIVITY

            watch_integral = n.WatchIntegralNode(integral_name,
                                                 participant,
                                                 mesh,
                                                 line=line,
                                                 scale_with_connectivity=scale_with_connectivity)
            watch_integral_nodes.append(watch_integral)
            participant.watch_integrals.append(watch_integral)

        # Now that participant_node is completely built, add it and children to the graph and our dictionary
        participant_nodes[name] = participant

    # Receive Mesh Participants
    # This can't be done in the participants loop, since it references participants which might not yet be created
    # <participant />
    for participant_el in root.findall("participant"):
        name = get_attribute(participant_el, "name")
        participant = participant_nodes[
            name
        ]  # This should not fail, because we created participants before

        # <receive-mesh />
        for receive_mesh_el in participant_el.findall("receive-mesh"):
            mesh_name = get_attribute(receive_mesh_el, "name")
            mesh = mesh_nodes[mesh_name]

            from_participant_name = get_attribute(receive_mesh_el, "from")
            from_participant = participant_nodes[from_participant_name]

            api_access_str = receive_mesh_el.get("api-access")
            api_access = convert_string_to_bool(api_access_str) if api_access_str else h.RECEIVE_MESH_API_ACCESS
            line: int = receive_mesh_el.sourceline

            receive_mesh = n.ReceiveMeshNode(
                participant, mesh, from_participant, api_access, line=line
            )
            participant.receive_meshes.append(receive_mesh)
            receive_mesh_nodes.append(receive_mesh)

    # Coupling Scheme – <coupling-scheme:… />
    for (coupling_scheme_el, kind) in find_all_with_prefix(root, "coupling-scheme"):
        coupling_scheme = None
        line: int = coupling_scheme_el.sourceline
        match kind:
            case "serial-explicit" | "serial-implicit" | "parallel-explicit" | "parallel-implicit":
                # <participants />
                participants_list = coupling_scheme_el.findall("participants")
                if len(participants_list) > 1:
                    message: str = (
                            "Multiple 'participants' tags in '"
                            + coupling_scheme_el.tag
                            + "'"
                    )
                    error(message)
                elif len(participants_list) < 1:
                    error_missing_attribute(coupling_scheme_el, "participants")
                participants = participants_list[0]
                first_participant_name = get_attribute(participants, "first")
                first_participant = participant_nodes[first_participant_name]
                second_participant_name = get_attribute(participants, "second")
                second_participant = participant_nodes[second_participant_name]

                type = e.CouplingSchemeType(kind)

                time_window_size: float = h.COUPLING_SCHEME_TIME_WINDOW_SIZE
                for time_window_size_el in coupling_scheme_el.findall("time-window-size"):
                    time_window_size_str: str = time_window_size_el.get("value")
                    time_window_size: float = float(
                        time_window_size_str) if time_window_size_str else h.COUPLING_SCHEME_TIME_WINDOW_SIZE

                max_time_windows: int = h.COUPLING_SCHEME_MAX_TIME_WINDOWS
                for max_time_window_el in coupling_scheme_el.findall("max-time-windows"):
                    max_time_window_str: str = max_time_window_el.get("value")
                    max_time_windows: int = int(
                        max_time_window_str) if max_time_window_str else h.COUPLING_SCHEME_MAX_TIME_WINDOWS

                coupling_scheme = n.CouplingSchemeNode(
                    type,
                    first_participant,
                    second_participant,
                    line=line,
                    time_window_size=time_window_size,
                    max_time_windows=max_time_windows,
                )
            case "multi":
                control_participant = None
                participants = []
                # <participant name="..." />
                for participant_el in coupling_scheme_el.findall("participant"):
                    name = get_attribute(participant_el, "name")
                    participant = participant_nodes[name]
                    participants.append(participant)

                    control = (
                            "control" in participant_el.attrib
                            and convert_string_to_bool(participant_el.get("control"))
                    )
                    if control:
                        assert (
                                control_participant is None
                        )  # there must not be multiple control participants
                        control_participant = participant

                assert (
                        control_participant is not None
                ), "There must be a control participant"

                max_time_windows: int = h.COUPLING_SCHEME_MAX_TIME_WINDOWS
                time_window_size: float = h.COUPLING_SCHEME_TIME_WINDOW_SIZE
                for time_window_size_el in coupling_scheme_el.findall("time-window-size"):
                    time_window_size_str: str = time_window_size_el.get("value")
                    time_window_size: float = float(
                        time_window_size_str) if time_window_size_str else h.COUPLING_SCHEME_TIME_WINDOW_SIZE

                for max_time_window_el in coupling_scheme_el.findall("max-time-windows"):
                    max_time_windows_str: str = max_time_window_el.get("value")
                    max_time_windows: int = int(
                        max_time_windows_str) if max_time_windows_str else h.COUPLING_SCHEME_MAX_TIME_WINDOWS

                coupling_scheme = n.MultiCouplingSchemeNode(
                    control_participant,
                    participants,
                    line=line,
                    max_time_windows=max_time_windows,
                    time_window_size=time_window_size,
                )
            case _:
                # TODO This does not print multi as a possible type.
                error_unknown_type(coupling_scheme_el, kind, e.CouplingSchemeType)

        assert (
                coupling_scheme is not None
        )  # there must always be one participant that is in control

        # Exchanges – <exchange />
        for exchange_el in coupling_scheme_el.findall("exchange"):
            data_name = get_attribute(exchange_el, "data")
            data = data_nodes[data_name]
            mesh_name = get_attribute(exchange_el, "mesh")
            mesh = mesh_nodes[mesh_name]
            from_participant_name = get_attribute(exchange_el, "from")
            from_participant = participant_nodes[from_participant_name]
            to_participant_name = get_attribute(exchange_el, "to")
            to_participant = participant_nodes[to_participant_name]
            line: int = exchange_el.sourceline

            exchange = n.ExchangeNode(
                coupling_scheme, data, mesh, from_participant, to_participant, line=line
            )
            coupling_scheme.exchanges.append(exchange)
            exchange_nodes.append(exchange)

        # Acceleration
        for (acceleration_el, a_kind) in find_all_with_prefix(
                coupling_scheme_el, "acceleration"
        ):
            if kind in ["serial-explicit", "parallel-explicit"]:
                possible_types = list_to_string(
                    ["serial-implicit", "parallel-implicit", "multi"]
                )
                message: str = (
                        f"The coupling scheme of type '{kind}' does not support accelerations.\nUse one of "
                        + possible_types
                        + "\nOtherwise remove the acceleration tag."
                )
                error(message)

            try:
                type = e.AccelerationType(a_kind)
            except ValueError:
                error_unknown_type(acceleration_el, a_kind, e.AccelerationType)
            line: int = acceleration_el.sourceline

            acceleration = n.AccelerationNode(coupling_scheme, type, line=line)

            possible_types_list = ["aitken", "IQN-ILS", "IQN-IMVJ"]

            if a_kind == "constant" and acceleration_el.find("data"):
                possible_types: str = list_to_string(possible_types_list)
                message: str = (
                        "No data tag is expected for 'constant' acceleration.\nUse one of "
                        + possible_types
                        + "\nOtherwise remove the acceleration tag."
                )
                error(message)

            if a_kind in possible_types_list:
                # Accelerated data
                for a_data in acceleration_el.findall("data"):
                    a_data_name = get_attribute(a_data, "name")
                    data = data_nodes[a_data_name]
                    a_mesh_name = get_attribute(a_data, "mesh")
                    mesh = mesh_nodes[a_mesh_name]
                    line: int = a_data.sourceline
                    a_data_node = n.AccelerationDataNode(acceleration, data, mesh, line=line)
                    acceleration.data.append(a_data_node)
                    acceleration_data_nodes.append(a_data_node)

                # Preconditioner (just one expected)
                preconditioner: n.PreconditionerNode | None = None
                for preconditioner_el in acceleration_el.findall("preconditioner"):
                    p_type_str = preconditioner_el.get("type")
                    try:
                        p_type = e.PreconditionerType(p_type_str)
                    except ValueError:
                        error_unknown_type(preconditioner_el, p_type_str, e.PreconditionerType)

                    freeze_after_str = preconditioner_el.get("freeze-after")
                    freeze_after = int(freeze_after_str) if freeze_after_str else h.PRECONDITIONER_FREEZE_AFTER

                    update_on_threshold_str = preconditioner_el.get("update-on-threshold")
                    update_on_threshold = convert_string_to_bool(
                        update_on_threshold_str) if update_on_threshold_str else h.PRECONDITIONER_UPDATE_ON_THRESHOLD

                    preconditioner = n.PreconditionerNode(p_type, acceleration, freeze_after, update_on_threshold)

                if preconditioner:
                    acceleration.preconditioner = preconditioner

                if a_kind == "aitken":
                    continue

                # AccelerationFilter (only possible on IQN-ILS and IQN-IMVJ
                acceleration_filter: n.AccelerationFilterNode | None = None
                for acceleration_filter_el in acceleration_el.findall("filter"):
                    a_filter_type_str = acceleration_filter_el.get("type", h.ACCELERATION_FILTER_TYPE)
                    try:
                        a_filter_type = e.AccelerationFilterType(a_filter_type_str)
                    except ValueError:
                        error_unknown_type(acceleration_filter_el, a_filter_type_str, e.AccelerationFilterType)

                    a_filter_limit_str = acceleration_filter_el.get("limit")
                    a_filter_limit = float(a_filter_limit_str) if a_filter_limit_str else h.ACCELERATION_FILTER_LIMIT

                    acceleration_filter = n.AccelerationFilterNode(acceleration, a_filter_type, a_filter_limit)

                if acceleration_filter:
                    acceleration.filter = acceleration_filter

            coupling_scheme.acceleration = acceleration
            acceleration_nodes.append(acceleration)

        for (convergence_measure_el, c_kind) in find_all_with_postfix(
                coupling_scheme_el, "-convergence-measure"
        ):
            match kind:
                case "serial-implicit" | "parallel-implicit" | "multi":
                    try:
                        type = e.ConvergenceMeasureType(c_kind)
                    except ValueError:
                        possible_types_list = get_enum_values(e.ConvergenceMeasureType)
                        error_unknown_type(
                            convergence_measure_el, c_kind, possible_types_list
                        )

                    c_data_name = get_attribute(convergence_measure_el, "data")
                    c_data = data_nodes[c_data_name]
                    c_mesh_name = get_attribute(convergence_measure_el, "mesh")
                    c_mesh = mesh_nodes[c_mesh_name]
                    line: int = convergence_measure_el.sourceline

                    # Only one of these can occur at the same time
                    limit_str = convergence_measure_el.get("limit")
                    abs_limit_str = convergence_measure_el.get("abs-limit")
                    limit = float(limit_str) if limit_str else float(
                        abs_limit_str) if abs_limit_str else h.CONVERGENCE_MEASURE_LIMIT

                    rel_limit_str = convergence_measure_el.get("rel-limit")
                    rel_limit = float(rel_limit_str) if rel_limit_str else h.CONVERGENCE_MEASURE_LIMIT

                    convergence_measure = n.ConvergenceMeasureNode(
                        coupling_scheme,
                        type,
                        c_data,
                        c_mesh,
                        line=line,
                        limit=limit,
                        rel_limit=rel_limit
                    )
                    coupling_scheme.convergence_measures.append(convergence_measure)
                    convergence_measure_nodes.append(convergence_measure)

                case "parallel-explicit" | "serial-explicit":
                    possible_types: str = list_to_string(
                        ["serial-implicit", "parallel-implicit", "multi"]
                    )
                    message: str = (
                            f"The coupling scheme of type '{kind}' does not support convergence-measure.\nUse one of "
                            + possible_types
                            + f"\nOtherwise remove the {c_kind}-convergence-measure tag."
                    )
                    error(message)

        match kind:
            case "serial-explicit" | "serial-implicit" | "parallel-explicit" | "parallel-implicit":
                coupling_nodes.append(coupling_scheme)
            case "multi":
                multi_coupling_nodes.append(coupling_scheme)

    # M2N – <m2n:… />
    for (m2n_el, kind) in find_all_with_prefix(root, "m2n"):
        try:
            type = e.M2NType(kind)
        except ValueError:
            possible_types_list = get_enum_values(e.M2NType)
            error_unknown_type(m2n_el, kind, possible_types_list)
        acceptor_name = get_attribute(m2n_el, "acceptor")
        acceptor = participant_nodes[acceptor_name]
        connector_name = get_attribute(m2n_el, "connector")
        connector = participant_nodes[connector_name]
        line: int = m2n_el.sourceline

        directory = m2n_el.get("exchange-directory", h.M2N_DIRECTORY)

        m2n = n.M2NNode(type, acceptor, connector, line=line, directory=directory)
        m2n_nodes.append(m2n)

    # BUILD GRAPH
    # from found nodes and inferred edges

    # Use an undirected graph
    g = nx.Graph()

    for data in data_nodes.values():
        add_node_with_attributes(g, data)

    for mesh in mesh_nodes.values():
        add_node_with_attributes(g, mesh)
        for data in mesh.use_data:
            g.add_edge(data, mesh, attr=Edge.USE_DATA)

    for participant in participant_nodes.values():
        add_node_with_attributes(g, participant)
        for mesh in participant.provide_meshes:
            g.add_edge(participant, mesh, attr=Edge.PROVIDE_MESH__PARTICIPANT_PROVIDES)
        # Use data and write data, as well as receive mesh nodes are added later

    for read_data in read_data_nodes:
        add_node_with_attributes(g, read_data)
        g.add_edge(read_data, read_data.data, attr=Edge.READ_DATA__DATA_READ_BY)
        g.add_edge(read_data, read_data.mesh, attr=Edge.READ_DATA__MESH_READ_BY)
        g.add_edge(
            read_data,
            read_data.participant,
            attr=Edge.READ_DATA__PARTICIPANT__BELONGS_TO,
        )

    for write_data in write_data_nodes:
        add_node_with_attributes(g, write_data)
        g.add_edge(write_data, write_data.data, attr=Edge.WRITE_DATA__WRITES_TO_DATA)
        g.add_edge(write_data, write_data.mesh, attr=Edge.WRITE_DATA__WRITES_TO_MESH)
        g.add_edge(
            write_data,
            write_data.participant,
            attr=Edge.WRITE_DATA__PARTICIPANT__BELONGS_TO,
        )

    for receive_mesh in receive_mesh_nodes:
        add_node_with_attributes(g, receive_mesh)
        g.add_edge(receive_mesh, receive_mesh.mesh, attr=Edge.RECEIVE_MESH__MESH)
        g.add_edge(
            receive_mesh,
            receive_mesh.from_participant,
            attr=Edge.RECEIVE_MESH__PARTICIPANT_RECEIVED_FROM,
        )
        g.add_edge(
            receive_mesh,
            receive_mesh.participant,
            attr=Edge.RECEIVE_MESH__PARTICIPANT__BELONGS_TO,
        )

    for mapping in mapping_nodes:
        add_node_with_attributes(g, mapping)
        if mapping.from_mesh:
            g.add_edge(mapping, mapping.from_mesh, attr=Edge.MAPPING__FROM_MESH)
        if mapping.to_mesh:
            g.add_edge(mapping, mapping.to_mesh, attr=Edge.MAPPING__TO_MESH)
        g.add_edge(
            mapping,
            mapping.parent_participant,
            attr=Edge.MAPPING__PARTICIPANT__BELONGS_TO,
        )

    for export in export_nodes:
        add_node_with_attributes(g, export)
        g.add_edge(
            export, export.participant, attr=Edge.EXPORT__PARTICIPANT__BELONGS_TO
        )

    for action in action_nodes:
        add_node_with_attributes(g, action)
        g.add_edge(
            action, action.participant, attr=Edge.ACTION__PARTICIPANT__BELONGS_TO
        )
        g.add_edge(action, action.mesh, attr=Edge.ACTION__MESH)
        if action.target_data is not None:
            g.add_edge(action, action.target_data, attr=Edge.ACTION__TARGET_DATA)
        for source_data in action.source_data:
            g.add_edge(action, source_data, attr=Edge.ACTION__SOURCE_DATA)

    for watch_point in watch_point_nodes:
        add_node_with_attributes(g, watch_point)
        g.add_edge(
            watch_point,
            watch_point.participant,
            attr=Edge.WATCH_POINT__PARTICIPANT__BELONGS_TO,
        )
        g.add_edge(watch_point, watch_point.mesh, attr=Edge.WATCH_POINT__MESH)

    for watch_integral in watch_integral_nodes:
        add_node_with_attributes(g, watch_integral)
        g.add_edge(
            watch_integral,
            watch_integral.participant,
            attr=Edge.WATCH_INTEGRAL__PARTICIPANT__BELONGS_TO,
        )
        g.add_edge(watch_integral, watch_integral.mesh, attr=Edge.WATCH_INTEGRAL__MESH)

    for coupling in coupling_nodes:
        add_node_with_attributes(g, coupling)
        # Edges to and from exchanges will be added by exchange nodes
        g.add_edge(
            coupling,
            coupling.first_participant,
            attr=Edge.COUPLING_SCHEME__PARTICIPANT_FIRST,
        )
        g.add_edge(
            coupling,
            coupling.second_participant,
            attr=Edge.COUPLING_SCHEME__PARTICIPANT_SECOND,
        )

    for coupling in multi_coupling_nodes:
        add_node_with_attributes(g, coupling)
        for participant in coupling.participants:
            g.add_edge(
                coupling, participant, attr=Edge.MULTI_COUPLING_SCHEME__PARTICIPANT
            )
        # Previous, “regular” multi-coupling scheme participant edge, gets overwritten
        g.add_edge(
            coupling,
            coupling.control_participant,
            attr=Edge.MULTI_COUPLING_SCHEME__PARTICIPANT__CONTROL,
        )

    for exchange in exchange_nodes:
        add_node_with_attributes(g, exchange)
        g.add_edge(
            exchange, exchange.from_participant, attr=Edge.EXCHANGE__EXCHANGED_FROM
        )
        g.add_edge(exchange, exchange.to_participant, attr=Edge.EXCHANGE__EXCHANGES_TO)
        g.add_edge(exchange, exchange.data, attr=Edge.EXCHANGE__DATA)
        g.add_edge(exchange, exchange.mesh, attr=Edge.EXCHANGE__MESH)
        g.add_edge(
            exchange,
            exchange.coupling_scheme,
            attr=Edge.EXCHANGE__COUPLING_SCHEME__BELONGS_TO,
        )

    for acceleration in acceleration_nodes:
        add_node_with_attributes(g, acceleration)
        g.add_edge(
            acceleration,
            acceleration.coupling_scheme,
            attr=Edge.ACCELERATION__COUPLING_SCHEME__BELONGS_TO,
        )

    for acceleration_data in acceleration_data_nodes:
        add_node_with_attributes(g, acceleration_data)
        g.add_edge(
            acceleration_data,
            acceleration_data.acceleration,
            attr=Edge.ACCELERATION_DATA__ACCELERATION__BELONGS_TO,
        )
        g.add_edge(
            acceleration_data, acceleration_data.data, attr=Edge.ACCELERATION_DATA__DATA
        )
        g.add_edge(
            acceleration_data, acceleration_data.mesh, attr=Edge.ACCELERATION_DATA__MESH
        )

    for convergence_measure in convergence_measure_nodes:
        add_node_with_attributes(g, convergence_measure)
        g.add_edge(
            convergence_measure,
            convergence_measure.coupling_scheme,
            attr=Edge.CONVERGENCE_MEASURE__COUPLING_SCHEME__BELONGS_TO,
        )
        g.add_edge(
            convergence_measure,
            convergence_measure.data,
            attr=Edge.CONVERGENCE_MEASURE__DATA,
        )
        g.add_edge(
            convergence_measure,
            convergence_measure.mesh,
            attr=Edge.CONVERGENCE_MEASURE__MESH,
        )

    for m2n in m2n_nodes:
        add_node_with_attributes(g, m2n)
        g.add_edge(m2n, m2n.acceptor, attr=Edge.M2N__PARTICIPANT_ACCEPTOR)
        g.add_edge(m2n, m2n.connector, attr=Edge.M2N__PARTICIPANT_CONNECTOR)

    return g


def add_node_with_attributes(g: nx.Graph, node_obj) -> None:
    """
    Add the given node to the given graph, alongside a dict of the nodes attributes.
    :param g: The graph to add the node to.
    :param node_obj: The node to add to the graph.
    :return: None
    """
    # Get all the attributes of the node and copy them, as to not modify the originals
    attributes: dict = vars(node_obj).copy()
    clean_attributes: dict[str, str | int | list[str]] = {}

    # A set to keep track of keys that reference other nodes
    # To later ignore attributes which contain named elements,
    # e.g., "name=Generator", we need to keep track of these attributes
    ref_keys: set[str] = {"name"}

    for key, value in attributes.items():
        # Ignore "line" attribute to make the check location/order independent
        if key == "line":
            continue

        # Store the enum value as a string
        if hasattr(value, "value") and isinstance(value, Enum):
            clean_attributes[key] = value.value

        # Handle lists of attributes
        elif isinstance(value, list):
            if len(value) == 0:
                # Store 0 to prove the list is empty
                clean_attributes[key] = 0
            # If the list is not empty, check if the contained object has a "name" attribute
            elif hasattr(value[0], "name"):
                # If so, then store the name and add the key to the "reference_keys"
                clean_attributes[key] = sorted([item.name for item in value])
                ref_keys.add(key)
            # Store a list of primitive types
            elif isinstance(value[0], (int, float, str, bool)):
                clean_attributes[key] = value.copy()
            else:
                # Store the count of other nodes
                clean_attributes[key] = len(value)

        # Handle single node attributes
        elif hasattr(value, "name"):
            # If they have a name, store the key in the "reference_keys"
            clean_attributes[key] = value.name
            ref_keys.add(key)

        elif hasattr(value, "__dict__"):
            # Otherwise, save the class name
            clean_attributes[key] = value.__class__.__name__

        # Primitive data types such as bool, int, str can be added directly
        else:
            clean_attributes[key] = value

    # Add metadata
    clean_attributes["_class_type"] = node_obj.__class__.__name__

    # Store sorted list of reference keys (safe for export/serialization)
    clean_attributes["_ref_keys"] = sorted(list(ref_keys))

    g.add_node(node_obj, **clean_attributes)
