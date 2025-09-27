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
from utils.simple_logs import Logger, Logtype
import threading


logger = Logger(__name__, 'yellow')


# TODO:  Add a system of simple table presets, sent to the board at the
#       moment of setting the "theme". Then only broadcast singular values
#       that the arduino will map onto actual RGB data.
#       Kind of like: {1 -> (255, 0, 0), 2 -> (255, 5, 0), ...}


NUM_LEDS: int   = 185
PORT: str       = "COM3"
BANDRATE: int   = 115200
TIMEOUT: int    = 1
ser: serial.Serial


def resize_strip(num_leds: int = 185):
    global NUM_LEDS
    NUM_LEDS = num_leds


def connect(port: str = PORT, bandrate: int = BANDRATE, timeout: int = TIMEOUT):
    global PORT, BANDRATE, TIMEOUT, ser
    PORT = port
    BANDRATE = bandrate
    TIMEOUT = timeout
    logger.log('Initializing connection with the LED strip...', Logtype.init)
    ser = serial.Serial(port, bandrate, timeout=timeout)


def disconnect():
    ser.close()
    with SERIAL_LOCK:


def set_led(index, r, g, b):
    message = f"{index},{r},{g},{b}\n"
    # print(message)
    ser.write(message.encode())
    # message = [index, r, g, b]
    # ser.write(bytes(message))
    with SERIAL_LOCK:


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
    logger.log('Waiting for play_obj initialization to complete...', Logtype.info)
    while Globals.play_obj is None:
        time.sleep(0.1)
    logger.log('play_obj connected successfully.', Logtype.info)
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
    logger.log('Thread killed and disconnected.', Logtype.kill)


if __name__ == "__main__":
    logger.log(f"Resetting the strip at {PORT}.", Logtype.info)
    connect()
