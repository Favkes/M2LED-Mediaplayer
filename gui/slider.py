from utils.globals import Globals
import tkinter as tk
from utils.simple_logs import Logger, Logtype
import numpy as np


logger = Logger(__name__, 'blue')


class Slider:
    registered_sliders = []


    def __init__(self,
                 parent_frame: tk.Frame,
                 from_: int = 0,
                 to: int = 1,
                 start: int = 0,
                 orient: str = 'vertical',
                 showvalue: bool = False,
                 showlabel: bool = True,
                 length: int = 100,
                 command = lambda x: None,
                 linked_global: str = None,
                 input_to_global_ratio: float = 1,
                 label_text: str = 'Name',
                 value_label_format: str = '{}') -> None:

        Slider.registered_sliders.append(self)

        self.parent = parent_frame
        self.value = start / input_to_global_ratio
        self.from_ = from_
        self.to = to
        self.length = length
        self.linked_global = linked_global
        self.input_to_global_ratio = input_to_global_ratio
        self.is_labeled = showlabel
        self.is_vertical = orient == 'vertical'
        self.value_format = value_label_format

        self.scale = tk.Scale(
            parent_frame,
            from_=from_,
            to=to,
            orient=orient,
            showvalue=showvalue,
            length=length,
            command=command,
        )
        self.scale.set(self.value)

        self.label = tk.Label(
            self.parent,
            text=label_text
        )

        self.value_label = tk.Label(
            self.parent,
            text=self.value_format.format(self.value)
        )


    def grid(self,
             start_col: int = 0,
             start_row: int = 0,
             padx: int = 0) -> None:

        widget_shift = np.array([1, 0])
        if self.is_vertical:
            widget_shift = np.array([0, 1])
        widget_position = np.array([start_col, start_row])

        if self.is_labeled:
            self.label.grid(
                column=widget_position[0], row=widget_position[1], padx=padx
            )
            widget_position += widget_shift

        self.scale.grid(
            column=widget_position[0], row=widget_position[1], padx=padx
        )
        widget_position += widget_shift

        self.value_label.grid(
            column=widget_position[0], row=widget_position[1], padx=padx
        )
        widget_position += widget_shift


    def update(self, val: int | float,
               label_val: bool = False) -> None:

        if label_val:
            scale_val = round(val / self.input_to_global_ratio, 2)
            self.value = round(val, 2)
        else:
            scale_val = round(val, 2)
            self.value = round(val * self.input_to_global_ratio, 2)

        self.scale.set(scale_val)
        self.value_label.config(text=self.value_format.format(self.value))

        try:
            self.value = type( getattr(Globals, self.linked_global) )(self.value)
            setattr(Globals, self.linked_global, self.value)
        except Exception as e:
            logger.log(f'{e}', Logtype.error)
