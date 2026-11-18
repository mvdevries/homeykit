import pytest
from pytest_bdd import scenarios

pytestmark = pytest.mark.e2e

scenarios("features/bridge_name_page.feature")
