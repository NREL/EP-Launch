import wx


# wx callbacks need an event argument even though we usually don't use it, so the next line disables that check
# noinspection PyUnusedLocal
class WeatherDialog(wx.Dialog):
    CLOSE_SIGNAL_OK = 0
    CLOSE_SIGNAL_CANCEL = 1

    def __init__(self, *args, **kwargs):
        super(WeatherDialog, self).__init__(*args, **kwargs)
        self.Bind(wx.EVT_CLOSE, self.handle_close_cancel)
        self.selected_weather_file = None
        self._recent_files = None
        self._favorite_files = None
        self.choice_recent = None
        self.choice_fave = None
        self.text_select_file = None
        self.SetTitle("Choose Weather Configuration")

    def initialize(self, recent_files, favorite_files):
        self._recent_files = recent_files
        self._favorite_files = favorite_files
        this_border = 4
        sizer_main_vertical = wx.BoxSizer(wx.VERTICAL)

        single_row_sizer = wx.BoxSizer(wx.HORIZONTAL)
        st1 = wx.StaticText(self, label='Use Design Days Only; *NO* Weather File:', style=wx.ALIGN_RIGHT)
        single_row_sizer.Add(st1, proportion=9, border=this_border, flag=wx.ALIGN_CENTER_VERTICAL)
        dd_button = wx.Button(self, label='Select This!')
        dd_button.Bind(wx.EVT_BUTTON, self.handle_dd_only)
        single_row_sizer.Add(dd_button, flag=wx.ALL, proportion=1, border=this_border)
        sizer_main_vertical.Add(single_row_sizer, flag=wx.ALL, border=this_border)

        single_row_sizer = wx.BoxSizer(wx.HORIZONTAL)
        wf_button = wx.Button(self, label='Find on Disk...')
        wf_button.Bind(wx.EVT_BUTTON, self.handle_select_new_file)
        single_row_sizer.Add(wf_button, flag=wx.ALL, proportion=2, border=this_border)
        self.text_select_file = wx.TextCtrl(self)
        single_row_sizer.Add(self.text_select_file, flag=wx.ALL, proportion=7, border=this_border)
        select_button = wx.Button(self, label="Select This!")
        self.Bind(wx.EVT_BUTTON, self.handle_select_file, select_button)
        single_row_sizer.Add(select_button, flag=wx.ALL, proportion=1, border=this_border)
        sizer_main_vertical.Add(single_row_sizer, flag=wx.ALL, border=this_border)

        if recent_files:
            single_row_sizer = wx.BoxSizer(wx.HORIZONTAL)
            st1 = wx.StaticText(self, label='Recents:', style=wx.ALIGN_RIGHT)
            single_row_sizer.Add(st1, flag=wx.ALL | wx.ALIGN_CENTER_VERTICAL, proportion=2, border=this_border)
            self.choice_recent = wx.Choice(self, choices=recent_files)
            self.choice_recent.SetSelection(0)
            single_row_sizer.Add(self.choice_recent, flag=wx.ALL, proportion=7, border=this_border)
            recent_button = wx.Button(self, label="Select This!")
            self.Bind(wx.EVT_BUTTON, self.handle_recent, recent_button)
            single_row_sizer.Add(recent_button, flag=wx.ALL, proportion=1, border=this_border)
            sizer_main_vertical.Add(single_row_sizer, flag=wx.ALL, border=this_border)

        if favorite_files:
            single_row_sizer = wx.BoxSizer(wx.HORIZONTAL)
            st1 = wx.StaticText(self, label='Favorites:', style=wx.ALIGN_RIGHT)
            single_row_sizer.Add(st1, flag=wx.ALL | wx.ALIGN_CENTER_VERTICAL, proportion=2, border=this_border)
            self.choice_fave = wx.Choice(self, choices=favorite_files)
            self.choice_fave.SetSelection(0)
            single_row_sizer.Add(self.choice_fave, flag=wx.ALL, proportion=7, border=this_border)
            fave_button = wx.Button(self, label="Select This!")
            self.Bind(wx.EVT_BUTTON, self.handle_favorite, fave_button)
            single_row_sizer.Add(fave_button, flag=wx.ALL, proportion=1, border=this_border)
            sizer_main_vertical.Add(single_row_sizer, flag=wx.ALL, border=this_border)

        cancel_button = wx.Button(self, label='Cancel')
        cancel_button.Bind(wx.EVT_BUTTON, self.handle_close_cancel)
        sizer_main_vertical.Add(cancel_button, flag=wx.ALIGN_CENTER | wx.ALL, border=this_border)

        self.SetSizer(sizer_main_vertical)
        sizer_main_vertical.Fit(self)

    def handle_dd_only(self, e):
        self.selected_weather_file = None  # OK+None = DD Only
        self.EndModal(WeatherDialog.CLOSE_SIGNAL_OK)

    def handle_select_new_file(self, e):
        filename = wx.FileSelector("Select weather file", wildcard="Weather File(*.epw)|*.epw",
                                   flags=wx.FD_OPEN | wx.FD_FILE_MUST_EXIST)
        if filename == '':
            return  # user cancelled
        self.text_select_file.SetValue(filename)

    def handle_select_file(self, e):
        self.selected_weather_file = 'Selected File'  # OK+String = Weather file!
        self.EndModal(WeatherDialog.CLOSE_SIGNAL_OK)

    def handle_recent(self, e):
        self.selected_weather_file = self._recent_files[self.choice_recent.GetSelection()]  # OK+String = Weather file!
        self.EndModal(WeatherDialog.CLOSE_SIGNAL_OK)

    def handle_favorite(self, e):
        self.selected_weather_file = self._favorite_files[self.choice_fave.GetSelection()]  # OK+String = Weather file!
        self.EndModal(WeatherDialog.CLOSE_SIGNAL_OK)

    def handle_close_cancel(self, e):
        self.EndModal(WeatherDialog.CLOSE_SIGNAL_CANCEL)
