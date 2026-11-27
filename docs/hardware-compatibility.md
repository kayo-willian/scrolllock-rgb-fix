# Hardware compatibility

[Documentation index](README.md) · [Home](../README.md) · [Português (Brasil)](../pt-BR/docs/compatibilidade-de-hardware.md)

This is an evidence-based compatibility reference, not a list of certified devices or supported operating systems.

## Hardware and environment evidence

| Item | Recorded status |
| --- | --- |
| Generic wired USB gaming keyboard | Original development device; exact model not recorded here |
| Ubuntu 26.04 / GNOME / Wayland | Original historical prototype environment |
| Scroll Lock firmware trigger | Direct LED writes activated the RGB backlight on the original device |
| Other RGB keyboards | Unverified; may use a different lighting protocol |
| Current daemon on multiple physical devices | Broader validation still pending |
| Other desktop environments and distributions | Not independently verified here |

See the [historical record](technical-record.md) and the [original PDF](RGB_ScrollLock_Ubuntu_EN.pdf) for the prototype investigation. The [original photographs](images/) document physical appearance, not current revision test results.

## Installation branches

The installer recognizes the following package managers when Python cannot import evdev. The current service requires a functioning systemd manager regardless of package manager.

| Package manager | Example family | Package |
| --- | --- | --- |
| apt | Debian / Ubuntu / Linux Mint | python3-evdev |
| dnf | Fedora / RHEL | python3-evdev |
| pacman | Arch / Manjaro | python-evdev |
| zypper | openSUSE | python3-evdev |
| apk | apk-based systems | py3-evdev |

Package availability and runtime behavior vary. The apk branch does not establish Alpine/OpenRC compatibility. The installer checks for systemd's runtime directory or the systemctl command, but that initial check alone does not prove the manager works.

## Controlled hardware validation

Before testing, use a noncritical device, retain another input method and review the [troubleshooting guide](troubleshooting.md). Record the exact commit and environment. Do not test unidentified LED nodes or capture typed text.

| Check | Evidence to record |
| --- | --- |
| Firmware trigger | Whether the identified LED changes the RGB state |
| Device association | Whether the evdev device and LED resolve to the same input owner |
| Key press | Backlight response to Scroll Lock |
| Caps Lock / Num Lock | Any reset, flicker or unexpected change |
| USB reconnect | Whether the correct device is rediscovered and the initial state is off |
| Stop / restart | Actual service state, logs and observed behavior |
| Multiple keyboards | Whether only the intended eligible pair is selected |

These are suggested checks, not results of new experiments. The offline tests do not replace them.

Report sanitized findings using the [issue tracker](https://github.com/kayo-willian/scrolllock-rgb-fix/issues) or use the [security policy](../SECURITY.md) for sensitive findings.

[Architecture](architecture.md) · [Troubleshooting](troubleshooting.md)
