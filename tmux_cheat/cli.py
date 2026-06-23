#!/usr/bin/env python3
import argparse
import os
import shutil
import sys

from .cheatsheet import SECTIONS

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
# Rendering
# ---------------------------------------------------------------------------

def _resolve_prefix(cli_prefix: str | None) -> str:
    if cli_prefix:
        return cli_prefix
    env = os.environ.get("TMUX_PREFIX")
    if env:
        return env
    return "Ctrl+b"


def _render_sections(sections: list, prefix: str, colors: _Colors, term_width: int) -> None:
    for section in sections:
        print()
        title = f" {section['name']} "
        bar_len = max(0, (term_width - len(title)) // 2)
        bar = "─" * bar_len
        print(colors.header(f"{bar}{title}{bar}"))

        # Find the longest key string so we can align descriptions.
        entries = [(k.replace("{prefix}", prefix), d) for k, d in section["entries"]]
        max_key = max(len(k) for k, _ in entries)

        for key, desc in entries:
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
            "  3. Default: Ctrl+b\n\n"
            "Examples:\n"
            "  tmux-cheat                       # show everything\n"
            "  tmux-cheat sessions windows      # show specific categories\n"
            "  tmux-cheat --prefix Ctrl+a       # override prefix key once\n"
            "  TMUX_PREFIX=Ctrl+a tmux-cheat    # override prefix key persistently\n"
            "  tmux-cheat --list                # list available categories\n"
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
            "prefix key to show in shortcuts (overrides TMUX_PREFIX env var). "
            "Example: --prefix 'Ctrl+a'"
        ),
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

    prefix = _resolve_prefix(args.prefix)

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
        sections = SECTIONS

    print(
        colors.bold("tmux cheat sheet")
        + colors.dim(f"  (prefix: {colors.key(prefix)})")
    )
    print(colors.dim("source: https://tmuxcheatsheet.com/"))

    _render_sections(sections, prefix, colors, term_width)
