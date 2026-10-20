# Verification record

Date: October 20, 2026. Preview 0.1.

## Physical TV

Samsung UN55HU7250, 2014 NT14U family, configured for US, connected by Wi-Fi:

- Identity and advertised service descriptions read over the local network.
- Normal encrypted remote PIN pairing completed with acknowledgement validation; a Menu button command was sent. No physical-screen confirmation of that button's effect was received.
- A generated H.264/AAC MP4 was fetched by the TV's media renderer.
- The renderer reported PLAYING at 2, 6 and 10 seconds, then STOPPED at the full 10-second duration with status OK.
- The original HDMI1 input was restored and the temporary media server stopped.
- These are API-level playback observations. A person has not confirmed picture/audio, and this is not a native-widget HTML playback test.

## Shared app: desktop browser

Chromium browser preview:

- Right arrow moved between home cards; OK opened the selected screen.
- On-screen character input and Backspace changed the video link.
- An invalid link produced visible validation feedback.
- A named video was saved and remained in the library after page reload.
- The bundled demo reached `ended=true`, currentTime=10, duration=10, with no video error.
- High contrast persisted after reload; removal of a test library item completed through the confirmation screen.

## Automated checks run locally

- Library persistence, duplicate URL handling, resume boundaries, rejected unsafe URL schemes/userinfo, corrupt storage and unavailable storage.
- ECMAScript 5 grammar for shared scripts and the first platform adapter.
- Native manifest, ZIP integrity and deterministic package build.
- HTTP byte ranges including suffix requests, HEAD, sync XML and rejection of source/traversal requests.

## Unverified

Native user-widget installation, actual TV-app key delivery, app HTML-video decoding/audio, app persistence on the TV, native removal, other TV browsers/manufacturers and subscription streaming. No firmware was installed. No Paramount+ login or playback has been demonstrated.
