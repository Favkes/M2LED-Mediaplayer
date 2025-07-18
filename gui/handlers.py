from utils.globals import Globals
from utils import preset_loader


def timeshift_sliderfunc(app, x):
    app.slider_timedelta.update(int(x))


#- ADVANCED SETTINGS
def threshold_sliderfunc(app, x):
    app.threshold_slider.update(int(x))


def temporal_smoothing_sliderfunc(app, x):
    app.temporal_smoothing_slider.update(int(x))


def temporal_smoothing_secondary_sliderfunc(app, x):
    app.temporal_smoothing_secondary_slider.update(int(x))


def noise_decay_sliderfunc(app, x):
    app.noise_decay_slider.update(int(x))


def save_preset(app):
    preset_loader.save_settings()
