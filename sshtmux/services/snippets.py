import curses
import os
from time import sleep

from rich.console import Console
from rich.prompt import Prompt

from sshtmux.core.config import settings

console = Console()


def choose_cmd(path):
    lines = None

    try:
        with open(path, "r") as arquivo:
            lines = arquivo.readlines()
    except FileNotFoundError:
        print("File not found")
        exit(1)
    except Exception as e:
        print(f"Error to open file {path}: {e}")
        exit(1)

    if not lines:
        print(f"Empty file: {path}")
        return None

    def browser(stdscr):
        index = 0
        scroll = 0
        height, width = stdscr.getmaxyx()

        while True:
            stdscr.clear()
            stdscr.addstr("Choose a command\n\n")

            for i in range(scroll, min(scroll + height - 3, len(lines))):
                line_showed = lines[i].strip()
                if len(line_showed) > width - 4:
                    line_showed = line_showed[: width - 4]

                if i == index:
                    stdscr.addstr(f">> {i + 1}: {line_showed}\n", curses.A_REVERSE)
                else:
                    stdscr.addstr(f"   {i + 1}: {line_showed}\n")

            key = stdscr.getch()

            if key == ord("j") or key == curses.KEY_DOWN:
                if index < len(lines) - 1:
                    index += 1
                if index >= scroll + height - 3:
                    scroll += 1
            elif key == ord("k") or key == curses.KEY_UP:
                if index > 0:
                    index -= 1
                if index < scroll:
                    scroll -= 1

            elif key == ord("\n"):
                return lines[index].strip()

            elif key == ord("q"):
                break

    return curses.wrapper(browser)


def get_snippets_files():
    snippets = ["Cancel"]
    snippets_path = settings.sshtmux.SSHTMUX_SNIPPETS_PATH
    if os.path.exists(snippets_path):
        for _, _, filenames in os.walk(snippets_path):
            for filename in filenames:
                snippets.append(filename)
    snippets_idx = [str(index) for index, _ in enumerate(snippets)]
    return snippets, snippets_idx


def _show_menu(options):
    console.print("Snippets:", style="bold underline")
    for idx, option in enumerate(options):
        console.print(f"{idx}. {option}")


def prompt_snippet():
    cmd = None
    choices, choices_idx = get_snippets_files()
    _show_menu(choices)
    choice = Prompt.ask(
        "Choose snippet:",
        choices=choices_idx,
        default=choices_idx[0],
        show_choices=False,
    )
    snippet_file = choices[int(choice)]
    if snippet_file == choices[0]:
        return

    try:
        cmd = choose_cmd(
            f"{settings.sshtmux.SSHTMUX_SNIPPETS_PATH}{os.sep}{snippet_file}"
        )
    except Exception as e:
        print(str(e))
        sleep(2)
    return cmd
