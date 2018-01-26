from gettext import gettext as _

import wx

from eplaunch.interface import settingdialog

# wx callbacks need an event argument even though we usually don't use it, so the next line disables that check
# noinspection PyUnusedLocal
class EpLaunchFrame(wx.Frame):

    def __init__(self, *args, **kwargs):
        # begin wxGlade: mainApplicationFrame.__init__
        kwargs["style"] = wx.DEFAULT_FRAME_STYLE
        wx.Frame.__init__(self, *args, **kwargs)
        self.window_1 = wx.SplitterWindow(self, wx.ID_ANY)
        self.window_1_pane_1 = wx.Panel(self.window_1, wx.ID_ANY)
        self.dir_ctrl_1 = wx.GenericDirCtrl(self.window_1_pane_1, -1, size=(200, 225), style=wx.DIRCTRL_DIR_ONLY)
        tree = self.dir_ctrl_1.GetTreeCtrl()
        #self.Bind(wx.EVT_TREE_ITEM_ACTIVATED, self.handle_dir_item_selected, tree)
        self.Bind(wx.EVT_TREE_ITEM_RIGHT_CLICK, self.handle_dir_right_click, tree)
        self.Bind(wx.EVT_TREE_SEL_CHANGED, self.handle_dir_selection_changed, tree)

        self.window_1_pane_2 = wx.Panel(self.window_1, wx.ID_ANY)
        self.list_ctrl_files = wx.ListCtrl(self.window_1_pane_2, wx.ID_ANY,
                                           style=wx.LC_HRULES | wx.LC_REPORT | wx.LC_VRULES)

        self.status_bar = self.CreateStatusBar(1)
        self.status_bar.SetStatusText('Status bar - reports on simulations in progress')

        # initialize these here in the constructor to hush up the compiler messages
        self.tb = None
        self.out_tb = None
        self.menu_bar = None

        self.build_primary_toolbar()
        self.build_out_toolbar()
        self.build_menu_bar()

        self.__set_properties()
        self.__do_layout()
        # end wxGlade

    def close_frame(self):
        """May do additional things during close, including saving the current window state/settings"""
        self.Close()

    def build_primary_toolbar(self):
        self.tb = wx.ToolBar(self, style=wx.TB_HORIZONTAL | wx.NO_BORDER | wx.TB_FLAT | wx.TB_TEXT)

        t_size = (24, 24)
        # new_bmp =  wx.ArtProvider.GetBitmap(wx.ART_NEW, wx.ART_TOOLBAR, t_size)
        # open_bmp = wx.ArtProvider.GetBitmap(wx.ART_FILE_OPEN, wx.ART_TOOLBAR, t_size)
        # copy_bmp = wx.ArtProvider.GetBitmap(wx.ART_COPY, wx.ART_TOOLBAR, t_size)
        # paste_bmp= wx.ArtProvider.GetBitmap(wx.ART_PASTE, wx.ART_TOOLBAR, t_size)
        forward_bmp = wx.ArtProvider.GetBitmap(wx.ART_GO_FORWARD, wx.ART_TOOLBAR, t_size)
        error_bmp = wx.ArtProvider.GetBitmap(wx.ART_ERROR, wx.ART_TOOLBAR, t_size)

        file_open_bmp = wx.ArtProvider.GetBitmap(wx.ART_FILE_OPEN, wx.ART_TOOLBAR, t_size)
        exe_bmp = wx.ArtProvider.GetBitmap(wx.ART_EXECUTABLE_FILE, wx.ART_TOOLBAR, t_size)
        up_bmp = wx.ArtProvider.GetBitmap(wx.ART_GO_UP, wx.ART_TOOLBAR, t_size)
        folder_bmp = wx.ArtProvider.GetBitmap(wx.ART_FOLDER, wx.ART_TOOLBAR, t_size)
        page_bmp = wx.ArtProvider.GetBitmap(wx.ART_HELP_PAGE, wx.ART_TOOLBAR, t_size)
        help_bmp = wx.ArtProvider.GetBitmap(wx.ART_HELP, wx.ART_TOOLBAR, t_size)

        self.tb.SetToolBitmapSize(t_size)

        ch_id = wx.NewId()
        workflow_choices = [
            "EnergyPlus SI (*.IDF)",
            "EnergyPlus IP (*.IDF)",
            "AppGPostProcess (*.HTML)",
            "CalcSoilSurfTemp",
            "CoeffCheck",
            "CoeffConv",
            "Basement",
            "Slab",
            "File Operations"
        ]
        workflow_choice = wx.Choice(self.tb, ch_id, choices=workflow_choices)
        workflow_choice.SetSelection(0)
        self.tb.AddControl(workflow_choice)
        self.Bind(wx.EVT_CHOICE, self.handle_choice_selection_change, workflow_choice)

        tb_weather = self.tb.AddTool(
            10, "Weather", file_open_bmp, wx.NullBitmap, wx.ITEM_NORMAL, "Weather", "Long help for 'Weather'", None
        )
        self.Bind(wx.EVT_TOOL, self.handle_tb_weather, tb_weather)
        self.tb.AddTool(
            20, "Run", forward_bmp, wx.NullBitmap, wx.ITEM_NORMAL, "Run", "Long help for 'Run'", None
        )
        self.tb.AddTool(
            30, "Cancel", error_bmp, wx.NullBitmap, wx.ITEM_NORMAL, "Cancel", "Long help for 'Cancel'",
            None)
        self.tb.AddSeparator()
        self.tb.AddTool(
            40, "IDF Editor", exe_bmp, wx.NullBitmap, wx.ITEM_NORMAL, "IDF Editor", "Long help for 'IDF Editor'", None
        )
        self.tb.AddTool(
            50, "Text Editor", exe_bmp, wx.NullBitmap, wx.ITEM_NORMAL, "Text Editor", "Long help for 'Text Editor'",
            None
        )
        self.tb.AddSeparator()
        self.tb.AddTool(
            80, "Explorer", folder_bmp, wx.NullBitmap, wx.ITEM_NORMAL, "Explorer", "Long help for 'Explorer'", None
        )
        self.tb.AddTool(
            80, "Update", up_bmp, wx.NullBitmap, wx.ITEM_NORMAL, "Update", "Long help for 'Update'", None
        )
        tb_settings = self.tb.AddTool(
            80, "Settings", page_bmp, wx.NullBitmap, wx.ITEM_NORMAL, "Settings", "Long help for 'Settings'",
            None)
        self.Bind(wx.EVT_TOOL, self.handle_tb_settings, tb_settings)
        self.tb.AddTool(
            90, "Help", help_bmp, wx.NullBitmap, wx.ITEM_NORMAL, "Help", "Long help for 'Help'", None
        )

        self.tb.Realize()

    def build_out_toolbar(self):
        t_size = (16, 16)
        self.out_tb = wx.ToolBar(self, style=wx.TB_HORIZONTAL | wx.NO_BORDER | wx.TB_FLAT | wx.TB_TEXT)
        self.out_tb.SetToolBitmapSize(t_size)

        norm_bmp = wx.ArtProvider.GetBitmap(wx.ART_NORMAL_FILE, wx.ART_TOOLBAR, t_size)

        self.out_tb.AddTool(
            10, "Tables", norm_bmp, wx.NullBitmap, wx.ITEM_NORMAL, "Help", "Long help for 'Help'", None
        )
        self.out_tb.AddTool(
            10, "Meters", norm_bmp, wx.NullBitmap, wx.ITEM_NORMAL, "Help", "Long help for 'Help'", None
        )
        self.out_tb.AddTool(
            10, "Variables", norm_bmp, wx.NullBitmap, wx.ITEM_NORMAL, "Help", "Long help for 'Help'", None
        )
        self.out_tb.AddTool(
            10, "Errors", norm_bmp, wx.NullBitmap, wx.ITEM_NORMAL, "Help", "Long help for 'Help'", None
        )
        self.out_tb.AddTool(
            10, "RDD", norm_bmp, wx.NullBitmap, wx.ITEM_NORMAL, "Help", "Long help for 'Help'", None
        )
        self.out_tb.AddTool(
            10, "MDD", norm_bmp, wx.NullBitmap, wx.ITEM_NORMAL, "Help", "Long help for 'Help'", None
        )
        self.out_tb.AddSeparator()
        self.out_tb.AddTool(
            10, "EIO", norm_bmp, wx.NullBitmap, wx.ITEM_NORMAL, "Help", "Long help for 'Help'", None
        )
        self.out_tb.AddTool(
            10, "SVG", norm_bmp, wx.NullBitmap, wx.ITEM_NORMAL, "Help", "Long help for 'Help'", None
        )
        self.out_tb.AddTool(
            10, "DXF", norm_bmp, wx.NullBitmap, wx.ITEM_NORMAL, "Help", "Long help for 'Help'", None
        )
        self.out_tb.AddTool(
            10, "MTD", norm_bmp, wx.NullBitmap, wx.ITEM_NORMAL, "Help", "Long help for 'Help'", None
        )
        self.out_tb.AddTool(
            10, "ZSZ", norm_bmp, wx.NullBitmap, wx.ITEM_NORMAL, "Help", "Long help for 'Help'", None
        )
        self.out_tb.AddTool(
            10, "SSZ", norm_bmp, wx.NullBitmap, wx.ITEM_NORMAL, "Help", "Long help for 'Help'", None
        )
        self.out_tb.Realize()

    def build_menu_bar(self):

        self.menu_bar = wx.MenuBar()

        file_menu = wx.Menu()
        menu_file_run = file_menu.Append(10, "Run File", "Run currently selected file for selected workflow")
        self.Bind(wx.EVT_MENU, self.handle_menu_file_run, menu_file_run)
        menu_file_cancel_selected = file_menu.Append(11, "Cancel Selected", "Cancel selected files")
        self.Bind(wx.EVT_MENU, self.handle_menu_file_cancel_selected, menu_file_cancel_selected)
        menu_file_cancel_all = file_menu.Append(13, "Cancel All", "Cancel all queued files")
        self.Bind(wx.EVT_MENU, self.handle_menu_file_cancel_all, menu_file_cancel_all)
        menu_file_quit = file_menu.Append(wx.ID_EXIT, 'Quit', 'Quit application')
        self.Bind(wx.EVT_MENU, self.handle_menu_file_quit, menu_file_quit)
        self.menu_bar.Append(file_menu, '&File')

        edit_menu = wx.Menu()
        menu_edit_undo = edit_menu.Append(20, "Undo")
        self.Bind(wx.EVT_MENU, self.handle_menu_edit_undo, menu_edit_undo)
        edit_menu.AppendSeparator()
        menu_edit_cut = edit_menu.Append(21, "Cut")
        self.Bind(wx.EVT_MENU, self.handle_menu_edit_cut, menu_edit_cut)
        menu_edit_copy = edit_menu.Append(22, "Copy")
        self.Bind(wx.EVT_MENU, self.handle_menu_edit_copy, menu_edit_copy)
        menu_edit_paste = edit_menu.Append(23, "Paste")
        self.Bind(wx.EVT_MENU, self.handle_menu_edit_paste, menu_edit_paste)
        self.menu_bar.Append(edit_menu, "&Edit")

        folder_menu = wx.Menu()
        recent_folder_menu = folder_menu.Append(31, "Recent")
        folder_menu.AppendSeparator()
        folder_menu.Append(32, "c:\\EnergyPlus8-8-0")
        folder_menu.Append(33, "c:\\documents")
        folder_menu.Append(34, "c:\\projectX\\working\\task1")
        folder_menu.Append(35, "c:\\projectY\\dev\\task2")
        folder_menu.AppendSeparator()
        folder_menu.Append(36, "Favorites")
        folder_menu.AppendSeparator()
        folder_menu.Append(37, "c:\\EnergyPlus8-8-0\Examples")
        folder_menu.Append(38, "c:\\documents\\about")
        folder_menu.Append(39, "c:\\projectZ\\do")
        folder_menu.AppendSeparator()
        folder_menu.Append(310, "Add Current Folder to Favorites")
        folder_menu.Append(311, "Remove Current Folder from Favorites")
        self.menu_bar.Append(folder_menu, "F&older")
        # disable the menu items that are just information
        self.menu_bar.Enable(31,False)
        self.menu_bar.Enable(36,False)

        weather_menu = wx.Menu()
        weather_menu.Append(41, "Select..")
        weather_menu.AppendSeparator()
        weather_menu.Append(42, "Recent")
        weather_menu.AppendSeparator()
        weather_menu.Append(43, "Chicago.TMY")
        weather_menu.Append(44, "Boston.TMY")
        weather_menu.Append(45, "Philadelphia.TMY")
        weather_menu.Append(46, "Austin.TMY")
        weather_menu.AppendSeparator()
        weather_menu.Append(47, "Favorites")
        weather_menu.AppendSeparator()
        weather_menu.Append(48, "Detroit.TMY")
        weather_menu.Append(49, "Denver.TMY")
        weather_menu.Append(410, "San Francisco.TMY")
        weather_menu.AppendSeparator()
        weather_menu.Append(411, "Add Weather to Favorites")
        weather_menu.Append(412, "Remove Weather from Favorites")
        self.menu_bar.Append(weather_menu, "&Weather")
        # disable the menu items that are just information
        self.menu_bar.Enable(42,False)
        self.menu_bar.Enable(47,False)

        output_menu = wx.Menu()

        out_table_menu = wx.Menu()
        out_table_menu.Append(501, "Table.csv")
        out_table_menu.Append(502, "Table.tab")
        out_table_menu.Append(503, "Table.txt")
        out_table_menu.Append(504, "Table.html")
        out_table_menu.Append(505, "Table.xml")
        output_menu.Append(599, "Table",out_table_menu)

        out_variable_menu = wx.Menu()
        out_variable_menu.Append(506, ".csv")
        out_variable_menu.Append(507, ".tab")
        out_variable_menu.Append(508, ".txt")
        output_menu.Append(598, "Variables",out_variable_menu)

        out_meter_menu = wx.Menu()
        out_meter_menu.Append(509, "Meter.csv")
        out_meter_menu.Append(510, "Meter.tab")
        out_meter_menu.Append(511, "Meter.txt")
        output_menu.Append(597, "Meter",out_meter_menu)

        output_menu.Append(513, ".err")
        output_menu.Append(514, ".end")
        output_menu.Append(515, ".rdd")
        output_menu.Append(516, ".mdd")
        output_menu.Append(517, ".eio")
        output_menu.Append(518, ".svg")
        output_menu.Append(519, ".dxf")
        output_menu.Append(520, ".mtd")

        out_sizing_menu = wx.Menu()
        out_sizing_menu.Append(521, "Zsz.csv")
        out_sizing_menu.Append(522, "Zsz.tab")
        out_sizing_menu.Append(523, "Zsz.txt")
        out_sizing_menu.Append(524, "Ssz.csv")
        out_sizing_menu.Append(525, "Ssz.tab")
        out_sizing_menu.Append(526, "Ssz.txt")
        output_menu.Append(596, "Sizing",out_sizing_menu)

        out_delight_menu = wx.Menu()
        out_delight_menu.Append(527, "DElight.in")
        out_delight_menu.Append(528, "DElight.out")
        out_delight_menu.Append(529, "DElight.eldmp")
        out_delight_menu.Append(530, "DElight.dfdmp")
        output_menu.Append(595, "DElight",out_delight_menu)

        out_map_menu = wx.Menu()
        out_map_menu.Append(531, "Map.csv")
        out_map_menu.Append(532, "Map.tab")
        out_map_menu.Append(533, "Map.txt")
        output_menu.Append(594, "Map",out_map_menu)

        output_menu.Append(534, "Screen.csv")
        output_menu.Append(535, ".expidf")
        output_menu.Append(536, ".epmidf")
        output_menu.Append(537, ".epmdet")
        output_menu.Append(538, ".shd")
        output_menu.Append(539, ".wrl")
        output_menu.Append(540, ".audit")
        output_menu.Append(541, ".bnd")
        output_menu.Append(542, ".dbg")
        output_menu.Append(543, ".sln")
        output_menu.Append(544, ".edd")
        output_menu.Append(545, ".eso")
        output_menu.Append(546, ".mtr")
        output_menu.Append(547, "Proc.csv")
        output_menu.Append(548, ".sci")
        output_menu.Append(549, ".rvaudit")
        output_menu.Append(550, ".sql")
        output_menu.Append(551, ".log")

        out_bsmt_menu = wx.Menu()
        out_bsmt_menu.Append(552, ".bsmt")
        out_bsmt_menu.Append(553, "_bsmt.out")
        out_bsmt_menu.Append(554, "_bsmt.audit")
        out_bsmt_menu.Append(555, "_bsmt.csv")
        output_menu.Append(593, "bsmt",out_bsmt_menu)

        out_slab_menu = wx.Menu()
        out_slab_menu.Append(556, ".slab")
        out_slab_menu.Append(557, "_slab.out")
        out_slab_menu.Append(558, "_slab.ger")
        output_menu.Append(592, "slab",out_slab_menu)

        self.menu_bar.Append(output_menu, "&Output")

        options_menu = wx.Menu()
        option_version_menu = wx.Menu()
        option_version_menu.Append(711,"EnergyPlus 8.6.0")
        option_version_menu.Append(712,"EnergyPlus 8.7.0")
        option_version_menu.Append(713,"EnergyPlus 8.8.0")
        option_version_menu.Append(714,"EnergyPlus 8.9.0")
        options_menu.Append(71, "Version",option_version_menu)
        options_menu.AppendSeparator()
        options_menu.Append(72, "Workflow Directories...")
        options_menu.Append(73, "Workflow Order...")
        options_menu.AppendSeparator()

        option_favorite_menu = wx.Menu()
        option_favorite_menu.Append(741,"4")
        option_favorite_menu.Append(742,"8")
        option_favorite_menu.Append(743,"12")
        option_favorite_menu.Append(744,"Clear")
        options_menu.Append(74, "Favorites",option_favorite_menu)

        option_recent_menu = wx.Menu()
        option_recent_menu.Append(741,"4")
        option_recent_menu.Append(742,"8")
        option_recent_menu.Append(743,"12")
        option_recent_menu.Append(744,"Clear")
        options_menu.Append(74, "Recent",option_recent_menu)

        options_menu.Append(74, "Remote...")
        options_menu.AppendSeparator()
        options_menu.Append(71, "<workspacename> Options...")
        options_menu.Append(71, "<workspacename> Command Line...")
        self.menu_bar.Append(options_menu, "&Settings")

        help_menu = wx.Menu()
        help_menu.Append(61, "EnergyPlus Getting Started")
        help_menu.Append(62, "EnergyPlus Input Output Reference")
        help_menu.Append(63, "EnergyPlus Output Details and Examples")
        help_menu.Append(64, "EnergyPlus Engineering Reference")
        help_menu.Append(65, "EnergyPlus Auxiliar Programs")
        help_menu.Append(66, "Application Guide for Plant Loops")
        help_menu.Append(67, "Application Guide for EMS")
        help_menu.Append(68, "Using EnergyPlus for Compliance")
        help_menu.Append(69, "External Interface Application Guide")
        help_menu.Append(610, "Tips and Tricks Using EnergyPlus")
        help_menu.Append(611, "EnergyPlus Acknowledgments")
        help_menu.AppendSeparator()
        help_menu.Append(612, "Check for Updates..")
        help_menu.Append(613, "View Entire Update List on Web..")
        help_menu.AppendSeparator()
        help_menu.Append(614, "Using EP-Launch Help")
        help_menu.Append(615, "About EP-Launch")
        self.menu_bar.Append(help_menu, "&Help")

        self.SetMenuBar(self.menu_bar)

    def __set_properties(self):
        # begin wxGlade: mainApplicationFrame.__set_properties
        self.SetTitle(_("EP-Launch 3"))
        self.list_ctrl_files.AppendColumn(_("Status"), format=wx.LIST_FORMAT_LEFT, width=-1)
        self.list_ctrl_files.AppendColumn(_("File Name"), format=wx.LIST_FORMAT_LEFT, width=-1)
        self.list_ctrl_files.AppendColumn(_("Weather File"), format=wx.LIST_FORMAT_LEFT, width=-1)
        self.list_ctrl_files.AppendColumn(_("Size"), format=wx.LIST_FORMAT_LEFT, width=-1)
        self.list_ctrl_files.AppendColumn(_("Errors"), format=wx.LIST_FORMAT_LEFT, width=-1)
        self.list_ctrl_files.AppendColumn(_("EUI"), format=wx.LIST_FORMAT_LEFT, width=-1)
        self.list_ctrl_files.AppendColumn(_("Floor Area"), format=wx.LIST_FORMAT_LEFT, width=-1)

        rows = [
            ["Running", "5Zone.idf", "Chicago.TMY", "8172", "-", "-", "-"],
            ["Complete", "6Zone.idf", "Chicago.TMY", "9847", "0", "1.58", "765"],
            ["Old", "7Zone.idf", "Chicago.TMY", "8172", "-", "-", "-"],
            ["Queued", "8Zone.idf", "Chicago.TMY", "8172", "-", "-", "-"]
        ]

        index = 0
        for row in rows:
            self.list_ctrl_files.InsertItem(index, row[0])
            self.list_ctrl_files.SetItem(index, 1, row[1])
            self.list_ctrl_files.SetItem(index, 2, row[2])
            self.list_ctrl_files.SetItem(index, 3, row[3])
            self.list_ctrl_files.SetItem(index, 4, row[4])
            self.list_ctrl_files.SetItem(index, 5, row[5])
            self.list_ctrl_files.SetItem(index, 6, row[6])
            index = index + 1

        self.window_1.SetMinimumPaneSize(20)
        # end wxGlade

    def __do_layout(self):
        # begin wxGlade: mainApplicationFrame.__do_layout
        sizer_main_app_vertical = wx.BoxSizer(wx.VERTICAL)
        sizer_3 = wx.BoxSizer(wx.VERTICAL)
        sizer_5 = wx.BoxSizer(wx.VERTICAL)
        sizer_5.Add(self.dir_ctrl_1, 1, wx.EXPAND, 0)
        self.window_1_pane_1.SetSizer(sizer_5)
        sizer_3.Add(self.list_ctrl_files, 1, wx.EXPAND, 0)
        self.window_1_pane_2.SetSizer(sizer_3)
        self.window_1.SplitVertically(self.window_1_pane_1, self.window_1_pane_2)
        sizer_main_app_vertical.Add(self.tb, 0, wx.EXPAND, 0)
        sizer_main_app_vertical.Add(self.out_tb, 0, wx.EXPAND, 0)
        sizer_main_app_vertical.Add(self.window_1, 1, wx.EXPAND, 0)
        self.SetSizer(sizer_main_app_vertical)
        sizer_main_app_vertical.Fit(self)
        self.Layout()
        # end wxGlade

    def handle_menu_file_run(self, event):
        self.status_bar.SetStatusText('Clicked File->Run')

    def handle_menu_file_cancel_selected(self, event):
        self.status_bar.SetStatusText('Clicked File->CancelSelected')

    def handle_menu_file_cancel_all(self, event):
        self.status_bar.SetStatusText('Clicked File->CancelAll')

    def handle_menu_file_quit(self, event):
        self.close_frame()
        self.status_bar.SetStatusText('Quitting Program')

    def handle_menu_edit_undo(self, event):
        self.status_bar.SetStatusText('Clicked Edit->Undo')

    def handle_menu_edit_cut(self, event):
        self.status_bar.SetStatusText('Clicked Edit->Cut')

    def handle_menu_edit_copy(self, event):
        self.status_bar.SetStatusText('Clicked Edit->Copy')

    def handle_menu_edit_paste(self, event):
        self.status_bar.SetStatusText('Clicked Edit->Paste')

    def handle_dir_item_selected(self, event):
        self.status_bar.SetStatusText("Dir-ItemSelected")
        # event.Skip()

    def handle_dir_right_click(self, event):
        self.status_bar.SetStatusText("Dir-RightClick")
        # event.Skip()

    def handle_dir_selection_changed(self, event):
        self.status_bar.SetStatusText("Dir-SelectionChanged")
        # event.Skip()

    def handle_choice_selection_change(self, event):
        self.status_bar.SetStatusText('Choice selection changed to ' + event.String)

    def handle_tb_weather(self, event):
        self.status_bar.SetStatusText('Clicked Weather toolbar item')

    def handle_tb_settings(self, event):
        settings_dialog = settingdialog.SettingsDialog(None, title='Change Color Depth')
        return_value = settings_dialog.ShowModal()
        print(return_value)
        # May need to refresh the main UI if something changed in the settings
        settings_dialog.Destroy()
