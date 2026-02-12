#!/usr/bin/env python3

import sys
import termios
import tty
from pathlib import Path
from rich.console import Console
from rich.panel import Panel
from rich.text import Text
import shutil
import threading
import queue

console = Console()
task_queue = queue.Queue()
clipboard = None
move_clipboard = None


# =========================
# THREAD WORKER
# =========================

def copy_worker(src, dst):
    try:
        if src.is_dir():
            shutil.copytree(src, dst)
        else:
            shutil.copy2(src, dst)

        task_queue.put(("copy_done", src.name))
    except Exception as e:
        task_queue.put(("copy_error", str(e)))


# =========================
# UTIL
# =========================

def load_entries(path):
    items = [path.parent]
    items.extend(sorted(path.iterdir(), key=lambda p: (not p.is_dir(), p.name.lower())))
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


def generate_new_name(path):
    counter = 1
    new_path = path
    while new_path.exists():
        new_name = f"{path.stem} ({counter}){path.suffix}"
        new_path = path.parent / new_name
        counter += 1
    return new_path


# =========================
# FILE OPERATIONS
# =========================

def delete_selected():
    global entries, selected

    if selected == 0:
        return

    target = entries[selected]
    confirm = input(f"Delete '{target.name}'? (y/n): ")

    if confirm.lower() != "y":
        return

    if target.is_file():
        target.unlink()
    elif target.is_dir():
        shutil.rmtree(target)

    refresh()


def copy_selected():
    global clipboard

    if selected == 0:
        return

    clipboard = entries[selected]

def move_worker(src,  dst):
    try:
        shutil.move(src, dst)
        task_queue.put(("move_done", src.name))
    except Exception as e:
        task_queue.put(("move_error", str(e)))


def paste_clipboard():
    global clipboard, move_clipboard

    source = clipboard if clipboard else move_clipboard

    if source is None:
        return

    destination = current_path / source.name

    if destination.exists():
        confirm = input(f"'{destination.name}' exists. Replace? (y/n): ")

        if confirm.lower() == "y":
            if destination.is_file():
                destination.unlink()
            else:
                shutil.rmtree(destination)
        else:
            destination = generate_new_name(destination)

    if move_clipboard:
        thread = threading.Thread(
            target=move_worker,
            args=(source, destination),
            daemon=True
        )
        move_clipboard = None
    else:
        thread = threading.Thread(
            target=copy_worker,
            args=(source, destination),
            daemon=True
        )
        clipboard = None

    thread.start()


def move_selected():
    global move_clipboard

    if selected == 0:
        return
    
    move_clipboard = entries[selected]

def rename_selected():
    global entries, selected, current_path

    if selected == 0:
        return

    target = entries[selected]

    new_name = input(f"Rename '{target.name}' to: ").strip()

    if not new_name:
        return

    new_path = target.parent / new_name

    if new_path.exists():
        confirm = input(f"'{new_name}' already exists. Replace? (y/n): ")
        if confirm.lower() != "y":
            return

        if new_path.is_file():
            new_path.unlink()
        elif new_path.is_dir():
            shutil.rmtree(new_path)

    try:
        target.rename(new_path)
    except Exception as e:
        console.print(f"Rename error: {e}", style="red")
        input("Press Enter to continue...")
        return

    entries = load_entries(current_path)
    selected = 0

def refresh():
    global entries, selected
    entries = load_entries(current_path)
    selected = 0


# =========================
# UI
# =========================

def draw_list():
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


def draw_view():
    height = console.size.height - 4
    visible_lines = file_lines[scroll:scroll+height]

    text = Text()
    for line in visible_lines:
        text.append(line + "\n")

    console.print(
        Panel(
            text,
            title="Violet — viewing (q to return)",
        )
    )



# =========================
# INPUT HANDLERS
# =========================

def handle_list_key(key):
    global selected, current_path, mode, file_lines, scroll

    if key == "\x1b[A":
        selected -= 1

    elif key == "\x1b[B":
        selected += 1

    elif key == "d":
        delete_selected()

    elif key == "c":
        copy_selected()

    elif key == "p":
        paste_clipboard()
    
    elif key == "m":
        move_selected()

    elif key == "r":
        rename_selected()

    elif key == "\r":
        current = entries[selected]

        if selected == 0:
            current_path = current_path.parent
            refresh()

        elif current.is_dir():
            current_path = current
            refresh()

        elif current.is_file():
          try:
           content = current.read_text(errors="ignore")
           file_lines = content.splitlines()

           if not file_lines:
              file_lines = ["(Empty file)"]

           mode = "view"
           scroll = 0
          except Exception as e:
            file_lines = [f"Error opening file: {e}"]
            mode = "view"
        scroll = 0


    selected = max(0, min(selected, len(entries) - 1))


def handle_view_key(key):
    global mode, scroll

    if key == "q":
        mode = "list"
        scroll = 0

    elif key == "\x1b[A":
        scroll -= 1

    elif key == "\x1b[B":
        scroll += 1

    scroll = max(0, min(scroll, max(0, len(file_lines) - 30)))


# =========================
# INITIAL STATE
# =========================

current_path = Path.home()
entries = load_entries(current_path)
selected = 0
mode = "list"
file_lines = []
scroll = 0


# =========================
# MAIN LOOP
# =========================

while True:
    console.clear()

    # Check thread messages
    while not task_queue.empty():
        msg_type, message = task_queue.get()

        if msg_type == "copy_done":
            console.print(f"\nCopy finished: {message}", style="green")
            refresh()

        elif msg_type == "copy_error":
            console.print(f"\nCopy error: {message}", style="red")

        elif msg_type == "move_done":
             console.print(f"\nMove finished: {message}", style="cyan")
             refresh()

        elif msg_type == "move_error":
             console.print(f"\nMove error: {message}", style="red")


    if mode == "list":
        draw_list()
    else:
        draw_view()

    key = read_key()

    if key == "q" and mode == "list":
        break

    if mode == "list":
        handle_list_key(key)
    else:
        handle_view_key(key)