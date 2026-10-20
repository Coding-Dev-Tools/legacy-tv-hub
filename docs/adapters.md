# Adding a platform

Keep the shared `app/` independent of a manufacturer's APIs. An installed package may inject a script defining `window.HubPlatform` before `app.js`:

```js
window.HubPlatform = {
    name: 'Platform name',
    keys: function () { return {UP: 38, DOWN: 40, LEFT: 37, RIGHT: 39, ENTER: 13, RETURN: 8, EXIT: 27}; },
    ready: function () {},
    blockNavigation: function (event) {},
    returnToHub: function () {},
    exit: function () {}
};
```

Use the platform's documented key codes and lifecycle methods. PLAY, PAUSE, STOP, FF and REW mappings are optional. Without an adapter the app uses standard browser keyboard events.

Preview 0.2 adds optional `runtimeInfo()` and `createTVPlayer(notify)` hooks. The former returns sanitized `firmware` and `systemVersion` strings. The latter returns `load(url, resumeSeconds)`, `play()`, `pause()`, `seek(deltaSeconds)`, `snapshot()` and `close()`. Snapshots contain `currentTime` and `duration` in seconds, `paused`, `ended` and `error`. Notifications use `loadedmetadata`, `playing`, `waiting`, `pause`, `timeupdate`, `ended` and `error`. The Samsung implementation and its unverified hardware assumptions are described in [native-player.md](native-player.md). The portable browser build has no dependency on these hooks.

A new adapter needs a manifest/build recipe, supported developer installation, removal instructions, actual remote-input tests, complete bundled playback including audio, local-storage persistence, and a restart test on a named physical model. Parsing ES5 or rendering in desktop Chromium does not prove TV compatibility.

Firmware work is a separate per-board effort. It needs a redistributable source/toolchain/BSP, verified boot/update/recovery path and licensed playback components where required. Do not distribute a guessed cross-model firmware image or claim that a web wrapper upgrades the browser engine or protected-media support.

Near-term work: verify the first Legacy user-widget installation, exercise other TV browsers, implement platform packages based on actual available developer workflows, and expand the compatibility matrix with reproducible reports.
