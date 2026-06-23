#!/usr/bin/env python3
import argparse
import copy
import os
import shutil
import sys
from pathlib import Path

from .cheatsheet import SECTIONS
from .config import COMMAND_DESCRIPTIONS, find_config_file, parse_config

# ---------------------------------------------------------------------------
# ANSI helpers
# ---------------------------------------------------------------------------

def _supports_color() -> bool:
    if not sys.stdout.isatty():
        return False
    term = os.environ.get("TERM", "")
    return term not in ("dumb", "")


class _Colors:
    def __init__(self, enabled: bool):
        self._on = enabled

    def _wrap(self, code: str, text: str) -> str:
        return f"\033[{code}m{text}\033[0m" if self._on else text

    def header(self, t: str) -> str:  return self._wrap("1;36", t)  # bold cyan
    def key(self, t: str) -> str:     return self._wrap("1;33", t)  # bold yellow
    def desc(self, t: str) -> str:    return self._wrap("0", t)      # default
    def dim(self, t: str) -> str:     return self._wrap("2", t)      # dim
    def bold(self, t: str) -> str:    return self._wrap("1", t)
    def green(self, t: str) -> str:   return self._wrap("32", t)


# ---------------------------------------------------------------------------
# Config-driven overrides
# ---------------------------------------------------------------------------

def _apply_config_overrides(sections: list, config: dict) -> tuple[list, list]:
    """
    Return (updated_sections, extra_entries) where:
    - updated_sections has default keys replaced by the user's custom bindings
    - extra_entries is a list of (key, description) for no-prefix or fully custom
      bindings that don't map to any existing cheat sheet entry
    """
    cmd_to_key = config.get("cmd_to_key", {})
    cmd_to_no_prefix = config.get("cmd_to_no_prefix", {})
    unbound = config.get("unbound", set())

    # Track which commands were consumed by existing entries so we can show
    # the remainder as a "Custom Bindings" section.
    used_commands: set[str] = set()

    result = []
    for section in sections:
        new_entries = []
        for entry in section["entries"]:
            key_tmpl, desc = entry[0], entry[1]
            cmd = entry[2] if len(entry) > 2 else None

            if cmd:
                used_commands.add(cmd)
                if cmd in cmd_to_key:
                    # User rebound this command to a new key with prefix.
                    new_key = key_tmpl.replace(
                        key_tmpl.split()[-1],  # replace the trailing default key
                        cmd_to_key[cmd],
                    )
                    # Safer: preserve {prefix} if it was there, swap just the key part.
                    if key_tmpl.startswith("{prefix}"):
                        new_key = "{prefix} " + cmd_to_key[cmd]
                    else:
                        new_key = cmd_to_key[cmd]
                    new_entries.append((new_key, desc))
                    continue
                if cmd in cmd_to_no_prefix:
                    # Command is now bound without a prefix.
                    new_entries.append((cmd_to_no_prefix[cmd], desc))
                    continue
                # Check if the default key was explicitly unbound.
                default_key = key_tmpl.split()[-1]  # e.g. "%" from "{prefix} %"
                if default_key in unbound:
                    continue  # omit removed bindings
            new_entries.append(entry[:2])

        if new_entries:
            result.append({**section, "entries": new_entries})

    # Collect custom no-prefix bindings not already mapped to a cheat sheet entry.
    extra: list[tuple[str, str]] = []
    for cmd, key in cmd_to_no_prefix.items():
        if cmd in used_commands:
            continue
        desc = COMMAND_DESCRIPTIONS.get(cmd, cmd)
        extra.append((key, desc))

    # Collect custom prefix bindings for commands not in the default cheat sheet.
    for cmd, key in cmd_to_key.items():
        if cmd in used_commands:
            continue
        # Skip internal plumbing like send-prefix
        if cmd in ("send-prefix",):
            continue
        desc = COMMAND_DESCRIPTIONS.get(cmd, cmd)
        extra.append(("{prefix} " + key, desc))

    return result, extra


# ---------------------------------------------------------------------------
# Rendering
# ---------------------------------------------------------------------------

def _resolve_prefix(cli_prefix: str | None, config_prefix: str | None) -> str:
    if cli_prefix:
        return cli_prefix
    env = os.environ.get("TMUX_PREFIX")
    if env:
        return env
    if config_prefix:
        return config_prefix
    return "Ctrl+b"


def _render_sections(sections: list, prefix: str, colors: _Colors, term_width: int) -> None:
    for section in sections:
        print()
        title = f" {section['name']} "
        bar_len = max(0, (term_width - len(title)) // 2)
        bar = "─" * bar_len
        print(colors.header(f"{bar}{title}{bar}"))

        entries = [(k.replace("{prefix}", prefix), d) for k, d in section["entries"]]
        max_key = max(len(k) for k, _ in entries)

        for key, desc in entries:
            padding = " " * (max_key - len(key))
            print(f"  {colors.key(key)}{padding}  {colors.dim('│')}  {colors.desc(desc)}")

    print()


def _render_extra(entries: list, prefix: str, colors: _Colors, term_width: int) -> None:
    if not entries:
        return
    print()
    title = " Custom Bindings "
    bar_len = max(0, (term_width - len(title)) // 2)
    bar = "─" * bar_len
    print(colors.header(f"{bar}{title}{bar}"))

    resolved = [(k.replace("{prefix}", prefix), d) for k, d in entries]
    max_key = max(len(k) for k, _ in resolved)
    for key, desc in resolved:
        padding = " " * (max_key - len(key))
        print(f"  {colors.key(key)}{padding}  {colors.dim('│')}  {colors.desc(desc)}")
    print()


def _list_categories(colors: _Colors) -> None:
    print()
    print(colors.bold("Available categories:"))
    for s in SECTIONS:
        print(f"  {colors.green(s['slug']):<20}  {s['name']}")
    print()
    print(colors.dim("Pass one or more category names as positional arguments, or omit for all."))
    print()


# ---------------------------------------------------------------------------
# Entry point
# ---------------------------------------------------------------------------

def main() -> None:
    parser = argparse.ArgumentParser(
        prog="tmux-cheat",
        description="tmux keyboard shortcuts and command cheat sheet",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=(
            "Prefix key resolution order (first wins):\n"
            "  1. --prefix flag\n"
            "  2. TMUX_PREFIX environment variable\n"
            "  3. ~/.tmux.conf  (or ~/.config/tmux/tmux.conf)\n"
            "  4. Default: Ctrl+b\n\n"
            "Examples:\n"
            "  tmux-cheat                        # show everything\n"
            "  tmux-cheat sessions windows       # show specific categories\n"
            "  tmux-cheat --prefix Ctrl+a        # override prefix key once\n"
            "  tmux-cheat --config ~/my.conf     # use a specific config file\n"
            "  tmux-cheat --no-config            # ignore tmux config file\n"
            "  tmux-cheat --list                 # list available categories\n"
        ),
    )
    parser.add_argument(
        "categories",
        nargs="*",
        metavar="CATEGORY",
        help="one or more category slugs to display (default: all)",
    )
    parser.add_argument(
        "--prefix",
        metavar="KEY",
        help=(
            "prefix key to show in shortcuts (overrides config file and TMUX_PREFIX). "
            "Example: --prefix 'Ctrl+a'"
        ),
    )
    parser.add_argument(
        "--config",
        metavar="FILE",
        help="path to tmux config file (default: ~/.tmux.conf)",
    )
    parser.add_argument(
        "--no-config",
        action="store_true",
        help="ignore tmux config file; use defaults only",
    )
    parser.add_argument(
        "--list", "-l",
        action="store_true",
        help="list available category names and exit",
    )
    parser.add_argument(
        "--no-color",
        action="store_true",
        help="disable ANSI color output",
    )

    args = parser.parse_args()
    colors = _Colors(enabled=not args.no_color and _supports_color())
    term_width = shutil.get_terminal_size((80, 24)).columns

    if args.list:
        _list_categories(colors)
        return

    # Load tmux config unless suppressed.
    tmux_config: dict = {}
    config_path: Path | None = None

    if not args.no_config:
        if args.config:
            config_path = Path(args.config).expanduser()
            if not config_path.exists():
                parser.error(f"Config file not found: {config_path}")
        else:
            config_path = find_config_file()

        if config_path:
            tmux_config = parse_config(config_path)

    prefix = _resolve_prefix(args.prefix, tmux_config.get("prefix"))

    valid_slugs = {s["slug"] for s in SECTIONS}
    if args.categories:
        unknown = [c for c in args.categories if c not in valid_slugs]
        if unknown:
            parser.error(
                f"Unknown category/categories: {', '.join(unknown)}. "
                f"Run 'tmux-cheat --list' to see available options."
            )
        sections = [s for s in SECTIONS if s["slug"] in set(args.categories)]
    else:
        sections = list(SECTIONS)

    sections, extra_entries = _apply_config_overrides(sections, tmux_config)

    header = colors.bold("tmux cheat sheet") + colors.dim(f"  (prefix: {colors.key(prefix)})")
    if config_path:
        header += colors.dim(f"  [{config_path}]")
    print(header)
    print(colors.dim("source: https://tmuxcheatsheet.com/"))

    _render_sections(sections, prefix, colors, term_width)
    _render_extra(extra_entries, prefix, colors, term_width)
