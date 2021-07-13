import wx


class ViewerDialog(wx.Dialog):
    CLOSE_SIGNAL_OK = 0
    CLOSE_SIGNAL_CANCEL = 1
    DEFAULT_STRING = '<DEFAULT>'

    def __init__(self, *args, **kwargs):
        super(ViewerDialog, self).__init__(*args, **kwargs)
        self.SetSize((550, 400))
        self.SetTitle("Viewers")
        self.viewer_overrides = {}
        self.suffixes = []
        self.extension_to_viewer = {}

    def initialize_ui(self, list_of_suffixes, dict_of_viewer_overrides):
        self.suffixes = list_of_suffixes
        self.viewer_overrides = dict_of_viewer_overrides

        extension_list = ['txt']
        # only keep the extensions for each suffix that are unique
        for suffix in self.suffixes:
            if '.' in suffix:
                to_add = suffix.split('.')[1]
            else:
                to_add = suffix
            if to_add not in extension_list:
                extension_list.append(to_add)

        for extension in extension_list:
            if extension in self.viewer_overrides:
                self.extension_to_viewer[extension] = self.viewer_overrides[extension]
            else:
                self.extension_to_viewer[extension] = self.DEFAULT_STRING

        viewer_list_label = wx.StaticText(self, wx.ID_ANY, "Extensions")
        self.viewer_type_list_box = wx.ListBox(self, wx.ID_ANY, choices=extension_list)
        self.viewer_type_list_box.Bind(wx.EVT_LISTBOX, self.handle_viewer_type_click)

        application_path_label = wx.StaticText(self, wx.ID_ANY, "Application Path")
        self.application_ctrl = wx.TextCtrl(self, wx.ID_ANY, self.extension_to_viewer['txt'], style=wx.TE_MULTILINE
                                                                                                    | wx.TE_READONLY)

        instructions_label = wx.StaticText(self, wx.ID_ANY, "Only set applications for extensions that don't open with "
                                                            "the desired applications automatically. Typically, "
                                                            "extension 'htm' opens using a web browser, extension "
                                                            "'csv' opens using a spreadsheet program, extension 'txt' "
                                                            "opens using a text editor, etc. By default, the 'txt' "
                                                            "extension also opens all non-typical extensions such as "
                                                            "'err' and 'eio'.")

        self.viewer_type_list_box.SetSelection(0)

        button_default = wx.Button(self, wx.ID_ANY, "Default")
        button_select = wx.Button(self, wx.ID_ANY, "Select...")
        button_ok = wx.Button(self, wx.ID_OK, "")
        button_cancel = wx.Button(self, wx.ID_CANCEL, "")

        vert_sizer_main = wx.BoxSizer(wx.VERTICAL)
        horiz_sizer_bottom = wx.BoxSizer(wx.HORIZONTAL)
        horiz_sizer_top = wx.BoxSizer(wx.HORIZONTAL)
        vert_sizer_right = wx.BoxSizer(wx.VERTICAL)
        vert_sizer_left = wx.BoxSizer(wx.VERTICAL)
        horiz_sizer_right = wx.BoxSizer(wx.HORIZONTAL)

        vert_sizer_left.Add(viewer_list_label, flag=wx.ALL, border=5)
        vert_sizer_left.Add(self.viewer_type_list_box, 1, flag=wx.ALL | wx.EXPAND, border=5)
        horiz_sizer_top.Add(vert_sizer_left, flag=wx.ALL | wx.EXPAND, border=5)

        vert_sizer_right.Add(application_path_label, flag=wx.ALL, border=5)
        vert_sizer_right.Add(self.application_ctrl, flag=wx.ALL | wx.EXPAND, border=5)

        horiz_sizer_right.Add(button_default, flag=wx.ALL, border=5)
        horiz_sizer_right.Add(button_select, flag=wx.ALL, border=5)

        vert_sizer_right.Add(horiz_sizer_right, flag=wx.ALL | wx.EXPAND, border=5)
        vert_sizer_right.Add(instructions_label, 1, flag=wx.ALL| wx.EXPAND, border=5)

        horiz_sizer_top.Add(vert_sizer_right, 1, flag=wx.ALL | wx.EXPAND, border=5)

        vert_sizer_main.Add(horiz_sizer_top, 1, flag=wx.EXPAND)

        horiz_sizer_bottom.Add(button_ok, flag=wx.ALL, border=5)
        horiz_sizer_bottom.Add(button_cancel, flag=wx.ALL, border=5)

        vert_sizer_main.Add(horiz_sizer_bottom, flag=wx.ALIGN_RIGHT)

        self.SetSizer(vert_sizer_main)

        button_default.Bind(wx.EVT_BUTTON, self.handle_button_default)
        button_select.Bind(wx.EVT_BUTTON, self.handle_button_select)
        button_ok.Bind(wx.EVT_BUTTON, self.handle_close_ok)
        button_cancel.Bind(wx.EVT_BUTTON, self.handle_close_cancel)

    def handle_close_ok(self, e):
        self.viewer_overrides = {}
        for extension, application in self.extension_to_viewer.items():
            if application is not self.DEFAULT_STRING:
                self.viewer_overrides[extension] = application
        self.EndModal(ViewerDialog.CLOSE_SIGNAL_OK)

    def handle_close_cancel(self, e):
        self.EndModal(ViewerDialog.CLOSE_SIGNAL_CANCEL)

    def handle_button_default(self, e):
        self.application_ctrl.SetValue(self.DEFAULT_STRING)
        current_extension = self.viewer_type_list_box.GetString(self.viewer_type_list_box.GetSelection())
        self.extension_to_viewer[current_extension] = self.DEFAULT_STRING

    def handle_button_select(self, e):
        application_file_name = wx.FileSelector("Select application", wildcard='*.exe')
        self.application_ctrl.SetValue(application_file_name)
        current_extension = self.viewer_type_list_box.GetString(self.viewer_type_list_box.GetSelection())
        self.extension_to_viewer[current_extension] = application_file_name

    def handle_viewer_type_click(self, e):
        selected_extension = e.GetEventObject().GetStringSelection()
        self.application_ctrl.SetValue(self.extension_to_viewer[selected_extension])
