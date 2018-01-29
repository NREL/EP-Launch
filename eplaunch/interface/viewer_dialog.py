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

        #kwds["style"] = wx.DEFAULT_DIALOG_STYLE
        #wx.Dialog.__init__(self, *args, **kwds)
        list_box_1 = wx.ListBox(self, wx.ID_ANY,
                                     choices=["Text Editor", "csv", "html", "svg", "dxf"])
        radio_btn_1 = wx.RadioButton(self, wx.ID_ANY, "Use Text Editor")
        radio_btn_2 = wx.RadioButton(self, wx.ID_ANY, "Use Preview")
        radio_btn_3 = wx.RadioButton(self, wx.ID_ANY, "Use Specific Application")
        text_ctrl_1 = wx.TextCtrl(self, wx.ID_ANY, "c:\\programs\\text editor\\textedit.exe",
                                       style=wx.TE_MULTILINE)
        button_3 = wx.Button(self, wx.ID_ANY, "Auto Find")
        button_4 = wx.Button(self, wx.ID_ANY, "Select...")
        button_1 = wx.Button(self, wx.ID_OK, "")
        button_2 = wx.Button(self, wx.ID_CANCEL, "")

        vert_sizer_main = wx.BoxSizer(wx.VERTICAL)
        horiz_sizer_bottom = wx.BoxSizer(wx.HORIZONTAL)
        horiz_sizer_top = wx.BoxSizer(wx.HORIZONTAL)
        vert_sizer_right = wx.BoxSizer(wx.VERTICAL)
        horiz_sizer_right = wx.BoxSizer(wx.HORIZONTAL)
        horiz_sizer_top.Add(list_box_1, 1, wx.ALL | wx.EXPAND, 5)
        vert_sizer_right.Add(radio_btn_1, 0, 0, 0)
        vert_sizer_right.Add(radio_btn_2, 0, 0, 0)
        vert_sizer_right.Add(radio_btn_3, 0, 0, 0)
        vert_sizer_right.Add(text_ctrl_1, 0, wx.EXPAND, 0)
        horiz_sizer_right.Add(button_3, 0, 0, 0)
        horiz_sizer_right.Add(button_4, 0, 0, 0)
        vert_sizer_right.Add(horiz_sizer_right, 1, wx.ALL | wx.EXPAND, 5)
        horiz_sizer_top.Add(vert_sizer_right, 1, wx.ALL | wx.EXPAND, 5)
        vert_sizer_main.Add(horiz_sizer_top, 1, wx.EXPAND, 0)
        horiz_sizer_bottom.Add(button_1, 0, wx.ALIGN_CENTER | wx.ALL, 5)
        horiz_sizer_bottom.Add(button_2, 0, wx.ALIGN_CENTER, 0)
        vert_sizer_main.Add(horiz_sizer_bottom, 0, wx.ALIGN_CENTER, 5)
        self.SetSizer(vert_sizer_main)
        #vert_sizer_main.Fit(self)
        #self.Layout()


        # pnl = wx.Panel(self)
        #
        # hbox_1 = wx.BoxSizer(wx.HORIZONTAL)
        #
        # extensionList = ['Text'
        #               'csv',
        #               'html',
        #               'err',
        #               'eio',
        #               'tab',
        #               'rdd',
        #               'mdd',
        #               'svg',
        #               'dxf']
        #
        # listBox = wx.ListBox(pnl, 60, size= (750, 100), choices=extensionList, style=wx.LB_SINGLE | wx.LB_ALWAYS_SB)
        #
        # vbox = wx.BoxSizer(wx.HORIZONTAL)
        #
        # add_button = wx.Button(self, label='Add..')
        # remove_button = wx.Button(self, label='Remove')
        # hbox_1.Add(add_button, flag=wx.RIGHT, border=5)
        # hbox_1.Add(remove_button, flag=wx.LEFT, border=5)
        #
        # hbox_2 = wx.BoxSizer(wx.HORIZONTAL)
        # ok_button = wx.Button(self, label='Ok')
        # cancel_button = wx.Button(self, label='Cancel')
        # hbox_2.Add(ok_button, flag=wx.RIGHT, border=5)
        # hbox_2.Add(cancel_button, flag=wx.LEFT, border=5)
        #
        # vbox.Add(pnl, proportion=1, flag=wx.ALL | wx.EXPAND, border=5)
        # vbox.Add(hbox_1, flag=wx.ALIGN_CENTER | wx.TOP | wx.BOTTOM, border=10)
        # vbox.Add(hbox_2, flag=wx.ALIGN_CENTER | wx.TOP | wx.BOTTOM, border=10)
        #
        # self.SetSizer(vbox)
        #
        # ok_button.Bind(wx.EVT_BUTTON, self.handle_close_ok)
        # cancel_button.Bind(wx.EVT_BUTTON, self.handle_close_cancel)

    def handle_close_ok(self, e):
        # Do some saving here before closing it
        self.EndModal(ViewerDialog.CLOSE_SIGNAL_OK)

    def handle_close_cancel(self, e):
        self.EndModal(ViewerDialog.CLOSE_SIGNAL_CANCEL)
