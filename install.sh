#!/usr/bin/env bash
set -euo pipefail

if ! command -v uv &>/dev/null; then
    echo "uv not found — installing via the official installer..."
    curl -LsSf https://astral.sh/uv/install.sh | sh
    export PATH="$HOME/.local/bin:$PATH"
fi

if uv tool list 2>/dev/null | sed 's/\x1b\[[0-9;]*m//g' | grep -q '^tmux-cheat'; then
    echo "Upgrading existing tmux-cheat installation..."
else
    echo "Installing tmux-cheat..."
fi
uv tool install --force .
echo "Done. Run 'tmux-cheat' to get started."
