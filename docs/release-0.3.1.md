# Preview 0.3.1

Fix native and portable ZIP entry ordering across Windows and Linux. Native filesystem path comparisons can sort uppercase names differently between platforms; archives now sort explicitly by their case-sensitive relative names. The package test verifies canonical ordering in all three archives, and CI retains the exact committed checksum check.

The playback and offline setup code is unchanged from 0.3.0. App/native version markers are 0.3.1 / 0.301. Existing 0.3.0 release assets keep their original checksums. See the 0.3.0 notes for the setup, recovery and browser test improvements and docs/verification.md for physical-TV measurements.
