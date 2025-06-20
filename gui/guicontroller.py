import tkinter as tk
from tkinter import filedialog
from utils import m2led_functionality, mp3dataextract
import m2led_audioprocessing
from utils.globals import Globals
import time
import threading
from PIL import Image, ImageTk
import pydub


#TODO: Next we've got to successfully remake the m2led_audioprocessing.audio_thread() func
#      to actually be callable from within this script.
#      Then we have to consider the possibility of storing the entire tkinter structure
#      in a separate file tree for better readibility, and containing it's functions in some
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
#       - Further quality optimalizations (communication module, better protocols, etc.)


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

    print('Resetting playback thread...')

    # Scheduling the currently playing thread to die and allowing next one to exist
    Globals.switch_focused_playback_thread()


    cover_image_ref = mp3dataextract.grab_cover(Globals.source_path)
    cover_image_label.config(
        image=cover_image_ref,
        width=300,
        height=300
    )

    # Reinitializing the necessary variables
    Globals.reinit()
    # Rounding up
    Globals.time_progress_max = round(
        mp3dataextract.grab_duration(Globals.source_path) + 0.5
    )
    # Updating GUI elements
    slider_playback.config(
        to=Globals.time_progress_max
    )
    slider_playback.set(Globals.time_progress)
    title_label.config(
        text=mp3dataextract.grab_name(Globals.source_path)
    )

    # Loading raw data from file
    Globals.load_from_path()

    # Creating the new thread and tying it to its life indicator flag
    print('Creating new playback thread...')
    Globals.playback_thread = threading.Thread(
        target=m2led_audioprocessing.audio_thread,
        args=(Globals.focused_playback_thread_index,),
        daemon=True
    )
    Globals.playback_thread.start()
    print('Playback thread started.')


cover_image_ref = mp3dataextract.grab_cover(Globals.source_path)
cover_image_label = tk.Label(
    cover_frame,
    image=cover_image_ref,
    width=300,
    height=300
)


#- TITLE LABEL
title_label = tk.Label(
    main_frame,
    text=mp3dataextract.grab_name(Globals.source_path),
    wraplength=200
)


#- GRAPH CANVAS
def graphdisplay_progressloop():
    global graph_1_image, graph_2_image
    graph_1_image = m2led_functionality.convert_2_tkinter_image(Globals.graph_1)
    graph_2_image = m2led_functionality.convert_2_tkinter_image(Globals.graph_2)
    graph_image_label.config(
        image=graph_1_image,
        width=Globals.graph_x,
        height=Globals.graph_y
    )
    graph_image_postprocessed_label.config(
        image=graph_2_image,
        width=Globals.graph_x,
        height=Globals.graph_y
    )
    root_window.after(10, graphdisplay_progressloop)


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
graph_image_postprocessed_label = tk.Label(
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
def playbacktimeline_sliderfunc(x):
    # Globals.time_progress = float(x)
    label_playback.config(
        text=f"{m2led_functionality.format_time(round(Globals.time_progress))} : "
             f"{m2led_functionality.format_time(Globals.time_progress_max)}"
    )


def playbacktimeline_progressloop():
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
        # print(Globals.time_progress)
    root_window.after(100, playbacktimeline_progressloop)


slider_playback = tk.Scale(
    controls_frame,
    from_=0,
    to=Globals.time_progress_max,
    orient="horizontal",
    showvalue=False,
    length=200,
    command=playbacktimeline_sliderfunc
)

label_playback = tk.Label(
    controls_frame,
    text=f"{m2led_functionality.format_time(round(Globals.time_progress))} : "
         f"{m2led_functionality.format_time(Globals.time_progress_max)}"
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

    def temporalsmoothing_sliderfunc(x):
        Globals.temporal_smoothing = round(int(x)/20, 2)
        temporalsmoothing_value_label.config(
            text=str(Globals.temporal_smoothing)
        )

    def temporalsmoothingsecondary_sliderfunc(x):
        Globals.temporal_smoothing_secondary = round(int(x)/20, 2)
        temporalsmoothingsecondary_value_label.config(
            text=str(Globals.temporal_smoothing_secondary)
        )

    def noisedecay_sliderfunc(x):
        Globals.noise_decay = round(int(x)/20, 2)
        noisedecay_value_label.config(
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
    temporalsmoothing_slider = tk.Scale(
        sliders_frame,
        from_=20,
        to=0,
        orient='vertical',
        showvalue=False,
        length=100,
        command=lambda x: temporalsmoothing_sliderfunc(x)
    )
    temporalsmoothing_slider.set(Globals.temporal_smoothing*20)
    temporalsmoothing_label = tk.Label(
        sliders_frame,
        text="Temporal\nSmoothing"
    )
    temporalsmoothing_value_label = tk.Label(
        sliders_frame,
        text=str(Globals.temporal_smoothing)
    )

    # SECONDARY TEMPORAL SMOOTHING
    temporalsmoothingsecondary_slider = tk.Scale(
        sliders_frame,
        from_=20,
        to=0,
        orient='vertical',
        showvalue=False,
        length=100,
        command=lambda x: temporalsmoothingsecondary_sliderfunc(x)
    )
    temporalsmoothingsecondary_slider.set(Globals.temporal_smoothing_secondary*20)
    temporalsmoothingsecondary_label = tk.Label(
        sliders_frame,
        text="Temporal\nSmoothing (2)"
    )
    temporalsmoothingsecondary_value_label = tk.Label(
        sliders_frame,
        text=str(Globals.temporal_smoothing_secondary)
    )

    # SECONDARY TEMPORAL SMOOTHING
    noisedecay_slider = tk.Scale(
        sliders_frame,
        from_=20,
        to=0,
        orient='vertical',
        showvalue=False,
        length=100,
        command=lambda x: noisedecay_sliderfunc(x)
    )
    noisedecay_slider.set(Globals.noise_decay * 20)
    noisedecay_label = tk.Label(
        sliders_frame,
        text="Noise\nDecay"
    )
    noisedecay_value_label = tk.Label(
        sliders_frame,
        text=str(Globals.noise_decay)
    )

    # ------------------------- INITIALIZATION:
    # ACTIVATION THRESHOLD
    xpadding = 5
    threshold_label.grid(
        column=0, row=0, padx=xpadding
    )
    threshold_slider.grid(
        column=0, row=1, padx=xpadding
    )
    threshold_value_label.grid(
        column=0, row=2, padx=xpadding
    )

    # PRIMARY TEMPORAL SMOOTHING
    temporalsmoothing_label.grid(
        column=1, row=0, padx=xpadding
    )
    temporalsmoothing_slider.grid(
        column=1, row=1, padx=xpadding
    )
    temporalsmoothing_value_label.grid(
        column=1, row=2, padx=xpadding
    )

    # SECONDARY TEMPORAL SMOOTHING
    temporalsmoothingsecondary_label.grid(
        column=2, row=0, padx=xpadding
    )
    temporalsmoothingsecondary_slider.grid(
        column=2, row=1, padx=xpadding
    )
    temporalsmoothingsecondary_value_label.grid(
        column=2, row=2, padx=xpadding
    )

    # SECONDARY TEMPORAL SMOOTHING
    noisedecay_label.grid(
        column=3, row=0, padx=xpadding
    )
    noisedecay_slider.grid(
        column=3, row=1, padx=xpadding
    )
    noisedecay_value_label.grid(
        column=3, row=2, padx=xpadding
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
graph_image_postprocessed_label.grid(
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
ready_playback()
playbacktimeline_progressloop()
graphdisplay_progressloop()
root_window.mainloop()
