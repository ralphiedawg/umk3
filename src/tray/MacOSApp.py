import rumps

class MacOSApp(rumps.App):
    def __init__(self):
        super().__init__(
            "UMK",
            icon="src/tray/icons/umklogoTemplate.png",
            template=True,
            quit_button="Quit",
        )

if __name__ == "__main__":
    MacOSApp().run()
