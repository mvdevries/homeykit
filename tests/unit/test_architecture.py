import ast
from pathlib import Path

import pytest

PROJECT_ROOT = Path(__file__).resolve().parents[2]

FORBIDDEN_IN_DOMAIN = ("application", "infrastructure", "endpoints", "container")
FORBIDDEN_IN_APPLICATION = ("infrastructure", "endpoints", "container")
FORBIDDEN_LIBRARIES_IN_INNER_LAYERS = ("pyhap", "httpx", "homey", "segno", "base36")


def imported_modules(path: Path) -> list[tuple[int, str]]:
    tree = ast.parse(path.read_text())
    modules: list[tuple[int, str]] = []
    for node in ast.walk(tree):
        if isinstance(node, ast.ImportFrom):
            prefix = "." * node.level
            modules.append((node.level, prefix + (node.module or "")))
        elif isinstance(node, ast.Import):
            modules.extend((0, alias.name) for alias in node.names)
    return modules


def layer_files(layer: str) -> list[Path]:
    return sorted((PROJECT_ROOT / layer).rglob("*.py"))


def first_segment(module: str) -> str:
    return module.lstrip(".").split(".")[0]


def violations(layer: str, forbidden_layers: tuple[str, ...]) -> list[str]:
    found = []
    for path in layer_files(layer):
        for level, module in imported_modules(path):
            segment = first_segment(module)
            relative_name = path.relative_to(PROJECT_ROOT)
            if level > 0 and segment in forbidden_layers:
                found.append(f"{relative_name} imports {module}")
            if segment in FORBIDDEN_LIBRARIES_IN_INNER_LAYERS:
                found.append(f"{relative_name} imports the library {module}")
    return found


@pytest.mark.parametrize(
    ("layer", "forbidden_layers"),
    [
        ("domain", FORBIDDEN_IN_DOMAIN),
        ("application", FORBIDDEN_IN_APPLICATION),
    ],
)
def test_given_an_inner_layer_when_its_imports_are_read_then_no_outer_layer_is_used(
    layer, forbidden_layers
):
    assert violations(layer, forbidden_layers) == []
