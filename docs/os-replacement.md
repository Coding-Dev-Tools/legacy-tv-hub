# Replacing the operating system: investigated paths

October 20, 2026. First target: UN55HU7250FXZA, NT14U family. **No compatible replacement OS, modern browser engine or modern subscription playback stack has been built or installed.** An access method would enable further research; it would not itself supply those components.

## What was checked

| Candidate | Finding | Consequence for this TV |
| --- | --- | --- |
| Existing SamyGO Firmware Patcher | Reviewed version 0.34 source. It has no MSDU10 parser or NT14U family entry. | The older patcher is not an established way to build this board's replacement firmware. [Original source](https://github.com/kratz00/SamyGO_Firmware_Patcher). |
| H Root Enabler | The developer's 2020 procedure uses the TV browser and USB files; necessary attachments are restricted to forum members. The developer did not establish a latest working firmware in that thread. | A research candidate, with no validation on this model's reported 1330. No package was installed or exploit run. Its documented USB requirement also falls outside the current no-added-hardware path. [Developer's procedure](https://forum.samygo.tv/viewtopic.php?p=108284#p108284). |
| Native H-series software patch | Its author reports testing on H MST hardware and describes fixed offsets. | That is not NT14U compatibility evidence. No native patch was applied. [Author's report](https://forum.samygo.tv/viewtopic.php?t=14360). |
| Synacktiv Q60T firmware research | Its parser expects MSDU11. This board's inspected update uses MSDU10. A bounded local trial of the published key/IV derivation against the 1,408-byte encrypted TOC candidate produced no valid padding or readable structured header. | The tested derivation did not unlock this update. This does not establish that every other derivation or extraction method will fail. [Pinned research source](https://github.com/synacktiv/samsung-q60t-exploit/blob/db3697456be6f95599ea09ad1570bb80dd8797e1/firmware/decrypt.py). |
| MSDU10/NT14M extraction reports | Community authors describe extraction work for T-NT14MAKUC and model-dependent keys. | An NT14M result is not proof that NT14U can be decrypted. The inspected update remains unmounted and its drivers/bootloader unexamined. [Original extraction report](https://forum.samygo.tv/viewtopic.php?p=109354), [later key discussion](https://forum.samygo.tv/viewtopic.php?p=113128). |
| unixtract MSD10 implementation and published candidates | Reviewed the original project's MSD10 parser and seven published MSD10 candidates at commit `144cf51e3e1b6e832119fde60f676a6def8266f7`. None is labeled NT14U. A local test of their documented derivations against the 1,408-byte TOC candidate found zero valid structured headers. | This further bounded trial did not extract the board's firmware. It does not rule out unpublished keys or other methods. No third-party implementation or keys are included in this MIT project. [Original source](https://github.com/theubusu/unixtract/tree/144cf51e3e1b6e832119fde60f676a6def8266f7), [sanitized result](evidence/msdu10-candidate-check.json). |

The local trial used only a published update file and a small locally written probe. The downloaded third-party decryption/exploit script was not executed. It did not contact the TV, retrieve device or service credentials, modify an update, or produce a replacement image.

## Reproduce the offline inspection

Extract the official archive locally, then inspect its `upgrade.msd` file:

```sh
python tools/inspect_firmware.py /path/to/upgrade.msd --expect-family T-NT14UAKUC
python -m unittest discover -s tests -v
```

The standard-library tool opens the input read-only, validates header and section bounds/overlaps, reports the declared family, and hashes the file. It supports MSDU10 only. The family check compares a header string; it is not a connected-device compatibility or signature check. It has no flash, repack, network, root or decryption operation.

On the existing official 1320.0 payload it found 10 sections and reproduced SHA-256 `018dc05ccae4e0e0c7e9b0b0f1d1dc1067ae02ba8486b56ec91cb78695ef8beb`. The payload is 899,539,310 bytes. See the [inspection output](evidence/nt14u-1320-container.json). This is an older vendor download, not a dump of the reported installed 1330 system. No payload or vendor binary is redistributed here.

## What must exist before a replacement can be installed

1. **A verified entry and recovery path for the exact board/firmware.** Establish a supported loader or a reviewed working access method, identify the boot/update verification behavior, obtain a recoverable backup, and demonstrate recovery. The paired button remote supplies none of this.
2. **A working board port.** Identify and provide the kernel/boot configuration, memory layout, panel/display, input, storage, Wi-Fi, audio and hardware video support. A generic Android, Tizen or Linux image is not evidence that these work on NT14U.
3. **A runtime that can actually execute newer software.** Establish the CPU/ABI, library, graphics and decoder requirements of the chosen browser/player, then test them on the board. Root access alone does not update those libraries or drivers.
4. **Authorized protected streaming.** Obtain each service's supported integration and required licensed content protection. Demonstrate account login and sustained protected playback on the target. A new interface, newer Linux kernel or unprotected demo does not satisfy this gate.
5. **A board-specific update with a validated rollback.** A replacement needs successful boot, picture, sound, remote, networking, restart and interruption/recovery tests before it can be called installable. No such image or test result exists in this repository.

These are unmet engineering prerequisites, not requests for permission to perform a completed upgrade. The present recommendation under the no-added-hardware/no-permanent-PC constraint is to retain the installed system while investigating a verifiable entry/recovery path and obtaining the missing board components. There is currently no demonstrated software-only replacement that provides all modern streaming services.

## Native app installation error

The owner reported an installation error without a stage or code. The preceding temporary sync-server session recorded zero TV manifest downloads, package downloads or startup events and was stopped after its test window. An inactive server can cause a sync/download failure, but the actual cause of the reported error has not been established. A later bounded identity/discovery attempt timed out. No installed-app or firmware change can be inferred from those observations.

Resolving a Legacy widget installation would permit app runtime tests. It would not replace the operating system. Future installation attempts need the TV reachable, the temporary installer actively serving the package, and the on-TV developer workflow available.

The TV subsequently became reachable again and positively identified as UN55HU7250. After a report of a blank screen, a paired Exit command was sent; network queries reported HDMI1 and no active renderer media, with status OK. There were still zero TV manifest/package fetches or widget startup events. A later identity request timed out again. These observations do not establish that the app installed, caused the blank screen, or repaired the TV.
