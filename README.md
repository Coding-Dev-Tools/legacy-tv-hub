# Legacy TV Hub

A shared, remote-friendly media app for older smart TVs, with separate installation adapters for each platform.

**Preview 0.2.1. This is an app project, not universal TV firmware. It does not enable Paramount+ or upgrade a TV's browser engine or DRM.** The native package remains version 0.200 and targets Samsung's 2014 Legacy platform. Other manufacturers are in scope, but their native adapters are not implemented yet.

[Open the browser app](https://coding-dev-tools.github.io/legacy-tv-hub/app/) · [Offline browser copy](docs/standalone-browser.md) · [Download previews](https://github.com/Coding-Dev-Tools/legacy-tv-hub/releases)

**Modern streaming replacement acceptance: not met.** See the [feature matrix](docs/compatibility.md) and [latest cache test](docs/verification.md#october-21-cached-browser-copy). Passing the demo does not establish subscription-service compatibility.

The public browser build runs independently of your computer. An older TV still needs a compatible browser, TLS connection and video decoder.

![Legacy TV Hub home screen](assets/home.png)

## What the app does

- A home screen navigated with arrows, OK and Return.
- A local library of direct video links, recent videos and resume positions.
- An on-screen keyboard for entering links with a TV remote.
- Play/pause, seeking, clear playback errors and high contrast mode.
- A bundled offline video for checking playback.
- An optional [browser-cache build](docs/standalone-browser.md). The research TV reopened the app and completed its demo with the asset server stopped. Persistence across a power cycle remains unverified.
- An optional Samsung Legacy native-player bridge, with remote-accessible browser fallback, and read-only firmware information. Both native APIs still need physical-TV validation; see [adapter details](docs/native-player.md).
- No account, analytics, CDN scripts or runtime package dependencies.

The app plays formats the existing TV player supports. A streaming service's website URL is not a direct video URL. Subscription playback requires the service's authorized integration and supported content protection.

## Compatibility: scope versus proof

| Target | Current evidence | Installation |
| --- | --- | --- |
| Desktop Chromium | Browser preview exercised; see [verification](docs/verification.md) | `python serve.py --preview` |
| Samsung 2014 Legacy / Orsay | The shared browser app executed on a physical UN55HU7250; its bundled video, pause/resume, return home and a storage round-trip passed. A later copy reopened and played the clip from browser cache with its asset server closed. **Cold-start persistence, native installation/player and hardware remote input remain unverified.** | Native user-widget ZIP, temporary sync server, [browser-cache copy](docs/standalone-browser.md) and [measured browser-launch method](docs/samsung-legacy-browser.md) provided |
| Other TVs with an HTML5 browser | Shared ES5 app is the candidate; model-specific browser/video/TLS tests are required | Browser build; native installation varies |
| Samsung Tizen | Native adapter not implemented | Requires its own WGT/signing workflow |
| LG webOS / NetCast | Native adapters not implemented | Requires the appropriate platform package and available developer installation path |
| Android / Google TV, Fire TV | Native adapter not implemented | Requires an Android app or suitable browser/runtime |
| Roku and other closed platforms | No implementation or validated install path | Requires a platform-specific implementation and vendor-supported installation |
| TVs without a usable app/browser installation path | Blocked under a software-only constraint | Wi-Fi access alone does not create an installation or boot path |

An OS replacement also requires the exact board support, display/input/network/audio/video drivers, compatible boot/update verification, and recovery. The repository does not contain those vendor components. Each claim of support must name a model and describe an actual test; "all old TVs" is the project scope, not a compatibility claim.

## Run the browser preview

Python 3.10+ is used for development and temporary installation only:

```sh
python build.py
python serve.py --preview
```

Open the localhost URL printed by the server. It stops after 15 minutes; Ctrl+C stops it earlier. The source app is in `app/`. An installed native package includes the app and demo, and does not need a permanently running computer. Remote video sources must remain available independently.

## Samsung 2014 native package

`python build.py` produces `LegacyTVHub_0.200_USA_20261020.zip` and its SHA-256 manifest in `release.json`. It is a Legacy user widget, not a Tizen WGT, Android APK, USB firmware update or replacement for Smart Hub.

Run the short-lived sync server with your TV's local IPv4 address:

```sh
python serve.py --tv YOUR_TV_IP
```

It serves `widgetlist.xml` and the package on port 80, accepts only the named TV and this computer, and changes no firewall rules. Starting it does not install anything. See [installation and removal](docs/samsung-legacy.md). The developer flow must be available on the TV; it has not yet been verified on the research unit.

## Develop and test

The [physical browser test record](docs/verification.md#october-20-evening-physical-browser-execution) documents the first on-TV execution of the shared app. A later [cache test](docs/standalone-browser.md) reopened and played the app's demo with its asset server closed. It removes continuous app serving for that measured browser session; power-cycle persistence and permanent installation remain unverified. The tested GitHub-hosted image failed to load on this TV.

```sh
npm ci --ignore-scripts
npm test
python build.py
python -m unittest discover -s tests
```

The optional GitHub Actions template is in `docs/ci-checks.yml`; it is not enabled automatically. Acorn is a development-only parser used to enforce ES5 syntax. Keep browser code free of modern-only syntax, `fetch`, external frameworks and required cloud services. The build is deterministic. The server exposes an explicit file list and has a fixed lifetime.

## Contribute another TV

Use the compatibility-report issue template. Include model, year, country, platform, app version, install method, actual remote keys, complete video test and removal result. Omit serial numbers, MAC addresses, Wi-Fi names, account data, pairing codes and tokens. Native packaging adapters should be isolated from the shared app, with their own repeatable installation and removal instructions.

The [research summary](docs/research.md) records the current firmware/DRM boundary. MIT licensed; see [LICENSE](LICENSE).

For actual OS replacement research, see the [candidate methods and missing components](docs/os-replacement.md). A read-only MSDU10 container inspector is included in `tools/inspect_firmware.py`; it does not produce or install firmware.
