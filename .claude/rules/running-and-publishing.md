# Rule: running on the Homey and publishing

- **Only run the app on the Homey when the maintainer asks.** Start it as a background task with
  `npx homey app run --remote` and restart it after every code change. Do not use a terminal pane for it.
- **Only upload or publish a build on explicit request.** Releases are made by the release pipeline when a pull
  request is merged to `main`; do not upload by hand.
