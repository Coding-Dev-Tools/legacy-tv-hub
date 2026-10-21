# Optional copy stored in the TV browser

October 21, 2026. A physical UN55HU7250 stored Legacy TV Hub and the bundled H.264/AAC clip using HTML5 Application Cache. After the asset listener was closed and a different document had loaded, a new app document opened from that cache and played the full clip without a video error. The later preview 0.2.1 variant also displayed its offline-copy status on the TV. See the [measured result](evidence/physical-cache-2026-10-21.json).

This supplies a cached copy of the existing player. It does not replace Smart Hub, install a native widget, update firmware or enable Paramount+. Browser/process restart and persistence across TV power loss have **not** been verified. A cached copy can be cleared or evicted, so this is not yet a validated permanent installation.

## Automatic temporary setup

```sh
python serve.py --setup --tv YOUR_TV_IP
```

The command builds and verifies the offline copy, opens the identified TV browser, and waits for its cache-ready acknowledgment. It then closes the asset listener and requests the clean app URL again. Acknowledgment contains only the app version and a temporary token; normal use sends no reports. Setup times out with an unverified result if the TV does not acknowledge. Save the printed URL in the TV browser's bookmarks. Automatic bookmark creation is unavailable to the page.

## Build and load manually

From the repository root, using Python 3.10 or newer:

```sh
python tools/build_offline_web.py
python serve.py --offline --tv YOUR_TV_IP --port 8769
```

The builder creates `dist/offline/` and `dist/LegacyTVHub_offline_web_0.3.1.zip`. The server verifies its asset hashes, exposes only the declared files, serves the manifest as `text/cache-manifest`, and stops automatically after 15 minutes. It needs no native ZIP, firewall changes, accounts or additional packages. For manual serving, stop it after the app reports its stored copy. `--duration` can extend the temporary window up to one hour.

Open the server's printed URL in the TV browser, including its port. On the measured Samsung target, the repository's browser launcher can open it over the LAN:

```sh
python tools/samsung_legacy_browser.py --tv YOUR_TV_IP --url http://YOUR_PC_IP:8769/
```

Wait for **Offline copy stored** or **Offline copy ready** in the app header. Save the exact URL in the TV browser's bookmarks if its UI supports this. A web page cannot create that bookmark itself. Stop the server, navigate to another page, and reopen the same URL from the TV to check local use. Do not treat a still-open page as proof of an offline reopen.

The diagnostic result listener used during development could receive reports but could not serve app files. It is absent from the public build: no collector, background reporting or account data is included.

## What remains dependent on the TV and network

- The cache includes the app files and bundled demo. Videos added to the library still need an independently available source; arbitrary movies and service catalogs are not downloaded by this feature.
- Only browsers implementing the old AppCache feature can use this variant. Modern browsers may ignore it and continue requiring hosting. The regular browser build and native package remain separate options.
- AppCache keeps the original address as its identity. Clearing browser data, changing the origin or cache eviction can require another temporary transfer. Reopen the exact original URL even after its server stops.
- An update-check failure while the host is absent is expected when an existing cached copy remains usable. It is different from an initial save failure. The header distinguishes these cases.
- Firmware, browser engine, hardware codecs, protected playback, app-store access and picture/audio hardware are unchanged. No subscription service has passed account login or protected playback in this project.

## Native installation boundary

Samsung's [2014 testing guide](https://d3unf4s5rp9dfh.cloudfront.net/SmartTV_Legacy/getting-started/Testing+Your+Application+on+a+TV+for+2014.pdf) describes the local `develop` login, Apps-panel IP setting and Start App Sync. Its [Legacy FAQ](https://developer.samsung.com/smarttv/legacy/samsung-legacy-platform-faq.html) confirms that Tizen packages are incompatible and that USB testing needs a vendor-issued signature. No supported network upload command or successful native sync has been established on the research TV. A browser launch is not a substitute for that installation workflow.

Paramount+ currently specifies Samsung Tizen models from 2017 onward in its [supported-device list](https://support.paramountplus.com/s/article/PI-On-which-devices-can-I-watch-Paramount?language=en_US). An authorized integration and compatible protected playback would still need to be obtained and demonstrated on this 2014 platform. The replacement-software requirement remains **not met**.
