# Rule: tests

- Every change comes with tests: unit tests for logic, integration tests for the bridge and services, end-to-end
  tests for the settings page. Coverage must stay at or above 90%.
- Unit tests mirror the layers (`tests/unit/domain`, `application`, `infrastructure`, `endpoints`), one test file
  per source file and one `Test<Unit>` class per unit. A test is named
  `test_given_<state>_when_<action>_then_<result>` and has its arrange, act and assert parts separated by blank
  lines.
- Integration and end-to-end tests are Gherkin scenarios: `.feature` files in `tests/integration/features` and
  `tests/e2e/features`, with the steps in `tests/integration/steps` and `tests/e2e/steps`. Write scenarios in
  plain sentences a user would recognise, and reuse existing steps before adding new ones.
- Test devices are generic and come from `tests/support/sample_devices.py`. Never use real devices, names,
  addresses or tokens in tests, fixtures or snapshots.
