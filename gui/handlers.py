from utils.globals import Globals


#- ADVANCED SETTINGS
def threshold_sliderfunc(app, x):
    x = int(x)
    Globals.activation_threshold = x
    app.threshold_slider.update(x)


def temporal_smoothing_sliderfunc(app, x):
    x = int(x)
    Globals.temporal_smoothing = round(x / 20, 2)
    app.temporal_smoothing_slider.update(
        x,
        label_multiplier=1/20
    )


def temporal_smoothing_secondary_sliderfunc(app, x):
    x = int(x)
    Globals.temporal_smoothing_secondary = round(x / 20, 2)
    app.temporal_smoothing_secondary_slider.update(
        x,
        label_multiplier=1/20
    )


def noise_decay_sliderfunc(app, x):
    x = int(x)
    Globals.noise_decay = round(x / 20, 2)
    app.noise_decay_slider.update(
        x,
        label_multiplier=1/20
    )
