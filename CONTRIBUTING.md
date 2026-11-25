# Contributing to Scroll Lock Keyboard RGB Fix

Contributions are welcome. This is an independent Linux utility for keyboards whose firmware responds to the physical Scroll Lock LED. You can fork it, improve documentation, report hardware results or submit a focused fix. These guidelines apply to upstream contributions, not independent forks under the [MIT license](LICENSE).

## Scope

Keep changes focused on Scroll Lock LED synchronization, device discovery, hotplug, service lifecycle, distribution compatibility and safe installation. This is not a general RGB driver, key remapper or input recording tool. Discuss new dependencies, privilege changes or major architectural changes in an issue first.

Hardware reports are valuable even without code. State the keyboard model if known, Linux distribution, desktop/compositor, kernel, systemd and Python/evdev versions. Separate observed results from assumptions about other systems.

See the [GitHub contributors list](https://github.com/kayo-willian/scrolllock-rgb-fix/graphs/contributors) for commit credits.

## Getting started

Use a Linux development machine with Git, Bash, Python and evdev. For Debian/Ubuntu, install the development dependency with `sudo apt install -y python3-evdev`. The offline tests run as an ordinary user and do not need a keyboard, root access or a running systemd manager.

1. Fork the repository and clone your fork.
2. Add the upstream remote and create a branch:

   ```sh
   git clone https://github.com/YOUR-USERNAME/scrolllock-rgb-fix.git
   cd scrolllock-rgb-fix
   git remote add upstream https://github.com/kayo-willian/scrolllock-rgb-fix.git
   git fetch upstream
   git switch -c fix/descriptive-name upstream/main
   ```

3. Run the existing tests:

   ```sh
   bash tests/test_syntax.sh
   python3 tests/test_daemon.py
   ```

4. Make the smallest coherent change. Add regression tests and rerun the checks. Review the diff, commit, push and open a pull request against upstream `main`.

   ```sh
   git diff --check
   git status --short
   git add -- path/to/changed-file
   git commit -m "fix: describe the change"
   git push -u origin fix/descriptive-name
   ```

Replace the example username, branch and file path.

## Safety and compatibility

- Keep discovery dynamic; never hardcode numbered evdev or sysfs paths. Verify that the input device and LED belong together, and handle ambiguity conservatively.
- Do not record arbitrary keystrokes, key sequences, input payloads or personal data. Never add telemetry or network access to the daemon without a reviewed design.
- Treat device names and paths as untrusted. Restrict writes to the intended Scroll Lock LED; do not modify unrelated devices, permissions, authentication or other system services.
- Preserve recovery, resource cleanup, hotplug handling and explicit shutdown. Test device errors, missing nodes, disconnects and multiple-device cases using mocks and temporary paths.
- Review root operations in the installer, uninstaller and unit. Avoid unrelated package changes, unsafe overwrites, broad permission changes or silent failures. Keep existing data and administrator changes safe.
- Distinguish a package-manager branch from demonstrated distribution support. Do not claim OpenRC support merely because apk is recognized.

Live tests are optional. Use a noncritical keyboard and an alternative input method, review [troubleshooting](docs/troubleshooting.md) and know how to stop the service. Check Scroll Lock toggles, Caps/Num Lock interaction, reconnection, stop/restart and logs. Test multiple devices only with explicit control of the target. Record the exact revision, environment and observed outcome. Do not infer hardware results from mocked tests.

## Issues and review

Search existing issues and pull requests first. Use the bug report or feature proposal template; include minimal reproduction, expected and actual behavior, and sanitized evidence. Project-created issues and templates are bilingual. Contributors may write in English or Brazilian Portuguese without translating their own report.

Do not publish raw key events, typed text, private logs, serial numbers, personal paths or credentials. Report suspected vulnerabilities through [SECURITY.md](SECURITY.md).

Keep code, comments, commits and PR descriptions in English. Preserve the existing English and Brazilian Portuguese READMEs and update both for significant usage changes. Update [CHANGELOG.md](CHANGELOG.md) under Unreleased for meaningful changes. Explain compatibility, actual validation and untested cases. For docs-only work, check links, commands and accuracy.

Disclose material AI assistance, verify the changes yourself, credit external work and submit only material you have the right to contribute under MIT. Do not invent authorship, test results or supported platforms.

PRs are reviewed before merge. There is no promised response time or release schedule. Follow the [code of conduct](CODE_OF_CONDUCT.md).
