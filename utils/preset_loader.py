import os
import json

from utils.globals import Globals
from gui.slider import Slider


def save_settings() -> None:
    settings = {
        'time_offset': Globals.time_offset,
        'activation_threshold': Globals.activation_threshold,
        'temporal_smoothing': Globals.temporal_smoothing,
        'temporal_smoothing_secondary': Globals.temporal_smoothing_secondary,
        'noise_decay': Globals.noise_decay
    }
    with open(f'presets/{Globals.uuid}.json', 'w+') as file:
        json.dump(settings, file, indent=4)


def load_settings(default: bool = False) -> None:
    path = f'presets/{Globals.uuid}.json'
    if default or not os.path.exists(path):
        path = 'data/default_preset.json'

    with open(path) as file:
        settings: dict = json.load(file)

    for key, value in settings.items():
        setattr(Globals, key, value)

    # Updating the Slider objects assigned to certain Globals.params
    for slider in Slider.registered_sliders:
        slider.update(settings[slider.linked_global], label_val=True)
