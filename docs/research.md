# Research boundary

The first research target was a US Samsung UN55HU7250FXZA, a 2014 Legacy TV. The owner reported firmware 1330; the complete installed identifier was not obtained. Its network API reports the firmware as Unknown.

Samsung's exact-model support page supplied a T-NT14UAKUC 1320.0 archive. It was downloaded and both ZIP entries passed CRC reads. Its SHA-256 was `1a0b607e800d5367222925f758165b2d3b6ce4e5293ca168628dacfc7994fb84`; this is a locally computed digest, not a vendor-published signature. The 899,539,310-byte update payload has an MSDU10 header with ten sections and a Salted__ table-of-contents area. It was not decrypted, mounted, modified or sent to a TV.

The service-family diagram describes ARM Cortex-A9, 2 GB DDR3 and 4 GB eMMC. Bootloader versions, signing enforcement, full drivers and recovery remain unverified. Samsung's source portal returned zero results for the model, NT14U and T-NT14UAKUC searches; no complete model-specific buildable source/BSP was obtained. This does not prove none was ever published.

Samsung documents 2014 as Legacy, with generation-level WebKit 537.42 and PlayReady 2.5 support; Widevine Modular support starts in 2017. Those facts do not establish every streaming service's exact current DRM requirements. Paramount+ lists Samsung Tizen support from 2017 onward; this project has no authorized Legacy playback integration and has not demonstrated login or playback. A new interface does not supply that integration.

Across manufacturers, retain the distinction between an app, an updated browser engine, certified protected playback, and flashable OS firmware. A working shared app is not evidence for the other three.

The follow-up [OS replacement investigation](os-replacement.md) records the H-series root candidate, a failed bounded decryption trial and a reproducible offline container inspector. No replacement operating system has been built or booted on the TV.

Sources:

- [Samsung model support](https://www.samsung.com/latin/support/model/UN55HU7250FXZA/)
- [Official inspected archive](https://downloadcenter.samsung.com/content/FM/202005/20200529173847866/T-NT14UAKUC.zip)
- [Samsung platform and DRM specifications](https://developer.samsung.com/smarttv/develop/faq/specifications-and-feature-support.html)
- [Samsung browser user-agent specifications](https://developer.samsung.com/browser/user-agent-string-format.html)
- [Samsung HU7250 service-family diagram, manufacturer document mirror](https://www.manualslib.com/manual/2212390/Samsung-Un-Hu7250f-Series.html?page=84)
- [Samsung Open Source Release Center](https://opensource.samsung.com/)
- [Paramount+ supported devices](https://support.paramountplus.com/s/article/PI-On-which-devices-can-I-watch-Paramount?language=en_US)
