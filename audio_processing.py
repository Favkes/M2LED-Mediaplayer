import numpy as np
import time
import cv2

from utils.globals import Globals
from utils import functionality


def audio_thread(thread_index: int):
    print('[Playback Daemon] Creating playback of index', thread_index)
    # Loading the play_buffer object
    Globals.play_obj = functionality.get_wav_at_second(
        Globals.song_container,
        Globals.time_progress
    ).play()

    Globals.time_start = time.time()

    # If player paused, pause the thread immediately
    if Globals.is_paused:
        Globals.play_obj.pause()

    samples = np.array(Globals.song_container.get_array_of_samples())
    if Globals.song_container.channels == 2:
        samples = samples.reshape((-1, 2))
        samples = samples.mean(axis=1)
    # normalize
    samples = samples / np.max(np.abs(samples))

    ascending_arr = np.array([i for i in range(Globals.graph_x - Globals.bass_cut)], dtype=np.uint16)
    previous_frame = np.zeros(Globals.samples_per_frame // 2 + 1, np.uint8)
    previous_frame_threshold = np.zeros(Globals.graph_x - Globals.bass_cut, np.uint8)
    noise_floor = np.zeros_like(previous_frame)

    img = np.zeros((Globals.graph_y, Globals.graph_x, 3), np.uint8)
    img_threshold = np.zeros_like(img)

    graphdisplayvariable = 0
    while Globals.play_obj.is_playing() or not Globals.is_unfinished:
        # Clearing the images
        img[:]           = 0
        img_threshold[:] = 0

        cv2.line(
            img,
            (0, Globals.graph_y - Globals.activation_threshold),
            (Globals.graph_x, Globals.graph_y - Globals.activation_threshold),
            (255, 255, 0),
            1
        )

        elapsed_sec = max(Globals.time_progress - Globals.time_offset, 0)
        current_sample = int(elapsed_sec * Globals.rate)

        if current_sample + Globals.samples_per_frame < len(samples):
            chunk = samples[current_sample: current_sample + Globals.samples_per_frame]
            mid = Globals.graph_y // 2
            scaled = (chunk * (mid - 10)).astype(np.int32) + mid

            mono_data = scaled * np.hanning(len(scaled))
            spectrum_full = np.abs(np.fft.rfft(mono_data))
            freqs = np.fft.rfftfreq(len(mono_data), d=1.0 / Globals.rate)
            spectrum_full = spectrum_full * np.sqrt(freqs)

            # half_len = len(spectrum_full) // 2
            # spectrum_quarter = spectrum_full[:half_len]

            time_smoothed = Globals.temporal_smoothing * previous_frame + spectrum_full
            previous_frame = time_smoothed

            noise_floor = Globals.noise_decay * noise_floor + (1 - Globals.noise_decay) * time_smoothed
            cleaned = time_smoothed - noise_floor
            cleaned[cleaned < 0] = 0

            # freqs = np.interp(
            #     np.linspace(0, len(cleaned), winX - bass_cut),
            #     np.arange(len(cleaned)),
            #     cleaned
            # )

            out_arr = cleaned[:Globals.graph_x - Globals.bass_cut]
            out_arr *= 2
            out_arr = m2led_functionality.smooth_array(out_arr, kernel_size=7)

            window_scaling_ratio = Globals.graph_y / (len(out_arr) * 10000)
            out_arr *= window_scaling_ratio
            out_arr *= ascending_arr

            out_arr_threshold = out_arr.copy()
            out_arr_threshold[out_arr < Globals.activation_threshold] = Globals.activation_threshold
            out_arr_threshold -= Globals.activation_threshold


            out_arr_threshold = Globals.temporal_smoothing_secondary * previous_frame_threshold + out_arr_threshold
            previous_frame_threshold = out_arr_threshold
            Globals.out_arr = out_arr_threshold

            # step = max(1, len(out_arr) // winX)
            previous = (Globals.bass_cut, Globals.graph_y)
            previous_ = (Globals.bass_cut, Globals.graph_y)
            for i, val in enumerate(out_arr):
                x = Globals.bass_cut + i
                y = Globals.graph_y - round(val)
                current = (x, y)
                cv2.line(img, previous, current, (0, 255, 0), 1)
                previous = current

                y_ = Globals.graph_y - round(out_arr_threshold[i])
                current_ = (x, y_)
                cv2.line(img_threshold, previous_, current_, (0, 255, 255), 1)
                previous_ = current_

            Globals.graph_1 = img.copy()
            Globals.graph_2 = img_threshold.copy()

        if cv2.waitKey(10) == 27 or not Globals.is_playback_thread_alive[thread_index]:
            print('[Playback Daemon] Killing playback of index', thread_index)
            Globals.play_obj.stop()
            break


if __name__ == "__main__":
    audio_thread()
