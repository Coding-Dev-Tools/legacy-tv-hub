# Launch the app in the Samsung Legacy browser

The UN55HU7250 can load Legacy TV Hub using a browser-launch request over its local network. The owner confirmed the app was visible, and the real browser completed its bundled video and pause/resume tests. **This is browser execution, not an installation or firmware replacement.** The first physical test required a temporary local server.

The standard-library launcher verifies the TV's model, reads the RemoteControlReceiver service description, validates the advertised DIAL endpoint and posts a plain HTTP(S) application URL to its WebBrowser resource:

```sh
python tools/samsung_legacy_browser.py --tv YOUR_TV_IP --url YOUR_COMPLETE_APP_URL
```

Both placeholders must be replaced. The default expected model is `UN55HU7250`; `--expected-model` can select another exact model, but no other model has passed hardware testing. The initial descriptor paths and port 8080 control adapter were observed on NT14U. This is not universal discovery across all Samsung generations.

For a local development test, first run `python build.py` and `python serve.py --tv YOUR_TV_IP`. In another terminal, give the launcher the server's printed HTTP URL. Stop the server after testing. For continuing use without a permanent PC, a compatible independently hosted copy or completed native installation is required. Neither delivery method has yet passed on this unit: native widget installation remains unverified, and a GitHub-hosted HTTPS image failed even though a Samsung-hosted HTTPS image loaded.

## What the result means

`launch_request_accepted=true` means that the TV accepted the request. It does not verify that the page rendered or video played. On this unit the service reported `stopped` even while a page executed, so the state is explicitly advisory. Actual support requires on-TV observation or results from a deliberately instrumented test page. The distributed app has no such telemetry.

The tool rejects public/link-local TV addresses, embedded URL credentials, non-HTTP application schemes, a model mismatch, unexpected advertised hosts/ports and appliance redirects. It does not use a pairing PIN, collect device identifiers, change HTTPS/security settings, send firmware or start subscription playback. See the [physical test record](verification.md#october-20-evening-physical-browser-execution).
