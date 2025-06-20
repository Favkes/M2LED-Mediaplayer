from utils import mp3dataextract
import pydub


SOURCE_PATH:       str                = "./Music/Tenebre Rosso Sangue.mp3"
PROGRESS_TIME_MAX: int                = round(mp3dataextract.grab_duration(SOURCE_PATH) + 0.5)
SONG_CONTAINER:    pydub.AudioSegment = pydub.AudioSegment.from_mp3(SOURCE_PATH)
FPS:               int                = 30
SAMPLES_PER_FRAME: int                = int(SONG_CONTAINER.frame_rate / FPS)

GLOBALS: dict = {
    'ACTIVATION_THRESHOLD':             0,                  # Obv
    'BASS_CUT':                         0,                  # Low-cut to ensure some bass is left out
    'FPS':                              FPS,
    'GRAPHX':                           300,                # Width of the graph canvas
    'GRAPHY':                           150,                # Height of the graph canvas
    'IS_PAUSED':                        True,               # When paused with button
    'IS_NEWLY_LOADED':                  True,               # Only at file load
    'NOISE_DECAY':                      0.95,
    'PROGRESS_TIME':                    0,                  # Total elapsed time running
    'PROGRESS_TIME_MAX':                PROGRESS_TIME_MAX,  # Total length of the file (time)
    'PLAY_OBJ':                         None,               # Music playing object
    'SAMPLES_PER_FRAME':                SAMPLES_PER_FRAME,
    'SOURCE_PATH':                      SOURCE_PATH,        # MP3 file path
    'SONG_CONTAINER':                   SONG_CONTAINER,     # Raw data from MP3 file
    'TIME_OFFSET':                      -0.65,
    'TEMPORAL_SMOOTHING':               0.9,                # Main processing
    'TEMPORAL_SMOOTHING_SECONDARY':     0.7,                # Post-processing
    'WINX':                             627,                # Width of the GUI window
    'WINY':                             500                 # Height of the GUI window
}

# RATE = GLOBALS['SONG_CONTAINER'].frame_rate

del FPS
del PROGRESS_TIME_MAX
del SAMPLES_PER_FRAME
del SOURCE_PATH
del SONG_CONTAINER


if __name__ == "__main__":
    print('\x1b[0;34;40mGlobals initialized. And nothing else LOL.\x1b[0m')
