import pynput as pn

from pynput.keyboard import Key
import subprocess
import sys

def send_cmd(cmd):
    board = pn.keyboard.Controller()
    if cmd == "pause":
        board.tap(Key.media_play_pause)
    elif cmd == "mute":
        board.tap(Key.media_volume_mute)
    elif cmd == "skip5":
        board.tap(Key.right)
    elif cmd == "back5":
        board.tap(Key.left)
    elif cmd == "skip":
        board.tap(Key.media_next)
        if sys.platform == 'darwin':
            subprocess.run(['nowplaying-cli', 'next'])
    elif cmd == "rewind":
        board.tap(Key.media_previous)
        if sys.platform == 'darwin':
            subprocess.run(['nowplaying-cli', 'previous'])
    else:
        return("Invalid Command")
    return("Command Successful!")

if __name__ == "__main__":
    while True:
        send_cmd(input(f"Command: \n"))
