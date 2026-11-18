# Homeykit

A Homey app in Python that offers Homey as a HomeKit bridge (HAP-python). See `CONTRIBUTING.md` for the
commands, tests and pipelines. The rules for working in this repository are in `.claude/rules/`.

## Agreements

- **The working language is English**, see `.claude/rules/language.md`. User-facing texts live in
  `locales/nl.json` and `locales/en.json`, never hardcoded in `settings/`.
- **Never write comments or docstrings in code**, see `.claude/rules/comments.md`. Let the code explain
  itself with small functions and descriptive names: too verbose is better than not clear enough.
- Keep functions small and let them do one thing. A name describes what the function does.
- Python 3.14 and modern: type hints, dataclasses with `slots`, `match`, `Protocol`, `asyncio`.
- Changes go through a branch and a pull request, never directly to `main`. Merge only when the maintainer
  says so. No `Co-Authored-By` or other Claude attribution in commits and pull requests.
- Only run the app on the Homey when the maintainer asks. Start and stop it as a background task with
  `npx homey app run --remote`, and restart it after every code change.
- Uploading and publishing a build is only done on explicit request.
- Branch names start with `breaking/`, `feature/` or `fix/`: the release pipeline derives the version from
  them (major, minor, patch). Pull requests are squash merged; the pipeline reads the branch name from the pull request.
- Tests live in `tests/unit`, `tests/integration` and `tests/e2e` (pytest, coverage at least 90%). Test
  devices are generic (`tests/support/sample_devices.py`); never put real devices, names or addresses in them.
- Format and lint with `uv run ruff format .` and `uv run ruff check .`; the pipeline fails otherwise.
- No secrets, personal data, real device names or home network addresses anywhere in the repository.

## Structure

The code follows the four layers of Clean Architecture. Dependencies only point inwards:

```
domain/            Entities and rules without I/O: models, validation, errors and the constants (defaults.py)
application/       The use cases (one class per file) and ports.py, the interfaces they need
infrastructure/    Everything that touches the outside, implementing the ports:
  repositories/      Homey settings, through SettingsAccess
  gateways/          The Homey Web API (httpx)
  homekit/           HAP-python: the bridge (hap_bridge.py), accessories, service profiles, pairing URI
  local_address.py   The IP address of the Homey
endpoints/         The thin entry points for the Homey API, one decorator (`@endpoint`) injects the services
container.py       Wires the implementations into the use cases (the composition root)
app.py, api.py     Homey entry points; they stay in the root
```

- `domain` imports nothing from the other layers. `application` only imports `domain` and its own ports, never
  HAP-python, httpx or Homey. `infrastructure` implements the ports. `endpoints`, `container.py` and `app.py` sit
  on the outside and may know everything.
- Use the shared helpers instead of writing new ones: `TaskSet`, `PeriodicTask` and `cancel_task` for background
  tasks (`application/background_tasks.py`), `run_logging_errors` for "log the failure and carry on"
  (`application/error_logging.py`) and `SettingsAccess` for reading and writing settings.

## Things you need to know

- `self.homey.api` in the Python SDK is **not** the Homey Web API. For devices the app asks for a token
  (`get_owner_api_token`) and the local address (`get_local_url`) and uses `httpx`. Homey limits the number
  of requests (429): fetch icons slowly.
- Homey puts its own styles on `label`, `button` and `input` (capitals, padding, height). Use plain elements
  (`div`, `span`) in `settings/` and make the padding of inputs mandatory. The `hidden` attribute only works
  because of the rule `[hidden] { display: none !important }`.
- The app icon (`assets/icon.svg`) is used by Homey as a mask: only its transparency counts, Homey colours it
  with the `brandColor`. Filled pictures or coloured tiles become one flat shape.
- Tokens in translations are `__name__`, not `{name}`. Errors from the backend are codes
  (`bridge_name_too_long`) that the page translates.
- The Homey API returns devices as an object with `capabilitiesObj`; the icon of the device type is in
  `iconObj`. Chosen icons (`iconOverride`) cannot be fetched through the API.
- pyhap only builds the pairing URI with `pyqrcode`; `homekit/setup_uri.py` calculates it itself.
- HomeKit IDs (`aid`) of accessories are stored in the Homey settings so rooms and automations in the Home app
  keep working. Do not delete them, and keep the order of services and characteristics in an accessory the
  same (that determines the `iid`).
- pyhap chooses the IP address once at start and listens and advertises on it. If the address changes later,
  the mDNS advertisement is wrong and the server listens on the old address. `application/address_watchdog.py`
  checks this every minute and `BridgeSupervisor` then restarts the bridge (the pairing stays, it lives in
  the state file).
- Old setting keys (`aangeboden`, `aids`, `bridge_naam`, `start_vertraging_aan`,
  `start_vertraging_seconden`) are moved to the English keys at startup by
  `repositories/legacy_settings_migration.py` and then removed. An existing new value is never overwritten.
