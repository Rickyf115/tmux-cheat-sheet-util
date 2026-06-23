# tmux-cheat

A terminal cheat sheet for tmux keyboard shortcuts and commands, sourced from [tmuxcheatsheet.com](https://tmuxcheatsheet.com/).

```
tmux cheat sheet  (prefix: Ctrl+b)

───────────────────── Sessions ──────────────────────
  Ctrl+b $                        │  Rename current session
  Ctrl+b d                        │  Detach from current session
  tmux new-session -s name        │  Start a new named session
  ...
```

## Installation

Requires [uv](https://docs.astral.sh/uv/). If you don't have it:

```sh
curl -LsSf https://astral.sh/uv/install.sh | sh
```

### System-wide install (recommended)

```sh
git clone https://github.com/Rickyf115/tmux-cheat-sheet-util
cd tmux-cheat-sheet-util
./install.sh
```

`install.sh` will install uv if it isn't already present, then run
`uv tool install .` to put `tmux-cheat` on your `PATH`.

### Development setup

```sh
git clone https://github.com/Rickyf115/tmux-cheat-sheet-util
cd tmux-cheat-sheet-util
uv venv
uv sync
source .venv/bin/activate
```

`uv sync` installs the project and all dev dependencies into the local `.venv`.

## Usage

```
tmux-cheat [CATEGORY ...] [--prefix KEY] [--list] [--no-color]
```

| Flag / Argument | Description |
|---|---|
| `CATEGORY ...` | One or more category slugs to display. Omit to show all. |
| `--prefix KEY` | Override the prefix key shown in shortcuts (one-time). |
| `--list`, `-l` | Print available category slugs and exit. |
| `--no-color` | Disable ANSI color output (auto-disabled when not a TTY). |

### Examples

```sh
# Show everything (default Ctrl+b prefix)
tmux-cheat

# Show only sessions and panes sections
tmux-cheat sessions panes

# Show with a custom prefix key (one-time)
tmux-cheat --prefix 'Ctrl+a'

# Pipe to less without color codes
tmux-cheat --no-color | less

# List available categories
tmux-cheat --list
```

### Available categories

| Slug | Contents |
|---|---|
| `sessions` | Session management (new, attach, kill, rename, …) |
| `windows` | Window/tab management (create, switch, rename, …) |
| `panes` | Pane management (split, resize, zoom, move, …) |
| `copy` | Copy mode navigation and selection |
| `misc` | Command prompt, key binding list, clock, reload config |

## Configuring the prefix key

tmux's default prefix is `Ctrl+b`, but many users remap it (commonly to `Ctrl+a`).
Set the `TMUX_PREFIX` environment variable so `tmux-cheat` always shows your actual prefix.

### Temporary (current shell session only)

```sh
export TMUX_PREFIX='Ctrl+a'
tmux-cheat
```

### Permanent — bash

Add to `~/.bashrc` or `~/.bash_profile`:

```sh
export TMUX_PREFIX='Ctrl+a'
```

Then reload:

```sh
source ~/.bashrc
```

### Permanent — zsh

Add to `~/.zshrc`:

```sh
export TMUX_PREFIX='Ctrl+a'
```

Then reload:

```sh
source ~/.zshrc
```

### Permanent — fish

```fish
set -Ux TMUX_PREFIX 'Ctrl+a'
```

### Prefix resolution order

1. `--prefix` flag (highest priority, one-time override)
2. `TMUX_PREFIX` environment variable
3. Default: `Ctrl+b`

## Uninstall

```sh
uv tool uninstall tmux-cheat
```
