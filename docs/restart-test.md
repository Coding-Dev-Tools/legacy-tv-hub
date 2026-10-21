# Verify a cached copy after a TV restart

This test checks the app files, bundled video and saved state on a physical TV. It does not establish native installation, firmware replacement or subscription-service playback. The latest attempt on the UN55HU7250 is [blocked by an unreachable TV](evidence/restart-attempt-2026-10-21.json); restart persistence remains unverified.

## Prepare once while the TV is reachable

1. Complete [offline setup](standalone-browser.md) and wait for the TV's cache-ready acknowledgment. Record the app version and exact URL, including its port and path. Bookmark that URL in the TV browser.
2. Add a harmless named library entry, select a setting such as high contrast, and record their values. For a separate resume test, use a lawful video source that will still be available after the restart, pause partway through it, close the player and record the saved position. This source is independent of the app's cached demo.
3. Stop the setup/file server. Verify that its port is no longer listening. A still-running HTTP server returning errors is weaker evidence than a closed asset listener.
4. Leave the app, then reopen its exact saved URL with the file server stopped. Play the entire bundled demo, pause/resume it, and return Home. Record picture, sound, remote response and any video error. This establishes a baseline without the file server.

Do not run setup again between the baseline and the restart result. Doing so could refill a lost cache and invalidate the persistence test. Do not clear browser data, change the URL or restore factory settings.

## Cold-boot and reopen

Use Samsung's [normal cold-boot procedure](https://www.samsung.com/us/support/troubleshoot/TSG10002361/): with the TV on, hold the Samsung remote's Power button until it powers off and back on. If that procedure is unavailable, disconnect power for 30 seconds, reconnect it, and turn the TV on. Record which procedure was actually used. A short Power press that enters standby is a different test.

After the TV reconnects to its network, reopen the exact bookmarked URL. Keep the app file server stopped throughout. Verify:

- The expected app version loads in a fresh document.
- The entire bundled demo plays with picture and sound; pause/resume and Return/Home work.
- The previously saved library entry and setting remain.
- The independent resume test starts near its recorded position, if that test was prepared.

A temporary report-only listener may observe app events, provided it cannot serve any app or media files. Document that instrumentation and shut it down after the test. Normal app use includes no such listener or reporting. Remote browser-launch acceptance alone does not prove that a page opened, and a new page identity alone does not prove a TV cold boot.

## Report the measured result

Record model/platform, app version, restart method, baseline and post-restart times, whether the asset listener was closed throughout, complete playback/error results, saved-state results, and human picture/sound/remote observations. Omit serial numbers, account data, pairing material, private addresses and saved media URLs from public reports.

Use **passed** only for checks actually observed after the recorded restart. Use **failed** for an observed loss of cache or saved state. Use **unverified** when the TV cannot be reached, the restart is unconfirmed, no fresh document execution is observed, or setup had to run again before testing. Keep partial results separate: app files, media playback and saved state can have different outcomes.

If the cache was lost, another temporary transfer can restore the browser copy, but that recovery is not a persistence pass. Even a full pass does not guarantee that future cache eviction, browser-data clearing or firmware changes will preserve it. It also does not establish automatic launch at TV startup.
