import wx

from eplaunch.utilities.locateworkflows import LocateWorkflows


class WorkflowDirectoriesDialog(wx.Dialog):
    CLOSE_SIGNAL_OK = 0
    CLOSE_SIGNAL_CANCEL = 1

    list_of_directories = []

    def __init__(self, *args, **kwargs):
        super(WorkflowDirectoriesDialog, self).__init__(*args, **kwargs)
        self.list_of_directories = []
        self.directory_listbox = None
        self.initialize_ui()
        self.SetSize((800, 250))
        self.SetTitle("Workflow Directories")

    def initialize_ui(self):
        pnl = wx.Panel(self)
        vbox = wx.BoxSizer(wx.VERTICAL)

        self.directory_listbox = wx.ListBox(pnl, 60, size=(750, 100), choices=self.list_of_directories,
                                            style=wx.LB_SINGLE | wx.LB_ALWAYS_SB)
        hbox_1 = wx.BoxSizer(wx.HORIZONTAL)
        add_button = wx.Button(self, label='Add..')
        remove_button = wx.Button(self, label='Remove')
        auto_find_button = wx.Button(self, label='Auto Find..')
        hbox_1.Add(add_button, flag=wx.RIGHT, border=5)
        hbox_1.Add(remove_button, flag=wx.CENTER, border=5)
        hbox_1.Add(auto_find_button, flag=wx.LEFT, border=5)

        hbox_2 = wx.BoxSizer(wx.HORIZONTAL)
        ok_button = wx.Button(self, wx.ID_OK, label='Ok')
        self.SetAffirmativeId(ok_button.GetId())
        cancel_button = wx.Button(self, wx.ID_CANCEL, label='Cancel')
        hbox_2.Add(ok_button, flag=wx.RIGHT, border=5)
        hbox_2.Add(cancel_button, flag=wx.LEFT, border=5)

        vbox.Add(pnl, proportion=1, flag=wx.ALL | wx.EXPAND, border=5)
        vbox.Add(hbox_1, flag=wx.ALIGN_CENTER | wx.TOP | wx.BOTTOM, border=10)
        vbox.Add(hbox_2, flag=wx.ALIGN_CENTER | wx.TOP | wx.BOTTOM, border=10)

        self.SetSizer(vbox)

        add_button.Bind(wx.EVT_BUTTON, self.handle_add)
        remove_button.Bind(wx.EVT_BUTTON, self.handle_remove)
        auto_find_button.Bind(wx.EVT_BUTTON, self.handle_auto_find)

        ok_button.Bind(wx.EVT_BUTTON, self.handle_close_ok)
        cancel_button.Bind(wx.EVT_BUTTON, self.handle_close_cancel)

    def set_listbox(self, list_of_directories):
        self.list_of_directories = list_of_directories
        if len(self.list_of_directories) == 0:
            lw = LocateWorkflows()
            self.list_of_directories = lw.find()
        self.directory_listbox.SetItems(self.list_of_directories)

    def handle_add(self, e):
        dlg = wx.DirDialog(self, "Select a workflow directory", "", wx.DD_DEFAULT_STYLE | wx.DD_DIR_MUST_EXIST)
        if dlg.ShowModal() == wx.ID_OK:
            print(dlg.GetPath())
            self.directory_listbox.Append(dlg.GetPath())
        dlg.Destroy()

    def handle_remove(self, e):
        selected_item = self.directory_listbox.GetSelection()
        self.directory_listbox.Delete(selected_item)

    def handle_auto_find(self, e):
        current_items = self.directory_listbox.GetStrings()
        lw = LocateWorkflows()
        found_items = lw.find()
        for found_item in found_items:
            if found_item not in current_items:
                self.directory_listbox.Append(found_item)

    def handle_close_ok(self, e):
        # Do some saving here before closing it
        self.EndModal(e.EventObject.Id)
        self.list_of_directories = self.directory_listbox.GetStrings()

    def handle_close_cancel(self, e):
        self.EndModal(WorkflowDirectoriesDialog.CLOSE_SIGNAL_CANCEL)
