import pytest
from pytest_bdd import scenarios

pytestmark = pytest.mark.integration

scenarios("features/app_startup.feature")
