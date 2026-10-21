# Preview 0.3.0

This release improves the usable Legacy media app and its setup/testing workflow. It does not contain replacement firmware, a modern browser engine or subscription-service integration.

- `python serve.py --setup --tv TV_IP` builds the offline copy, verifies the TV, opens the app and waits for a cache acknowledgment before automatically stopping its server and requesting an offline reopen.
- Closing a video before metadata arrives preserves its previous resume position. Editing a link resets that video's history; duplicate-link edits are rejected atomically. Renaming preserves history.
- A failed playback request keeps the actual video error visible instead of overwriting it with an autoplay prompt. Damaged saved JSON is distinguished from inaccessible storage and can be saved again.
- A single release version drives the app, native widget, portable build and offline build. ZIP OS attributes, text line endings, dates and checksum files are deterministic.
- Active CI covers Linux and Windows, with full browser playback and UI regressions on Linux. Local browser tests also exercise delayed metadata, storage recovery, editing and error escape.

See docs/verification.md for exact local and physical-TV evidence. Cold-start persistence, native installation/removal, native PLAYER playback, physical remote keys, picture/audio observation and Paramount+ remain separate, unverified outcomes.
