# Scroll Lock RGB Fix

[Português (Brasil)](../pt-BR/docs/registro-tecnico.md) · [Original PDF](RGB_ScrollLock_Ubuntu_EN.pdf) · [Home](../README.md) · [Index](README.md)

**Ubuntu 26.04 with GNOME (Wayland) — generic USB gaming keyboard**

This historical record describes how the author restored RGB lighting on his keyboard in Ubuntu 26.04. He retained the steps to understand or reapply the solution after a system update or keyboard replacement. The paths and code examples belong to the July 2026 prototype. For the repository version, see [installation](../README.md#installation) and [troubleshooting](troubleshooting.md).

This text preserves the prototype record and does not necessarily describe the current daemon. Historical examples are not installation instructions; use the current guide and do not execute commands with old device paths.

## The problem

On the generic semi-mechanical gaming keyboard from the kit, the firmware activates RGB lighting when the computer turns on the standard Scroll Lock LED, a feature found on low-cost keyboards. According to the record, this used to work on Windows and in the Linux text console (TTY), where the kernel directly controls the LED. In Ubuntu 26.04, GNOME used Wayland by default after Xorg support ended in GNOME 49. In that session, the physical indicator did not automatically follow the Scroll Lock state. Pressing the key had no effect.

## The solution

The author used a small Python program that remained in the background, reading the keyboard directly. Each time Scroll Lock was pressed, the program wrote to the system file controlling the LED to turn the lighting on or off. A systemd unit automatically started the program at each boot. The files created were the script `/usr/local/bin/scrolllock-rgb.py` and the unit `/etc/systemd/system/scrolllock-rgb.service`.

## 1. The Python script — scrolllock-rgb.py

The program that kept RGB working is reproduced below in parts, in the order of the original document.

### 1.1. Imports

```python
#!/usr/bin/env python3
import evdev
from evdev import ecodes
import glob
import time
```

The first line selects Python 3. The evdev library, installed with `sudo apt install python3-evdev`, allows reading keyboard and mouse events. The ecodes module provides standardized codes for each key, including Scroll Lock. The glob module searches files by name pattern to find the LED automatically. The time module allows brief pauses during execution.

### 1.2. Finding the Scroll Lock LED

```python
def find_led_path():
    matches = glob.glob("/sys/class/leds/*scrolllock*")
    if matches:
        return matches[0] + "/brightness"
    return None
```

Linux exposes the LED in `/sys/class/leds/`. The number in names such as `input2::scrolllock` or `input24::scrolllock` depends on the detection order of USB devices and can change after reboot. Hardcoding that number made the script stop working after a boot. The prototype began searching for a directory containing “scrolllock” at startup and used the first match.

### 1.3. Finding the keyboard

```python
def find_keyboard():
    for path in evdev.list_devices():
        dev = evdev.InputDevice(path)
        caps = dev.capabilities().get(ecodes.EV_KEY, [])
        if ecodes.KEY_SCROLLLOCK in caps and ecodes.KEY_A in caps:
            return dev
    return None
```

A computer can expose the keyboard, mouse and media buttons as separate input devices. The function iterated over connected devices and accepted one capable of sending both Scroll Lock and the A key. This distinguished the main keyboard from secondary “Consumer Control” and “System Control” interfaces that could appear separately on the same USB keyboard.

### 1.4. Preparing to listen for events

```python
LED_PATH = find_led_path()
device = find_keyboard()

if LED_PATH is None or device is None:
    raise SystemExit("Keyboard or LED not found yet")

state = 0
```

The two functions located the LED and keyboard. If either was still missing, such as during keyboard detection at boot, the program exited with the error message. Systemd attempted to start it again as described in section 2. The `state` variable stored the desired state, 1 for on or 0 for off.

### 1.5. Controlling the LED

```python
def set_led(value):
    with open(LED_PATH, "w") as f:
        f.write(str(value))
```

The function opened the LED file and wrote 0 or 1. The effect was the same as the manual write used in the initial test with `echo 1 | sudo tee /sys/class/leds/.../brightness`.

### 1.6. Main loop

```python
for event in device.read_loop():
    if event.type == ecodes.EV_KEY and event.code == ecodes.KEY_SCROLLLOCK and event.value == 1:
        state = 1 - state
        set_led(state)
    elif event.type == ecodes.EV_LED:
        time.sleep(0.05)
        set_led(state)
```

The loop waited continuously for events.

- When Scroll Lock was pressed, `event.value == 1` identified the press and excluded release. The program toggled from 0 to 1 or 1 to 0 and sent the new state to the LED.
- When GNOME changed an indicator, such as Caps Lock or Num Lock, the keyboard received a packet containing the state of all three LEDs together. This could turn Scroll Lock off. On receiving EV_LED, the script waited 0.05 seconds for the GNOME write and reapplied the stored state.

## 2. The systemd unit — scrolllock-rgb.service

Systemd manages automatic program startup in Ubuntu, including at boot. The author created a unit to run the script at each startup without opening a terminal.

```ini
[Unit]
Description=Syncs the Scroll Lock LED with the keyboard's RGB
After=multi-user.target

[Service]
ExecStart=/usr/bin/python3 /usr/local/bin/scrolllock-rgb.py
Restart=always
RestartSec=2
User=root

[Install]
WantedBy=multi-user.target
```

| Section or key | Explanation |
|---|---|
| `[Unit]` | General unit information. |
| `Description=...` | Name shown when checking service status. |
| `After=multi-user.target` | Orders startup after the multi-user target, intended to avoid an early attempt. |
| `[Service]` | Configures program execution. |
| `ExecStart=...` | Specifies the exact command that invokes Python 3 with the script. |
| `Restart=always` | Systemd attempts to restart the program after exit or error. |
| `RestartSec=2` | Waits two seconds before the next attempt. When the keyboard had not yet been recognized at boot, the script could fail and retry until it worked. |
| `User=root` | Runs as administrator with permission to write to the LED file. |
| `[Install]` | Defines how the service integrates with startup. |
| `WantedBy=multi-user.target` | When enabled, associates service startup with the multi-user target at each boot. |

## 3. Commands used in the terminal

The following sequence reproduces the author's investigation and changes on the original machine. The name `input24::scrolllock` corresponded to his keyboard at that time. The two `tee` examples with `...` abbreviate file contents in the PDF.

| Order | Recorded command | Purpose and observation |
|---|---|---|
| 1 | `echo $XDG_SESSION_TYPE` | Showed whether the graphical session used Wayland or Xorg (X11). The result identified Wayland, relevant to the LED synchronization problem. |
| 2 | `lsusb` | Listed connected USB devices, including the keyboard, with manufacturer information. |
| 3 | `ls /usr/share/xsessions/` | Looked for installed Xorg sessions. The author encountered a missing-directory error and recorded the removal of Xorg from GNOME in Ubuntu 25.10/26.04. |
| 4 | `sudo apt update` | Updated the package index before installation attempts. |
| 5 | `sudo apt install xserver-xorg gnome-session` | Attempted to install Xorg and the GNOME session. The author abandoned this approach because GNOME 49 no longer offered an Xorg session. |
| 6 | `dpkg -L gnome-session \| grep xsessions` | Filtered package files related to graphical sessions. Confirmed that the package did not include an Xorg session, only Wayland. |
| 7 | `ls /sys/class/leds/ \| grep -i scroll` | Searched LED entries for the word “scroll” and located the file controlling the indicator and RGB on that keyboard. |
| 8 | `echo 1 \| sudo tee /sys/class/leds/input24::scrolllock/brightness` | Wrote 1 to the identified node. The RGB lit up, confirming direct-write activation on that machine independently of GNOME. |
| 9 | `cat /proc/bus/input/devices \| grep -A 5 -i keyboard` | Examined names, identifiers and event files of recognized devices to locate the main keyboard. |
| 10 | `sudo apt install python3-evdev` | Installed the library used by the script to read events directly from the system. |
| 11 | `sudo mkdir -p /usr/local/bin && sudo tee /usr/local/bin/scrolllock-rgb.py > /dev/null << 'EOF' ... EOF` | Created the directory if necessary and wrote the Python program using the content between EOF markers, without an interactive editor. |
| 12 | `sudo chmod +x /usr/local/bin/scrolllock-rgb.py` | Granted execute permission to invoke the file as a program. |
| 13 | `sudo python3 /usr/local/bin/scrolllock-rgb.py` | Tested the script in the terminal before automating it. It waited for events until stopped with Ctrl+C. |
| 14 | `sudo tee /etc/systemd/system/scrolllock-rgb.service > /dev/null << 'EOF' ... EOF` | Wrote the systemd unit that configured execution, including subsequent boots. |
| 15 | `sudo systemctl daemon-reload` | Asked systemd to reload new or changed definitions. |
| 16 | `sudo systemctl enable scrolllock-rgb.service` | Enabled the service to start automatically at boot. |
| 17 | `sudo systemctl start scrolllock-rgb.service` | Started the service immediately without rebooting the machine. |
| 18 | `sudo systemctl restart scrolllock-rgb.service` | Restarted the service to apply a script change. |
| 19 | `systemctl status scrolllock-rgb.service --no-pager` | Displayed state, runtime and recent log entries without opening a pager. |
| 20 | `systemctl is-enabled scrolllock-rgb.service` | Checked automatic startup. The expected response was “enabled”. |
| 21 | `journalctl -u scrolllock-rgb.service --no-pager` | Consulted the complete message history for this service to diagnose problems. |
| 22 | `sudo reboot` | Rebooted the computer to verify automatic startup without manual intervention in the original environment. |

The original document advises keeping the record and, if Scroll Lock fails again, starting with the status and log commands from section 3, `systemctl status` and `journalctl`.
