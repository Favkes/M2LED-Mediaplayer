from utils.globals import Globals
import tkinter as tk
from utils.simple_logs import Logger, Logtype


logger = Logger(__name__, 'blue')


class Slider:
    def __init__(self,
                 parent_frame: tk.Frame,
                 from_: int = 0,
                 to: int = 1,
                 start: int = 0,
                 orient: str = 'vertical',
                 showvalue: bool = False,
                 length: int = 100,
                 command = lambda x: None,
                 linked_global: str = None,
                 input_to_global_ratio: float = 1,
                 label_text: str = 'Name') -> None:

        self.parent = parent_frame
        self.value = start
        self.from_ = from_
        self.to = to
        self.length = length
        self.linked_global = linked_global
        self.input_to_global_ratio = input_to_global_ratio

        self.scale = tk.Scale(
            parent_frame,
            from_=from_,
            to=to,
            orient=orient,
            showvalue=showvalue,
            length=100,
            command=command,
        )
        self.scale.set(start)

        self.label = tk.Label(
            self.parent,
            text=label_text
        )

        self.value_label = tk.Label(
            self.parent,
            text=str(self.value)
        )

    def grid(self,
             start_col: int = 0,
             start_row: int = 0,
             padx: int = 0) -> None:
        self.label.grid(
            column=start_col, row=start_row, padx=padx
        )
        self.scale.grid(
            column=start_col, row=start_row + 1, padx=padx
        )
        self.value_label.grid(
            column=start_col, row=start_row + 2, padx=padx
        )


    def update(self, val: int | float,
               label_val: bool = False) -> None:

        if label_val:
            scale_val = round(val / self.input_to_global_ratio, 2)
            label_val = round(val, 2)
        else:
            scale_val = round(val, 2)
            label_val = round(val * self.input_to_global_ratio, 2)

        self.scale.set(scale_val)
        self.value_label.config(text=str(label_val))

        try:
            label_val = type( getattr(Globals, self.linked_global) )(label_val)
            setattr(Globals, self.linked_global, label_val)
        except Exception as e:
            logger.log(f'{e}', Logtype.error)
