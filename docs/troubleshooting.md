# Troubleshooting Guide

This guide helps diagnose and resolve common issues with the Scroll Lock RGB Fix service.

---

## 1. Check Service Status

Check whether the service is loaded, enabled, and currently active:

```bash
systemctl status scrolllock-rgb.service --no-pager
```

Expected output should show `Active: active (running)`.

If the service is in a failed state, inspect the logs as shown below.

---

## 2. Inspect Real-Time Service Logs

View the systemd journal logs for the service:

```bash
# Follow logs in real time
journalctl -u scrolllock-rgb.service -f

# Or view the last 50 log entries
journalctl -u scrolllock-rgb.service -n 50 --no-pager
```

Look for lines indicating:
- `Monitoring keyboard: <Keyboard Name> (/dev/input/eventX)`
- `Target LED node: /sys/class/leds/.../brightness`
- `Scroll Lock pressed. Toggling RGB state to: 1`

---

## 3. Verify Hardware Compatibility (Manual LED Test)

Before troubleshooting software, verify that your keyboard firmware actually uses the physical Scroll Lock LED as its RGB controller trigger.

### Step 3.1: Locate the LED sysfs node
```bash
ls /sys/class/leds/ | grep -i scroll
```
You should see an entry like `input3::scrolllock` or similar.

### Step 3.2: Test lighting manually
Turn the LED (and keyboard RGB) ON:
```bash
echo 1 | sudo tee /sys/class/leds/*scrolllock*/brightness
```

Turn the LED (and keyboard RGB) OFF:
```bash
echo 0 | sudo tee /sys/class/leds/*scrolllock*/brightness
```

* **If the keyboard RGB turns on and off:** Your keyboard is 100% compatible with this fix.
* **If the LED changes state (or nothing happens) and the RGB does not turn on:** Your keyboard might use a proprietary USB HID protocol (such as OpenRGB-supported controllers) rather than the standard Scroll Lock LED trick.

---

## 4. Keyboard Not Detected

If the logs say:
```text
[scrolllock-rgb] keyboard not found. Retrying in 2.0s...
```

Check `/proc/bus/input/devices` to see all connected input devices:

```bash
cat /proc/bus/input/devices | grep -E 'Name|Handlers'
```

The daemon looks for a device that supports both `KEY_SCROLLLOCK` and `KEY_A` (to filter out secondary devices like "Consumer Control" or "System Control"). If your keyboard presents itself under an unusual descriptor, you can inspect device capabilities using:

```bash
python3 -c "
import evdev
for p in evdev.list_devices():
    d = evdev.InputDevice(p)
    print(d.path, d.name)
"
```

---

## 5. Interaction with Caps Lock / Num Lock

On GNOME (Wayland), whenever Caps Lock or Num Lock is pressed, the compositor broadcasts an LED update event (`EV_LED`) to the keyboard. On generic keyboards, this broadcast can unintentionally reset the Scroll Lock LED to 0 (turning off the RGB).

The daemon automatically intercepts `EV_LED` events and restores the desired Scroll Lock state after a 50ms settling delay. If you notice a brief flicker when pressing Caps Lock, this is the expected behavior of GNOME re-synchronizing the LEDs.

---

## 6. USB Reconnection (Hotplug)

The daemon v2.0 includes automatic hotplug recovery. If you unplug the keyboard or move it to a different USB port:
1. The daemon detects that the file descriptor closed.
2. It logs `Keyboard connection lost`.
3. It begins scanning every 2 seconds until the keyboard and LED are re-detected.
4. Once plugged back in, it resumes listening automatically without requiring `systemctl restart`.
