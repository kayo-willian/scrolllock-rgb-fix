#!/usr/bin/env python3
"""
scrolllock-rgb.py

Synchronizes the Scroll Lock LED with the RGB lighting of generic gaming
keyboards that use this LED as a firmware trigger on GNOME/Wayland
systems, where the compositor does not propagate the LED state to the
physical hardware.

Features:
- Dynamic discovery of keyboard input device and Scroll Lock LED in sysfs.
- Resilient self-healing loop: handles USB keyboard disconnection and reconnection (hotplug).
- Correct restoration of Scroll Lock LED state when GNOME changes CapsLock/NumLock.
- Graceful shutdown on SIGTERM / SIGINT signals.
"""

import glob
import logging
import os
import signal
import sys
import time
from typing import Optional

try:
    import evdev
    from evdev import InputDevice, ecodes
except ImportError:
    sys.stderr.write(
        "[scrolllock-rgb] ERROR: python3-evdev is not installed.\n"
        "[scrolllock-rgb] Please install it via your package manager (e.g. 'sudo apt install python3-evdev').\n"
    )
    sys.exit(1)

logging.basicConfig(
    level=logging.INFO,
    format="[scrolllock-rgb] %(asctime)s [%(levelname)s] %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
)
logger = logging.getLogger("scrolllock-rgb")

RETRY_INTERVAL = 2.0
RESTORE_DELAY = 0.05
_shutdown_requested = False


def sig_handler(signum, frame):
    global _shutdown_requested
    logger.info(f"Signal {signum} received, shutting down gracefully...")
    _shutdown_requested = True


signal.signal(signal.SIGINT, sig_handler)
signal.signal(signal.SIGTERM, sig_handler)


def find_led_path() -> Optional[str]:
    """Locate the Scroll Lock LED brightness file under /sys/class/leds/."""
    matches = glob.glob("/sys/class/leds/*scrolllock*/brightness")
    if matches:
        return matches[0]
    dirs = glob.glob("/sys/class/leds/*scrolllock*")
    for d in dirs:
        b_path = os.path.join(d, "brightness")
        if os.path.exists(b_path):
            return b_path
    return None


def find_keyboard() -> Optional[InputDevice]:
    """Find the actual keyboard among all input devices.

    The device must support both the Scroll Lock key and the A key in
    order to filter out auxiliary devices such as 'Consumer Control'
    or 'System Control'.
    """
    try:
        device_paths = evdev.list_devices()
    except Exception as e:
        logger.warning(f"Error listing input devices: {e}")
        return None

    for path in device_paths:
        try:
            dev = InputDevice(path)
            caps = dev.capabilities().get(ecodes.EV_KEY, [])
            if ecodes.KEY_SCROLLLOCK in caps and ecodes.KEY_A in caps:
                return dev
        except (PermissionError, OSError):
            continue
    return None


def set_led(led_path: str, value: int) -> bool:
    """Write brightness value (0 or 1) to the LED sysfs node."""
    try:
        with open(led_path, "w") as f:
            f.write(f"{value}\n")
        return True
    except OSError as e:
        logger.error(f"Failed to write to LED at {led_path}: {e}")
        return False


def run_keyboard_listener(device: InputDevice, led_path: str) -> None:
    """Listen for events on the keyboard and synchronize the LED."""
    global _shutdown_requested
    state = 0
    logger.info(f"Monitoring keyboard: {device.name} ({device.path})")
    logger.info(f"Target LED node: {led_path}")

    # Set initial state (0 = off)
    set_led(led_path, state)

    try:
        for event in device.read_loop():
            if _shutdown_requested:
                break

            if (
                event.type == ecodes.EV_KEY
                and event.code == ecodes.KEY_SCROLLLOCK
                and event.value == 1  # Key press (not release or repeat)
            ):
                state = 1 - state
                logger.info(f"Scroll Lock pressed. Toggling RGB state to: {state}")
                set_led(led_path, state)

            elif event.type == ecodes.EV_LED:
                # GNOME or compositor updated Caps/Num Lock.
                # Wait briefly for compositor to finish, then re-assert Scroll Lock state.
                time.sleep(RESTORE_DELAY)
                set_led(led_path, state)

    except (OSError, IOError) as e:
        logger.warning(f"Keyboard connection lost ({device.path}): {e}")
    finally:
        try:
            device.close()
        except Exception:
            pass


def main():
    global _shutdown_requested
    if os.geteuid() != 0:
        logger.warning("Running without root privileges. Writing to /sys/class/leds/ requires root.")

    logger.info("Starting Scroll Lock RGB Fix service v2.0...")

    while not _shutdown_requested:
        led_path = find_led_path()
        device = find_keyboard()

        if led_path and device:
            run_keyboard_listener(device, led_path)
            if _shutdown_requested:
                break
            logger.info(f"Re-detecting devices in {RETRY_INTERVAL}s...")
        else:
            missing = []
            if not device:
                missing.append("keyboard")
            if not led_path:
                missing.append("Scroll Lock LED")
            logger.info(f"{' and '.join(missing)} not found. Retrying in {RETRY_INTERVAL}s...")

        time.sleep(RETRY_INTERVAL)

    logger.info("Scroll Lock RGB Fix service terminated.")


if __name__ == "__main__":
    main()
