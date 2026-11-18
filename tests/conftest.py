import importlib
import sys
import types
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent.parent
PACKAGE_NAME = "homeykit"


def register_project_as_package() -> None:
    package = types.ModuleType(PACKAGE_NAME)
    package.__path__ = [str(PROJECT_ROOT)]
    sys.modules[PACKAGE_NAME] = package


def register_homey_sdk_stub() -> None:
    homey_package = types.ModuleType("homey")
    homey_app_module = types.ModuleType("homey.app")
    homey_homey_module = types.ModuleType("homey.homey")
    homey_app_module.App = type("App", (), {})
    homey_homey_module.Homey = object
    homey_package.app = homey_app_module
    homey_package.homey = homey_homey_module
    sys.modules["homey"] = homey_package
    sys.modules["homey.app"] = homey_app_module
    sys.modules["homey.homey"] = homey_homey_module


register_project_as_package()
register_homey_sdk_stub()
importlib.invalidate_caches()

pytest_plugins = [
    "tests.support.fixtures",
    "tests.integration.steps.scenario_context",
    "tests.integration.steps.bridge_steps",
    "tests.integration.steps.device_steps",
    "tests.integration.steps.api_steps",
    "tests.integration.steps.homey_app_steps",
    "tests.e2e.steps.page_steps",
]


def pytest_collection_modifyitems(items):
    items.sort(key=lambda item: item.get_closest_marker("e2e") is not None)
