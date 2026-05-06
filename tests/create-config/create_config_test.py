from precice_config_graph import xml_processing
from precice_config_graph.graph import builder, operations


def test_create_config():
    expected_config: str = "tests/create-config/precice-config.xml"
    path_to_actual: str = "tests/create-config"
    filename: str = "create-config.xml"

    xml = xml_processing.parse_file(expected_config)
    graph = builder.get_graph(xml)

    operations.create_config_file(graph, path=path_to_actual, filename=filename)

    assert operations.check_config_equivalence(expected_config, f"{path_to_actual}/{filename}")


def test_format():
    expected_path: str = "tests/create-config/precice-config.xml"
    actual_path: str = "tests/create-config/create-config.xml"


    with open(expected_path, "r") as file:
        expected_str = file.read()

    with open(actual_path, "r") as file:
        actual_str = file.read()

    assert expected_str == actual_str, "Formatting produced different results."
