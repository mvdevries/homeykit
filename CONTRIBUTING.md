# Contributing

Thanks for your interest in Homeykit. Bug reports, ideas and pull requests are welcome. This is a small
hobby project, so replies can take a few days.

## Language

Everything in this repository is in English: code, commit messages, pull requests, issues and documentation.
Texts shown to users live in `locales/en.json` and `locales/nl.json`.

## Before you start

- Open an issue first for anything bigger than a small fix, so we can agree on the approach.
- Devices that are not supported yet (thermostats, TVs, speakers) are a known gap; an issue describing the
  device and its capabilities is a good start.
- Never put real device names, addresses, tokens or other personal data in issues, tests or code.

## Setting up

You need Node.js, the Homey CLI (`npx homey`), Docker and [uv](https://docs.astral.sh/uv/).

```
uv sync
uv run playwright install chromium
```

Log in once with `npx homey login` and pick a Homey with `npx homey select`.

## Making a change

1. Branch from `main`. The branch name starts with the kind of change, because the release pipeline derives
   the version from it:
   - `breaking/…` for a change that breaks existing users (major version)
   - `feature/…` for a new feature (minor version)
   - `fix/…` for a fix or anything else (patch version)
2. Keep the code style of the project:
   - small functions that do one thing, with descriptive names (too verbose is better than not clear enough)
   - **no comments or docstrings in code**: explain in the pull request or the README instead
   - dependencies point inwards: `domain`, `application`, `infrastructure` (see `CLAUDE.md` for the layout)
3. Add tests. Unit tests for logic, integration tests for the bridge and services, end-to-end tests for the
   settings page. Test devices come from `tests/support/sample_devices.py` and stay generic.
4. Run everything locally:

   ```
   uv run ruff format .
   uv run ruff check .
   uv run pytest
   ```

   Coverage must stay at or above 90%.
5. Open a pull request against `main` with a clear title (it becomes the changelog text) and a description of
   what changed and why. The pull request checks must pass.

Pull requests are squash merged, so the title of the pull request becomes the commit message on `main`.

## Running on a Homey

```
npx homey app dependencies install      # prepare the Python packages
npx homey app validate                  # validate
npx homey app run --remote              # run on the Homey with live logs
npx homey app install                   # install permanently
```

`run` does not reload changed code: stop and start it again after a change.

## Tests and quality

```
uv run ruff format .                    # format
uv run ruff check .                     # lint
uv run pytest                           # all tests with coverage
uv run pytest tests/unit                # only unit tests
```

The rules live in `pyproject.toml`.

- **Unit tests** (`tests/unit`, mirroring the layers) cover the domain rules, conversions, profiles, repositories,
  gateways and services. Their names read `test_given_<state>_when_<action>_then_<result>`.
- **Integration tests** are Gherkin scenarios (`tests/integration/features`) that run the real HAP-python bridge
  on loopback against a fake Homey API, including a snapshot of the HomeKit description of all supported devices.
- **End-to-end tests** are Gherkin scenarios (`tests/e2e/features`) that drive the settings page in Chromium
  (Playwright) against the real services.
- The steps live next to the features (`steps/`) and are written with pytest-bdd.

## Pipelines and releases

- **Pull request** (`.github/workflows/pull-request.yml`): checks the branch name, runs lint and formatting, all
  tests with a coverage report (also as a comment on the pull request) and a build validation.
- **Release** (`.github/workflows/release.yml`): on every merge to `main` it determines the version, runs the
  same checks, uploads the app to Athom and creates a tag and GitHub release. The upload runs in the
  `production` environment, which holds the secret `HOMEY_PAT`.
- **CodeQL** (`.github/workflows/codeql.yml`) scans the Python code, the settings page and the workflows for
  security problems on pushes and pull requests to `main`, and every week.
- **Dependabot** updates the GitHub Actions and the Python packages weekly. Minor and patch updates arrive in
  one pull request per ecosystem, and major updates in a separate one so they can be reviewed on their own.

The version comes from the branch name of the merged pull request:

| Branch name   | Version bump |
|---------------|--------------|
| `breaking/…`  | major        |
| `feature/…`   | minor        |
| `fix/…`       | patch        |

The pipeline raises the latest `v<version>` tag by that kind of version. The title of the pull request becomes
the squash commit title and the changelog text. The version in the manifest is replaced during the run and is
not committed.

## AI assistance

This project is itself built with AI assistance (see the README). You may use AI tools for your contribution too,
as long as you understand and have tested what you submit and it follows the rules above. You are responsible for
your pull request, not the tool.

## Reporting security problems

Please follow [SECURITY.md](SECURITY.md) and do not open a public issue.
