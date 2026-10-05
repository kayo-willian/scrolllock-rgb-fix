# Scroll Lock Keyboard RGB Fix

[![Linux](https://img.shields.io/badge/Linux-Supported-brightgreen?logo=linux&logoColor=white)](https://kernel.org)
[![Python](https://img.shields.io/badge/Python-3.8%2B-blue?logo=python&logoColor=white)](https://python.org)
[![systemd](https://img.shields.io/badge/systemd-integrated-orange?logo=linux)](https://systemd.io)
[![Wayland](https://img.shields.io/badge/Wayland-GNOME%2049%2B-informational)](https://wayland.freedesktop.org)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)

*Read this in other languages:* [Português (Brasil)](README.pt-BR.md)

---

A lightweight, automated background service that fixes the RGB lighting behavior on generic gaming keyboards using the physical **Scroll Lock LED** as a firmware trigger on Linux systems running **GNOME on Wayland**.

Specifically designed for modern Linux environments (such as Ubuntu 26.04+ where GNOME has removed Xorg sessions), where the display compositor does not synchronize the Scroll Lock LED state with the physical hardware.

---

## 💡 The Problem

Many affordable gaming keyboards (often marketed as "semi-mechanical RGB") do not provide Linux drivers or proprietary lighting software. Instead, their internal firmware activates the RGB backlight whenever the operating system turns ON the standard **Scroll Lock LED**.

While this works out of the box in Windows and in Linux virtual consoles (TTY):

* Under **GNOME on Wayland**, the compositor intercepts key events but does not propagate Scroll Lock LED state updates to the physical USB keyboard.
* Since recent GNOME versions (GNOME 49+ / Ubuntu 25.10+) dropped legacy Xorg sessions entirely, switching display servers is no longer possible.
* Pressing Scroll Lock does nothing, leaving the keyboard unlit.

---

## ⚡ The Solution

This project provides a robust, native background daemon and `systemd` service that communicates directly with the Linux kernel input subsystem:

```text
[ Physical Keyboard ]
         │
         │  Press Scroll Lock key
         ▼
[ /dev/input/eventX ]
         │
         │  Direct kernel event loop (python3-evdev)
         ▼
[ scrolllock-rgb.py ] ──► Toggles internal state (0 <-> 1)
         │
         │  Direct sysfs write
         ▼
[ /sys/class/leds/*scrolllock*/brightness ]
         │
         │  Hardware trigger
         ▼
[ Keyboard Firmware ] ──► RGB Backlight ON / OFF ✨
```

### Key Features (v2.0)
- **Zero Configuration & Dynamic Discovery:** Automatically finds the correct keyboard and Scroll Lock LED path in `/sys/class/leds/` at runtime, even if device indexes change across reboots.
- **Device Filtering:** Safely distinguishes true keyboards from auxiliary USB descriptors (such as "Consumer Control" or "System Control").
- **Hotplug Resilient:** Detects USB disconnections and reconnections automatically in-process without crashing or requiring a service restart.
- **Caps Lock / Num Lock Conflict Recovery:** GNOME updates all keyboard LEDs whenever Caps Lock or Num Lock is pressed, which inadvertently turns off Scroll Lock. The daemon intercepts compositor LED updates and immediately restores the desired RGB state.
- **Multi-Distribution Automated Installer:** Single-command installation for Ubuntu, Debian, Fedora, Arch Linux, and openSUSE.

---

## 📦 Compatibility & Requirements

* **Operating System:** Linux with `systemd`
* **Desktop Environment:** GNOME (Wayland or X11), KDE Plasma, Hyprland, Sway, etc.
* **Dependencies:** Python 3 and `python3-evdev` (automatically installed by `install.sh`)
* **Hardware:** Any keyboard whose RGB controller relies on the physical Scroll Lock LED state

| Distribution | Package Manager | Status |
| :--- | :--- | :--- |
| **Ubuntu / Debian / Linux Mint** | `apt` | ✅ Fully Supported |
| **Fedora / RHEL** | `dnf` | ✅ Fully Supported |
| **Arch Linux / Manjaro** | `pacman` | ✅ Fully Supported |
| **openSUSE (Tumbleweed / Leap)** | `zypper` | ✅ Fully Supported |
| **Alpine Linux** | `apk` | ✅ Fully Supported |

---

## 🚀 Quick Start (Automated Installation)

Clone the repository and run the automated installer:

```bash
# 1. Clone the repository
git clone https://github.com/kayo-willian/scrolllock-rgb-fix.git
cd scrolllock-rgb-fix

# 2. Run the automated installer (requires sudo)
sudo ./install.sh
```

The installer will:
1. Detect your distribution's package manager and install `python3-evdev` if missing.
2. Install the daemon to `/usr/local/bin/scrolllock-rgb.py`.
3. Configure and activate the `systemd` background service (`scrolllock-rgb.service`).
4. Start the service immediately and enable it at boot.

Press your keyboard's **Scroll Lock** key to toggle your RGB lighting!

---

## 🔍 Verification & Logs

Check if the service is active and running:

```bash
systemctl status scrolllock-rgb.service --no-pager
```

View real-time event logs (key presses, LED states, reconnections):

```bash
journalctl -u scrolllock-rgb.service -f
```

---

## 🛠️ Uninstallation

To completely remove the service, configuration, and scripts from your system:

```bash
sudo ./uninstall.sh
```

---

## 🧪 Testing & Development

Run the automated test suite locally:

```bash
# Run syntax and file checks
./tests/test_syntax.sh

# Run unit tests with device mocks
python3 ./tests/test_daemon.py
```

For hardware troubleshooting steps, see [docs/troubleshooting.md](docs/troubleshooting.md).

For deep architectural explanations and the terminal command history used to develop this fix, see the technical guide [docs/RGB_ScrollLock_Ubuntu_EN.pdf](docs/RGB_ScrollLock_Ubuntu_EN.pdf).

---

## 📄 License

This project is open-source software licensed under the [MIT License](LICENSE).
