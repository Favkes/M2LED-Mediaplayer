import tkinter as tk

from utils.globals import Globals
from utils.simple_logs import Logger, Logtype
from utils import ledcomm
import gui.handlers
import serial.tools.list_ports


logger = Logger(__name__, 'blue')


class Menu(tk.Menu):
    def __init__(self, app_root: tk.Tk):
        logger.log('Initializing Menu...', Logtype.init)

        super().__init__(app_root)
        self.root = app_root

        Globals.is_loading_presets = tk.BooleanVar(value=True)
        Globals.is_saving_presets = tk.BooleanVar(value=True)

        self.playlist_menu = None
        self.preset_menu = None
        self.connect_menu = None
        self.connect_menu_available_ports = None

        self.init_playlist_menu()
        self.init_preset_menu()
        self.init_connect_menu()


    def init_playlist_menu(self):
        logger.log('Initializing Menu.Playlist...', Logtype.init)

        self.playlist_menu = tk.Menu(self, tearoff=0)
        self.add_cascade(
            label='Playlist', menu=self.playlist_menu
        )
        self.playlist_menu.add_command(
            label="New Playlist",
            command=lambda: gui.handlers.save_playlist_new(logger)
        )
        self.playlist_menu.add_command(
            label="Open Playlist",
            command=lambda: gui.handlers.open_playlist(logger)
        )


    def init_preset_menu(self):
        logger.log('Initializing Menu.Preset...', Logtype.init)

        self.preset_menu = tk.Menu(self, tearoff=0)
        self.add_cascade(
            label="Preset settings", menu=self.preset_menu
        )
        self.preset_menu.add_command(
            label="Save current",
            command=lambda: gui.handlers.save_preset(logger)
        )
        self.preset_menu.add_checkbutton(
            label="Save automatically",
            command=lambda: gui.handlers.check_preset_save_automatically(logger),
            variable=Globals.is_saving_presets
        )
        self.preset_menu.add_checkbutton(
            label="Load automatically",
            command=lambda: gui.handlers.check_preset_load_automatically(logger),
            variable=Globals.is_loading_presets
        )


    def init_connect_menu(self):
        logger.log('Initializing Menu.Connect...', Logtype.init)

        def safe_connect(port):
            logger.log(f'Connecting to serial device at {port}...', Logtype.info)
            ledcomm.connect(port=port)

        def generate_connect_menu_available_ports():
            self.connect_menu_available_ports.delete(0, 'end')
            for port in serial.tools.list_ports.comports():
                if Globals.platform == 'linux' or Globals.platform == 'linux2':
                    if not port.device[5:].startswith('ttyUSB'):
                        continue
                self.connect_menu_available_ports.add_command(
                    label=port.device,
                    command=lambda: safe_connect(port.device)
                )

        self.connect_menu = tk.Menu(self, tearoff=0)
        self.add_cascade(
            label="Connect Settings", menu=self.connect_menu
        )
        self.connect_menu_available_ports = tk.Menu(self.connect_menu, tearoff=0,
                                                    postcommand=generate_connect_menu_available_ports)
        self.connect_menu.add_cascade(
            label='Connect to',
            menu=self.connect_menu_available_ports,
        )

        self.connect_menu.add_command(
            label='Disconnect',
            command=ledcomm.disconnect
        )





if __name__ == "__main__":
    logger.log('Running menu-preview app window...', Logtype.create)
    root = tk.Tk()
    menu = Menu(root)
    root.config(menu=menu)
    logger.log('Running preview app', Logtype.info)
    tk.mainloop()
