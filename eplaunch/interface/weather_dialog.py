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
        self.panel = None
        self.rdo_dd, self.rdo_select, self.rdo_recent, self.rdo_fave = [None] * 4
        self.SetTitle("Choose Weather Configuration")

    def initialize(self, recent_files, favorite_files):
        self._recent_files = recent_files
        self._favorite_files = favorite_files
        radio_margin_width = 230
        this_border = 8
        sizer_main_vertical = wx.BoxSizer(wx.VERTICAL)

        self.panel = wx.Panel(self, wx.ID_ANY)

        title = wx.StaticText(self.panel, wx.ID_ANY, 'Choose a Weather File Configuration Option')
        title_sizer = wx.BoxSizer(wx.HORIZONTAL)
        title_sizer.Add(title, 0, wx.ALL, border=this_border)

        sizer_main_vertical.Add(title_sizer, 0, wx.CENTER)
        sizer_main_vertical.Add(wx.StaticLine(self.panel, ), 0, wx.ALL | wx.EXPAND, border=this_border)

        single_row_sizer = wx.BoxSizer(wx.HORIZONTAL)
        self.rdo_dd = wx.RadioButton(self.panel, label='Design Days:')
        self.rdo_dd.SetMinSize((radio_margin_width, -1))
        single_row_sizer.Add(self.rdo_dd, flag=wx.ALIGN_CENTER_VERTICAL)
        st1 = wx.StaticText(self.panel, label='** Use Design Days Only; No Weather File **', style=wx.ALIGN_LEFT)
        single_row_sizer.Add(st1, border=this_border, flag=wx.ALIGN_CENTER_VERTICAL)
        sizer_main_vertical.Add(single_row_sizer, flag=wx.ALL, border=this_border)

        single_row_sizer = wx.BoxSizer(wx.HORIZONTAL)
        self.rdo_select = wx.RadioButton(self.panel, label='Selected EPW:')
        self.rdo_select.SetValue(value=True)
        self.rdo_select.SetMinSize((radio_margin_width, -1))
        single_row_sizer.Add(self.rdo_select, flag=wx.ALIGN_CENTER_VERTICAL)
        self.text_select_file = wx.TextCtrl(self.panel)
        single_row_sizer.Add(self.text_select_file, proportion=1, flag=wx.RIGHT | wx.ALIGN_CENTER_VERTICAL,
                             border=this_border)
        wf_button = wx.Button(self.panel, label='Find on Disk...')
        wf_button.Bind(wx.EVT_BUTTON, self.handle_select_new_file)
        single_row_sizer.Add(wf_button, flag=wx.ALIGN_CENTER_VERTICAL)
        sizer_main_vertical.Add(single_row_sizer, flag=wx.ALL | wx.EXPAND, border=this_border)

        if recent_files:
            single_row_sizer = wx.BoxSizer(wx.HORIZONTAL)
            self.rdo_recent = wx.RadioButton(self.panel, label='Recent EPW:')
            self.rdo_recent.SetValue(value=True)
            self.rdo_recent.SetMinSize((radio_margin_width, -1))
            single_row_sizer.Add(self.rdo_recent, flag=wx.ALIGN_CENTER_VERTICAL)
            self.choice_recent = wx.Choice(self.panel, choices=recent_files)
            self.choice_recent.SetSelection(0)
            self.choice_recent.Bind(wx.EVT_CHOICE, self.handle_choice_recent)
            single_row_sizer.Add(self.choice_recent, flag=wx.ALIGN_CENTER_VERTICAL)
            sizer_main_vertical.Add(single_row_sizer, flag=wx.ALL, border=this_border)

        if favorite_files:
            single_row_sizer = wx.BoxSizer(wx.HORIZONTAL)
            self.rdo_fave = wx.RadioButton(self.panel, label='Favorite EPW:')
            self.rdo_fave.SetValue(value=True)
            self.rdo_fave.SetMinSize((radio_margin_width, -1))
            single_row_sizer.Add(self.rdo_fave, flag=wx.ALIGN_CENTER_VERTICAL)
            self.choice_fave = wx.Choice(self.panel, choices=favorite_files)
            self.choice_fave.SetSelection(0)
            self.choice_fave.Bind(wx.EVT_CHOICE, self.handle_choice_fave)
            single_row_sizer.Add(self.choice_fave, flag=wx.ALIGN_CENTER_VERTICAL)
            sizer_main_vertical.Add(single_row_sizer, flag=wx.ALL, border=this_border)

        single_row_sizer = wx.BoxSizer(wx.HORIZONTAL)
        ok_button = wx.Button(self.panel, label='OK')
        ok_button.Bind(wx.EVT_BUTTON, self.handle_close_ok)
        single_row_sizer.Add(ok_button, flag=wx.ALIGN_CENTER_VERTICAL)
        cancel_button = wx.Button(self.panel, label='Cancel')
        cancel_button.Bind(wx.EVT_BUTTON, self.handle_close_cancel)
        single_row_sizer.Add(cancel_button, flag=wx.ALIGN_CENTER_VERTICAL)
        sizer_main_vertical.Add(single_row_sizer, flag=wx.ALL | wx.ALIGN_CENTER, border=this_border)

        self.rdo_dd.SetValue(value=True)
        self.panel.SetSizer(sizer_main_vertical)
        sizer_main_vertical.Fit(self)

    def handle_choice_recent(self, e):
        self.rdo_recent.SetValue(value=True)

    def handle_choice_fave(self, e):
        self.rdo_fave.SetValue(value=True)

    def handle_select_new_file(self, e):
        filename = wx.FileSelector("Select weather file", wildcard="Weather File(*.epw)|*.epw",
                                   flags=wx.FD_OPEN | wx.FD_FILE_MUST_EXIST)
        if filename == '':
            return  # user cancelled
        self.text_select_file.SetValue(filename)
        self.rdo_select.SetValue(value=True)

    def handle_close_ok(self, e):
        if self.rdo_dd.GetValue():
            self.selected_weather_file = None  # OK+None = DD Only
        elif self.rdo_select.GetValue():
            if self.text_select_file.GetValue() == '':
                wx.MessageDialog(
                    self,
                    "Weather file path is blank, choose another option or enter a weather file path in the box",
                    "Weather File Error",
                    style=wx.OK
                ).ShowModal()
                return
            self.selected_weather_file = self.text_select_file.GetValue()
        elif self.rdo_recent.GetValue():
            self.selected_weather_file = self._recent_files[self.choice_recent.GetSelection()]
        elif self.rdo_fave.GetValue():
            self.selected_weather_file = self._favorite_files[self.choice_fave.GetSelection()]
        self.EndModal(WeatherDialog.CLOSE_SIGNAL_OK)

    def handle_close_cancel(self, e):
        self.EndModal(WeatherDialog.CLOSE_SIGNAL_CANCEL)
