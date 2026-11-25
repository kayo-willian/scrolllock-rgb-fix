# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

### Fixed
- Pair the keyboard with its own Scroll Lock LED. Skip missing or ambiguous matches.

### Added
- Code of conduct, security reporting policy, bilingual issue templates and an English pull request template.

### Changed
- Update contributor onboarding, English and Portuguese READMEs and troubleshooting instructions.
- Clarify the actual systemd requirement, independent device/LED selection, root execution, installation and removal behavior, and limits of hardware validation. No daemon, installer or service behavior changed.

The existing version headings below are historical entries; this documentation update does not create a release or change a version.

---

## [2.0.0] - 2026-10-04

### Added
- **Multi-Distribution Automated Installer (`install.sh`)**:
  - Automatically identifies system package manager (`apt`, `dnf`, `pacman`, `zypper`, `apk`).
  - Automatically installs `python3-evdev` if missing.
  - Robust systemd validation supporting Ubuntu, Debian, Fedora, Arch, and openSUSE.
  - Deploys binaries to standard `/usr/local/bin` and systemd units to `/etc/systemd/system`.
- **Automated Uninstaller (`uninstall.sh`)**:
  - Stops, disables, and completely purges the service and daemon cleanly.
- **In-Process USB Hotplug & Reconnection**:
  - The Python daemon now handles device disconnections (`OSError`, unplugging, port switching) gracefully in-process without crashing or causing restart loops in systemd.
- **Enhanced Signal Handling**:
  - Graceful termination on `SIGTERM` and `SIGINT` with resource cleanup.
- **Automated Test Suite (`tests/`)**:
  - Added `tests/test_syntax.sh` for shell and python syntax checking.
  - Added `tests/test_daemon.py` with mock-based unit tests for discovery, LED control, and input event dispatching.
- **Documentation**:
  - Added dedicated `docs/troubleshooting.md` guide.
  - Added `CONTRIBUTING.md` and `CHANGELOG.md`.
  - Added bilingual README (English and Brazilian Portuguese).
  - Preserved historical technical documentation `docs/RGB_ScrollLock_Ubuntu_EN.pdf`.

### Changed
- Standardized logging to timestamped format captured cleanly by `journald`.
- Removed deprecated `systemd-udev-settle.service` dependency in favor of native asynchronous device detection.

---

## [1.0.0] - 2026-07-17

### Added
- Initial working prototype for Ubuntu 26.04 LTS (GNOME / Wayland).
- Dynamic device detection (`/sys/class/leds/*scrolllock*/brightness` and `/dev/input/event*`).
- Keyboard identification filtering against `KEY_SCROLLLOCK` and `KEY_A`.
- GNOME Wayland Caps Lock / Num Lock conflict mitigation using `EV_LED` event interception.
- Basic `systemd` service unit.
- Comprehensive technical development journal in PDF format.
