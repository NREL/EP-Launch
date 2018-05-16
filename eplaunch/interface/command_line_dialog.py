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

        instructions = wx.TextCtrl(pnl, size=(750, 250), style=wx.TE_MULTILINE | wx.TE_READONLY)
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
        vbox.Add(instructions, flag=wx.EXPAND | wx.ALL, border=10)

        input = wx.TextCtrl(pnl)
        input.AppendText("parametric=true    pause=false")
        vbox.Add(input, flag=wx.EXPAND | wx.ALL, border=10)

        hbox_1 = wx.BoxSizer(wx.HORIZONTAL)
        ok_button = wx.Button(pnl, label='Ok')
        cancel_button = wx.Button(pnl, label='Cancel')
        hbox_1.Add(ok_button, flag=wx.RIGHT, border=5)
        hbox_1.Add(cancel_button, flag=wx.LEFT, border=5)

        vbox.Add(hbox_1, flag=wx.ALIGN_RIGHT | wx.ALL, border=10)

        pnl.SetSizer(vbox)

        ok_button.Bind(wx.EVT_BUTTON, self.handle_close_ok)
        cancel_button.Bind(wx.EVT_BUTTON, self.handle_close_cancel)

    def handle_close_ok(self, e):
        # Do some saving here before closing it
        self.EndModal(CommandLineDialog.CLOSE_SIGNAL_OK)

    def handle_close_cancel(self, e):
        self.EndModal(CommandLineDialog.CLOSE_SIGNAL_CANCEL)
