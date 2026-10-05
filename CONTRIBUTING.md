# Contributing to Scroll Lock Keyboard RGB Fix

Thank you for your interest in contributing to this project!

---

## Code of Conduct & Guidelines

- **Focus:** Keep contributions focused on solving RGB/LED synchronization issues for Linux generic keyboards, especially on modern Wayland display servers.
- **Portability:** Keep scripts compatible across mainstream systemd-based Linux distributions (Ubuntu, Debian, Fedora, Arch Linux, openSUSE).
- **No Hardcoded Paths:** Never hardcode numbered paths such as `/dev/input/event3` or `/sys/class/leds/input3::scrolllock`. Always use dynamic detection.
- **Root Safety:** Never execute unnecessary destructive operations in install/uninstall scripts.

---

## Development & Testing Workflow

1. Fork the repository and create your feature branch:
   ```bash
   git checkout -b feature/my-new-feature
   ```

2. Make your changes.

3. Run the automated test suite before opening a pull request:
   ```bash
   # Static checks (syntax, required files)
   ./tests/test_syntax.sh

   # Unit tests with mocks
   python3 ./tests/test_daemon.py
   ```

4. If hardware is available, test with a physical keyboard:
   - Toggle Scroll Lock;
   - Press Caps Lock and Num Lock repeatedly to test conflict restoration;
   - Unplug and re-plug the keyboard to test hotplug recovery;
   - Verify `systemctl status scrolllock-rgb.service`.

5. Submit a Pull Request clearly explaining the changes, problem solved, and tests performed.
