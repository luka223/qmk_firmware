# Keychron Q1 HE – battery-monitor firmware (unofficial)

> **Disclaimer:** This is **unofficial, community-modified firmware**. It is not affiliated with,
> endorsed by, or supported by Keychron or the QMK project. Flash it **at your own risk**.
> It is a derivative of the QMK / Keychron firmware and is licensed under **GPLv2** (see
> [license_GPLv2.md](license_GPLv2.md)).

## What this is

A fork of [Keychron/qmk_firmware](https://github.com/Keychron/qmk_firmware) trimmed down to the
**Keychron Q1 HE** only. It adds one feature: the keyboard **reports its battery level** to a
program on the PC, including when it is connected through the 2.4 GHz **Keychron Link** receiver.

- Over the **USB cable**, a program sends raw HID command `0xA4` and the keyboard replies.
- Over **2.4 GHz**, the stock receiver does not forward PC → keyboard requests, so the keyboard
  **pushes** the same `0xA4` report on its own every 2 seconds while connected. The PC program
  just listens on the receiver's raw HID interface.
- Over **Bluetooth** nothing is pushed; Windows reads the battery through the standard BLE battery service.

The battery report is ported from [Keychron PR #477](https://github.com/Keychron/qmk_firmware/pull/477)
by [OutersGIT](https://github.com/OutersGIT) (written for the K10 HE; not merged upstream).
Thanks to them for the original work.

| Layout | Status |
|---|---|
| `ansi_encoder` (PID `0x0B10`) | Built. Hardware testing in progress. |
| `iso_encoder` (PID `0x0B11`) | Builds, **untested**. USB device version not bumped. |
| `jis_encoder` (PID `0x0B12`) | Not build-checked, **untested**. USB device version not bumped. |

## Base version

Keychron has not published the exact source of the official Q1 HE firmware **1.4.0**
(Launcher reports `v1.4.0 2026-08-03-09:40:49`; the public source still says 1.3.1). This fork is
based on **`07bfc38a4b`** (2026-07-21, "Fix K0 Max matrix not working") on Keychron's `2025q3`
branch: the last public commit before the 1.4.0 build time. The `keyboards/keychron/q1_he/` folder
has not changed since April 2026, so this should be very close to 1.4.0, but it **may not be
byte-identical**.

These later public commits are **not** included:

- `9a6b37a77c` (2026-08-07) Add EEPROM driver header
- `620468c58b` (2026-08-07) Block raw HID send while pairing
- `fb316dae6d` (2026-09-02) Fix snap click keys releasing when set to FIRST_KEY and SECOND_KEY

## Differences from official 1.4.0

1. Raw HID command `0xA4` (battery report), answered over USB and pushed every 2 s over 2.4 GHz.
   The `FEATURE_BATTERY` bit is set in the `0xA2` feature reply.
2. Battery voltage is also measured while on the USB cable, so the USB reply has a current value.
3. Launcher shows the version as **`v1.4.0-battery-monitor`** (no build date; the reply is limited
   to 31 characters).

## Battery report format

32-byte raw HID report, usage page `0xFF60`, usage `0x61`, VID `0x3434`:

| Byte | Meaning |
|---|---|
| 0 | `0xA4` |
| 1 | battery % |
| 2–3 | battery voltage in mV, little-endian |
| 4 | charging: 0 = on battery, 1 = charging, 2 = full |
| 5 | connection: `0x01` USB, `0x02` Bluetooth, `0x04` 2.4 GHz |
| 6 | model id: `2` = Q1 HE (own choice; the K10 HE mod uses `1`) |

**Host program over the receiver:** don't ask, listen. Open every `VID 0x3434` interface with usage
page `0xFF60`, keep reports where byte 0 is `0xA4` (and byte 6 is `2`), and store the latest one with
a timestamp. If nothing arrives for ~30–60 s, the keyboard is asleep or off: show "last seen"
instead of a number.

## Build (Windows)

1. Install [QMK MSYS](https://msys.qmk.fm/).
2. Clone this repo. **Don't run plain `qmk setup`** (it clones upstream qmk_firmware). Instead,
   point QMK at this clone and fetch the submodules:
   ```
   qmk config user.qmk_home=D:/projects/qmk_firmware
   git submodule update --init --recursive
   ```
3. Build:
   ```
   qmk compile -kb keychron/q1_he/ansi_encoder -km keychron
   ```
   (or `make keychron/q1_he/ansi_encoder:keychron`)
4. The output is `keychron_q1_he_ansi_encoder_keychron.bin` in the repo root.

## Flash

1. **Back up** your keymap and HE profiles in [Keychron Launcher](https://launcher.keychron.com/)
   first. Flashing may reset them.
2. Install [QMK Toolbox](https://github.com/qmk/qmk_toolbox/releases) and open the `.bin`.
3. Enter bootloader mode: unplug USB → set the mode switch to **Cable** → hold **Esc** (or press
   the reset button under the space bar) → plug USB back in. Toolbox shows
   "STM32 DFU device connected".
4. Click **Flash**. If 2.4 GHz does not reconnect afterwards, re-pair with the receiver.
5. Check: Launcher (over the USB cable) shows `v1.4.0-battery-monitor`.

## Go back to official firmware

Connect with the USB cable, open https://launcher.keychron.com → **Firmware**, and flash the latest
official firmware. If Launcher won't offer it because of the custom version text, use the
forced-flash page: https://launcher.keychron.com/#/firmware/flash?force=true&keep=true

The STM32 bootloader is in ROM, so a bad flash can't brick the keyboard: bootloader mode always
works and you can flash again.

## Test tools

Both scripts need `pip install hidapi`. Close Launcher first so it doesn't hold the device.

- `python tools/q1he_battery.py` – asks the keyboard for its battery once over the USB cable.
  Prints %, mV, charging state, connection and model id.
- `python tools/q1he_battery.py --listen` – prints pushed `0xA4` reports from any Keychron raw HID
  interface (use this with the 2.4 GHz receiver; a report should appear about every 2 s).
- `python tools/q1he_version.py` – read-only; prints the firmware version text and USB device version.
