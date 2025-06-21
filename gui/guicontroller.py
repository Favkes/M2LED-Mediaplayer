import tkinter as tk
from tkinter import filedialog
import time
import threading
from PIL import Image, ImageTk

from utils import functionality, data_extract
from utils.globals import Globals
import audio_processing
from utils import ledcomm


#TODO: Now we have to consider the possibility of storing the entire tkinter structure
#      in a separate file tree for better readability, and containing it's functions in some
#      cleaner way as well.
#      Then we just have to ensure that the graphs we've made are working nicely and
#      accordingly, and theoretically all is done.
#      Further improvements include:
#       - Segmentation of the buffer for quicker loading and lighter memory load
#       - Automated parameter tuning (thresholds, smoothing, etc.) as an option
#       - Playlist support
#       - Downloading the files automatically from youtube
#         (either Selenium and manual youtube choosing (maybe a browser plugin?)
#          or requests and command support)
#       - Optimized project structure, docs, Github repo
#       - Further quality optimizations (communication module, better protocols, etc.)


_greentext = '\x1b[1;32;40m'
_bluetext = '\x1b[1;34;40m'
_defaulttext = '\x1b[0m'


print(_greentext + '[Main] Connecting to LED strip...' + _defaulttext)
ledcomm.connect()

print(_greentext + '[Main] Initializing components...' + _defaulttext)
root_window = tk.Tk()
root_window.title("M2LED alpha-1.1")
root_window.geometry(f"{Globals.win_x}x{Globals.win_y}")
root_window.resizable(False, False)

main_frame = tk.Frame(root_window)
main_frame.grid(
    column=0, row=0
)

cover_frame = tk.Frame(main_frame, borderwidth=5)
graph_frame = tk.Frame(main_frame, borderwidth=5)
button_frame = tk.Frame(main_frame)
controls_frame = tk.Frame(main_frame)

# Starting the LED broadcasting thread
ledcomm_thread = threading.Thread(target=ledcomm.arduino_comm_thread_func)


#- COVER DISPLAY
def loadfile():
    global cover_image_ref
    source_path_ = tk.filedialog.askopenfilename(
        initialdir='./Music',
        title="Select an audio file",
        filetypes=[("MP3 files", "*.mp3"), ("All Files", "*.*")]
    )
    if source_path_ == "":
        return
    Globals.source_path = source_path_

    startstop_buttonfunc(force_pause=True)
    ready_playback()


def ready_playback():
    global cover_image_ref

    print(_greentext + '[Main] Resetting playback thread...' + _defaulttext)

    # Scheduling the currently playing thread to die and allowing next one to exist
    Globals.switch_focused_playback_thread()


    cover_image_ref = data_extract.grab_cover(Globals.source_path)
    cover_image_label.config(
        image=cover_image_ref,
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
    slider_playback.config(
        to=Globals.time_progress_max
    )
    slider_playback.set(Globals.time_progress)
    title_label.config(
        text=data_extract.grab_name(Globals.source_path)
    )

    # Loading raw data from file
    Globals.load_from_path()

    # Creating the new thread and tying it to its life indicator flag
    print(_greentext +  '[Main] Creating new playback thread...' + _defaulttext)
    Globals.playback_thread = threading.Thread(
        target=audio_processing.audio_thread,
        args=(Globals.focused_playback_thread_index,),
        daemon=True
    )
    Globals.playback_thread.start()
    if not ledcomm_thread.is_alive():
        ledcomm_thread.start()
    print(_greentext + '[Main] Playback thread started.' + _defaulttext)


cover_image_ref = data_extract.grab_cover(Globals.source_path)
cover_image_label = tk.Label(
    cover_frame,
    image=cover_image_ref,
    width=300,
    height=300
)


#- TITLE LABEL
title_label = tk.Label(
    main_frame,
    text=data_extract.grab_name(Globals.source_path),
    wraplength=200
)


#- GRAPH CANVAS
def graph_display_asyncloop():
    global graph_1_image, graph_2_image
    graph_1_image = functionality.convert_2_tkinter_image(Globals.graph_1)
    graph_2_image = functionality.convert_2_tkinter_image(Globals.graph_2)
    graph_image_label.config(
        image=graph_1_image,
        width=Globals.graph_x,
        height=Globals.graph_y
    )
    graph_image_post_processed_label.config(
        image=graph_2_image,
        width=Globals.graph_x,
        height=Globals.graph_y
    )
    root_window.after(10, graph_display_asyncloop)


graph_1_image = ImageTk.PhotoImage(
    Image.new('RGB', (Globals.graph_x, Globals.graph_y), color='black')
)
graph_2_image = ImageTk.PhotoImage(
    Image.new('RGB', (Globals.graph_x, Globals.graph_y), color='black')
)
graph_image_label = tk.Label(
    graph_frame,
    image=graph_1_image,
    width=Globals.graph_x,
    height=Globals.graph_y
)
graph_image_post_processed_label = tk.Label(
    graph_frame,
    image=graph_2_image,
    width=Globals.graph_x,
    height=Globals.graph_y
)


#- STARTSTOP BUTTON
def startstop_buttonfunc(force_pause: bool = False):
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

    button_startstop.config(text="Start" if Globals.is_paused else "Stop")

    # If done playing and pressed -> play again
    if not Globals.is_unfinished:
        Globals.is_unfinished = True
        ready_playback()


button_startstop = tk.Button(
    button_frame,
    text="Start",
    command=startstop_buttonfunc,
    width=18
)


#- LOAD BUTTON
button_load = tk.Button(
    button_frame,
    text="Open File",
    command=loadfile,
    width=18
)


#- TIME SHIFT SLIDER
def timeshift_sliderfunc(x):
    Globals.time_offset = -round(int(x) / 20, 2)
    label_timedelta.config(
        text=f"Δt = {-Globals.time_offset:.2f} s"
    )


slider_timedelta = tk.Scale(
    controls_frame,
    from_=0,
    to=30,
    orient="horizontal",
    showvalue=False,
    length=200,
    command=timeshift_sliderfunc
)
slider_timedelta.set(-Globals.time_offset * 20)

label_timedelta = tk.Label(
    controls_frame,
    text=f"Δt = {-Globals.time_offset:.2f} s"
)


#- PLAYBACK TIMELINE
def playback_timeline_sliderfunc(x):
    # Globals.time_progress = float(x)
    label_playback.config(
        text=f"{functionality.format_time(round(Globals.time_progress))} : "
             f"{functionality.format_time(Globals.time_progress_max)}"
    )


def playback_timeline_asyncloop():
    current = slider_playback.get()

    # EOF:
    if Globals.is_unfinished and current >= Globals.time_progress_max:
        Globals.is_unfinished = False
        Globals.is_paused = True
        button_startstop.config(text="Start" if Globals.is_paused else "Stop")

    # Playing:
    if not Globals.is_paused and Globals.is_unfinished:
        # slider_playback.set(current + 1)
        Globals.calculate_time_progress()
        slider_playback.set(Globals.time_progress)
    root_window.after(100, playback_timeline_asyncloop)


slider_playback = tk.Scale(
    controls_frame,
    from_=0,
    to=Globals.time_progress_max,
    orient="horizontal",
    showvalue=False,
    length=200,
    command=playback_timeline_sliderfunc
)

label_playback = tk.Label(
    controls_frame,
    text=f"{functionality.format_time(round(Globals.time_progress))} : "
         f"{functionality.format_time(Globals.time_progress_max)}"
)


#- ADVANCED SETTINGS WINDOW
def advanced_settings_buttonfunc():
    settings_window = tk.Toplevel(root_window)
    settings_window.title('Advanced Settings')
    settings_window.geometry('300x200')

    sliders_frame = tk.Frame(settings_window)
    sliders_frame.pack()

    # FUNCTIONS
    def threshold_sliderfunc(x):
        Globals.activation_threshold = int(x)
        threshold_value_label.config(
            text=str(x)
        )

    def temporal_smoothing_sliderfunc(x):
        Globals.temporal_smoothing = round(int(x)/20, 2)
        temporal_smoothing_value_label.config(
            text=str(Globals.temporal_smoothing)
        )

    def temporal_smoothing_secondary_sliderfunc(x):
        Globals.temporal_smoothing_secondary = round(int(x)/20, 2)
        temporal_smoothing_secondary_value_label.config(
            text=str(Globals.temporal_smoothing_secondary)
        )

    def noise_decay_sliderfunc(x):
        Globals.noise_decay = round(int(x)/20, 2)
        noise_decay_value_label.config(
            text=str(Globals.noise_decay)
        )


    # ACTIVATION THRESHOLD
    threshold_slider = tk.Scale(
        sliders_frame,
        from_=Globals.graph_y,
        to=0,
        orient='vertical',
        showvalue=False,
        length=100,
        command=lambda x: threshold_sliderfunc(x),
    )
    threshold_slider.set(Globals.activation_threshold)
    threshold_label = tk.Label(
        sliders_frame,
        text="Activation\nThreshold"
    )
    threshold_value_label = tk.Label(
        sliders_frame,
        text=str(Globals.activation_threshold)
    )

    # PRIMARY TEMPORAL SMOOTHING
    temporal_smoothing_slider = tk.Scale(
        sliders_frame,
        from_=20,
        to=0,
        orient='vertical',
        showvalue=False,
        length=100,
        command=lambda x: temporal_smoothing_sliderfunc(x)
    )
    temporal_smoothing_slider.set(Globals.temporal_smoothing*20)
    temporal_smoothing_label = tk.Label(
        sliders_frame,
        text="Temporal\nSmoothing"
    )
    temporal_smoothing_value_label = tk.Label(
        sliders_frame,
        text=str(Globals.temporal_smoothing)
    )

    # SECONDARY TEMPORAL SMOOTHING
    temporal_smoothing_secondary_slider = tk.Scale(
        sliders_frame,
        from_=20,
        to=0,
        orient='vertical',
        showvalue=False,
        length=100,
        command=lambda x: temporal_smoothing_secondary_sliderfunc(x)
    )
    temporal_smoothing_secondary_slider.set(Globals.temporal_smoothing_secondary*20)
    temporal_smoothing_secondary_label = tk.Label(
        sliders_frame,
        text="Temporal\nSmoothing (2)"
    )
    temporal_smoothing_secondary_value_label = tk.Label(
        sliders_frame,
        text=str(Globals.temporal_smoothing_secondary)
    )

    # SECONDARY TEMPORAL SMOOTHING
    noise_decay_slider = tk.Scale(
        sliders_frame,
        from_=20,
        to=0,
        orient='vertical',
        showvalue=False,
        length=100,
        command=lambda x: noise_decay_sliderfunc(x)
    )
    noise_decay_slider.set(Globals.noise_decay * 20)
    noise_decay_label = tk.Label(
        sliders_frame,
        text="Noise\nDecay"
    )
    noise_decay_value_label = tk.Label(
        sliders_frame,
        text=str(Globals.noise_decay)
    )

    # ------------------------- INITIALIZATION:
    # ACTIVATION THRESHOLD
    x_padding = 5
    threshold_label.grid(
        column=0, row=0, padx=x_padding
    )
    threshold_slider.grid(
        column=0, row=1, padx=x_padding
    )
    threshold_value_label.grid(
        column=0, row=2, padx=x_padding
    )

    # PRIMARY TEMPORAL SMOOTHING
    temporal_smoothing_label.grid(
        column=1, row=0, padx=x_padding
    )
    temporal_smoothing_slider.grid(
        column=1, row=1, padx=x_padding
    )
    temporal_smoothing_value_label.grid(
        column=1, row=2, padx=x_padding
    )

    # SECONDARY TEMPORAL SMOOTHING
    temporal_smoothing_secondary_label.grid(
        column=2, row=0, padx=x_padding
    )
    temporal_smoothing_secondary_slider.grid(
        column=2, row=1, padx=x_padding
    )
    temporal_smoothing_secondary_value_label.grid(
        column=2, row=2, padx=x_padding
    )

    # SECONDARY TEMPORAL SMOOTHING
    noise_decay_label.grid(
        column=3, row=0, padx=x_padding
    )
    noise_decay_slider.grid(
        column=3, row=1, padx=x_padding
    )
    noise_decay_value_label.grid(
        column=3, row=2, padx=x_padding
    )

    # CLOSE BUTTON
    close_button = tk.Button(
        settings_window,
        text = "Close",
        command=settings_window.destroy
    )
    close_button.pack(pady=10)


advanced_button = tk.Button(
    controls_frame,
    text="Advanced Settings",
    command=advanced_settings_buttonfunc
)


#- OBJECT STRUCTURING
print(_greentext + '[Main] Loading components...' + _defaulttext)
cover_frame.grid(
    column=0, row=0)
cover_image_label.grid(
    column=0, row=0)
title_label.grid(
    column=0, row=1)

graph_frame.grid(
    column=1, row=0
)
graph_image_label.grid(
    column=0, row=0
)
graph_image_post_processed_label.grid(
    column=0, row=1
)

button_frame.grid(
    column=0, row=2)
button_startstop.grid(
    column=0, row=2)
button_load.grid(
    column=1, row=2)

controls_frame.grid(
    column=0, row=3)
slider_timedelta.grid(
    column=0, row=2)
label_timedelta.grid(
    column=1, row=2)
slider_playback.grid(
    column=0, row=3)
label_playback.grid(
    column=1, row=3)

advanced_button.grid(
    column=0, row=4
)

# APP INITIALIZATION
print(_greentext + '[Main] Initializing necessary threads...' + _defaulttext)
ready_playback()
playback_timeline_asyncloop()
graph_display_asyncloop()


def on_exit():
    print(_greentext + "[Main] GUI closed by user, scheduling all threads to die." + _defaulttext)
    Globals.killall()
    root_window.destroy()


print(_greentext + '[Main] Setup successful. Opening GUI.' + _defaulttext)
root_window.protocol("WM_DELETE_WINDOW", on_exit)
root_window.mainloop()
