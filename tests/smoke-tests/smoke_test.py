# This smoke test does not test generated graphs for correctness. Instead, it just tests if graph generation does not
# fail on the inputs.
# Provide files to test in the "./configs/"-folder. This script will test all files (including those in subfolders)
# whose names end in the ".xml"-extension.

import git
import pathlib
import pytest

from precice_config_graph import graph
from precice_config_graph import xml_processing


EXTERNAL_DIR = pathlib.Path(__file__).parent / "external"
PRECICE_DIR = EXTERNAL_DIR / "precice"
TUTORIALS_DIR = EXTERNAL_DIR / "tutorials"


def get_configs():
    if not PRECICE_DIR.exists():
        git.Repo.clone_from(
            "https://github.com/precice/precice.git", PRECICE_DIR, depth=1
        )

    if not TUTORIALS_DIR.exists():
        git.Repo.clone_from(
            "https://github.com/precice/tutorials.git", TUTORIALS_DIR, depth=1
        )

    return list(TUTORIALS_DIR.rglob("*/precice-config.xml")) + list(
        PRECICE_DIR.rglob("tests/*/precice-config.xml")
    )


@pytest.mark.parametrize("config", get_configs())
def test_smoke(config):
    print(f"Testing graph generation of {config}")
    xml = xml_processing.parse_file(config)
    assert xml is not None, "Parsing failed"
    G = graph.get_graph(xml)
    assert G
