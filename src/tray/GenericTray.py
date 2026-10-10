import pystray 
import cairosvg

from PIL import Image, ImageDraw

from src.media.Client import Client
from src.media.Server import Server

from typing import cast
import threading
import io

"""
TODO:
2. Mode Switch
    a. when clicked, change the state
    b. 'Mode: Client'
3. Killswitch:
    a. 'Killswitch: Active'
4. Settings menu:
    a. Server Port
    b. client timeout
    c. How many frames to process per second
3. Dark/Light mode icons


"""


class TrayApp():
    def __init__(
            self, 
            icon_url: str = 'icons/UMKSVG24.svg',
            mode: str = 'Client',
            server_port: int = 2022
            
        ):

        self.icon_url = icon_url
        self.mode = mode
        self.server_port = server_port

        img_data = cast(bytes, cairosvg.svg2png(url = icon_url)) # type safety i guess?
        self.img = Image.open(io.BytesIO(img_data))

        self.icon = pystray.Icon(
            name = 'UMK3',
            icon = self.img,
            title = "UMK title thing",
            menu = pystray.Menu(
                pystray.MenuItem(lambda text: f'Operation Mode: {self.mode}', self.mode_toggle),
                pystray.MenuItem('Initialize', self.initialize),
                pystray.MenuItem('Quit UMK', self.quit),
                )
            )

    def quit(self, icon, item):
        icon.stop()   

    def mode_toggle(self, icon, item):
        if self.mode == 'Client':
            self.mode = 'Server'
        else:
            self.mode = 'Client'
        print("Operation mode switched to " + self.mode)
        icon.update_menu()

    def initialize(self):
        print(f'Initializing in {self.mode} mode...')
        if self.mode == 'Client':
            self.client = Client()
            self.client_thread = threading.Thread(target=self.client.run)
            self.client_thread.start()
        else:
            if self.client:
                del self.client
            self.server = Server(port = self.server_port)
            self.server.run_server()

    def run(self):
        self.icon.run()
     
if __name__ == "__main__":
    #T = TrayApp('icons/UMKSVG24.svg')
    #T.run()
    s = Server()
    s.run_server()
