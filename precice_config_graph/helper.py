import precice_config_graph.enums as e

"""This file contains helper items, such as default values and constants."""

INDENT: str = " " * 4

# Default values for nodes and config
MESH_DIMENSIONALITY: int = 3

RECEIVE_MESH_API_ACCESS: bool = False

COUPLING_SCHEME_MAX_TIME_WINDOWS: int = 10
COUPLING_SCHEME_TIME_WINDOW_SIZE: float = 1e-1

MAPPING_POLYNOMIAL: e.MappingPolynomialType = e.MappingPolynomialType.SEPARATE
MAPPING_X_DEAD: bool = False
MAPPING_Y_DEAD: bool = False
MAPPING_Z_DEAD: bool = False
MAPPING_SOLVER_RTOL: float = 1e-9
MAPPING_VERTICES_PER_CLUSTER: int = 50
MAPPING_RELATIVE_OVERLAP: float = 0.15
MAPPING_PROJECT_TO_INPUT: bool = True
MAPPING_MULTISCALE_TYPE: e.MappingMultiscaleType = e.MappingMultiscaleType.COLLECT
MAPPING_MULTISCALE_AXIS: e.MappingMultiscaleAxis = e.MappingMultiscaleAxis.X
MAPPING_MULTISCALE_RADIUS: float = 1

EXPORT_DIRECTORY: str = "."

WATCH_INTEGRAL_SCALE_WITH_CONNECTIVITY: bool = False

M2N_DIRECTORY: str = ".."

CONVERGENCE_MEASURE_LIMIT: float = 1e-1
CONVERGENCE_MEASURE_REL_LIMIT: float = 1e-1

PRECONDITIONER_FREEZE_AFTER: int = -1
PRECONDITIONER_UPDATE_ON_THRESHOLD: bool = True

ACCELERATION_FILTER_TYPE: e.AccelerationFilterType = e.AccelerationFilterType.QR3
ACCELERATION_FILTER_LIMIT: float = 1e-16

MAPPING_BASIS_FUNCTION_SUPPORT_RADIUS: float = 0.5
MAPPING_BASIS_FUNCTION_SHAPE_PARAMETER: float = 1

MAPPING_EXECUTOR_GPU_DEVICE_ID: int = 0
MAPPING_EXECUTOR_N_THREADS: int = 0
