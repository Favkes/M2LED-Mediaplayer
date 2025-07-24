import tkinter as tk

from utils.globals import Globals
from utils.simple_logs import Logger, Logtype
import gui.handlers


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

        self.init_playlist_menu()
        self.init_preset_menu()


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




if __name__ == "__main__":
    logger.log('Running menu-preview app window...', Logtype.create)
    root = tk.Tk()
    menu = Menu(root)
    root.config(menu=menu)
    logger.log('Running preview app', Logtype.info)
    tk.mainloop()
