import wx


class ViewerDialog(wx.Dialog):

    CLOSE_SIGNAL_OK = 0
    CLOSE_SIGNAL_CANCEL = 1

    def __init__(self, *args, **kwargs):
        super(ViewerDialog, self).__init__(*args, **kwargs)
        self.initialize_ui()
        self.SetSize((400, 400))
        self.SetTitle("Viewer")

    def initialize_ui(self, *args, **kwds):
        extensionList = ['Text',
                       'csv',
                       'html',
                       'err',
                       'eio',
                       'tab',
                       'rdd',
                       'mdd',
                       'svg',
                       'dxf']

        list_box_1 = wx.ListBox(self, wx.ID_ANY,  choices=extensionList)
        radio_btn_1 = wx.RadioButton(self, wx.ID_ANY, "Use Text Editor")
        radio_btn_2 = wx.RadioButton(self, wx.ID_ANY, "Use Preview")
        radio_btn_3 = wx.RadioButton(self, wx.ID_ANY, "Use Specific Application")
        text_ctrl_1 = wx.TextCtrl(self, wx.ID_ANY, "c:\\programs\\text editor\\textedit.exe",
                                       style=wx.TE_MULTILINE)
        button_auto_find = wx.Button(self, wx.ID_ANY, "Auto Find")
        button_select = wx.Button(self, wx.ID_ANY, "Select...")
        button_ok = wx.Button(self, wx.ID_OK, "")
        button_cancel = wx.Button(self, wx.ID_CANCEL, "")

        vert_sizer_main = wx.BoxSizer(wx.VERTICAL)
        horiz_sizer_bottom = wx.BoxSizer(wx.HORIZONTAL)
        horiz_sizer_top = wx.BoxSizer(wx.HORIZONTAL)
        vert_sizer_right = wx.BoxSizer(wx.VERTICAL)
        horiz_sizer_right = wx.BoxSizer(wx.HORIZONTAL)
        horiz_sizer_top.Add(list_box_1, 1, flag=wx.ALL | wx.EXPAND, border=10)

        vert_sizer_right.Add(radio_btn_1, flag=wx.ALL, border = 5)
        vert_sizer_right.Add(radio_btn_2, flag=wx.ALL, border = 5)
        vert_sizer_right.Add(radio_btn_3, flag=wx.ALL, border = 5)
        vert_sizer_right.Add(text_ctrl_1, flag=wx.ALL | wx.EXPAND, border=5)

        horiz_sizer_right.Add(button_auto_find, flag=wx.ALL, border = 5)
        horiz_sizer_right.Add(button_select, flag=wx.ALL, border = 5)

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
