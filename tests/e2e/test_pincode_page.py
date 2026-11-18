import pytest
from pytest_bdd import scenarios

pytestmark = pytest.mark.e2e

scenarios("features/pincode_page.feature")
