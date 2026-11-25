#!/usr/bin/env python3
"""
tests/test_scrolllock_rgb.py

Unit tests for scrolllock-rgb.py functions and logic using unittest and mocks.
"""

import os
import sys
import tempfile
from pathlib import Path
import unittest
from unittest.mock import MagicMock, Mock, patch, mock_open

# Add project root to sys.path
PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
sys.path.insert(0, PROJECT_ROOT)

import evdev
from evdev import ecodes
import importlib
scrolllock_rgb = importlib.import_module("scrolllock-rgb")
sys.modules["scrolllock_rgb"] = scrolllock_rgb


class TestScrollLockRGB(unittest.TestCase):

    @patch("builtins.open", new_callable=mock_open)
    def test_set_led_success(self, mock_file):
        success = scrolllock_rgb.set_led("/sys/class/leds/input3::scrolllock/brightness", 1)
        self.assertTrue(success)
        mock_file.assert_called_once_with("/sys/class/leds/input3::scrolllock/brightness", "w")
        mock_file().write.assert_called_once_with("1\n")

    @patch("builtins.open", side_effect=OSError("Permission denied"))
    def test_set_led_failure(self, mock_file):
        success = scrolllock_rgb.set_led("/sys/class/leds/input3::scrolllock/brightness", 0)
        self.assertFalse(success)

    @patch("scrolllock_rgb.set_led")
    def test_run_keyboard_listener_scrolllock_toggle(self, mock_set_led):
        mock_dev = MagicMock()
        mock_dev.name = "Test Keyboard"
        mock_dev.path = "/dev/input/event3"

        # Simulate events:
        # 1. Scroll Lock pressed (value 1) -> toggle state from 0 to 1
        # 2. Caps Lock changed LED (EV_LED) -> restore state 1
        # 3. Scroll Lock pressed again (value 1) -> toggle state from 1 to 0
        event1 = MagicMock(type=ecodes.EV_KEY, code=ecodes.KEY_SCROLLLOCK, value=1)
        event2 = MagicMock(type=ecodes.EV_LED, code=0, value=0)
        event3 = MagicMock(type=ecodes.EV_KEY, code=ecodes.KEY_SCROLLLOCK, value=1)

        mock_dev.read_loop.return_value = [event1, event2, event3]

        scrolllock_rgb.run_keyboard_listener(mock_dev, "/fake/led/path")

        # Initial set_led(0), then set_led(1) on event1, set_led(1) on event2, set_led(0) on event3
        calls = [c[0] for c in mock_set_led.call_args_list]
        self.assertEqual(calls, [
            ("/fake/led/path", 0),
            ("/fake/led/path", 1),
            ("/fake/led/path", 1),
            ("/fake/led/path", 0),
        ])


class PairingTests(unittest.TestCase):
    def setUp(self):
        tree = tempfile.TemporaryDirectory()
        self.addCleanup(tree.cleanup)
        self.root = Path(tree.name)
        self.events = {}
        self.leds = []

    def event(self, number, owner):
        name = f"event{number}"
        parent = self.root / "devices" / owner
        target = parent / name
        target.mkdir(parents=True)
        (target / "device").symlink_to(parent)
        alias = self.root / "class/input" / name
        alias.parent.mkdir(parents=True, exist_ok=True)
        alias.symlink_to(target)
        device = Mock(path=f"/dev/input/{name}")
        device.capabilities.return_value = {scrolllock_rgb.ecodes.EV_KEY: [scrolllock_rgb.ecodes.KEY_A, scrolllock_rgb.ecodes.KEY_SCROLLLOCK]}
        self.events[device.path] = device
        return device

    def led(self, name, owner):
        parent = self.root / "devices" / owner
        target = parent / name
        target.mkdir(parents=True)
        (target / "device").symlink_to(parent)
        (target / "brightness").touch()
        alias = self.root / "class/leds" / name
        alias.parent.mkdir(parents=True, exist_ok=True)
        alias.symlink_to(target)
        path = str(alias / "brightness")
        self.leds.append(path)
        return path

    def cycle(self):
        selected = []
        real = os.path.realpath

        def resolve(path):
            return real(str(path).replace("/sys/class/input/", str(self.root / "class/input") + "/"))

        def listen(device, led):
            selected.append((device, led))
            scrolllock_rgb._shutdown_requested = True

        def stop(_):
            scrolllock_rgb._shutdown_requested = True
        with patch.object(scrolllock_rgb, "_shutdown_requested", False), \
             patch.object(scrolllock_rgb.evdev, "list_devices", return_value=list(self.events)), \
             patch.object(scrolllock_rgb, "InputDevice", side_effect=self.events.__getitem__), \
             patch.object(scrolllock_rgb.glob, "glob", return_value=self.leds), \
             patch.object(os.path, "realpath", side_effect=resolve), \
             patch.object(scrolllock_rgb, "run_keyboard_listener", side_effect=listen), \
             patch.object(scrolllock_rgb.time, "sleep", side_effect=stop):
            scrolllock_rgb.main()
        return selected

    def test_pair_is_independent_of_led_order(self):
        a = self.event(8, "usb/input10")
        self.event(2, "usb/input11")
        self.led("input11::scrolllock", "usb/input11")
        own = self.led("input10::scrolllock", "usb/input10")
        self.assertEqual(self.cycle(), [(a, own)])
        self.leds.reverse()
        self.assertEqual(self.cycle(), [(a, own)])

    def test_first_keyboard_without_led_does_not_steal_second_led(self):
        unpaired = self.event(3, "usb/input8")
        paired = self.event(5, "usb/input9")
        own = self.led("input9::scrolllock", "usb/input9")
        self.assertEqual(self.cycle(), [(paired, own)])
        unpaired.capabilities.assert_not_called()

    def test_ambiguous_leds_are_skipped(self):
        self.event(6, "usb/input7")
        self.led("left::scrolllock", "usb/input7")
        self.led("right::scrolllock", "usb/input7")
        self.assertEqual(self.cycle(), [])

    def test_missing_led_is_skipped(self):
        self.event(3, "usb/input8")
        self.assertEqual(self.cycle(), [])

    def test_auxiliary_interface_is_skipped(self):
        aux = self.event(3, "usb/input8")
        aux.capabilities.return_value = {scrolllock_rgb.ecodes.EV_KEY: [scrolllock_rgb.ecodes.KEY_SCROLLLOCK]}
        self.led("input8::scrolllock", "usb/input8")
        self.assertEqual(self.cycle(), [])
        aux.close.assert_called_once_with()

    def test_hotplug_re_resolves_reused_event_number(self):
        self.event(2, "usb/input1")
        before = self.led("input1::scrolllock", "usb/input1")
        self.assertEqual(self.cycle()[0][1], before)
        (self.root / "class/input/event2").unlink()
        device = self.event(2, "usb/input2")
        after = self.led("input2::scrolllock", "usb/input2")
        self.assertEqual(self.cycle(), [(device, after)])


if __name__ == "__main__":
    unittest.main()
