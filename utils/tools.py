from pydub import AudioSegment
import simpleaudio as sa
import numpy as np
import time
import cv2
from PIL import Image, ImageTk
import uuid

from utils.globals import Globals


#- FUNCTIONS
def smooth_array(arr, kernel_size=5):
    kernel = np.ones(kernel_size) / kernel_size
    return np.convolve(arr, kernel, mode='same')


def format_time(seconds: int) -> str:
    hours = seconds // 3600
    fstring = '%M:%S'
    if hours > 0:
        fstring = '%H:%M:%S'
    return time.strftime(fstring, time.gmtime(seconds))


def get_wav_at_second(container: AudioSegment, second: float) -> sa.WaveObject:
    segment = container[second * 1000:]
    return sa.WaveObject(
        segment.raw_data,
        num_channels=segment.channels,
        bytes_per_sample=segment.sample_width,
        sample_rate=segment.frame_rate
    )


def generate_uuid() -> str:
    return str(uuid.uuid4())



def convert_2_tkinter_image(img: np.ndarray):
    img_rgb = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
    img_pil = Image.fromarray(img_rgb)
    img_tk = ImageTk.PhotoImage(image=img_pil)
    return img_tk


#- GLOBAL ACCESS PROCEDURES
def change_activation_threshold(x) -> None:
    Globals.activation_threshold = x


def change_time_offset(x) -> None:
    Globals.time_offset = -(x - 10) / 10
