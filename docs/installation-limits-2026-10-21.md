# Further native-installation investigation

October 21, 2026. Target: Samsung UN55HU7250, identified over the LAN as `14_NT14U_2D_BT`. The TV was reachable again. Its identity API still returned `FirmwareVersion: Unknown`; 1330 remains the owner's reported version. No replacement firmware, native widget or subscription-service integration was installed during this investigation.

## New device measurements

The TV advertised GUI cloning and listed `HDCP,PrivateTZ` as the screen-sharing transports' protection types. These are screen-sharing fields, not a measurement of the browser's subscription-video DRM support.

A conventional SOAP `StartCloneView` request using the advertised `Normal` flag and published `PrivateTZ` transport returned HTTP 200 with **NOTOK_OtherMode**. It supplied no stream URL. No TV media was downloaded, no screen image was obtained, and no stream session was established. No source-change command was sent. This result is specific to the tested mode and is not a claim that every screen-sharing configuration is impossible.

Browser launches continued to return HTTP 201 with an instance path ending in `/ws/apps/WebBrowser/run`. A DELETE to that returned instance path at the TV's advertised multiscreen port returned HTTP **404**, as did the earlier singular-path attempt. An accepted launch still does not establish execution, installation, browser-process restart or a firmware change. No cold-start or power-cycle test passed.

See the [sanitized measurement](evidence/native-installation-2026-10-21.json). No screen-sharing decoder, protection bypass, factory-menu sequence, reset, downgrade or firmware write was attempted.

## What Samsung's remote install API actually provides

The [Smart View SDK reference](https://smartviewsdk.github.io/API-GUIDE/android-api/docs/overview-summary.html) describes `Application.install` using an application ID issued by Samsung after submission. Its example explains that installation opens the TV's installation page and still requires selection of Install with the remote. It does not document uploading an arbitrary local Legacy widget ZIP or replacing the operating system. Legacy TV Hub has no such Samsung-issued store ID.

Samsung's [SDK capabilities table](https://developer.samsung.com/smarttv/develop/extension-libraries/smart-view-sdk/getting-started.html) includes installed TV apps on 2014 devices, while marking the SDK's JavaScript web casting and wake-on-wireless features unavailable for that year. This table does not negate the separately measured browser launch request or AppCache copy. These are different interfaces.

The [2014 user-app guide](https://d3unf4s5rp9dfh.cloudfront.net/SmartTV_Legacy/getting-started/Testing+Your+Application+on+a+TV+for+2014.pdf) describes local `develop` login, the Apps-panel IP setting and Start App Sync. The [Legacy FAQ](https://developer.samsung.com/smarttv/legacy/samsung-legacy-platform-faq.html) confirms that Tizen applications are incompatible with this platform and that its USB testing route requires a Samsung-issued signature. The prepared native package has still not completed that installation workflow on the research TV.

## Components still missing for the requested replacement

| Required component | Current evidence | Why an app build does not resolve it |
| --- | --- | --- |
| A working native entry, update/boot method and recovery for this board and firmware | No validated loader, shell, flashable replacement image or recovery/rollback result. The paired remote and browser are the established network interfaces. | A successful ZIP build or browser launch does not establish permission or a mechanism to write and boot a new system. Boot/update verification behavior remains unexamined. |
| Complete board support and a compatible system runtime | No complete, buildable board-support package with panel, storage, input, networking, audio and video support has been obtained. The inspected official firmware remains encrypted and unmounted. | A generic ARM Linux/Android/Tizen build is not evidence of a working port to this TV. Further public searches did not obtain the missing package; that does not prove it was never published. |
| Authorized Paramount+ integration and compatible protected playback | No integration, account login, license-protected playback or supported Legacy app. Paramount+ lists Samsung Tizen models from 2017 onward. | A new home screen, cached player, decoder or operating-system build alone does not demonstrate service authorization and playback. See [Paramount+ supported devices](https://support.paramountplus.com/s/article/PI-On-which-devices-can-I-watch-Paramount?language=en_US). |
| Evidence for permanent independent operation | Warm browser-cache document reopen and demo playback passed in earlier tests. Native installation and persistence across browser/TV restart remain unverified. | No permanent PC process is running, but a cached warm reopen is a narrower result than a reliable replacement that boots into modern services. |

The software-only replacement request remains **unmet**. This investigation did not produce another app release or a purported firmware image: the outstanding dependencies are still unavailable. The existing cached player and preview packages retain their documented limits.
