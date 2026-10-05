#!/usr/bin/env bash
set -euo pipefail

SERVICE_NAME="scrolllock-rgb.service"
SERVICE_PATH="/etc/systemd/system/$SERVICE_NAME"
BIN_PATH="/usr/local/bin/scrolllock-rgb.py"

log() { printf '\033[1;32m[uninstall]\033[0m %s\n' "$*"; }
die() { printf '\033[1;31m[uninstall] ERROR:\033[0m %s\n' "$*" >&2; exit 1; }

[[ $EUID -eq 0 ]] || die "Run this uninstaller with sudo or as root."

log "Stopping and disabling $SERVICE_NAME..."
systemctl disable --now "$SERVICE_NAME" 2>/dev/null || true

log "Removing service file and daemon..."
rm -f "$SERVICE_PATH"
rm -f "$BIN_PATH"

log "Reloading systemd daemon..."
systemctl daemon-reload
systemctl reset-failed "$SERVICE_NAME" 2>/dev/null || true

log "Scroll Lock RGB Fix has been completely uninstalled."
