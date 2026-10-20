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

## Public distribution

The public GitHub Pages app was opened in Chromium and its complete demo reached ended=true at 10 seconds without a video error. Both public release ZIPs were downloaded anonymously and matched the published sizes and SHA-256 digests.

## October 20 retest of the published release

The production package and its unchanged demo were tested again on October 20, 2026. The overall request for a replacement that runs all modern streaming services **has not been met**.

| Check | Result | Evidence and limit |
| --- | --- | --- |
| Fresh dependency installation and JavaScript checks | PASS | `npm ci --ignore-scripts --no-audit --no-fund`; `npm test`. State/resume/error cases and ES5 syntax passed. |
| Native and portable package rebuild | PASS | Both rebuilt SHA-256 digests exactly matched `release.json` and the published release. |
| Local HTTP/package tests | PASS | All three Python test methods passed, including byte ranges, HEAD, sync manifest and file isolation. |
| Public browser demo | PASS in desktop Chromium | Arrow/OK navigation started the demo. It reached `currentTime=10`, `duration=10`, `ended=true`, `error=null`. Escape returned home. This is not a test of the old TV browser. |
| TV media-renderer playback | PASS at the network API level | The generated MP4 was byte-identical to `media/demo.mp4` in the published native ZIP. The TV fetched it, reported PLAYING with a progressing clock, then STOPPED at 10/10 seconds with status OK. HDMI1 was restored and the temporary media server stopped. Picture and sound were not confirmed by a person. |
| Remote browser launch | UNSUPPORTED by this TV API | A correctly serialized `RunBrowser` request returned HTTP 200 with `NOTOK_NotSupport`. Network access alone did not open the browser. |
| Native app execution | NOT VERIFIED | No reachable SDB installer was found; the known app's DIAL routes returned 404. Those checks do not prove every installation method is impossible. The documented on-TV developer sync/launch step remains necessary to attempt native testing. |
| Paramount+ or another subscription service | NOT IMPLEMENTED / NOT TESTED | No service integration, account login, license acquisition or protected playback test exists in this release. |
| All modern streaming services and software | NOT MET | The shared interface and one unprotected clip establish neither new browser/OS capabilities nor authorized service playback. |

An instrumented, removable test widget was prepared privately using the same production scripts, styles, adapter and video. It can report its own startup, key codes, a temporary storage round-trip and video state after installation. Preparing or serving that package is not evidence it ran on the TV. Private device addresses, pairing authentication and test collector tokens are excluded from this repository.

The [machine-readable summary](test-results-2026-10-20.json) records the measured checks and their scope.

![Desktop Chromium demo completed at 10 seconds; this is not a photograph or screenshot of the TV](../assets/desktop-demo-finished.jpg)

## Unverified

Native user-widget installation, actual TV-app key delivery, app HTML-video decoding/audio, app persistence on the TV, native removal, other TV browsers/manufacturers and subscription streaming. No firmware was installed. No Paramount+ login or playback has been demonstrated.
