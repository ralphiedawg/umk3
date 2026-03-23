import pynput as pn
from pynput.keyboard import Key

board = pn.keyboard.Controller()
while True:
    command = input(f"input command: \n")
    if command == "play":
        board.press(Key.media_play_pause)
