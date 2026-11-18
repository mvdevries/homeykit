import pytest
from pytest_bdd import scenarios

pytestmark = pytest.mark.e2e

scenarios("features/startup_delay_page.feature")
