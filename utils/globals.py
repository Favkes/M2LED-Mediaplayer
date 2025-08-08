import time
import tkinter as tk

import numpy as np
import pydub
import simpleaudio as sa

from utils import data_extract


# TODO: Add a preset file system to be able to save presets for
#       each mp3, and then use them automatically (or not ofc)


source_path:       str                  = "./Music/dummy.mp3"
time_progress_max: int                  = round(data_extract.grab_duration(source_path) + 0.5)
song_container:    pydub.AudioSegment   = pydub.AudioSegment.from_mp3(source_path)
fps:               int                  = 30
samples_per_frame: int                  = int(song_container.frame_rate / fps)


class Globals:
    activation_threshold                = 0
    bass_cut                            = 0                           # Low-cut to ensure some bass noise is left out
    fps                                 = fps

    graph_x                             = 300                         # Width of the graph canvas
    graph_y                             = 150                         # Height of the graph canvas
    win_x                               = 627                         # Width of the GUI window
    win_y                               = 500                         # Height of the GUI window

    is_paused                           = True                        # When paused with button
    is_unfinished                       = True                        # Only at file load

    should_everything_die               = False                       # Flag to kill all threads for clean exit.

    is_playback_thread_alive            = [True, False]               # Used to safely close playback threads
    focused_playback_thread_index       = 0                           # Index of live playback thread (currently)

    time_start                          = -1
    time_progress                       = 0                           # Total elapsed time running
    time_paused_start                   = -1                          # Used to keep track of pause length
    time_paused_total                   = 0                           # Used to compensate for the paused time
    time_progress_max                   = time_progress_max           # Total length of the file (time)
    time_offset                         = -0.65                       # Time in [s] that the FFT is ahead of playback

    play_obj: sa.play_buffer            = None                        # Music playing object
    rate                                = song_container.frame_rate
    samples_per_frame                   = samples_per_frame
    source_path                         = source_path                 # MP3 file path
    song_container                      = song_container              # Raw data from MP3 file

    uuid: str                           = None

    temporal_smoothing                  = 0.9                         # Main processing
    temporal_smoothing_secondary        = 0.7                         # Post-processing
    noise_decay                         = 0.95

    graph_1: np.ndarray                 = None
    graph_2: np.ndarray                 = None
    out_arr: np.ndarray                 = None

    is_loading_presets: tk.BooleanVar   = None
    is_saving_presets: tk.BooleanVar    = None


    @classmethod
    def reinit(cls) -> None:
        """
        Reinitializes the time variables and runtime flags
        for a clean start of a new playback thread.
        :return: None
        """
        cls.is_paused         = True
        cls.is_unfinished     = True

        cls.time_start        = time.time()
        cls.time_progress     = 0
        cls.time_paused_start = time.time()
        cls.time_paused_total = 0

        cls.graph_1 = np.zeros((cls.graph_y, cls.graph_x, 3), np.uint8)
        cls.graph_2 = np.zeros_like(cls.graph_1)
        cls.out_arr = np.zeros(cls.win_x - cls.bass_cut)

    @classmethod
    def load_from_path(cls):
        cls.time_progress_max:  int                 = round(data_extract.grab_duration(cls.source_path) + 0.5)
        cls.song_container:     pydub.AudioSegment  = pydub.AudioSegment.from_mp3(cls.source_path)
        cls.samples_per_frame:  int                 = int(cls.song_container.frame_rate / cls.fps)

    @classmethod
    def switch_focused_playback_thread(cls) -> None:
        """
        Schedules the currently running playback thread to kill itself,
        shifting focus to the second thread slot for cleaner thread management.
        :return: None
        """
        cls.is_playback_thread_alive[cls.focused_playback_thread_index] = False
        cls.focused_playback_thread_index = (cls.focused_playback_thread_index + 1) % 2
        cls.is_playback_thread_alive[cls.focused_playback_thread_index] = True

    @classmethod
    def calculate_time_progress(cls) -> None:
        """
        Recalculates the .time_progress param at present
        (adjusting for total pause-time and CPU drift)
        :return: None
        """
        cls.time_progress = time.time() - cls.time_start - cls.time_paused_total

    @classmethod
    def killall(cls) -> None:
        cls.should_everything_die = True
        cls.is_unfinished = False
        cls.is_playback_thread_alive[:] = [False] * len(cls.is_playback_thread_alive)



del fps
del time_progress_max
del samples_per_frame
del source_path
del song_container


if __name__ == "__main__":
    print('\x1b[0;34;40mGlobals initialized. And nothing else LOL.\x1b[0m')
