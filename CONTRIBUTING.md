# Contributing

Start with the supported scope in README.md and docs/compatibility.md. A browser page, accepted launch request or successful ZIP build is narrower evidence than a completed native installation or service playback.

## Local checks

Use Node 24 and Python 3.10+:

```sh
npm ci --ignore-scripts
npm test
python build.py
python -m unittest discover -s tests -v
npx playwright install chrome
npm run test:browser
```

The shared app and TV adapters use ES5 and include no external scripts, accounts or required cloud services. Development tests may use modern Node syntax. Keep platform adapters separate from the shared app. Playback changes need failure/recovery coverage as well as a successful video test.

## Releases

`package.json` supplies the release version and fixed release date. `python build.py` updates the generated app version, builds the native/portable/offline packages, and writes `release.json` and `SHA256SUMS`. Commit those generated text files together with the source. Native widget versions map `major.minor.patch` to `major.(minor*100+patch)`, with minor <= 9 and patch <= 99. Never replace an existing release's assets with changed bytes; publish a new version.

## Device reports

Use the compatibility issue form. Include exact model, year, country, platform, app version, installation/removal method, controls, complete playback, picture/audio observation and app/TV restart behavior. Label desktop simulations separately. Omit serial numbers, MAC addresses, Wi-Fi names, accounts, tokens, pairing codes, signed media links and private network traces.

Document unsupported models and failed tests as carefully as successful ones. An adapter should include reproducible installation and removal instructions before it is described as supported.
