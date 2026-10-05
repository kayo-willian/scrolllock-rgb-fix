#!/usr/bin/env python3
"""
tests/test_daemon.py

Unit tests for scrolllock-rgb.py functions and logic using unittest and mocks.
"""

import os
import sys
import unittest
from unittest.mock import MagicMock, patch, mock_open

# Add project root to sys.path
PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
sys.path.insert(0, PROJECT_ROOT)

import evdev
from evdev import ecodes
import importlib
scrolllock_rgb = importlib.import_module("scrolllock-rgb")
sys.modules["scrolllock_rgb"] = scrolllock_rgb


class TestScrollLockRGB(unittest.TestCase):

    @patch("glob.glob")
    def test_find_led_path_found_brightness(self, mock_glob):
        mock_glob.return_value = ["/sys/class/leds/input3::scrolllock/brightness"]
        path = scrolllock_rgb.find_led_path()
        self.assertEqual(path, "/sys/class/leds/input3::scrolllock/brightness")

    @patch("glob.glob")
    def test_find_led_path_not_found(self, mock_glob):
        mock_glob.return_value = []
        path = scrolllock_rgb.find_led_path()
        self.assertIsNone(path)

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

    @patch("evdev.list_devices")
    @patch("scrolllock_rgb.InputDevice")
    def test_find_keyboard_filters_correctly(self, mock_input_device, mock_list_devices):
        mock_list_devices.return_value = ["/dev/input/event0", "/dev/input/event1", "/dev/input/event2"]

        # Device 0: Power Button (neither key)
        dev0 = MagicMock()
        dev0.capabilities.return_value = {ecodes.EV_KEY: [ecodes.KEY_POWER]}

        # Device 1: Consumer Control (has ScrollLock, but not KEY_A)
        dev1 = MagicMock()
        dev1.capabilities.return_value = {ecodes.EV_KEY: [ecodes.KEY_SCROLLLOCK]}

        # Device 2: Real Keyboard (has both KEY_SCROLLLOCK and KEY_A)
        dev2 = MagicMock()
        dev2.capabilities.return_value = {ecodes.EV_KEY: [ecodes.KEY_SCROLLLOCK, ecodes.KEY_A]}

        def get_device(path):
            if path == "/dev/input/event0": return dev0
            if path == "/dev/input/event1": return dev1
            return dev2

        mock_input_device.side_effect = get_device

        detected = scrolllock_rgb.find_keyboard()
        self.assertIsNotNone(detected)
        self.assertEqual(detected, dev2)

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


if __name__ == "__main__":
    unittest.main()
