import rumps

from src.media.Client import Client
from src.media.Server import Server

import threading

class MacOSApp(rumps.App):
    def __init__(self):
        super().__init__(
            "UMK",
            icon="src/tray/icons/umklogoTemplate.png",
            template=True,
            quit_button="Quit",
        )
        self.is_client = True # If false, it's a server

        self.menu = []
        self.menu.add(rumps.MenuItem('Mode: Client', callback = self.switch_mode))

        if self.is_client:
            self.client = Client()
            self.menu.add(rumps.MenuItem('Connect'))
            self.menu.add(rumps.MenuItem(f'Killswitch: {self.client.killswitch}'))
        self.server_port = 2022

    @rumps.clicked('Mode: Client')
    def switch_mode(self, button):
        self.is_client = not self.is_client
        if not self.is_client:
            button.title = 'Mode: Server'

    @rumps.clicked('Connect')
    def connect_disconnect(self, button):
        if button.title == 'Connect':
            button.title = 'Disconnect'
            if self.is_client:
                print('Client class imported, initiating...')
                self.client_thread = threading.Thread(target=self.client.run)
                self.client_thread.start()
            else:
                del self.client
                button.title = 'Mode: Server'
                print('Server class imported, initiating...')
                self.server = Server(port = self.server_port)
                self.server.run_server()       
        else: 
            print('Disconnecting...')
            button.title = 'Connect'
            if self.is_client:
                self.client.killswitch = True



if __name__ == "__main__":
    MacOSApp().run()
