import wx


class CommandLineDialog(wx.Dialog):

    CLOSE_SIGNAL_OK = 0
    CLOSE_SIGNAL_CANCEL = 1

    def __init__(self, *args, **kwargs):
        super(CommandLineDialog, self).__init__(*args, **kwargs)
        self.initialize_ui()
        self.SetSize((800, 400))
        self.SetTitle("<workflowname> Command Line")

    def initialize_ui(self):
        pnl = wx.Panel(self)
        vbox = wx.BoxSizer(wx.VERTICAL)

        sampleList = ['c:\EnergyPlusV8-6-0\workflows',
                      'c:\EnergyPlusV8-7-0\workflows',
                      'c:\EnergyPlusV8-8-0\workflows',
                      'c:\EnergyPlusV8-9-0\workflows',]

        instructions = wx.TextCtrl(pnl, 60, pos=(10,10), size= (750, 250), style=wx.TE_MULTILINE | wx.TE_READONLY)
        instructions.AppendText("For workflow <workflowname> use the following command line arguments\n")
        instructions.AppendText("\n")
        instructions.AppendText("To create pauses in the simulation\n")
        instructions.AppendText("  pause=on\n")
        instructions.AppendText("\n")
        instructions.AppendText("To allow the use of parametric objects \n")
        instructions.AppendText("  parametric=true\n")
        instructions.AppendText("\n")
        instructions.AppendText("To display the results using digits\n")
        instructions.AppendText("  -digit\n")
        instructions.AppendText("\n")
        instructions.AppendText("\n")

        input = wx.TextCtrl(pnl, 61, pos=(10,270),size= (750, 20))
        input.AppendText("parametric=true    pause=false")

        hbox_1 = wx.BoxSizer(wx.HORIZONTAL)
        ok_button = wx.Button(self, label='Ok')
        cancel_button = wx.Button(self, label='Cancel')
        hbox_1.Add(ok_button, flag=wx.RIGHT, border=5)
        hbox_1.Add(cancel_button, flag=wx.LEFT, border=5)

        vbox.Add(pnl, proportion=1, flag=wx.ALL | wx.EXPAND, border=5)
        vbox.Add(hbox_1, flag=wx.ALIGN_CENTER | wx.TOP | wx.BOTTOM, border=10)

        self.SetSizer(vbox)

        ok_button.Bind(wx.EVT_BUTTON, self.handle_close_ok)
        cancel_button.Bind(wx.EVT_BUTTON, self.handle_close_cancel)

    def handle_close_ok(self, e):
        # Do some saving here before closing it
        self.EndModal(CommandLineDialog.CLOSE_SIGNAL_OK)

    def handle_close_cancel(self, e):
        self.EndModal(CommandLineDialog.CLOSE_SIGNAL_CANCEL)
