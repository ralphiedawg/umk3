import multiprocessing

multiprocessing.freeze_support()

import pystray 
import cairosvg

from PIL import Image, ImageDraw

from src.media.Client import Client
from src.media.Server import Server

from typing import cast
import threading
import io
import logging

from src.app_logging import configure_logging
from src.resource_paths import resource_path

logger = logging.getLogger(__name__)

class TrayApp():
    def __init__(
            self, 
            icon_url: str = 'icons/UMKSVG24.svg',
            mode: str = 'Client',
            server_port: int = 2022
            
        ):

        self.icon_url = str(resource_path(icon_url))
        self.mode = mode
        self.server_port = server_port

        self.client = None
        self.server = None

        self.client_thread = None
        self.server_thread = None
        self.killswitch_active = False

        img_data = cast(bytes, cairosvg.svg2png(url = self.icon_url)) # type safety i guess?
        self.img = Image.open(io.BytesIO(img_data))

        self.icon = pystray.Icon(
            name = 'UMK3',
            icon = self.img,
            title = "UMK title thing",
            menu = pystray.Menu(
                pystray.MenuItem(lambda text: f'Operation Mode: {self.mode}', self.mode_toggle),
                pystray.MenuItem('Initialize', self.initialize),
                pystray.MenuItem(
                    lambda text: f'Killswitch: {"Active" if self.killswitch_active else "Inactive"}',
                    self.killswitch_toggle,
                    visible=lambda item: self.mode == 'Client'
                ),
                pystray.MenuItem('Quit UMK', self.quit),
                )
            )

    def quit(self, icon, item):
        if self.server:
            self.server.shutdown()
            self.server = None
        if self.client:
            self.client.shutdown()
            self.client = None
        icon.stop()   

    def mode_toggle(self, icon, item):
        if self.mode == 'Client': self.mode = 'Server'
        else:
            self.mode = 'Client'
        print("Operation mode switched to " + self.mode)
        icon.update_menu()

    def killswitch_toggle(self, icon, item):
        self.killswitch_active = not self.killswitch_active
        if self.client:
            self.client.killswitch = self.killswitch_active
        print(f"Killswitch {'activated: dropping all commands' if self.killswitch_active else 'deactivated: executing commands'}")
        icon.update_menu()

    def initialize(self, icon=None, item=None):
        print(f'Initializing in {self.mode} mode...')
        if self.mode == 'Client':
            if self.server:
                self.server.shutdown()
                self.server = None

            if self.client:
                print('Client already running')
                return

            try:
                self.client = Client()
                self.client.killswitch = self.killswitch_active
                self.client_thread = threading.Thread(target=self.client.run, daemon=True)
                self.client_thread.start()
            except Exception:
                logger.exception("Failed to initialize client")
                self.client = None

        else:
            if self.client:
                self.client.shutdown()
                self.client = None

            if self.server_thread and self.server_thread.is_alive():
                print('Server already running')
                return

            try:
                self.server = Server(port=self.server_port)
                self.server_thread = threading.Thread(target=self.server.run_server, daemon=True)
                self.server_thread.start()
            except Exception:
                logger.exception("Failed to initialize server")
                if self.server:
                    self.server.shutdown()
                self.server = None

    def run(self):
        configure_logging()
        self.icon.run()
     
if __name__ == "__main__":
    T = TrayApp('icons/UMKSVG24.svg')
    T.run()
    #s = Server()
    #s.run_server()
