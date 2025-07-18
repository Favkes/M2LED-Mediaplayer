import tkinter as tk
from tkinter import filedialog
import time
import threading
from PIL import Image, ImageTk

from utils import tools, data_extract, ledcomm, preset_loader
from utils.globals import Globals
from utils.simple_logs import Logger, Logtype
import audio_processing
from gui.slider import Slider
import gui.handlers


logger = Logger(__name__, 'purple')


class AppStructure:
    ledcomm_thread = None

    def __init__(self):
        logger.log('Connecting to LED strip...', Logtype.info)
        ledcomm.connect()

        logger.log('Initializing components...', Logtype.init)
        self.root_window = tk.Tk()
        self.root_window.title("M2LED Beta-1.0")
        self.root_window.geometry(f"{Globals.win_x}x{Globals.win_y}")
        self.root_window.resizable(False, False)

        self.main_frame = tk.Frame(self.root_window)
        self.main_frame.grid(
            column=0, row=0
        )

        self.cover_frame = tk.Frame(self.main_frame, borderwidth=5)
        self.graph_frame = tk.Frame(self.main_frame, borderwidth=5)
        self.base_util_frame = tk.Frame(self.main_frame)
        self.button_frame = tk.Frame(self.base_util_frame)
        self.controls_frame = tk.Frame(self.base_util_frame)
        self.advanced_frame = tk.Frame(self.main_frame)

        self.cover_image_ref = data_extract.grab_cover(Globals.source_path)
        self.cover_image_label = tk.Label(
            self.cover_frame,
            image=self.cover_image_ref,
            width=300,
            height=300
        )
        #- TITLE LABEL
        self.title_label = tk.Label(
            self.base_util_frame,
            text=data_extract.grab_name(Globals.source_path),
            wraplength=200
        )

        self.graph_1_image = ImageTk.PhotoImage(
            Image.new('RGB', (Globals.graph_x, Globals.graph_y), color='black')
        )
        self.graph_2_image = ImageTk.PhotoImage(
            Image.new('RGB', (Globals.graph_x, Globals.graph_y), color='black')
        )
        self.graph_image_label = tk.Label(
            self.graph_frame,
            image=self.graph_1_image,
            width=Globals.graph_x,
            height=Globals.graph_y
        )
        self.graph_image_post_processed_label = tk.Label(
            self.graph_frame,
            image=self.graph_2_image,
            width=Globals.graph_x,
            height=Globals.graph_y
        )

        self.button_startstop = tk.Button(
            self.button_frame,
            text="Start",
            command=self.startstop_buttonfunc,
            width=18
        )

        # - LOAD BUTTON
        self.button_load = tk.Button(
            self.button_frame,
            text="Open File",
            command=self.loadfile,
            width=18
        )

        self.slider_timedelta = Slider(
            parent_frame=self.controls_frame,
            orient='horizontal',
            from_=0,
            to=40,
            length=200,

            start=Globals.time_offset,
            input_to_global_ratio=-1/20,
            linked_global='time_offset',

            command=lambda x: gui.handlers.timeshift_sliderfunc(self, x),
            showlabel=False,
            value_label_format='Δt = {:.2f} s'
        )

        self.slider_playback = tk.Scale(
            self.controls_frame,
            from_=0,
            to=Globals.time_progress_max,
            orient="horizontal",
            showvalue=False,
            length=200,
            command=self.playback_timeline_sliderfunc
        )

        self.label_playback = tk.Label(
            self.controls_frame,
            text=f"{tools.format_time(round(Globals.time_progress))} : "
                 f"{tools.format_time(Globals.time_progress_max)}"
        )

        self.advanced_button = tk.Button(
            self.controls_frame,
            text="Advanced Settings",
            command=self.advanced_settings_buttonfunc
        )


        # ACTIVATION THRESHOLD
        self.threshold_slider = Slider(
            parent_frame=self.advanced_frame,
            from_=Globals.graph_y,
            to=0,
            length=100,

            start=Globals.activation_threshold,
            linked_global='activation_threshold',
            input_to_global_ratio=1/1,

            command=lambda x: gui.handlers.threshold_sliderfunc(self, x),
            label_text="Activation\nThreshold"
        )

        # PRIMARY TEMPORAL SMOOTHING
        self.temporal_smoothing_slider = Slider(
            parent_frame=self.advanced_frame,
            from_=20,
            to=0,
            length=100,

            start=Globals.temporal_smoothing,
            linked_global='temporal_smoothing',
            input_to_global_ratio=1/20,

            command=lambda x: gui.handlers.temporal_smoothing_sliderfunc(self, x),
            label_text="Temporal\nSmoothing"
        )

        # SECONDARY TEMPORAL SMOOTHING
        self.temporal_smoothing_secondary_slider = Slider(
            parent_frame=self.advanced_frame,
            from_=20,
            to=0,
            length=100,

            start=Globals.temporal_smoothing_secondary,
            linked_global='temporal_smoothing_secondary',
            input_to_global_ratio=1/20,

            command=lambda x: gui.handlers.temporal_smoothing_secondary_sliderfunc(self, x),
            label_text="Temporal\nSmoothing (2)"
        )

        # NOISE DECAY
        self.noise_decay_slider = Slider(
            parent_frame=self.advanced_frame,
            from_=20,
            to=0,
            length=100,

            start=Globals.noise_decay,
            linked_global="noise_decay",
            input_to_global_ratio=1/20,

            command=lambda x: gui.handlers.noise_decay_sliderfunc(self, x),

            label_text="Noise\nDecay"
        )



    def load(self):
        # - OBJECT STRUCTURING
        logger.log('Loading components...', Logtype.info)
        self.cover_frame.grid(
            column=0, row=0)
        self.cover_image_label.grid(
            column=0, row=0)

        self.graph_frame.grid(
            column=1, row=0
        )
        self.graph_image_label.grid(
            column=0, row=0
        )
        self.graph_image_post_processed_label.grid(
            column=0, row=1
        )

        self.base_util_frame.grid(
            column=0, row=1
        )
        self.title_label.grid(
            column=0, row=1)

        self.button_frame.grid(
            column=0, row=2)
        self.button_startstop.grid(
            column=0, row=2)
        self.button_load.grid(
            column=1, row=2)

        self.controls_frame.grid(
            column=0, row=3)
        self.slider_timedelta.grid(
            start_col=0, start_row=2
        )
        self.slider_playback.grid(
            column=0, row=3)
        self.label_playback.grid(
            column=1, row=3)

        self.advanced_button.grid(
            column=0, row=4
        )
        self.advanced_frame.grid(
            column=1, row=1
        )

        x_padding = 5
        # ACTIVATION THRESHOLD
        self.threshold_slider.grid(
            start_col=0, start_row=0, padx=x_padding
        )
        # PRIMARY TEMPORAL SMOOTHING
        self.temporal_smoothing_slider.grid(
            start_col=1, start_row=0, padx=x_padding
        )
        # SECONDARY TEMPORAL SMOOTHING
        self.temporal_smoothing_secondary_slider.grid(
            start_col=2, start_row=0, padx=x_padding
        )
        # NOISE DECAY
        self.noise_decay_slider.grid(
            start_col=3, start_row=0, padx=x_padding
        )

        # Frame borders visualization
        # for child in self.main_frame.winfo_children():
        #     child.config(
        #         bd=2,
        #         bg='green'
        #     )
        # self.main_frame.config(
        #     bd=2,
        #     bg='red'
        # )


    def loadfile(self):
        source_path_ = tk.filedialog.askopenfilename(
            initialdir='./Music',
            title="Select an audio file",
            filetypes=[("MP3 files", "*.mp3"), ("All Files", "*.*")]
        )
        if source_path_ == "":
            return
        Globals.source_path = source_path_

        logger.log('Loading preset settings...', code=Logtype.info)

        mp3_id = data_extract.check_uuid(Globals.source_path)
        if mp3_id is None:
            mp3_id = tools.generate_uuid()
        Globals.uuid = mp3_id
        data_extract.add_uuid(Globals.source_path, Globals.uuid)

        # Loading settings from the file into Globals
        preset_loader.load_settings(default=False)

        logger.log('Loading preset settings complete.', code=Logtype.info)

        self.startstop_buttonfunc(force_pause=True)
        self.ready_playback()


    def ledcomm_init(self):
        self.ledcomm_thread = threading.Thread(target=ledcomm.arduino_comm_thread_func)


    def ready_playback(self):
        logger.log('Resetting playback thread...', Logtype.info)

        # Scheduling the currently playing thread to die and allowing next one to exist
        Globals.switch_focused_playback_thread()

        self.cover_image_ref = data_extract.grab_cover(Globals.source_path)
        self.cover_image_label.config(
            image=self.cover_image_ref,
            width=300,
            height=300
        )

        # Reinitializing the necessary variables
        Globals.reinit()
        # Rounding up
        Globals.time_progress_max = round(
            data_extract.grab_duration(Globals.source_path) + 0.5
        )
        # Updating GUI elements
        self.slider_playback.config(
            to=Globals.time_progress_max
        )
        self.slider_playback.set(Globals.time_progress)
        self.title_label.config(
            text=data_extract.grab_name(Globals.source_path)
        )

        # Loading raw data from file
        Globals.load_from_path()

        # Creating the new thread and tying it to its life indicator flag
        logger.log('Creating new playback thread...', Logtype.create)
        Globals.playback_thread = threading.Thread(
            target=audio_processing.audio_thread,
            args=(Globals.focused_playback_thread_index,),
            daemon=True
        )
        Globals.playback_thread.start()
        if not self.ledcomm_thread.is_alive():
            self.ledcomm_thread.start()
        time.sleep(0.001)
        logger.log('Playback thread started.', Logtype.info)


    def graph_display_asyncloop(self):
        self.graph_1_image = tools.convert_2_tkinter_image(Globals.graph_1)
        self.graph_2_image = tools.convert_2_tkinter_image(Globals.graph_2)
        self.graph_image_label.config(
            image=self.graph_1_image,
            width=Globals.graph_x,
            height=Globals.graph_y
        )
        self.graph_image_post_processed_label.config(
            image=self.graph_2_image,
            width=Globals.graph_x,
            height=Globals.graph_y
        )
        self.root_window.after(10, self.graph_display_asyncloop)


    def startstop_buttonfunc(self, force_pause: bool = False):
        # Pausing
        if not Globals.is_paused or force_pause:
            Globals.is_paused = True
            Globals.play_obj.pause()
            Globals.time_paused_start = time.time()
        # Resuming
        else:
            Globals.is_paused = False
            Globals.play_obj.resume()
            Globals.time_paused_total += time.time() - Globals.time_paused_start

        self.button_startstop.config(text="Start" if Globals.is_paused else "Stop")

        # If done playing and pressed -> play again
        if not Globals.is_unfinished:
            Globals.is_unfinished = True
            self.ready_playback()


    def playback_timeline_sliderfunc(self, x):
        # Globals.time_progress = float(x)
        self.label_playback.config(
            text=f"{tools.format_time(round(Globals.time_progress))} : "
                 f"{tools.format_time(Globals.time_progress_max)}"
        )


    def playback_timeline_asyncloop(self):
        current = self.slider_playback.get()

        # EOF:
        if Globals.is_unfinished and current >= Globals.time_progress_max:
            Globals.is_unfinished = False
            Globals.is_paused = True
            self.button_startstop.config(text="Start" if Globals.is_paused else "Stop")

        # Playing:
        if not Globals.is_paused and Globals.is_unfinished:
            # slider_playback.set(current + 1)
            Globals.calculate_time_progress()
            self.slider_playback.set(Globals.time_progress)
        self.root_window.after(100, self.playback_timeline_asyncloop)


    def advanced_settings_buttonfunc(self):
        # TODO: reassign to sth actually useful
        settings_window = tk.Toplevel(self.root_window)
        settings_window.title('Advanced Settings')
        settings_window.geometry('300x200')

        sliders_frame = tk.Frame(settings_window)
        sliders_frame.pack()

        # CLOSE BUTTON
        close_button = tk.Button(
            settings_window,
            text = "Close",
            command=settings_window.destroy
        )
        close_button.pack(pady=10)


    def _on_exit(self):
        logger.log("GUI closed by user, scheduling all threads to die.", Logtype.kill)
        Globals.killall()
        self.root_window.destroy()

    def run_app(self):
        logger.log('Initializing necessary threads...', Logtype.init)
        self.ready_playback()
        self.playback_timeline_asyncloop()
        self.graph_display_asyncloop()

        logger.log('Setup successful. Opening GUI.', Logtype.info)
        self.root_window.protocol("WM_DELETE_WINDOW", self._on_exit)
        self.root_window.mainloop()
