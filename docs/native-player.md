# Experimental Samsung Legacy playback bridge

Preview 0.2 adds a component that calls the TV's existing `SAMSUNG-INFOLINK-PLAYER` plugin from a Legacy user widget. The HTML video player remains the default. **This code has not executed on the physical research TV. It is not a replacement OS, new decoder, browser update or subscription-service integration.**

During playback, Down focuses the buttons. Left/Right select **Try TV player**; OK activates it. **Browser player** switches back, keeping the current position where reported. Up returns focus to the video for Left/Right seeking and OK pause/resume. Return closes either player.

## What is implemented

- Native start, resume, pause, bounded relative seeking, duration/progress callbacks and completion.
- String callback targets required by the old plugin, instance isolation and ignoring callbacks after close.
- Explicit handling of connection, authentication, stream and rendering failures. Failures restore an opaque background and leave the browser fallback accessible.
- The legacy 960×540 display coordinate space, with a transparent app plane only while native playback is selected.
- Optional read-only NNavi `GetFirmware` and `GetSystemVersion` queries for Display & help. No device identifier, app key, Wi-Fi information or account token is requested.
- No runtime server dependency, external script or telemetry in the distributed app. Video links must be independently available.

The bridge converts native time values from milliseconds to the shared app's seconds and supplies resume/relative-seek arguments in seconds. This is a contract under test, **not a measured finding on NT14U**. The full ten-second clip must confirm duration and timing on the actual model. The old NPAPI PLAYER interface must not be confused with the distinct SEF Player interface, whose archived reference describes its own duration return value in seconds.

## Validation completed

`npm test` checks native timing conversion, resume arguments, paused callbacks, bounded seeking, rejected URLs/operations, synchronous authentication failures, recovery and late-callback cleanup. Firmware-query tests limit calls to version information. These tests use a mock plugin.

A separate private browser fixture was visibly labeled **DESKTOP SIMULATION — no TV hardware is being tested**. It exercised remote-only selection of the native option, pause, replay/completion, switching to HTML video and an absent-plugin failure with usable fallback. Desktop Chromium also played the real bundled MP4 to ten seconds without an error. Simulation results establish UI behavior only; they do not demonstrate a Samsung plugin, native codecs or protected playback.

## Hardware acceptance still required

First establish installation and launch through the TV's developer workflow. Then measure native duration/progress against the ten-second clip, inspect picture and sound, test pause/resume/seek, fallback after failure, app restart, storage and removal. Firmware information is verified only when the actual widget returns it. No Paramount+ account login, license acquisition or playback test has occurred.

## Sources and API boundaries

- [Samsung's Legacy API archive page](https://developer.samsung.com/smarttv/legacy/api-references.html), linking the [manufacturer's API-reference ZIP](https://d3unf4s5rp9dfh.cloudfront.net/SmartTV_Legacy/Legacy-API_References.zip). The locally inspected archive was 8,636,407 bytes, SHA-256 `fa12b5b465bbfd033f9d29663593ce28514f4a6f6ff000b90353231672faa5c1`. Its NNavi reference documents the read-only version queries; SEF Player is a separate API.
- [Samsung DeviceAPI Guide V2.20](https://freethetv2011.s3.amazonaws.com/DeviceAPI_Guide%5BV2.20%5D%5B1%5D.pdf), manufacturer documentation for the older native PLAYER object, methods and callbacks.
- [Original Jellyfin Samsung player implementation](https://github.com/jellyfin-archive/jellyfin-samsungtv/blob/master/app/javascript/Gui/GuiPlayer/GuiPlayer.js) was inspected as implementation evidence for callback names and display coordinates. No implementation from that project was copied into this repository.
