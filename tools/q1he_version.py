"""Ask a Keychron Q1 HE for its firmware version and build date (read-only).

Sends Keychron raw-HID command 0xA1 (KC_GET_FIRMWARE_VERSION) and prints the
reply, e.g. "v1.4.0 2026-02-10-14:32:05". Nothing is written to the keyboard.

Requirements:  pip install hidapi
Connect the keyboard with the USB cable and set the side switch to Cable mode
(the 2.4 GHz dongle does not forward requests to the keyboard).
"""
import sys
import hid

VID = 0x3434
PIDS = {0x0B10: "Q1 HE ANSI", 0x0B11: "Q1 HE ISO", 0x0B12: "Q1 HE JIS"}
RAW_USAGE_PAGE = 0xFF60
RAW_USAGE_ID = 0x61
REPORT_SIZE = 32
KC_GET_FIRMWARE_VERSION = 0xA1


def find_raw_interface():
    for d in hid.enumerate(VID, 0):
        if (d["product_id"] in PIDS and d["usage_page"] == RAW_USAGE_PAGE
                and d["usage"] == RAW_USAGE_ID):
            return d
    return None


def main():
    info = find_raw_interface()
    if not info:
        sys.exit("Q1 HE raw-HID interface not found. Use the USB cable, "
                 "Cable mode, and close Keychron Launcher/VIA tabs.")

    dev = hid.device()
    dev.open_path(info["path"])
    try:
        # Leading 0x00 is the HID report ID (required by hidapi on Windows).
        packet = [0x00, KC_GET_FIRMWARE_VERSION] + [0x00] * (REPORT_SIZE - 1)
        dev.write(packet)
        reply = dev.read(REPORT_SIZE, 1000)
    finally:
        dev.close()

    if not reply or reply[0] != KC_GET_FIRMWARE_VERSION:
        sys.exit(f"Unexpected or no reply: {reply}")

    text = bytes(reply[1:]).split(b"\x00")[0].decode("ascii", "replace")
    bcd = info["release_number"]
    print(f"Model:            {PIDS[info['product_id']]}")
    print(f"USB bcdDevice:    {bcd >> 8 & 0xF}.{bcd >> 4 & 0xF}.{bcd & 0xF}")
    print(f"Firmware reply:   {text}")


if __name__ == "__main__":
    main()
