"""
Simple module made to allow communication between a python script and
an arduino controlling an addressable LED-strip over a USB-cable.
Allows for control over individual LEDs as well as broadcasting array values
and mapping them onto the strip automatically (yet to get optimized).
"""

import serial
import serial.tools.list_ports
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


NUM_LEDS: int       = 185
PORT: str | None    = None
BAUDRATE: int       = 115200
TIMEOUT: int        = 1
SER: serial.Serial | None  = None
SERIAL_LOCK         = threading.Lock()


def is_connected() -> bool:
    return SER is not None and SER.is_open


def resize_strip(num_leds: int = 185):
    global NUM_LEDS
    NUM_LEDS = num_leds


def get_first_device_available():
    return serial.tools.list_ports.comports()[0].device


def wait_and_connect(port: str, baudrate = 115200, timeout: int = 1, max_wait: float | int = 1):
    start_time = time.time()
    while time.time() - start_time < max_wait:
        try:
            ser = serial.Serial(port, baudrate, timeout=timeout)
            return ser
        except (OSError, serial.SerialException):
            time.sleep(0.1)
    raise TimeoutError(f"Port {port} not available after {max_wait}s")


def connect(port: str | None = PORT, baudrate: int = BAUDRATE, timeout: int = TIMEOUT):
    global PORT, BAUDRATE, TIMEOUT, SER

    if port is None:
        try:
            port = get_first_device_available()
        except IndexError:
            PORT = None
            logger.log('No COM port available.', Logtype.info)

    PORT = port
    BAUDRATE = baudrate
    TIMEOUT = timeout

    if is_connected():
        disconnect()

    logger.log('Initializing connection with the LED strip...', Logtype.init)

    try:
        SER = wait_and_connect(port, baudrate, timeout=timeout, max_wait=2.0)
        logger.log(f'Connection to LED strip initialized on port {port}.', Logtype.info)
    except TimeoutError as e:
        logger.log(f'Failed to connect: {e}', Logtype.warning)
    except serial.SerialException as e:
        # logger.log('Failed to connect with the LED strip, '
        #            'the application will boot without a serial output connection.\n'+str(e), Logtype.warning)
        logger.log(f'Serial exception: {e}', Logtype.warning)


def disconnect():
    global SER

    with SERIAL_LOCK:
        if not is_connected():
            # logger.log('Attempted to kill the serial output instance even though marked disconnected.',
            #            Logtype.warning)
            return
        else:
            assert SER is not None
            logger.log('Killing current serial output instance...', Logtype.kill)
            SER.close()
            SER = None


def set_led(index, r, g, b):
    with SERIAL_LOCK:
        if not is_connected():
            return

        message = f"{index},{r},{g},{b}\n"

        try:
            SER.write(message.encode())
        except (OSError, serial.SerialException) as e:
            logger.log(f'Serial write failed: {e}', Logtype.warning)
            disconnect()


def read_serial():
    while SER.in_waiting > 0:
        line = SER.readline().decode('utf-8').strip()
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
    if not is_connected():
        return

    try:
        # repeating the command to ensure it comes through:
        for _ in range(1):
            set_led(255, 0, 0, 0)

        # sending color data:
        for led in range(len(array)):
            index, (r, g, b) = array[led]
            set_led(index, r, g, b)
            # set_led(index, r//30 * 10, g//30 * 10, b//30 * 10)

        set_led(254, 0, 0, 0)  # show() command
    except serial.SerialException:  # lost serial connection
        logger.log('Lost serial output connection, the program will resume without broadcasting data until '
                   'reattached manually.', Logtype.warning)
        disconnect()


def arduino_comm_thread_func():
    if Globals.play_obj is None:
        logger.log('Waiting for play_obj initialization to complete...', Logtype.info)
    while Globals.play_obj is None:
        time.sleep(0.1)
    logger.log('play_obj connected successfully.', Logtype.info)

    if not is_connected():
        logger.log('Serial port not connected, continuing without connection to the LED strip. '
                   'This thread will now exit.', Logtype.warning)

    while not Globals.should_everything_die:
        time.sleep(0.1)
        while Globals.is_unfinished and not Globals.should_everything_die:
            if is_connected():
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
            else:
                time.sleep(0.5)
    disconnect()
    logger.log('Thread killed and disconnected.', Logtype.kill)


if __name__ == "__main__":
    logger.log(f"Resetting the strip at {PORT}.", Logtype.info)
    connect()
