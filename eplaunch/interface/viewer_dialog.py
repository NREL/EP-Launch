import wx


class ViewerDialog(wx.Dialog):
    CLOSE_SIGNAL_OK = 0
    CLOSE_SIGNAL_CANCEL = 1

    def __init__(self, *args, **kwargs):
        super(ViewerDialog, self).__init__(*args, **kwargs)
        self.initialize_ui()
        self.SetSize((550, 400))
        self.SetTitle("Viewers")

    def initialize_ui(self, *args, **kwds):
        extensionList = ['Text (Default)',
                         'Drawing (*.dxf)',
                         'VRML (*.wrl)',
                         'Spreadsheet (*.csv)',
                         'Diagramming (*.svg)',
                         'Web Browser (*.html)',
                         'ESO (*.eso)',
                         'Portable Document (*.pdf)',
                         'XML (*.xml)',
                         ]

        viewer_list_label = wx.StaticText(self, wx.ID_ANY, "Type")
        viewer_type_list_box = wx.ListBox(self, wx.ID_ANY, choices=extensionList)
        application_path_label = wx.StaticText(self, wx.ID_ANY, "Application Path")
        application_ctrl = wx.TextCtrl(self, wx.ID_ANY, "c:\\programs\\text editor\\textedit.exe",
                                       style=wx.TE_MULTILINE | wx.TE_READONLY)
        mime_label = wx.StaticText(self, wx.ID_ANY, "MIME Type")
        mime_ctrl = wx.TextCtrl(self, wx.ID_ANY, "text/plain", style=wx.TE_READONLY)
        button_auto_find = wx.Button(self, wx.ID_ANY, "Auto Find")
        button_select = wx.Button(self, wx.ID_ANY, "Select...")
        button_clear = wx.Button(self, wx.ID_ANY, "Clear")
        button_ok = wx.Button(self, wx.ID_OK, "")
        button_cancel = wx.Button(self, wx.ID_CANCEL, "")

        vert_sizer_main = wx.BoxSizer(wx.VERTICAL)
        horiz_sizer_bottom = wx.BoxSizer(wx.HORIZONTAL)
        horiz_sizer_top = wx.BoxSizer(wx.HORIZONTAL)
        vert_sizer_right = wx.BoxSizer(wx.VERTICAL)
        vert_sizer_left = wx.BoxSizer(wx.VERTICAL)
        horiz_sizer_right = wx.BoxSizer(wx.HORIZONTAL)

        vert_sizer_left.Add(viewer_list_label, flag=wx.ALL, border=5)
        vert_sizer_left.Add(viewer_type_list_box, 1, flag=wx.ALL | wx.EXPAND, border=5)
        horiz_sizer_top.Add(vert_sizer_left, flag=wx.ALL | wx.EXPAND, border=5)

        vert_sizer_right.Add(application_path_label, flag=wx.ALL, border=5)
        vert_sizer_right.Add(application_ctrl, flag=wx.ALL | wx.EXPAND, border=5)
        vert_sizer_right.Add(mime_label, flag=wx.ALL, border=5)
        vert_sizer_right.Add(mime_ctrl, flag=wx.ALL | wx.EXPAND, border=5)

        horiz_sizer_right.Add(button_auto_find, flag=wx.ALL, border=5)
        horiz_sizer_right.Add(button_select, flag=wx.ALL, border=5)
        horiz_sizer_right.Add(button_clear, flag=wx.ALL, border=5)

        vert_sizer_right.Add(horiz_sizer_right, 1, flag=wx.ALL | wx.EXPAND, border=5)

        horiz_sizer_top.Add(vert_sizer_right, 1, flag=wx.ALL | wx.EXPAND, border=5)

        vert_sizer_main.Add(horiz_sizer_top, 1, flag=wx.EXPAND)

        horiz_sizer_bottom.Add(button_ok, flag=wx.ALL, border=5)
        horiz_sizer_bottom.Add(button_cancel, flag=wx.ALL, border=5)

        vert_sizer_main.Add(horiz_sizer_bottom, flag=wx.ALIGN_RIGHT)

        self.SetSizer(vert_sizer_main)
        button_ok.Bind(wx.EVT_BUTTON, self.handle_close_ok)
        button_cancel.Bind(wx.EVT_BUTTON, self.handle_close_cancel)

    def handle_close_ok(self, e):
        # Do some saving here before closing it
        self.EndModal(ViewerDialog.CLOSE_SIGNAL_OK)

    def handle_close_cancel(self, e):
        self.EndModal(ViewerDialog.CLOSE_SIGNAL_CANCEL)
