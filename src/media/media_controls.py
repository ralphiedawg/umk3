import pynput as pn
from pynput.keyboard import Key

import subprocess
import sys

board = pn.keyboard.Controller()

def next_track():
    board.tap(Key.media_next)

    if sys.platform == 'darwin':
        subprocess.run(['nowplaying-cli', 'next'])

def previous_track():
    board.tap(Key.media_previous)

    if sys.platform == 'darwin':
        subprocess.run(['nowplaying-cli', 'previous'])

actions = {
    'pause': lambda: board.tap(Key.media_play_pause),
    'mute': lambda: board.tap(Key.media_volume_mute),
    'skip5': lambda: board.tap(Key.right),
    'back5': lambda: board.tap(Key.left),
    'skip': next_track,
    'rewind': previous_track,
}

def send_cmd(cmd):
    action = actions.get(cmd)
    if action:
        action()
        return "Command Successful!"
    return "Invalid Command"

if __name__ == "__main__":
    while True:
        print(send_cmd(input("Command:\n").strip()))
