# Samsung 2014 Legacy adapter

Status: packaged preview; no completed native installation or removal test on a physical TV yet.

Samsung's archived 2014 guide documents a local `develop` login with a blank password, an Apps-panel long-Enter menu, IP Setting, then Start User App Sync. The sync server address is the computer address printed by `serve.py`; its normal port is 80. This is a manual TV developer workflow, not a network-only installer.

After syncing, launch LegacyTVHub. Exercise arrows, OK, Return and Exit; play the full bundled demo, confirm picture and audio, save a compatible direct link, restart the app and check persistence. Then test removal using the app manager's delete option. No firmware or country/service-menu change is needed by this package.

Preview 0.3 also offers **Try TV player** during playback. Press Down to focus the controls, use Left/Right to select it, and press OK. Up returns focus to the video; Left/Right then seek. **Browser player** switches back. Check the full ten-second demo in each mode, including sound, seeking, pause/resume and return home. Display & help contains read-only firmware/system information when NNavi provides it. These new native features are experimental and have not run on the research TV yet.

If the developer workflow is absent, record that result. Do not label the model supported. The public guide's availability does not prove that a particular installed firmware or current backend still accepts the workflow.

Sources:

- [Samsung Legacy getting-started archive](https://developer.samsung.com/smarttv/legacy/development-guides/getting-started.html)
- [Samsung's 2014 testing guide, manufacturer document mirrored at Manuals+](https://manuals.plus/m/3eb8b926705f19bf28dc9bc710348f8a4df41a1ff22d55316b384b2a6c8ad0a3)
- [Original developer's widgetlist example](https://gist.github.com/t5k6/51ca45d01cd0e0491205b451b7dbac87)
- [Legacy manifest reference from the original Jellyfin Samsung app](https://github.com/jellyfin-archive/jellyfin-samsungtv/blob/master/config.xml)
