import webbrowser

import wx

from eplaunch import DOCS_URL, VERSION


# wx callbacks need an event argument even though we usually don't use it, so the next line disables that check
# noinspection PyUnusedLocal
class WelcomeDialog(wx.Dialog):
    CLOSE_SIGNAL_OK = 0

    def __init__(self, *args, **kwargs):
        super(WelcomeDialog, self).__init__(*args, **kwargs)
        self.SetTitle("EP-Launch")
        this_border = 12
        self.panel = wx.Panel(self, wx.ID_ANY)

        title = wx.StaticText(self.panel, wx.ID_ANY, 'Welcome to EP-Launch ' + VERSION)
        message = """
EP-Launch has been around for many years as a part of the EnergyPlus distribution.
Starting with the 3.0 release, it has changed drastically, completely redesigned and rewritten.
For full documentation or a quick start guide, click the "Open Docs" button below.
This dialog will only be shown once, but documentation is available in the Help menu.        
        """
        text_description = wx.StaticText(self.panel, wx.ID_ANY, message, style=wx.ALIGN_CENTRE_HORIZONTAL)
        ok_button = wx.Button(self.panel, label='OK')
        docs_button = wx.Button(self.panel, label='Open Docs')

        self.Bind(wx.EVT_CLOSE, self.handle_close_ok)
        ok_button.Bind(wx.EVT_BUTTON, self.handle_close_ok)
        docs_button.Bind(wx.EVT_BUTTON, self.handle_open_docs)

        button_row_sizer = wx.BoxSizer(wx.HORIZONTAL)
        button_row_sizer.Add(ok_button, flag=wx.LEFT | wx.RIGHT | wx.ALIGN_CENTER_VERTICAL, border=this_border)
        button_row_sizer.Add(docs_button, flag=wx.LEFT | wx.RIGHT | wx.ALIGN_CENTER_VERTICAL, border=this_border)

        sizer_main_vertical = wx.BoxSizer(wx.VERTICAL)
        sizer_main_vertical.Add(title, 0, wx.CENTER | wx.ALL, border=this_border)
        sizer_main_vertical.Add(text_description, proportion=1, flag=wx.ALL | wx.EXPAND, border=this_border)
        sizer_main_vertical.Add(button_row_sizer, flag=wx.ALL | wx.ALIGN_CENTER, border=this_border)

        self.panel.SetSizer(sizer_main_vertical)
        sizer_main_vertical.Fit(self)

    def handle_open_docs(self, e):
        webbrowser.open(DOCS_URL)

    def handle_close_ok(self, e):
        self.EndModal(WelcomeDialog.CLOSE_SIGNAL_OK)
