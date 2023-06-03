from typing import Callable, Dict
from tkinter import Tk, Label, Button, Toplevel, TOP, BOTH, LEFT


class TkGenericDialog:
    def __init__(self, default_padding: Dict[str, int]):
        self.pad = default_padding

    def display(self, parent: Tk, title: str, text: str):
        t = Toplevel(parent)
        t.title(title)
        Label(t, justify=LEFT, text=text).pack(side=TOP, expand=True, fill=BOTH, **self.pad)

        def dest():
            t.destroy()
        Button(t, text="OK", command=dest).pack(side=TOP, **self.pad)
        t.grab_set()
        t.transient(parent)
        parent.wait_window(t)

    def display_with_alt_button(
            self, parent: Tk, title: str, text: str, button_text: str, button_action: Callable
    ):
        t = Toplevel(parent)
        t.title(title)
        Label(t, justify=LEFT, text=text).pack(side=TOP, expand=True, fill=BOTH, **self.pad)

        def dest():
            t.destroy()
        Button(t, text=button_text, command=button_action).pack(side=TOP, **self.pad)
        Button(t, text="OK", command=dest).pack(side=TOP, **self.pad)
        t.grab_set()
        t.transient(parent)
        parent.wait_window(t)
