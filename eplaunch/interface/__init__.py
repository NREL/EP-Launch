from tkinter import Tk, Toplevel

DIALOG_WINDOW_OFFSET_X = 25
DIALOG_WINDOW_OFFSET_Y = 25


def set_dialog_geometry(dialog: Toplevel, parent: Tk, x: int = DIALOG_WINDOW_OFFSET_X, y: int = DIALOG_WINDOW_OFFSET_Y):
    # A small worker function that will set a Toplevel dialog in front of a Tk window with a specified offset
    dialog.update_idletasks()  # do a quick pass to make sure the window has handled GUI events
    dialog.geometry(
        "%dx%d+%d+%d" % (
            dialog.winfo_width(),
            dialog.winfo_height(),
            parent.winfo_x() + x,
            parent.winfo_y() + y
        )
    )
