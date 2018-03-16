import wx


class WorkflowDirectoriesDialog(wx.Dialog):

    CLOSE_SIGNAL_OK = 0
    CLOSE_SIGNAL_CANCEL = 1

    def __init__(self, *args, **kwargs):
        super(WorkflowDirectoriesDialog, self).__init__(*args, **kwargs)
        self.initialize_ui()
        self.SetSize((800, 250))
        self.SetTitle("Workflow Directories")

    def initialize_ui(self):
        pnl = wx.Panel(self)
        vbox = wx.BoxSizer(wx.VERTICAL)

        sampleList = ['c:\EnergyPlusV8-6-0\workflows',
                      'c:\EnergyPlusV8-7-0\workflows',
                      'c:\EnergyPlusV8-8-0\workflows',
                      'c:\EnergyPlusV8-9-0\workflows',]

        lb1 = wx.ListBox(pnl, 60, size= (750, 100), choices=sampleList, style=wx.LB_SINGLE | wx.LB_ALWAYS_SB)

        hbox_1 = wx.BoxSizer(wx.HORIZONTAL)
        add_button = wx.Button(self, label='Add..')
        remove_button = wx.Button(self, label='Remove')
        hbox_1.Add(add_button, flag=wx.RIGHT, border=5)
        hbox_1.Add(remove_button, flag=wx.LEFT, border=5)

        hbox_2 = wx.BoxSizer(wx.HORIZONTAL)
        ok_button = wx.Button(self, label='Ok')
        cancel_button = wx.Button(self, label='Cancel')
        hbox_2.Add(ok_button, flag=wx.RIGHT, border=5)
        hbox_2.Add(cancel_button, flag=wx.LEFT, border=5)

        vbox.Add(pnl, proportion=1, flag=wx.ALL | wx.EXPAND, border=5)
        vbox.Add(hbox_1, flag=wx.ALIGN_CENTER | wx.TOP | wx.BOTTOM, border=10)
        vbox.Add(hbox_2, flag=wx.ALIGN_CENTER | wx.TOP | wx.BOTTOM, border=10)

        self.SetSizer(vbox)

        ok_button.Bind(wx.EVT_BUTTON, self.handle_close_ok)
        cancel_button.Bind(wx.EVT_BUTTON, self.handle_close_cancel)

    def handle_close_ok(self, e):
        # Do some saving here before closing it
        self.EndModal(WorkflowDirectoriesDialog.CLOSE_SIGNAL_OK)

    def handle_close_cancel(self, e):
        self.EndModal(WorkflowDirectoriesDialog.CLOSE_SIGNAL_CANCEL)
