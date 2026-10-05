#!/usr/bin/env bash
set -euo pipefail

PROJECT_DIR="$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")" && pwd)"
BIN_PATH="/usr/local/bin/scrolllock-rgb.py"
SERVICE_NAME="scrolllock-rgb.service"
SERVICE_PATH="/etc/systemd/system/$SERVICE_NAME"

log() { printf '\033[1;32m[install]\033[0m %s\n' "$*"; }
warn() { printf '\033[1;33m[install] WARNING:\033[0m %s\n' "$*" >&2; }
die() { printf '\033[1;31m[install] ERROR:\033[0m %s\n' "$*" >&2; exit 1; }

# 1. Check permissions
[[ $EUID -eq 0 ]] || die "Run this installer with sudo or as root."

# 2. Check init system (systemd)
if ! [[ -d /run/systemd/system ]] && ! command -v systemctl >/dev/null 2>&1; then
    die "systemd is required to install and manage this service."
fi

# 3. Package manager auto-install for python3-evdev
install_evdev_package() {
    case "${1:-}" in
        apt)
            log "Updating package index and installing python3-evdev..."
            apt-get update -qq
            apt-get install -y python3-evdev
            ;;
        dnf)
            log "Installing python3-evdev with dnf..."
            dnf install -y python3-evdev
            ;;
        pacman)
            log "Installing python-evdev with pacman..."
            pacman -Sy --needed --noconfirm python-evdev
            ;;
        zypper)
            log "Installing python3-evdev with zypper..."
            zypper --non-interactive install python3-evdev
            ;;
        apk)
            log "Installing py3-evdev with apk..."
            apk add py3-evdev
            ;;
        *)
            die "Could not identify a supported package manager. Please install 'python3-evdev' manually."
            ;;
    esac
}

if ! python3 -c "import evdev" >/dev/null 2>&1; then
    log "Dependency python3-evdev not found. Attempting automatic installation..."
    if command -v apt-get >/dev/null 2>&1; then install_evdev_package apt
    elif command -v dnf >/dev/null 2>&1; then install_evdev_package dnf
    elif command -v pacman >/dev/null 2>&1; then install_evdev_package pacman
    elif command -v zypper >/dev/null 2>&1; then install_evdev_package zypper
    elif command -v apk >/dev/null 2>&1; then install_evdev_package apk
    else
        die "No supported package manager found (apt, dnf, pacman, zypper, apk). Please install 'python3-evdev' manually."
    fi
else
    log "Dependency python3-evdev is already installed."
fi

# 4. Verify source files exist
[[ -f "$PROJECT_DIR/scrolllock-rgb.py" ]] || die "scrolllock-rgb.py not found in $PROJECT_DIR."
[[ -f "$PROJECT_DIR/$SERVICE_NAME" ]] || die "$SERVICE_NAME not found in $PROJECT_DIR."

# 5. Install binaries and systemd unit
log "Installing Python daemon to $BIN_PATH..."
install -d -m 0755 "/usr/local/bin"
install -m 0755 "$PROJECT_DIR/scrolllock-rgb.py" "$BIN_PATH"

log "Installing systemd unit to $SERVICE_PATH..."
install -m 0644 "$PROJECT_DIR/$SERVICE_NAME" "$SERVICE_PATH"

# 6. Enable and start the service
log "Reloading systemd daemon..."
systemctl daemon-reload

log "Enabling and starting $SERVICE_NAME..."
systemctl enable --now "$SERVICE_NAME"
systemctl restart "$SERVICE_NAME"

# 7. Verification
if systemctl is-active --quiet "$SERVICE_NAME"; then
    log "Installation completed successfully!"
    log "Service status: ACTIVE"
    printf "\n"
    printf "You can now test your keyboard RGB by pressing the \033[1mScroll Lock\033[0m key.\n"
    printf "To view real-time logs, run: \033[1mjournalctl -u %s -f\033[0m\n" "$SERVICE_NAME"
else
    warn "The service was installed but did not become active immediately."
    systemctl status "$SERVICE_NAME" --no-pager || true
    die "Installation failed to start the service. Check logs with 'journalctl -u $SERVICE_NAME'."
fi
