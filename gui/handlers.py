from utils import preset_loader
from utils.globals import Globals
from utils.simple_logs import Logger, Logtype


#--CORE--
def timeshift_sliderfunc(app, x):
    app.slider_timedelta.update(int(x))


def threshold_sliderfunc(app, x):
    app.threshold_slider.update(int(x))


def temporal_smoothing_sliderfunc(app, x):
    app.temporal_smoothing_slider.update(int(x))


def temporal_smoothing_secondary_sliderfunc(app, x):
    app.temporal_smoothing_secondary_slider.update(int(x))


def noise_decay_sliderfunc(app, x):
    app.noise_decay_slider.update(int(x))


#--MENUS--
def save_preset(logger: Logger):
    logger.log(
        'Saving settings preset',
        Logtype.info
    )
    preset_loader.save_settings()


def check_preset_save_automatically(logger: Logger):
    logger.log(
        f'Saving automatically set to {Globals.is_saving_presets.get()}',
        Logtype.info
    )


def check_preset_load_automatically(logger: Logger):
    logger.log(
        f'Loading automatically set to {Globals.is_loading_presets.get()}',
        Logtype.info
    )


def save_playlist_new(logger: Logger):
    logger.log('Creating new playlist...', Logtype.info)


def open_playlist(logger: Logger):
    logger.log('Opening playlist...', Logtype.info)

