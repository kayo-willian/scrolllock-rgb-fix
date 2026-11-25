# Security Policy

[Português (Brasil)](pt-BR/SECURITY.md)

## Scope

Scroll Lock RGB Fix runs a privileged systemd service that reads evdev input events and writes to sysfs. The current development branch is `main`. There is no promised support period, response SLA or bug bounty.

Relevant findings include unintended input recording or disclosure, unsafe privileged file operations, writes to unrelated devices, service or installer privilege issues, and unintended effects on system state.

## Reporting

Use the [Security Advisories page](https://github.com/kayo-willian/scrolllock-rgb-fix/security/advisories) and **Report a vulnerability** if private reporting is available. Otherwise, open a public issue requesting a private contact method without exploit details, sensitive evidence or private identifiers. Do not assume that private reporting is enabled.

Include the affected commit, distribution, relevant runtime versions, expected security boundary, observed behavior, impact and a minimal safe reproduction. Use mocks and disposable resources where possible. Distinguish reproduced findings from hypotheses. Do not test on systems without permission or collect real keystrokes.

Never publish typed text, raw input event streams, private logs, credentials or identifying device information. Allow the maintainer a reasonable opportunity to investigate before publishing exploitable details.

Ordinary non-sensitive bugs belong in Issues. See [CONTRIBUTING.md](CONTRIBUTING.md) and [troubleshooting](docs/troubleshooting.md). If a local installation behaves unexpectedly, stop the service and inspect it rather than weakening system permissions.
