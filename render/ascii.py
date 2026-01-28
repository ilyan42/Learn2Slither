"""ASCII rendering functions for terminal display."""

import os
import sys
import termios
import tty

from Board.environment import Environment


# Key codes for arrow keys
KEY_UP = "\x1b[A"
KEY_DOWN = "\x1b[B"
KEY_RIGHT = "\x1b[C"
KEY_LEFT = "\x1b[D"


def get_key() -> str:
    """Read a single key press from terminal."""
    fd = sys.stdin.fileno()
    old_settings = termios.tcgetattr(fd)
    try:
        tty.setraw(fd)
        key = sys.stdin.read(3)
    finally:
        termios.tcsetattr(fd, termios.TCSADRAIN, old_settings)
    return key


def clear_screen() -> None:
    """Clear the terminal screen."""
    os.system("clear" if os.name == "posix" else "cls")


def display_grid_ascii(env: Environment, show_info: bool = True) -> None:
    """Display the game grid in ASCII format."""
    clear_screen()
    GREEN = "\033[92m"
    RED = "\033[91m"
    BLUE = "\033[94m"
    YELLOW = "\033[93m"
    RESET = "\033[0m"
    BOLD = "\033[1m"

    print(f"\n{BOLD}+{'=' * 21}+{RESET}")
    for y in range(len(env.grid)):
        print(f"{BOLD}|{RESET}", end=" ")
        for x in range(len(env.grid[0])):
            pos = (x, y)
            if pos == env.snake[0]:
                print(f"{YELLOW}O{RESET}", end=" ")
            elif pos in env.snake:
                print(f"{BLUE}o{RESET}", end=" ")
            elif pos in env.green_apples:
                print(f"{GREEN}G{RESET}", end=" ")
            elif pos == env.red_apple:
                print(f"{RED}R{RESET}", end=" ")
            else:
                print(".", end=" ")
        print(f"{BOLD}|{RESET}")
    print(f"{BOLD}+{'=' * 21}+{RESET}")

    if show_info:
        print(f"\n{BOLD}Longueur:{RESET} {len(env.snake)}")
        print(f"{BOLD}Etat:{RESET} {env.get_state()}")
