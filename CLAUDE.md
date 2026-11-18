# Homeykit

A Homey app in Python that offers Homey as a HomeKit bridge (HAP-python). `README.md` is for users and
`CONTRIBUTING.md` is for contributors. The rules for working here are in `.claude/rules/`.

## Rules

Each rule is a short file in `.claude/rules/`. Follow them in every task:

- `language.md`: everything in the repository is in English.
- `comments.md`: never add comments or docstrings to code.
- `code-style.md`: small functions, modern Python, respect the layers, use the shared helpers.
- `testing.md`: every change has tests, coverage at least 90%, generic test devices only.
- `git-and-pull-requests.md`: branch and pull request, branch name prefixes, squash merge, no attribution.
- `running-and-publishing.md`: run on the Homey and upload only when asked.
- `no-secrets-or-personal-data.md`: no secrets, personal data, device names or addresses in the repository.

## Project structure

```
app.py, api.py     Homey entry points (stay in the root)
container.py       Wires the implementations into the use cases
domain/            Models, rules, errors and constants, no I/O
application/       The use cases (one class per file) and ports.py, the interfaces they need
infrastructure/    Implements the ports: repositories/, gateways/, homekit/ (HAP-python), local_address.py
endpoints/         Thin entry points for the Homey API, built with the @endpoint decorator
settings/          The settings page (HTML, css/ and js/ per concern)
locales/           Translations: en.json and nl.json
assets/            Icon, logo and store images
tests/             unit/, integration/ and e2e/ (Gherkin features and steps), support/ (sample devices, fake Homey API)
.github/           Workflows (pull request, release, CodeQL) and Dependabot
.homeycompose/     The app manifest; app.json is generated from it
```

## Commands

| Task | Command |
|---|---|
| Set up | `uv sync`, `uv run playwright install chromium`, `npx homey app dependencies install` |
| Build and validate | `npx homey app validate --level publish` |
| Start on the Homey | `npx homey app run --remote` (a background task; restart after every change) |
| Install permanently | `npx homey app install` |
| Test | `uv run pytest` (all, with coverage), `uv run pytest tests/unit`, `tests/integration`, `tests/e2e` |
| Format and lint | `uv run ruff format .` and `uv run ruff check .` |
| Lint the workflows | `uv tool run --from actionlint-py actionlint` |
| Deploy | Merge a pull request to `main`; the release pipeline does the rest |

Deploying: `.github/workflows/release.yml` runs on every merge to `main` that changes the app (not only docs,
tests or workflows) and can be started by hand. It determines the version from the branch name of the merged
pull request, runs the checks, uploads to Athom in the `production` environment (secret `HOMEY_PAT`) and creates
a tag and GitHub release. The version in the manifest is replaced during the run and not committed.

## Architecture

The code follows the four layers of Clean Architecture. Dependencies only point inwards.

- `domain` imports nothing from the other layers.
- `application` only imports `domain` and its own ports, never HAP-python, httpx or the Homey SDK.
- `infrastructure` implements the ports. `endpoints`, `container.py` and `app.py` sit on the outside.
- An architecture test (`tests/unit/test_architecture.py`) fails if an inner layer imports an outer one.

Shared helpers, use these instead of writing new ones:

- `TaskSet`, `PeriodicTask` and `cancel_task` for background tasks (`application/background_tasks.py`)
- `run_logging_errors` for "log the failure and carry on" (`application/error_logging.py`)
- `SettingsAccess` for reading and writing settings (`infrastructure/repositories/settings_access.py`)
- `@endpoint` for the Homey API endpoints (`endpoints/endpoint.py`)

## Homey platform

- `self.homey.api` in the Python SDK is **not** the Homey Web API. For devices the app asks for a token
  (`get_owner_api_token`) and the local address (`get_local_url`) and uses `httpx`. Homey limits the number of
  requests (429): fetch icons slowly.
- The Homey API returns devices as an object with `capabilitiesObj`; the icon of the device type is in
  `iconObj`. Chosen icons (`iconOverride`) cannot be fetched through the API.
- The app icon (`assets/icon.svg`) is used by Homey as a mask: only its transparency counts, Homey colours it
  with the `brandColor`. Filled pictures or coloured tiles become one flat shape.
- Settings keys only store booleans, numbers, strings and dictionaries; lists are stored as JSON strings.
- Old setting keys (`aangeboden`, `aids`, `bridge_naam`, `start_vertraging_aan`,
  `start_vertraging_seconden`) are moved to the English keys at startup by
  `infrastructure/repositories/legacy_settings_migration.py` and then removed. An existing new value is never
  overwritten.

## HomeKit

- pyhap only builds the pairing URI with `pyqrcode`; `infrastructure/homekit/setup_uri.py` calculates it itself.
- HomeKit IDs (`aid`) of accessories are stored in the Homey settings so rooms and automations in the Home app
  keep working. Do not delete them, and keep the order of services and characteristics in an accessory the same
  (that determines the `iid`). A snapshot test guards the description of all supported devices.
- pyhap chooses the IP address once at start and listens and advertises on it. If the address changes later, the
  mDNS advertisement is wrong and the server listens on the old address. `application/address_watchdog.py`
  checks this every minute and `BridgeSupervisor` then restarts the bridge (the pairing stays, it lives in the
  state file).

## Settings page

- Homey puts its own styles on `label`, `button` and `input` (capitals, padding, height). Use plain elements
  (`div`, `span`) in `settings/` and make the padding of inputs mandatory. The `hidden` attribute only works
  because of the rule `[hidden] { display: none !important }`.
- Tokens in translations are `__name__`, not `{name}`. Errors from the backend are codes
  (`bridge_name_too_long`); the page translates them through `errors.<code>` in the locale files.
- Saving goes through `ui.saveWithToast`, which shows the toast and the error.

## Pipelines

- Pull requests run lint and formatting (ruff and actionlint), all tests with coverage, a build validation and a
  branch name check. `main` is protected by rulesets that require these checks and squash merges.
- Dependabot groups minor and patch updates in one pull request per ecosystem and major updates in a separate
  one.
- The Homey CLI runs directly on the runner (it needs Docker and QEMU); the Athom actions do not work for a
  Python app.
