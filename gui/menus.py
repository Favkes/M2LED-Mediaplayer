import tkinter as tk

from utils.globals import Globals


class Menu(tk.Menu):
    def __init__(self, app_root: tk.Tk):
        super().__init__(app_root)
        self.is_loading_presets = tk.BooleanVar(value=True)
        self.is_saving_presets = tk.BooleanVar(value=True)
        self.root = app_root

        self.playlist_menu = None
        self.preset_menu = None

        self.init_playlist_menu()
        self.init_preset_menu()


    def init_playlist_menu(self):
        self.playlist_menu = tk.Menu(self, tearoff=0)
        self.add_cascade(
            label='Playlist', menu=self.playlist_menu
        )
        self.playlist_menu.add_command(
            label="New Playlist", command=lambda: print('Creating new playlist...')
        )
        self.playlist_menu.add_command(
            label="Open Playlist", command=lambda: print('Opening playlist...')
        )


    def init_preset_menu(self):
        self.preset_menu = tk.Menu(self, tearoff=0)
        self.add_cascade(
            label="Preset settings", menu=self.preset_menu
        )
        self.preset_menu.add_command(
            label="Save current", command=lambda: print('Saving settings...')
        )
        self.preset_menu.add_checkbutton(
            label="Save automatically", command=lambda: print('Saving automatically switched...'),
            variable=self.is_saving_presets
        )
        self.preset_menu.add_checkbutton(
            label="Load automatically", command=lambda: print('Loading automatically switched'),
            variable=self.is_loading_presets
        )




if __name__ == "__main__":
    root = tk.Tk()
    menu = Menu(root)
    root.config(menu=menu)
    tk.mainloop()
