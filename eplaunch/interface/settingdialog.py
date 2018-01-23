import wx


class SettingsDialog(wx.Dialog):

    CLOSE_SIGNAL_OK = 0
    CLOSE_SIGNAL_CANCEL = 1

    def __init__(self, *args, **kwargs):
        super(SettingsDialog, self).__init__(*args, **kwargs)
        self.initialize_ui()
        self.SetSize((250, 200))
        self.SetTitle("Change Color Depth")

    def initialize_ui(self):
        pnl = wx.Panel(self)
        vbox = wx.BoxSizer(wx.VERTICAL)

        sb = wx.StaticBox(pnl, label='Colors')
        sbs = wx.StaticBoxSizer(sb, orient=wx.VERTICAL)
        sbs.Add(wx.RadioButton(pnl, label='256 Colors', style=wx.RB_GROUP))
        sbs.Add(wx.RadioButton(pnl, label='16 Colors'))
        sbs.Add(wx.RadioButton(pnl, label='2 Colors'))

        hbox_1 = wx.BoxSizer(wx.HORIZONTAL)
        hbox_1.Add(wx.RadioButton(pnl, label='Custom'))
        hbox_1.Add(wx.TextCtrl(pnl), flag=wx.LEFT, border=5)
        sbs.Add(hbox_1)

        pnl.SetSizer(sbs)

        hbox_2 = wx.BoxSizer(wx.HORIZONTAL)
        ok_button = wx.Button(self, label='Ok')
        close_button = wx.Button(self, label='Close')
        hbox_2.Add(ok_button)
        hbox_2.Add(close_button, flag=wx.LEFT, border=5)

        vbox.Add(pnl, proportion=1, flag=wx.ALL | wx.EXPAND, border=5)
        vbox.Add(hbox_2, flag=wx.ALIGN_CENTER | wx.TOP | wx.BOTTOM, border=10)

        self.SetSizer(vbox)

        ok_button.Bind(wx.EVT_BUTTON, self.handle_close_ok)
        close_button.Bind(wx.EVT_BUTTON, self.handle_close_cancel)

    def handle_close_ok(self, e):
        # Do some saving here before closing it
        self.EndModal(SettingsDialog.CLOSE_SIGNAL_OK)

    def handle_close_cancel(self, e):
        self.EndModal(SettingsDialog.CLOSE_SIGNAL_CANCEL)
