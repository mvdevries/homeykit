<p align="center">
  <img src="assets/readme-header.png" alt="Homeykit: your Homey as a HomeKit bridge" width="100%">
</p>

# Homeykit

A Homey app written in Python that offers your Homey as a HomeKit bridge, built on
[HAP-python](https://pypi.org/project/HAP-python). The Homey devices you choose appear in Apple's Home app
and work with Siri, widgets and HomeKit automations. Everything runs locally on the Homey, without a cloud.

## What the app does

- Publishes a HomeKit bridge (port 51827) and shows a QR code and pincode for pairing.
- Exposes the Homey devices you choose (lights, sockets, switches and sensors) to HomeKit and keeps them in sync in both directions.
- Settings for the bridge name, the pincode and an optional startup delay, in English and Dutch.
- Watches the IP address: if it changes, the bridge restarts briefly on the new address (the pairing is kept). Without a network address at startup, the app waits until there is one.

## Structure

The code is organised in layers. A layer only uses the layers below it.

```
app.py                  App: builds the services and starts and stops the bridge
api.py                  Endpoints of the app API, exported for Homey
config/                 Constants: ports, default names, setting keys
domain/                 Data models and rules without I/O
  homey_device.py         Homey device and capabilities
  device_row.py           A row in the device list
  pincode.py              Rules and generation of the pincode
  bridge_name.py          Rules for the bridge name
  startup_delay.py        The startup delay and its limits
repositories/           Reading and writing the Homey settings
  legacy_settings_migration.py  Moves settings from the old (Dutch) keys to the current ones
gateways/               Talking to the Homey Web API
  homey_web_api.py        HTTP client with token
  homey_devices_gateway.py  Devices, zones, icons and capabilities
network/                Finding the local IP address of the Homey
homekit/                HomeKit specifics
  service_profiles.py     Which HomeKit services a device gets
  value_conversions.py    Conversions between Homey and HomeKit values
  homey_accessory.py      HAP accessory per Homey device
  setup_uri.py            Pairing URI and QR code
services/               The logic: one class per file
  bridge_service.py       Creates, publishes and stops the HomeKit bridge
  bridge_supervisor.py    Decides when the bridge starts, restarts and stops
  device_sync_service.py  Keeps the accessories equal to the chosen devices
  device_overview_service.py  The device list for the page
  address_watchdog.py     Checks the IP address every minute and restarts the bridge on a change
  bridge_name_service.py  The bridge name: custom name or the name of the Homey
  startup_delay_service.py  Stores the startup delay
  settings_service.py     The settings for the page and their consequences
  icon_service.py         Fetching and caching device icons
  pairing_service.py      Pairing details: QR code, pincode, status
  pincode_service.py      The random or custom pincode
  service_container.py    Wires all services together
endpoints/              Thin endpoints that call the services
settings/               Settings page (HTML, with css/ and js/ per concern)
locales/                Translations (en.json, nl.json)
assets/                 Icon and store images
tests/                  unit/, integration/ and e2e/ tests, plus shared support code
```

## Development

Requires Node.js, the Homey CLI (`npx homey`), a running Docker and [uv](https://docs.astral.sh/uv/). Log in
once with `npx homey login` and pick a Homey with `npx homey select`.

```
npx homey app dependencies install      # prepare the Python packages
npx homey app validate                  # validate
npx homey app run --remote              # run on the Homey with live logs
npx homey app install                   # install permanently
```

`run` does not reload changed code: stop and start it again after a change.

### Quality

```
uv sync                                 # development environment
uv run ruff format .                    # format
uv run ruff check .                     # lint
uv run pytest                           # all tests with coverage
uv run pytest tests/unit                # only unit tests
uv run playwright install chromium      # once, for the end-to-end tests
```

The rules live in `pyproject.toml`. The tests use ten generic sample devices (`tests/support/sample_devices.py`):

- **Unit tests** cover the domain rules, conversions, profiles, repositories, gateways and services.
- **Integration tests** run the real HAP-python bridge on loopback against a fake Homey API, including a
  snapshot of the HomeKit description of all supported devices.
- **End-to-end tests** drive the settings page in Chromium (Playwright) against the real services.

Coverage must stay at or above 90%.

### Pipelines

- **Pull request** (`.github/workflows/pull-request.yml`): checks the branch name, runs lint and formatting,
  all tests with a coverage report (also as a comment on the pull request) and a build validation.
- **Release** (`.github/workflows/release.yml`): on every merge to `main` it determines the version, runs the
  same checks, uploads the app to Athom and creates a tag and GitHub release. The upload job runs in the
  `production` environment, which holds the secret `HOMEY_PAT`.
- **Dependabot** updates the GitHub Actions and the Python packages weekly.

### Versioning

The version is determined by the release pipeline from the branch name of the pull request you merge:

| Branch name   | Version bump |
|---------------|--------------|
| `breaking/…`  | major        |
| `feature/…`   | minor        |
| `fix/…`       | patch        |

Pull requests are squash merged. The pipeline looks up the pull request of the merged commit, takes its branch
name and raises the latest `v<version>` tag by that kind of version. The title of the pull request becomes the
squash commit title and the changelog text. The version in the manifest is replaced during the run and is not
committed.

### Publishing a test version by hand

```
HOMEY_HEADLESS=1 npx homey app publish
```

This needs a changelog entry for the current version in `.homeychangelog.json` and a `README.txt`. Publishing
it as a test version afterwards is done in [tools.developer.homey.app](https://tools.developer.homey.app).

## License

Homeykit is released under the [MIT License](LICENSE). Its runtime dependencies are Apache-2.0, BSD, MIT, MPL-2.0
and LGPL-2.1 (zeroconf) licensed and are installed as packages, not copied into this repository.

## Sources

- The store images and the header are made from the photo
  ["Turned on gray flat screen smart TV"](https://www.pexels.com/photo/turned-on-gray-flat-screen-smart-tv-1571459/)
  from Pexels, used under the [Pexels License](https://www.pexels.com/license/) (free for commercial use, no
  attribution required). The original is not included; the images are cropped and the header is darkened.
