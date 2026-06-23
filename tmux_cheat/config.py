"""Parse tmux configuration files to extract prefix and keybind overrides."""

import re
from pathlib import Path

# Maps normalized tmux command strings to human-readable descriptions.
# Used when displaying custom/no-prefix bindings discovered in the config.
COMMAND_DESCRIPTIONS: dict[str, str] = {
    "split-window -h":          "Split pane vertically (side by side)",
    "split-window -v":          "Split pane horizontally (top/bottom)",
    "new-window":               "Create a new window",
    "rename-window":            "Rename current window",
    "kill-window":              "Close current window",
    "previous-window":          "Switch to previous window",
    "next-window":              "Switch to next window",
    "last-window":              "Toggle last active window",
    "choose-tree -Zw":          "List windows (interactive)",
    "kill-pane":                "Close current pane",
    "last-pane":                "Toggle last active pane",
    "select-pane -L":           "Switch focus to left pane",
    "select-pane -R":           "Switch focus to right pane",
    "select-pane -U":           "Switch focus to pane above",
    "select-pane -D":           "Switch focus to pane below",
    "resize-pane -Z":           "Toggle zoom on current pane",
    "break-pane":               "Convert pane to its own window",
    "select-pane -t :.+":       "Select next pane",
    "display-panes":            "Show pane numbers",
    "next-layout":              "Cycle through pane layouts",
    "rotate-window":            "Rotate panes in window",
    "copy-mode":                "Enter copy mode",
    "paste-buffer":             "Paste from copy buffer",
    "detach-client":            "Detach from current session",
    "switch-client -p":         "Move to previous session",
    "switch-client -n":         "Move to next session",
    "command-prompt":           "Enter tmux command prompt",
    "list-keys":                "List all key bindings",
    "clock-mode":               "Show a clock in the current pane",
    "source-file ~/.tmux.conf": "Reload tmux configuration",
}


def find_config_file() -> Path | None:
    """Find the tmux config in standard locations."""
    candidates = [
        Path.home() / ".tmux.conf",
        Path.home() / ".config" / "tmux" / "tmux.conf",
    ]
    for p in candidates:
        if p.exists():
            return p
    return None


def tmux_key_to_display(key: str) -> str:
    """Convert a tmux key spec (e.g. 'C-a', 'M-Left') to display form ('Ctrl+a', 'Alt+Left')."""
    if key.startswith("C-"):
        return "Ctrl+" + key[2:]
    if key.startswith("M-"):
        return "Alt+" + key[2:]
    if key.startswith("S-"):
        return "Shift+" + key[2:]
    return key


def _normalize_cmd(cmd: str) -> str:
    """Strip inline comments and collapse whitespace."""
    cmd = re.split(r'\s+#\s', cmd)[0].strip()
    return re.sub(r'\s+', ' ', cmd)


def parse_config(path: Path) -> dict:
    """
    Parse a tmux.conf file and return a structured dict:

      prefix            str   Display-form prefix key, e.g. "Ctrl+a"
      config_file       Path  The file that was parsed
      cmd_to_key        dict  tmux_command -> display_key  (prefix-bound overrides)
      cmd_to_no_prefix  dict  tmux_command -> display_key  (no-prefix -n bindings)
      unbound           set   Raw tmux key names that were explicitly unbound
    """
    prefix_raw = "C-b"
    # display_key -> cmd  (we invert later)
    raw_bindings: dict[str, str] = {}
    raw_no_prefix: dict[str, str] = {}
    unbound: set[str] = set()

    for line in path.read_text().splitlines():
        line = line.strip()
        if not line or line.startswith('#'):
            continue

        # set[-option] [-g] prefix KEY
        m = re.match(r'set(?:-option)?\s+(?:-[a-z]+\s+)*prefix\s+(\S+)', line)
        if m:
            prefix_raw = m.group(1)
            continue

        # unbind[-key] [-n] KEY
        m = re.match(r'unbind(?:-key)?\s+(?:-\S+\s+)*(\S+)', line)
        if m:
            unbound.add(m.group(1))
            continue

        # bind[-key] -n KEY COMMAND  (no-prefix binding)
        m = re.match(r'bind(?:-key)?\s+-n\s+(\S+)\s+(.+)', line)
        if m:
            key = tmux_key_to_display(m.group(1))
            cmd = _normalize_cmd(m.group(2))
            raw_no_prefix[key] = cmd
            continue

        # bind[-key] [-T table] KEY COMMAND  (prefix binding)
        m = re.match(r'bind(?:-key)?\s+(?:-T\s+\S+\s+)?(\S+)\s+(.+)', line)
        if m:
            key = tmux_key_to_display(m.group(1))
            cmd = _normalize_cmd(m.group(2))
            raw_bindings[key] = cmd
            continue

    # Invert both maps: command -> key  (last binding wins if duplicates exist)
    cmd_to_key = {cmd: key for key, cmd in raw_bindings.items()}
    cmd_to_no_prefix = {cmd: key for key, cmd in raw_no_prefix.items()}

    return {
        "prefix": tmux_key_to_display(prefix_raw),
        "config_file": path,
        "cmd_to_key": cmd_to_key,
        "cmd_to_no_prefix": cmd_to_no_prefix,
        "unbound": unbound,
    }
