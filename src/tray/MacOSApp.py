import rumps

class MacOSApp(rumps.App):
    def __init__(self):
        super().__init__(
            "UMK",
            icon="src/tray/icons/umklogoTemplate.png",
            template=True,
            quit_button="Quit",
        )
        self.menu = ['Connect']
    @rumps.clicked('Connect')
    def connect(self, button):
        if button.title == 'Connect':
            print('Changing to disconnect')
            button.title = 'Disconnect'
        else: 
            print('Changing to connect')
            button.title = 'Connect'


if __name__ == "__main__":
    MacOSApp().run()
