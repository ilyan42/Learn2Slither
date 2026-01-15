from Board.environment import Environment
import random


import sys
import tty
import termios

KEY_UP = '\x1b[A'
KEY_DOWN = '\x1b[B'
KEY_RIGHT = '\x1b[C'
KEY_LEFT = '\x1b[D'




def get_key():
    fd = sys.stdin.fileno()
    old_settings = termios.tcgetattr(fd)

    try:
        tty.setraw(fd)
        key = sys.stdin.read(3)
    finally:
        termios.tcsetattr(fd, termios.TCSADRAIN, old_settings)

    return key

def main():
    env = Environment()
    state = env.get_state()
    while env.game_over == False:
        env.display_grid()
        print("Use arrow keys (Ctrl+C to quit)")

        key = get_key()

        if key == KEY_UP:
            env.move(env.UP)
        elif key == KEY_DOWN:
            env.move(env.DOWN)
        elif key == KEY_LEFT:
            env.move(env.LEFT)
        elif key == KEY_RIGHT:
            env.move(env.RIGHT)
        
    # env.update_grid()
    print (state)


if __name__ == "__main__":
	main()
