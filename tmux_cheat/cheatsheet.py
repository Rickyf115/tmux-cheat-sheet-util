"""
tmux cheat sheet data, sourced from https://tmuxcheatsheet.com/

Entries use {prefix} as a placeholder, replaced at render time with the
configured prefix key (default Ctrl+b, overridable via TMUX_PREFIX env var).
"""

SECTIONS = [
    {
        "name": "Sessions",
        "slug": "sessions",
        "entries": [
            ("{prefix} $",                     "Rename current session"),
            ("{prefix} d",                     "Detach from current session"),
            ("{prefix} (",                     "Move to previous session"),
            ("{prefix} )",                     "Move to next session"),
            ("tmux new-session",               "Start a new session"),
            ("tmux new-session -s name",       "Start a new named session"),
            ("tmux kill-session -t name",      "Kill a session by name"),
            ("tmux kill-server",               "Kill the tmux server (all sessions)"),
            ("tmux list-sessions  |  tmux ls", "List all sessions"),
            ("tmux attach-session -t name",    "Attach to a named session"),
            ("tmux attach-session -t #",       "Attach to session by index"),
            ("tmux rename-session -t old new", "Rename a session"),
        ],
    },
    {
        "name": "Windows",
        "slug": "windows",
        "entries": [
            ("{prefix} c",   "Create a new window"),
            ("{prefix} ,",   "Rename current window"),
            ("{prefix} &",   "Close current window"),
            ("{prefix} p",   "Switch to previous window"),
            ("{prefix} n",   "Switch to next window"),
            ("{prefix} l",   "Toggle last active window"),
            ("{prefix} 0-9", "Switch to window by number"),
            ("{prefix} w",   "List windows (interactive)"),
            ("{prefix} f",   "Find window by name"),
        ],
    },
    {
        "name": "Panes",
        "slug": "panes",
        "entries": [
            ("{prefix} %",         "Split pane vertically (side by side)"),
            ("{prefix} \"",        "Split pane horizontally (top/bottom)"),
            ("{prefix} ;",         "Toggle last active pane"),
            ("{prefix} {",         "Move pane left"),
            ("{prefix} }",         "Move pane right"),
            ("{prefix} z",         "Toggle zoom on current pane"),
            ("{prefix} !",         "Convert pane to its own window"),
            ("{prefix} x",         "Close current pane"),
            ("{prefix} o",         "Select next pane"),
            ("{prefix} q",         "Show pane numbers"),
            ("{prefix} q 0-9",     "Switch to pane by number"),
            ("{prefix} Arrow",     "Switch focus to pane in that direction"),
            ("{prefix} Space",     "Cycle through pane layouts"),
            ("{prefix} Ctrl+o",    "Rotate panes in window"),
            ("{prefix} Ctrl+Up",   "Resize pane up"),
            ("{prefix} Ctrl+Down", "Resize pane down"),
            ("{prefix} Ctrl+Left", "Resize pane left"),
            ("{prefix} Ctrl+Right","Resize pane right"),
        ],
    },
    {
        "name": "Copy Mode",
        "slug": "copy",
        "entries": [
            ("{prefix} [",      "Enter copy mode"),
            ("{prefix} ]",      "Paste from copy buffer"),
            ("{prefix} PgUp",   "Enter copy mode and scroll up"),
            ("Space",           "Start selection (in copy mode)"),
            ("Enter",           "Copy selection (in copy mode)"),
            ("q",               "Quit copy mode"),
            ("g",               "Go to top"),
            ("G",               "Go to bottom"),
            ("/",               "Search forward"),
            ("?",               "Search backward"),
            ("n",               "Next search match"),
            ("N",               "Previous search match"),
        ],
    },
    {
        "name": "Misc",
        "slug": "misc",
        "entries": [
            ("{prefix} :",  "Enter tmux command prompt"),
            ("{prefix} ?",  "List all key bindings"),
            ("{prefix} t",  "Show a clock in the current pane"),
            ("{prefix} ~",  "Show previous messages from tmux"),
            ("tmux source-file ~/.tmux.conf", "Reload tmux configuration"),
        ],
    },
]
