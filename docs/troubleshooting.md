# Troubleshooting Guide

[Português (Brasil)](../pt-BR/docs/troubleshooting.md) · [Home](../README.md)

Use a noncritical keyboard with another input method available. The shipped service runs as root. Do not capture or share arbitrary keyboard events.

## 1. Check status and logs

```sh
systemctl status scrolllock-rgb.service --no-pager
journalctl -u scrolllock-rgb.service -n 50 --no-pager
```

An active service may be waiting for a device. Look for the monitored keyboard name/path, target LED node, Scroll Lock toggle messages and errors. Check whether the reported keyboard and LED correspond to the intended device.

## 2. Verify the firmware response

Stop the service before manually writing LED state:

```sh
sudo systemctl stop scrolllock-rgb.service
ls -l /sys/class/leds/*scrolllock*/brightness
```

Identify **one** brightness node that belongs to your noncritical test keyboard. Do not use a wildcard with tee: that could write to several devices. The following example uses a fictional path; replace it only after verifying the correct device through its sysfs link. If you cannot identify it confidently, stop here.

```sh
LED=/sys/class/leds/input3::scrolllock/brightness
cat "$LED"
```

Record the original value. If the node is correct and writable, test it:

```sh
printf '1\n' | sudo tee "$LED"
printf '0\n' | sudo tee "$LED"
```

Restore the recorded value if necessary. An RGB change demonstrates the firmware trigger on that device, not full daemon compatibility. No change may indicate a different firmware protocol or a wrong node. To resume normal operation, run `sudo systemctl start scrolllock-rgb.service` if appropriate.

## 3. Keyboard not detected or wrong keyboard selected

```sh
grep -E 'Name|Handlers' /proc/bus/input/devices
ls -l /sys/class/leds/*scrolllock*
```

If a keyboard is skipped, compare the device links under its event and LED entries in sysfs. They must resolve to the same input device, which must have exactly one Scroll Lock LED. Sharing a USB port or composite HID parent is not sufficient. Do not hardcode event numbers or write to an unverified LED to work around this. Report the device arrangement, sanitized names and paths, and observed behavior.

## 4. Caps Lock / Num Lock interaction

The daemon reasserts its desired Scroll Lock state after an EV_LED event with a 50 ms settling delay. Some hardware/compositor combinations may behave differently. A brief flicker can occur. Report persistent resets or unexpected changes with the relevant environment and reproduction steps.

## 5. USB reconnection and shutdown

When the read loop reports a connection error, the daemon closes the selected input device and retries discovery at two-second intervals. A missing keyboard or LED also causes retrying. Each new listener initializes the state to off. The existing retry and shutdown logic is not a guarantee of prompt recovery or termination in all cases.

Use `sudo systemctl stop scrolllock-rgb.service` to stop, or `sudo systemctl disable --now scrolllock-rgb.service` to disable startup. Check actual unit status. If stopping fails, investigate systemd and the daemon logs before continuing with removal.

## 6. Installation or removal problems

A working systemd manager is required; package-manager detection is not evidence of full distribution support. Check Python and evdev availability, existing destination files, package errors and systemd diagnostics. The installer may replace its fixed daemon and unit paths; the uninstaller ignores stop/disable errors. Do not remove unrelated files or force package changes to bypass a failure.

See [README](../README.md) for normal installation, update and removal steps. Report ordinary issues using the repository templates; use [SECURITY.md](../SECURITY.md) for sensitive findings. Redact private logs, typed text, raw event data and identifying details.
