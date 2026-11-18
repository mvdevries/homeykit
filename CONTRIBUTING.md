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

See `README.md` for running the app on a Homey.

## Making a change

1. Branch from `main`. The branch name starts with the kind of change, because the release pipeline derives
   the version from it:
   - `breaking/…` for a change that breaks existing users (major version)
   - `feature/…` for a new feature (minor version)
   - `fix/…` for a fix or anything else (patch version)
2. Keep the code style of the project:
   - small functions that do one thing, with descriptive names (too verbose is better than not clear enough)
   - **no comments or docstrings in code**: explain in the pull request or the README instead
   - layers only use layers below them (see `README.md`)
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

## Reporting security problems

Please follow [SECURITY.md](SECURITY.md) and do not open a public issue.
