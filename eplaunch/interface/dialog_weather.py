from pathlib import Path
from tkinter import Tk, Toplevel, Frame, LabelFrame, StringVar, Radiobutton, TOP, W, Button, EW, NSEW, Entry, \
    ALL, ACTIVE, DISABLED, filedialog, Label, OptionMenu, E, messagebox, CENTER
from typing import List, Optional


class TkWeatherDialog(Toplevel):
    CLOSE_SIGNAL_OK = 0
    CLOSE_SIGNAL_CANCEL = 1
    WEATHER_TYPE_DD = "DD"
    WEATHER_TYPE_EPW = "EPW"

    def __init__(self, parent_window, recent_files: List[Path], favorite_files: List[Path], text: Optional[str] = None):
        super().__init__()
        self.alt_text = text
        self.title("Choose Weather Configuration")
        # assume cancel to allow for closing the dialog with the X
        self.exit_code = self.CLOSE_SIGNAL_CANCEL
        self.selected_weather_file: Optional[Path] = None
        # build the gui and call required modal methods
        self._define_tk_variables()
        self._epw_set = False
        self._build_gui(recent_files, favorite_files)
        self.grab_set()
        self.transient(parent_window)

    def _define_tk_variables(self):
        self._tk_var_weather_type = StringVar(value=self.WEATHER_TYPE_DD)
        self._tk_var_weather_type.trace('w', self._weather_type_changed)
        self._tk_var_recent = StringVar(value="")
        self._tk_var_favorite = StringVar(value="")
        self._tk_var_epw_path = StringVar(value="<epw path>")

    def _build_gui(self, recent_files: List[Path], favorite_files: List[Path]):
        lf = LabelFrame(self, text="Choose a Weather File Configuration Option")
        if self.alt_text:
            Label(lf, text=self.alt_text).pack(side=TOP, anchor=CENTER, padx=3, pady=3)
        Radiobutton(
            lf, text="Design Days (Use Design Days Only; No Weather File)",
            value=self.WEATHER_TYPE_DD, variable=self._tk_var_weather_type
        ).pack(
            side=TOP, anchor=W, padx=3, pady=3
        )
        Radiobutton(
            lf, text="Use Weather File (select below)", value=self.WEATHER_TYPE_EPW, variable=self._tk_var_weather_type
        ).pack(
            side=TOP, anchor=W, padx=3, pady=3
        )
        lf.grid(row=0, column=0, padx=3, pady=3, sticky=NSEW)
        epw_frame = LabelFrame(self, text="If using an EPW, specify it here")
        Label(epw_frame, text="Choose an EPW on disk: ").grid(
            row=0, column=0, columnspan=2, padx=3, pady=3, sticky=E,
        )
        self.btn_epw = Button(epw_frame, text="Select...", command=self._select_epw)
        self.btn_epw.grid(row=0, column=2, padx=3, pady=3, sticky=EW)
        self.options_recent = None
        self.btn_recent_engage = None
        self.options_favorite = None
        self.btn_favorite_engage = None
        if recent_files:
            Label(epw_frame, text="Choose from recent: ").grid(row=1, column=0, padx=3, pady=3, sticky=E)
            self.options_recent = OptionMenu(epw_frame, self._tk_var_recent, *recent_files)
            self.options_recent.grid(row=1, column=1, padx=3, pady=3, sticky=EW)
            self.btn_recent_engage = Button(epw_frame, text="Select", command=self._recent_engage)
            self.btn_recent_engage.grid(row=1, column=2, padx=3, pady=3, sticky=EW)
            self._tk_var_recent.set(str(recent_files[0]))
        if favorite_files:
            Label(epw_frame, text="Choose from favorites: ").grid(row=2, column=0, padx=3, pady=3, sticky=E)
            self.options_favorite = OptionMenu(epw_frame, self._tk_var_favorite, *favorite_files)
            self.options_favorite.grid(row=2, column=1, padx=3, pady=3, sticky=EW)
            self.btn_favorite_engage = Button(epw_frame, text="Select", command=self._favorite_engage)
            self.btn_favorite_engage.grid(row=2, column=2, padx=3, pady=3, sticky=EW)
            self._tk_var_favorite.set(str(favorite_files[0]))
        self.entry_epw = Entry(epw_frame, textvariable=self._tk_var_epw_path, state=DISABLED)
        self.entry_epw.grid(row=3, column=0, columnspan=3, padx=3, pady=3, sticky=EW)
        epw_frame.grid_rowconfigure(0, weight=1)
        epw_frame.grid_columnconfigure(ALL, weight=1)
        epw_frame.grid(row=1, column=0, padx=3, pady=3)
        button_frame = Frame(self)
        Button(button_frame, text="OK", command=self._ok).grid(row=0, column=0, padx=3, pady=3)
        Button(button_frame, text="Cancel", command=self._cancel).grid(row=0, column=1, padx=3, pady=3)
        button_frame.grid_rowconfigure(0, weight=1)
        button_frame.grid_columnconfigure(ALL, weight=1)
        button_frame.grid(row=2, column=0, padx=3, pady=3, sticky=EW)
        self.grid_rowconfigure(ALL, weight=1)
        self.grid_columnconfigure(ALL, weight=1)
        self._weather_type_changed()  # refresh the UI

    def _recent_engage(self):
        self._tk_var_epw_path.set(self._tk_var_recent.get())
        self._epw_set = True

    def _favorite_engage(self):
        self._tk_var_epw_path.set(self._tk_var_favorite.get())
        self._epw_set = True

    def _select_epw(self):
        filetypes = (
            ('EPW Weather Files', '*.epw'),
            ('All files', '*.*')
        )
        response = filedialog.askopenfilename(title="Specify Weather File", filetypes=filetypes)
        if response is None:
            return
        else:
            self._tk_var_epw_path.set(response)
            self._epw_set = True

    def _weather_type_changed(self, *_):
        status = ACTIVE if self._tk_var_weather_type.get() == self.WEATHER_TYPE_EPW else DISABLED
        self.btn_epw['state'] = status
        if self.options_favorite:
            self.options_favorite['state'] = status
        if self.btn_favorite_engage:
            self.btn_favorite_engage['state'] = status
        if self.options_recent:
            self.options_recent['state'] = status
        if self.btn_recent_engage:
            self.btn_recent_engage['state'] = status

    def _ok(self):
        self.exit_code = self.CLOSE_SIGNAL_OK
        if self._tk_var_weather_type.get() == self.WEATHER_TYPE_EPW:
            if not self._epw_set:
                messagebox.showerror("EPW", "Weather file option requested, but no EPW selected, select DD or an EPW")
                return
            self.selected_weather_file = Path(self._tk_var_epw_path.get())
        self.grab_release()
        self.destroy()

    def _cancel(self):
        self.exit_code = self.CLOSE_SIGNAL_CANCEL
        self.grab_release()
        self.destroy()


if __name__ == "__main__":
    root = Tk()
    root.title('Root Window for Toplevel Demo')
    file_listing = TkWeatherDialog(root, [Path('hello'), Path('world')], [Path('foo'), Path('bar')])
    root.mainloop()
