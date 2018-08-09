import wx


class Dialog(wx.Frame):

    def __init__(self, *args, **kwargs):
        super(Dialog, self).__init__(*args, **kwargs)

        self.txt_config = None
        self.txt_output = None
        self.btn_exit = None
        self.workflow_id = None

        self.initialize_ui()

    def initialize_ui(self):
        monospace_text = wx.TextAttr()
        monospace_text.SetFontFamily(wx.FONTFAMILY_TELETYPE)

        panel_main = wx.Panel(self, style=wx.BORDER_RAISED)
        sizer_main = wx.BoxSizer(wx.VERTICAL)

        self.txt_config = wx.TextCtrl(panel_main, -1, style=wx.TE_READONLY | wx.TE_MULTILINE | wx.HSCROLL)
        self.txt_config.SetDefaultStyle(monospace_text)
        self.txt_output = wx.TextCtrl(panel_main, -1, style=wx.TE_READONLY | wx.TE_MULTILINE | wx.HSCROLL)
        self.txt_output.SetDefaultStyle(monospace_text)
        self.btn_exit = wx.Button(panel_main, label="Close Dialog")
        self.Bind(wx.EVT_BUTTON, self.handle_close, self.btn_exit)

        sizer_main.Add((0, 10))

        sizer_config = wx.BoxSizer(wx.HORIZONTAL)
        sizer_config.Add((10, 0), proportion=1)
        sizer_config.Add(self.txt_config, proportion=12, flag=wx.EXPAND)
        sizer_config.Add((10, 0), proportion=1)
        sizer_main.Add(sizer_config, proportion=2, flag=wx.EXPAND)

        sizer_main.Add((0, 10))

        sizer_output = wx.BoxSizer(wx.HORIZONTAL)
        sizer_output.Add((10, 0), proportion=1)
        sizer_output.Add(self.txt_output, proportion=12, flag=wx.EXPAND)
        sizer_output.Add((10, 0), proportion=1)
        sizer_main.Add(sizer_output, proportion=5, flag=wx.EXPAND)

        sizer_main.Add((0, 10))

        sizer_main.Add(self.btn_exit, proportion=1, flag=wx.ALIGN_CENTER)

        sizer_main.Add((0, 10))

        panel_main.SetSizer(sizer_main)
        self.SetSize((500, 500))
        self.Centre()
        self.Show(True)

    def set_id(self, workflow_id):
        self.workflow_id = workflow_id

    def set_config(self, text):
        self.txt_config.SetValue(text)

    def update_output(self, message):
        self.txt_output.AppendText(message + '\n')

    def handle_close(self, e):
        self.Close(True)
