# Feature status and acceptance

Assessment date: October 20, 2026. Target tested: Samsung UN55HU7250 / 2014 Legacy platform. Preview 0.1 does **not** meet the requirement to replace modern TV software or run all modern streaming services. Other TV platforms need their own verified installation and runtime support.

The status labels below distinguish existing functions from future development. "Blocked" means there is no demonstrated implementation within the current software-only, no-permanent-PC constraint; it is not a claim that future vendor cooperation is impossible.

| Feature | Status | Supporting evidence and remaining limit |
| --- | --- | --- |
| Paramount+ | **Blocked** | Paramount+ lists Samsung Tizen models from 2017 onward. This 2014 Legacy model has no authorized integration in this project. No login or protected playback has been demonstrated. [Paramount+](https://support.paramountplus.com/s/article/PI-On-which-devices-can-I-watch-Paramount?language=en_US), [Samsung platform specifications](https://developer.samsung.com/smarttv/develop/faq/specifications-and-feature-support.html). |
| All other modern streaming services | **Blocked as a universal claim** | No subscription-service adapter is implemented. Each service needs a supported runtime, authorized access and an actual login/playback test. Lack of a test is not a finding that every individual service is impossible. |
| New operating system or browser engine | **Blocked** | No compatible newer OS image, complete board support, verified boot/update path or recovery process has been established. An app cannot replace the underlying browser engine. See the [firmware/source research](research.md). |
| Official firmware update | **Blocked pending evidence of a newer compatible release** | The owner reports 1330; the inspected exact-model download is 1320.0. It was not treated as an upgrade. The complete installed identifier and built-in updater outcome remain unverified. No firmware was installed. |
| Network remote control | **Available now, limited verification** | Normal encrypted pairing completed and button commands were sent. No on-TV confirmation of a command's visible effect has been received. See [verification](verification.md). |
| Casting compatible direct media through the existing DLNA renderer | **Available now for the tested clip** | The physical TV fetched the 10-second H.264/AAC file and reported full-duration playback. This does not establish general codec coverage, Chromecast, AirPlay, screen mirroring or protected service casting. A network media source must be independently available for ongoing use. |
| Direct-video library, resume, remote-friendly interface and contrast | **Custom development feasible; prototype available** | Shared ES5 app and Samsung Legacy package exist. Desktop browser behavior is verified. Native installation, TV key delivery, local storage and the app's HTML-video player still require physical-TV validation. |
| Broader media playback | **Custom development feasible within existing decoder limits** | Direct links can be tested individually. No new codec, hardware decoder or DRM capability has been added. The TV's DLNA renderer test does not prove the widget's HTML player works. |
| New picture/audio hardware capabilities | **Blocked** | No firmware or driver change was installed; no new panel, HDMI or audio capability is supplied by this app. Existing TV settings remain the applicable controls. |
| Native support for other TV manufacturers | **Custom development feasible only where a usable runtime/install path exists** | The browser core is shared; the Samsung Legacy adapter is the only native package currently implemented. See [adapter boundaries](adapters.md). No other manufacturer has passed hardware acceptance. |

No feature is marked "official update available": a newer compatible official release has not been established.

## Required evidence for a support claim

For a native app, record model/platform, install and launch, actual remote input, storage across restart, full video playback with observed picture and sound, recovery after interruption, and removal. A successful package build is not a successful installation.

For each subscription service, record the supported app or authorized integration and test a real account login, license-protected title, sustained playback, seeking, subtitles and audio selection where offered, playback after restart, and a clear network-error recovery path. Never include account details, tokens or protected media in a public report. An unsupported website opening, an app icon, a successful HTTP response or an unprotected demo is insufficient.

"All modern services and software" is an open-ended target rather than a reproducible test list. A release can claim only the named services, models, features and versions it has actually verified. Until at least the native runtime and the requested Paramount+ playback pass, the replacement requirement remains **not met**.
