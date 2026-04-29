import pynput as pn

from pynput.keyboard import Key
import subprocess

def send_cmd(cmd):
    board = pn.keyboard.Controller()
    if cmd == "pause":
        board.press(Key.media_play_pause)
    elif cmd == "mute":
        board.press(Key.media_volume_mute)
    elif cmd == "skip5":
        board.press(Key.right)
    elif cmd == "back5":
        board.press(Key.left)
    elif cmd == "skip":
        board.press(Key.media_next)
        subprocess.run(['nowplaying-cli', 'next'])
    elif cmd == "rewind":
        board.press(Key.media_previous)
        subprocess.run(['nowplaying-cli', 'previous'])
    else:
        return("Invalid Command")
    return("Command Successful!")

if __name__ == "__main__":
    while True:
        send_cmd(input(f"Command: \n"))
