from typing import Callable, Dict
from tkinter import Tk, Label, Button, Toplevel, TOP, BOTH, LEFT


class TkGenericDialog:
    def __init__(self, default_padding: Dict[str, int]):
        self.pad = default_padding

    def display(
            self, parent: Tk, title: str, text: str, button_text: str = "OK", button_action: Callable = None
    ):
        t = Toplevel(parent)
        t.title(title)
        Label(t, justify=LEFT, text=text).pack(side=TOP, expand=True, fill=BOTH, **self.pad)

        def dest():
            t.destroy()
        if button_action is None:
            button_action = dest
        Button(t, text=button_text, command=button_action).pack(side=TOP, **self.pad)
        t.grab_set()
        t.transient(parent)
        parent.wait_window(t)
