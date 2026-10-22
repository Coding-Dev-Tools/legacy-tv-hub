# Samsung 2014 Legacy adapter

Status: packaged preview; native installation and removal have not been completed on a physical TV.

Samsung's 2014 guide documents this sequence:

1. On the TV, open **Menu → Smart Features → Samsung Account → Log In** and sign in with user `develop` and a blank password.
2. Open the Smart Hub **Apps** panel.
3. In the Apps grid, hold **Enter** on any app and choose **IP Setting**. Enter the local computer address printed by `serve.py`.
4. Hold **Enter** on an app again and choose **Start App Sync**.
5. Wait for the TV to report that it is installing a new service, then select **Legacy TV Hub** to launch it.

The guide says the `develop` login must be activated before using User App Sync. The sync server address is the computer address printed by `serve.py`; its normal port is 80. This is a manual TV developer workflow, not a network-only installer. If the TV display is blank, the developer sign-in or sync menu is not visible; stop and restore the TV's display/menu before claiming an installation.

After syncing, launch LegacyTVHub. Exercise arrows, OK, Return and Exit; play the full bundled demo, confirm picture and audio, save a compatible direct link, restart the app and check persistence. Then test removal using the app manager's delete option. No firmware or country/service-menu change is needed by this package.

Preview 0.3 also offers **Try TV player** during playback. Press Down to focus the controls, use Left/Right to select it, and press OK. Up returns focus to the video; Left/Right then seek. **Browser player** switches back. Check the full ten-second demo in each mode, including sound, seeking, pause/resume and return home. Display & help contains read-only firmware/system information when NNavi provides it. These new native features are experimental and have not run on the research TV yet.

If the developer workflow is absent, record that result. Do not label the model supported. The public guide's availability does not prove that a particular installed firmware or current backend still accepts the workflow.

Sources:

- [Samsung Legacy getting-started archive](https://developer.samsung.com/smarttv/legacy/development-guides/getting-started.html)
- [Samsung's official 2014 testing guide (PDF)](https://d3unf4s5rp9dfh.cloudfront.net/SmartTV_Legacy/getting-started/Testing+Your+Application+on+a+TV+for+2014.pdf)
- [Original developer's widgetlist example](https://gist.github.com/t5k6/51ca45d01cd0e0491205b451b7dbac87)
- [Legacy manifest reference from the original Jellyfin Samsung app](https://github.com/jellyfin-archive/jellyfin-samsungtv/blob/master/config.xml)
