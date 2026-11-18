# Rule: tests

- Every change comes with tests: unit tests for logic, integration tests for the bridge and services, end-to-end
  tests for the settings page. Coverage must stay at or above 90%.
- Test devices are generic and come from `tests/support/sample_devices.py`. Never use real devices, names,
  addresses or tokens in tests, fixtures or snapshots.
