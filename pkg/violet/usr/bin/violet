#!/usr/bin/env python3

import sys
import termios
import tty
from pathlib import Path
from rich.console import Console
from rich.panel import Panel
from rich.text import Text

console = Console()

def load_entries(path):
    items = [path.parent]
    items.extend(path.iterdir())
    return items

def read_key():
    fd = sys.stdin.fileno()
    old = termios.tcgetattr(fd)
    try:
        tty.setraw(fd)
        ch1 = sys.stdin.read(1)
        if ch1 == "\x1b":
            ch2 = sys.stdin.read(1)
            ch3 = sys.stdin.read(1)
            return ch1 + ch2 + ch3
        return ch1
    finally:
        termios.tcsetattr(fd, termios.TCSADRAIN, old)

current_path = Path.home()
entries = load_entries(current_path)
selected = 0
mode = "list"
file_lines = []
scroll = 0

while True:
    console.clear()
    if mode == "view":
        console.print(
            Panel(
                Text("\n").join(file_lines[scroll:scroll+30]),
                title=f"Violet — arquivo (q p/ voltar)"
            )
        )
        key = read_key()
        if key == "q":
            mode = "list"
            scroll = 0
        elif key == "\x1b[A":
            scroll -= 1
        elif key == "\x1b[B":
            scroll += 1
        if scroll < 0:
            scroll = 0
        if scroll > max(0, len(file_lines)-30):
            scroll = max(0, len(file_lines)-30)
        continue

    lines = []
    for i, p in enumerate(entries):
        if i == 0:
            name = ".."
        else:
            name = p.name + ("/" if p.is_dir() else "")
        if i == selected:
            lines.append(Text("→ " + name, style="bold magenta"))
        else:
            lines.append(Text("  " + name))

    console.print(
        Panel(
            Text("\n").join(lines),
            title=f"Violet — {current_path}"
        )
    )

    key = read_key()
    if key == "q":
        break
    elif key == "\x1b[A":
        selected -= 1
    elif key == "\x1b[B":
        selected += 1
    elif key == "\r":
        current = entries[selected]
        if selected == 0:
            current_path = current_path.parent
            entries = load_entries(current_path)
            selected = 0
        elif current.is_dir():
            current_path = current
            entries = load_entries(current_path)
            selected = 0
        else:
            try:
                file_lines = current.read_text(errors="ignore").splitlines()
                mode = "view"
                scroll = 0
            except Exception:
                pass

#bloqueio
    if selected < 0:
        selected = 0
    if selected >= len(entries):
        selected = len(entries) - 1
