# from utils.globals import Globals
import tkinter as tk


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
                 label_text: str = 'Name') -> None:
        self.parent = parent_frame
        self.value = start
        self.from_ = from_
        self.to = to
        self.length = length

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
               label_multiplier: int | float = 1) -> None:
        scale_val = round(val, 2)
        label_val = round(val * label_multiplier, 2)
        self.scale.set(scale_val)
        self.value_label.config(text=str(label_val))
