"""
Simple module made to allow communication between a python script and
an arduino controlling an addressable LED-strip over a USB-cable.
Allows for control over individual LEDs as well as broadcasting array values
and mapping them onto the strip automatically (yet to get optimized).
"""

import serial
import numpy as np
from utils.globals import Globals
import time


NUM_LEDS: int   = 185
PORT: str       = "COM3"
BANDRATE: int   = 115200
TIMEOUT: int    = 1
ser: serial.Serial


_greentext = '\x1b[1;32;40m'
_bluetext = '\x1b[1;34;40m'
_defaulttext = '\x1b[0m'


def resize_strip(num_leds: int = 185):
    global NUM_LEDS
    NUM_LEDS = num_leds


def connect(port: str = PORT, bandrate: int = BANDRATE, timeout: int = TIMEOUT):
    global PORT, BANDRATE, TIMEOUT, ser
    PORT = port
    BANDRATE = bandrate
    TIMEOUT = timeout
    ser = serial.Serial(port, bandrate, timeout=timeout)


def disconnect():
    ser.close()


def set_led(index, r, g, b):
    message = f"{index},{r},{g},{b}\n"
    # print(message)
    ser.write(message.encode())
    # message = [index, r, g, b]
    # ser.write(bytes(message))


def read_serial():
    while ser.in_waiting > 0:
        line = ser.readline().decode('utf-8').strip()
        print('Arduino says:', line)


def broadcast_indices(array: list | np.ndarray):
    # repeating the command to ensure it comes through:
    for _ in range(1):
        set_led(255, 0, 0, 0)

    # sending color data:
    for led in range(len(array)):
        tmp = round(array[led])
        if tmp:
            set_led(tmp, 10, 10, 10)

    set_led(254, 0, 0, 0)  # show() command


def broadcast_colours(array: list | np.ndarray):
    # repeating the command to ensure it comes through:
    for _ in range(1):
        set_led(255, 0, 0, 0)

    # sending color data:
    for led in range(len(array)):
        index, (r, g, b) = array[led]
        set_led(index, r, g, b)
        # set_led(index, r//30 * 10, g//30 * 10, b//30 * 10)

    set_led(254, 0, 0, 0)  # show() command


def arduino_comm_thread_func():
    print(_bluetext + '[LedComm Thread] Waiting for play_obj initialization to complete...' + _defaulttext)
    while Globals.play_obj is None:
        time.sleep(0.1)
    print(_bluetext + '[LedComm Thread] play_obj connected successfully.' + _defaulttext)
    while not Globals.should_everything_die:
        time.sleep(0.1)
        while Globals.is_unfinished and not Globals.should_everything_die:
            original_len = len(Globals.out_arr)
            new_indices = np.linspace(0, Globals.graph_x, 185)
            xp = np.arange(original_len)
            resampled_array = np.interp(new_indices, xp, Globals.out_arr)

            instructions_array = []
            for i, val in enumerate(resampled_array):
                val = int(int(val)**.5)
                if val == 0:
                    continue
                leddata = (
                    i,
                    (val, val//2, 0)
                )
                instructions_array.append(leddata)
            # print('Sending:', instructions_array)
            broadcast_colours(instructions_array)
            # time.sleep(0.03)
    disconnect()
    print(_bluetext + '[LedComm Thread] Thread killed and disconnected.' + _defaulttext)


if __name__ == "__main__":
    print(f"Resetting the strip at {PORT}.")
    connect()
