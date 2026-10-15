"""Read Keychron Q1 HE battery from the custom firmware (command 0xA4).

  python q1he_battery.py           # USB cable: ask the keyboard once
  python q1he_battery.py --listen  # 2.4 GHz dongle: print pushed reports

Report bytes: [0]=0xA4 [1]=percent [2..3]=millivolts (LE)
              [4]=charging (0 battery, 1 charging, 2 full)
              [5]=transport (1 USB, 2 BT, 4 2.4 GHz) [6]=model id (2 = Q1 HE)

Requirements: pip install hidapi   (close Keychron Launcher first)
"""
import sys
import hid

VID = 0x3434
Q1HE_PIDS = {0x0B10, 0x0B11, 0x0B12}
RAW_USAGE_PAGE, RAW_USAGE_ID = 0xFF60, 0x61
REPORT_SIZE = 32
KC_GET_BATTERY = 0xA4
CHARGING = {0: "on battery", 1: "charging", 2: "full"}
TRANSPORT = {1: "USB", 2: "Bluetooth", 4: "2.4 GHz"}


def raw_interfaces(pids=None):
    return [d for d in hid.enumerate(VID, 0)
            if d["usage_page"] == RAW_USAGE_PAGE and d["usage"] == RAW_USAGE_ID
            and (pids is None or d["product_id"] in pids)]


def describe(r):
    mv = r[2] | (r[3] << 8)
    model = r[6] if len(r) > 6 else 0
    return (f"{r[1]}%  {mv} mV  {CHARGING.get(r[4], r[4])}  "
            f"via {TRANSPORT.get(r[5], r[5])}  model={model}")


def poll_usb():
    devs = raw_interfaces(Q1HE_PIDS)
    if not devs:
        sys.exit("Q1 HE not found on USB (cable connected, switch on Cable?)")
    dev = hid.device()
    dev.open_path(devs[0]["path"])
    try:
        dev.write([0x00, KC_GET_BATTERY] + [0x00] * (REPORT_SIZE - 1))
        for _ in range(5):  # skip any unrelated reports
            r = dev.read(REPORT_SIZE, 1000)
            if r and r[0] == KC_GET_BATTERY:
                print(describe(r))
                return
    finally:
        dev.close()
    sys.exit("No battery reply - is the custom firmware flashed?")


def listen():
    devs = raw_interfaces()
    if not devs:
        sys.exit("No Keychron raw-HID interface found (dongle plugged in?)")
    print("Listening on:", ", ".join(
        f"{d['product_string']} (PID {d['product_id']:04X})" for d in devs))
    opened = []
    for d in devs:
        h = hid.device()
        h.open_path(d["path"])
        h.set_nonblocking(False)
        opened.append(h)
    try:
        while True:
            for h in opened:
                r = h.read(REPORT_SIZE, 500)
                if r and r[0] == KC_GET_BATTERY:
                    print(describe(r), flush=True)
    except KeyboardInterrupt:
        pass
    finally:
        for h in opened:
            h.close()


if __name__ == "__main__":
    listen() if "--listen" in sys.argv else poll_usb()
