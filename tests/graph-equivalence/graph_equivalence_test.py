import precice_config_graph.graph as graph


def test_graph_equivalence_true():
    """
    Tests if graph.py's check_config_equivalence function works as expected.
    The configs are expected to be equivalent.
    """
    path_to_expected: str = "tests/graph-equivalence/equivalent/expected-precice-config.xml"
    path_to_actual: str = "tests/graph-equivalence/equivalent/actual-precice-config.xml"
    assert graph.check_config_equivalence(path_to_expected, path_to_actual,
                                          ignore_names=True), "Graphs are not equivalent."


def test_graph_equivalence_false():
    """
    Tests if graph.py's check_config_equivalence function works as expected.
    The configs are expected to not be equivalent.
    """
    path_to_expected: str = "tests/graph-equivalence/not-equivalent/expected-precice-config.xml"
    path_to_actual: str = "tests/graph-equivalence/not-equivalent/actual-precice-config.xml"
    assert not graph.check_config_equivalence(path_to_expected, path_to_actual,
                                              ignore_names=True), "Graphs are equivalent."
