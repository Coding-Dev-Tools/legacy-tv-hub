# Security and privacy

The TV app keeps its library locally. Regular use includes no analytics, account collection or background reporting. `--setup` temporarily accepts an acknowledgment from the named TV containing only the app version and a one-time setup token, then shuts down. Public archives contain no credentials, pairing material, firmware keys or exploit installers.

Setup tools are intended for a trusted private LAN. They bind a selected interface, restrict peers, refuse TV redirects and expose an explicit asset list. They are temporary development servers and should not be forwarded to the public internet. No firmware flashing, boot changes, resets or factory-menu steps are performed.

Report a reproducible issue using GitHub's private vulnerability reporting if available. A public issue can describe the affected component and impact without credentials, serial numbers, private media URLs or exploit payloads. Include the app version and the smallest reproduction needed to investigate.

This project cannot provide a new DRM implementation or service certification. Subscription compatibility requires an authorized integration and actual protected playback on the named model.
