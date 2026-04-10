import networkx as nx
try:
    import matplotlib.pyplot as plt
except ImportError:
    print(f"\033[1;31m[ERROR]\033[0m 'matplotlib' is required to plot the graph.")
    print(f"Please install it with: pip install '.[viz]'")

from precice_config_graph import nodes as n
from precice_config_graph.edges import Edge

def print_graph(graph: nx.Graph):
    SIZE: int = 300

    def color_for_node(node):
        match node:
            case n.DataNode():
                return [1, 0.3, 0]
            case n.ReadDataNode() | n.WriteDataNode():
                return [1, 0.5, 0.5]
            case n.MeshNode():
                return [0.9, 0.6, 0]
            case n.ReceiveMeshNode():
                return [0.95, 0.75, 0]
            case n.ParticipantNode():
                return [0.3, 0.6, 1.0]
            case n.ExchangeNode():
                return [0.8, 0.8, 0.8]
            case n.CouplingSchemeNode() | n.MultiCouplingSchemeNode():
                return [0.65, 0.65, 0.65]
            case n.WriteDataNode():
                return [0.7, 0, 1.0]
            case n.MappingNode():
                return [0.1, 0.7, 0.1]
            case n.ExportNode():
                return [0.5, 0.8, 1.0]
            case n.ActionNode():
                return [0.3, 0.5, 0.8]
            case n.WatchPointNode() | n.WatchIntegralNode():
                return [0.5, 0.0, 1.0]
            case _:
                return [0.5, 0.5, 0.5]

    def append_list(list, node, color, size=SIZE):
        list[2].append(node)
        list[3].append(color)
        list[4].append(size * list[1])

    nodes_circle = ["o", 1, [], [], []]
    nodes_circle_small = [".", 1, [], [], []]
    nodes_triangle_up = ["^", 1, [], [], []]
    nodes_triangle_down = ["v", 1, [], [], []]
    nodes_triangle_left = ["<", 1, [], [], []]
    nodes_triangle_right = [">", 1, [], [], []]
    nodes_square = ["s", 0.9, [], [], []]
    nodes_diamond = ["d", 0.9, [], [], []]
    nodes_diamond_wide = ["D", 0.8, [], [], []]
    nodes_pentagon = ["p", 1.4, [], [], []]
    nodes_hexagon_vertical = ["h", 1.4, [], [], []]
    nodes_hexagon_horizontal = ["H", 1.4, [], [], []]
    nodes_octagon = ["8", 1.2, [], [], []]
    nodes_plus = ["P", 1.1, [], [], []]
    nodes_cross = ["X", 1, [], [], []]
    nodes_star = ["*", 1.5, [], [], []]
    node_lists = [
        nodes_circle,
        nodes_circle_small,
        nodes_triangle_up,
        nodes_triangle_down,
        nodes_triangle_left,
        nodes_triangle_right,
        nodes_square,
        nodes_diamond,
        nodes_diamond_wide,
        nodes_pentagon,
        nodes_hexagon_vertical,
        nodes_hexagon_horizontal,
        nodes_octagon,
        nodes_plus,
        nodes_cross,
        nodes_star,
    ]

    for node in graph.nodes():
        color = color_for_node(node)
        match node:
            case n.ParticipantNode():
                append_list(nodes_star, node, color)
            case n.MeshNode():
                append_list(nodes_square, node, color)
            case n.CouplingSchemeNode() | n.MultiCouplingSchemeNode():
                append_list(nodes_octagon, node, color)
            case n.DataNode():
                append_list(nodes_diamond_wide, node, color)
            case n.AccelerationNode():
                append_list(nodes_plus, node, color)
            case _:
                append_list(nodes_circle, node, color)

    def label_for_edge(edge):
        match edge["attr"]:
            case (
            Edge.RECEIVE_MESH__PARTICIPANT__BELONGS_TO
            | Edge.MAPPING__PARTICIPANT__BELONGS_TO
            | Edge.EXCHANGE__COUPLING_SCHEME__BELONGS_TO
            | Edge.WRITE_DATA__PARTICIPANT__BELONGS_TO
            | Edge.READ_DATA__PARTICIPANT__BELONGS_TO
            | Edge.EXPORT__PARTICIPANT__BELONGS_TO
            | Edge.ACTION__PARTICIPANT__BELONGS_TO
            | Edge.WATCH_POINT__PARTICIPANT__BELONGS_TO
            | Edge.WATCH_INTEGRAL__PARTICIPANT__BELONGS_TO
            | Edge.ACCELERATION__COUPLING_SCHEME__BELONGS_TO
            | Edge.CONVERGENCE_MEASURE__COUPLING_SCHEME__BELONGS_TO
            ):
                return "belongs to"
            case Edge.ACCELERATION_DATA__ACCELERATION__BELONGS_TO:
                return "accelerates"
            case Edge.RECEIVE_MESH__PARTICIPANT_RECEIVED_FROM:
                return "received from"
            case Edge.PROVIDE_MESH__PARTICIPANT_PROVIDES:
                return "provides"
            case Edge.MAPPING__TO_MESH | Edge.EXCHANGE__EXCHANGES_TO:
                return "to"
            case Edge.MAPPING__FROM_MESH | Edge.EXCHANGE__EXCHANGED_FROM:
                return "from"
            case Edge.ACTION__SOURCE_DATA:
                return "source data"
            case Edge.ACTION__TARGET_DATA:
                return "target data"
            case (
            Edge.WATCH_POINT__MESH
            | Edge.WATCH_INTEGRAL__MESH
            | Edge.ACTION__MESH
            | Edge.ACCELERATION_DATA__MESH
            | Edge.CONVERGENCE_MEASURE__MESH
            ):
                return "mesh"
            case Edge.ACCELERATION_DATA__DATA | Edge.CONVERGENCE_MEASURE__DATA:
                return "data"
            case Edge.M2N__PARTICIPANT_ACCEPTOR:
                return "acceptor"
            case Edge.M2N__PARTICIPANT_CONNECTOR:
                return "connector"
            case Edge.COUPLING_SCHEME__PARTICIPANT_FIRST:
                return "first"
            case Edge.COUPLING_SCHEME__PARTICIPANT_SECOND:
                return "second"
            case Edge.MULTI_COUPLING_SCHEME__PARTICIPANT:
                return "participant"
            case Edge.MULTI_COUPLING_SCHEME__PARTICIPANT__CONTROL:
                return "control"
            case Edge.USE_DATA:
                return "uses"
            case Edge.WRITE_DATA__WRITES_TO_MESH | Edge.WRITE_DATA__WRITES_TO_DATA:
                return "writes to"
            case Edge.READ_DATA__DATA_READ_BY | Edge.READ_DATA__MESH_READ_BY:
                return "read by"
            case _:
                return ""

    node_labels = dict()
    for node in graph.nodes():
        match node:
            case n.ParticipantNode() | n.MeshNode() | n.DataNode() | n.WatchPointNode() | n.WatchIntegralNode():
                node_labels[node] = node.name
            case n.CouplingSchemeNode():
                node_labels[node] = f"Coupling Scheme ({node.type.value})"
            case n.MultiCouplingSchemeNode():
                node_labels[node] = "Multi Coupling Scheme"
            case n.ExchangeNode():
                node_labels[node] = "Exchange"
            case n.MappingNode():
                node_labels[node] = f"Mapping ({node.direction.name})"
            case n.ExportNode():
                node_labels[node] = f"Export ({node.format.value})"
            case n.ActionNode():
                node_labels[node] = f"Action ({node.type.value})"
            case n.WriteDataNode():
                node_labels[node] = f"Write {node.data.name}"
            case n.ReadDataNode():
                node_labels[node] = f"Read {node.data.name}"
            case n.ReceiveMeshNode():
                node_labels[node] = f"Receive {node.mesh.name}"
            case n.M2NNode():
                node_labels[node] = f"M2N {node.type.value}"
            case n.AccelerationNode():
                node_labels[node] = f"Acceleration {node.type.value}"
            case n.AccelerationDataNode():
                node_labels[node] = f"Accelerate {node.data.name}"
            case n.ConvergenceMeasureNode():
                node_labels[node] = f"{node.type.value}-convergence-measure"
            case _:
                node_labels[node] = ""

    pos = nx.spring_layout(
        graph, seed=1
    )  # set the seed so that generated graph always has same layout

    for list in node_lists:
        if len(list[2]) == 0:
            continue
        nx.draw_networkx_nodes(
            graph,
            pos,
            node_shape=list[0],
            nodelist=list[2],
            node_color=list[3],
            node_size=list[4],
        )
    nx.draw_networkx_labels(graph, pos, labels=node_labels)
    nx.draw_networkx_edges(graph, pos)
    nx.draw_networkx_edge_labels(
        graph,
        pos,
        edge_labels={
            tuple(edge): label_for_edge(d) for *edge, d in graph.edges(data=True)
        },
    )

    # Create a plot for the debugging view of the graph
    handles = []
    unique_types = []
    for list in node_lists:
        marker_type = list[0]
        marker_mult = list[1]
        for node in list[2]:
            name = node.__class__.__name__
            # Only display each node type once
            if name not in unique_types:
                unique_types.append(name)
                # Remove the 'Node' suffix
                label = name[:-4]
                handles.append(
                    plt.Line2D(
                        [],
                        [],
                        marker=marker_type,
                        color="w",
                        markerfacecolor=color_for_node(node),
                        markersize=12 * marker_mult,
                        label=label,
                    )
                )

    plt.legend(handles=handles, loc="upper left", title="Node types:")

    plt.show()
