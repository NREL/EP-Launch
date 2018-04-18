import fnmatch
import json
import os
from gettext import gettext as _

import wx

from eplaunch.interface import command_line_dialog
from eplaunch.interface import viewer_dialog
from eplaunch.interface import workflow_directories_dialog
from eplaunch.interface.exceptions import EPLaunchDevException
from eplaunch.interface.workflow_processing import event_result, WorkerThread
from eplaunch.workflows import manager as workflow_manager


# wx callbacks need an event argument even though we usually don't use it, so the next line disables that check
# noinspection PyUnusedLocal
class EpLaunchFrame(wx.Frame):
    class Identifiers:
        ToolBarRunButtonID = 20

    def __init__(self, *args, **kwargs):

        kwargs["style"] = wx.DEFAULT_FRAME_STYLE
        wx.Frame.__init__(self, *args, **kwargs)

        # Set the title!
        self.SetTitle(_("EP-Launch 3"))

        # initialize these here (and early) in the constructor to hush up the compiler messages
        self.primary_toolbar = None
        self.directory_tree_control = None
        self.output_toolbar = None
        self.tb_run = None
        self.menu_file_run = None
        self.menu_bar = None
        self.current_workflow = None
        self.workflow_instances = None
        self.workflow_choice = None
        self.directory_name = None
        self.current_file_name = None
        self.menu_output_toolbar = None
        self.menu_columns = None
        self.menu_command_line = None
        self.status_bar = None
        self.raw_file_list = None
        self.control_file_list = None

        # this is currently just a single background thread, eventually we'll need to keep a list of them
        self.workflow_worker = None

        # build out the whole GUI and do other one-time inits here
        self.gui_build()
        self.reset_raw_list_columns()

        # this sets up an event handler for workflow completion events
        event_result(self, self.handle_workflow_done)

        # these are things that need to be done frequently
        self.update_control_list_columns()
        self.update_file_lists()
        self.update_workflow_dependent_menu_items()

    def close_frame(self):
        """May do additional things during close, including saving the current window state/settings"""
        self.Close()

    @staticmethod
    def update_workflow_list():

        workflow_choice_strings = []
        workflow_instances = []

        # "built-in" workflow classes will ultimately just be a couple core things that are packaged up with the tool
        # we will then also search through the workflow directories and get all available workflows from there as well
        built_in_workflow_classes = workflow_manager.get_workflows()
        for workflow_class in built_in_workflow_classes:
            workflow_instance = workflow_class()
            workflow_instances.append(workflow_instance)
            workflow_name = workflow_instance.name()
            workflow_file_types = workflow_instance.get_file_types()

            file_type_string = "("
            first = True
            for file_type in workflow_file_types:
                if first:
                    first = False
                else:
                    file_type_string += ", "
                file_type_string += file_type
            file_type_string += ")"

            workflow_choice_strings.append("%s %s" % (workflow_name, file_type_string))

        return workflow_instances, workflow_choice_strings

    def update_workflow_dependent_menu_items(self):
        current_workflow_name = self.current_workflow.name()
        self.menu_output_toolbar.SetText("%s Output Toolbar..." % current_workflow_name)
        self.menu_columns.SetText("%s Columns..." % current_workflow_name)
        self.menu_command_line.SetText("%s Command Line..." % current_workflow_name)

    def update_control_list_columns(self):
        self.control_file_list.DeleteAllColumns()
        self.control_file_list.AppendColumn(_("File Name"), format=wx.LIST_FORMAT_LEFT, width=-1)
        current_workflow_columns = self.current_workflow.get_interface_columns()
        for current_column in current_workflow_columns:
            self.control_file_list.AppendColumn(_(current_column), format=wx.LIST_FORMAT_LEFT, width=-1)

    def reset_raw_list_columns(self):
        self.raw_file_list.AppendColumn(_("File Name"), format=wx.LIST_FORMAT_LEFT, width=-1)
        # self.raw_file_list.AppendColumn(_("Date Modified"), format=wx.LIST_FORMAT_LEFT, width=-1)
        # self.raw_file_list.AppendColumn(_("Type"), format=wx.LIST_FORMAT_LEFT, width=-1)
        self.raw_file_list.AppendColumn(_("Size"), format=wx.LIST_FORMAT_RIGHT, width=-1)

    @staticmethod
    def get_files_in_directory():
        file_list = [
            {"name": "5Zone.idf", "size": 128},
            {"name": "6Zone.idf", "size": 256},
            {"name": "7Zone.idf", "size": 389},
            {"name": "8Zone.idf", "size": 495},
            {"name": "9Zone.what", "size": 529},
            {"name": "admin.html", "size": 639}
        ]
        file_list.sort(key=lambda x: x['name'])
        return file_list

    def update_file_lists(self):

        # for now this will pick up the dummy cache file here in the source tree
        # this will eventually pick up the currently selected directory and find a cache file there
        this_dir = os.path.dirname(os.path.realpath(__file__))
        cache_file_path = os.path.join(this_dir, 'fake_cache_file.json')

        # if there is a cache file there, read the cached file data for the current workflow
        files_in_workflow = {}
        if os.path.exists(cache_file_path):
            file_blob = open(cache_file_path, 'r').read()
            content = json.loads(file_blob)
            workflows = content['workflows']
            current_workflow_name = self.current_workflow.name()
            if current_workflow_name in workflows:
                files_in_workflow = workflows[current_workflow_name]['files']

        # then get the entire list of files in the current directory to build up the listview items
        # if they happen to match the filename in the workflow cache, then add that info to the row structure
        files_in_dir = self.get_files_in_directory()
        workflow_file_patterns = self.current_workflow.get_file_types()
        control_list_rows = []
        raw_list_rows = []
        for file_struct in files_in_dir:
            if not all([x in file_struct for x in ['name', 'size']]):
                raise EPLaunchDevException('Developer issue: malformed response from get_files_in_directory')
            file_name = file_struct['name']
            file_size = file_struct['size']
            raw_list_rows.append([file_name, file_size])
            # we only include this row if the file matches the workflow pattern
            matched = False
            for file_type in workflow_file_patterns:
                if fnmatch.fnmatch(file_name, file_type):
                    matched = True
                    break
            if not matched:
                continue
            # listview row always includes the filename itself
            row = [file_name]
            # if it is also in the cache then the listview row can include additional data
            if file_name in files_in_workflow:
                cached_file_info = files_in_workflow[file_name]
                for column in self.current_workflow.get_interface_columns():
                    if column in cached_file_info:
                        row.append(cached_file_info[column])
            # always add the row to the main list
            control_list_rows.append(row)

        # clear all items from the listview and then add them back in
        self.control_file_list.DeleteAllItems()
        for row in control_list_rows:
            self.control_file_list.Append(row)
        self.control_file_list.SetColumnWidth(0, -1)  # autosize column width

        # clear all the items from the raw list as well and add all of them back
        self.raw_file_list.DeleteAllItems()
        for row in raw_list_rows:
            self.raw_file_list.Append(row)
        self.raw_file_list.SetColumnWidth(0, -1)
        self.raw_file_list.SetColumnWidth(1, -1)

    def run_workflow(self):
        if self.directory_name and self.current_file_name:
            if not self.workflow_worker:
                self.status_bar.SetLabel('Starting workflow')
                full_file_path = os.path.join(self.directory_name, self.current_file_name)
                self.workflow_worker = WorkerThread(self, self.current_workflow, full_file_path, None)
                self.tb_run.Enable(False)
                self.primary_toolbar.Realize()
                # self.menu_file_run.Enable(False)
            else:
                self.status_bar.SetLabel('A workflow is already running, concurrence will come soon...')
        else:
            self.status_bar.SetLabel(
                'Error: Make sure you select a directory and a file'
            )

    def gui_build(self):

        self.gui_build_menu_bar()

        # build the left/right main splitter
        main_left_right_splitter = wx.SplitterWindow(self, wx.ID_ANY)

        # build tree view and add it to the left pane
        directory_tree_panel = wx.Panel(main_left_right_splitter, wx.ID_ANY)
        self.directory_tree_control = wx.GenericDirCtrl(directory_tree_panel, -1, size=(200, 225), style=wx.DIRCTRL_DIR_ONLY)
        tree = self.directory_tree_control.GetTreeCtrl()
        self.Bind(wx.EVT_TREE_ITEM_RIGHT_CLICK, self.handle_dir_right_click, tree)
        self.Bind(wx.EVT_TREE_SEL_CHANGED, self.handle_dir_selection_changed, tree)
        # self.directory_tree_control.SelectPath("/home/edwin")
        directory_tree_sizer = wx.BoxSizer(wx.VERTICAL)
        directory_tree_sizer.Add(self.directory_tree_control, 1, wx.EXPAND, 0)
        directory_tree_panel.SetSizer(directory_tree_sizer)

        # build list views and add to the right pane
        file_lists_panel = wx.Panel(main_left_right_splitter, wx.ID_ANY)
        file_lists_splitter = wx.SplitterWindow(file_lists_panel, wx.ID_ANY)

        # build control list view (top right)
        control_file_list_panel = wx.Panel(file_lists_splitter, wx.ID_ANY)
        self.control_file_list = wx.ListCtrl(control_file_list_panel, wx.ID_ANY,
                                             style=wx.LC_HRULES | wx.LC_REPORT | wx.LC_VRULES)
        self.Bind(wx.EVT_LIST_ITEM_SELECTED, self.handle_list_ctrl_selection, self.control_file_list)
        control_file_list_sizer = wx.BoxSizer(wx.VERTICAL)
        control_file_list_sizer.Add(self.control_file_list, 1, wx.EXPAND, 0)
        control_file_list_panel.SetSizer(control_file_list_sizer)

        # build raw list view (bottom right)
        raw_file_list_panel = wx.Panel(file_lists_splitter, wx.ID_ANY)
        self.raw_file_list = wx.ListCtrl(raw_file_list_panel, wx.ID_ANY,
                                         style=wx.LC_HRULES | wx.LC_REPORT | wx.LC_VRULES)
        raw_file_list_sizer = wx.BoxSizer(wx.VERTICAL)
        raw_file_list_sizer.Add(self.raw_file_list, 1, wx.EXPAND, 0)
        raw_file_list_panel.SetSizer(raw_file_list_sizer)

        # not sure why but it works better if you make the split and unsplit it right away
        file_lists_splitter.SetMinimumPaneSize(20)
        file_lists_splitter.SplitHorizontally(control_file_list_panel, raw_file_list_panel)

        # self.file_lists_splitter.Unsplit(toRemove=self.raw_file_list_panel)
        sizer_right = wx.BoxSizer(wx.HORIZONTAL)
        sizer_right.Add(file_lists_splitter, 1, wx.EXPAND, 0)

        # add the entire right pane to the main left/right splitter
        file_lists_panel.SetSizer(sizer_right)
        main_left_right_splitter.SetMinimumPaneSize(20)
        main_left_right_splitter.SplitVertically(directory_tree_panel, file_lists_panel)

        # now set up the main frame's layout sizer
        main_app_vertical_sizer = wx.BoxSizer(wx.VERTICAL)
        self.gui_build_primary_toolbar()
        main_app_vertical_sizer.Add(self.primary_toolbar, 0, wx.EXPAND, 0)
        self.gui_build_output_toolbar()
        main_app_vertical_sizer.Add(self.output_toolbar, 0, wx.EXPAND, 0)
        main_app_vertical_sizer.Add(main_left_right_splitter, 1, wx.EXPAND, 0)

        # add the status bar
        self.gui_build_status_bar()

        # assign the final form's sizer
        self.SetSizer(main_app_vertical_sizer)
        main_app_vertical_sizer.Fit(self)

        # call this to finalize
        self.Layout()

    def gui_build_primary_toolbar(self):

        self.primary_toolbar = wx.ToolBar(self, style=wx.TB_HORIZONTAL | wx.NO_BORDER | wx.TB_FLAT | wx.TB_TEXT)

        t_size = (24, 24)
        self.primary_toolbar.SetToolBitmapSize(t_size)

        ch_id = wx.NewId()

        self.workflow_instances, workflow_choice_strings = self.update_workflow_list()
        self.workflow_choice = wx.Choice(self.primary_toolbar, ch_id, choices=workflow_choice_strings)
        self.primary_toolbar.AddControl(self.workflow_choice)
        self.primary_toolbar.Bind(wx.EVT_CHOICE, self.handle_choice_selection_change, self.workflow_choice)

        if not self.workflow_instances:
            self.current_workflow = None
        else:
            self.current_workflow = self.workflow_instances[0]
            self.workflow_choice.SetSelection(0)

        file_open_bmp = wx.ArtProvider.GetBitmap(wx.ART_FILE_OPEN, wx.ART_TOOLBAR, t_size)
        tb_weather = self.primary_toolbar.AddTool(
            10, "Weather", file_open_bmp, wx.NullBitmap, wx.ITEM_NORMAL, "Weather", "Long help for 'Weather'", None
        )
        self.primary_toolbar.Bind(wx.EVT_TOOL, self.handle_tb_weather, tb_weather)

        forward_bmp = wx.ArtProvider.GetBitmap(wx.ART_GO_FORWARD, wx.ART_TOOLBAR, t_size)
        self.tb_run = self.primary_toolbar.AddTool(
            self.Identifiers.ToolBarRunButtonID, "Run", forward_bmp, wx.NullBitmap, wx.ITEM_NORMAL, "Run",
            "Long help for 'Run'", None
        )
        self.primary_toolbar.Bind(wx.EVT_TOOL, self.handle_tb_run, self.tb_run)

        error_bmp = wx.ArtProvider.GetBitmap(wx.ART_ERROR, wx.ART_TOOLBAR, t_size)
        self.primary_toolbar.AddTool(
            30, "Cancel", error_bmp, wx.NullBitmap, wx.ITEM_NORMAL, "Cancel", "Long help for 'Cancel'",
            None)

        self.primary_toolbar.AddSeparator()

        exe_bmp = wx.ArtProvider.GetBitmap(wx.ART_EXECUTABLE_FILE, wx.ART_TOOLBAR, t_size)
        self.primary_toolbar.AddTool(
            40, "IDF Editor", exe_bmp, wx.NullBitmap, wx.ITEM_NORMAL, "IDF Editor", "Long help for 'IDF Editor'", None
        )
        self.primary_toolbar.AddTool(
            50, "Text Editor", exe_bmp, wx.NullBitmap, wx.ITEM_NORMAL, "Text Editor", "Long help for 'Text Editor'",
            None
        )

        self.primary_toolbar.AddSeparator()

        folder_bmp = wx.ArtProvider.GetBitmap(wx.ART_FOLDER, wx.ART_TOOLBAR, t_size)
        self.primary_toolbar.AddTool(
            80, "Explorer", folder_bmp, wx.NullBitmap, wx.ITEM_NORMAL, "Explorer", "Long help for 'Explorer'", None
        )

        up_bmp = wx.ArtProvider.GetBitmap(wx.ART_GO_UP, wx.ART_TOOLBAR, t_size)
        self.primary_toolbar.AddTool(
            80, "Update", up_bmp, wx.NullBitmap, wx.ITEM_NORMAL, "Update", "Long help for 'Update'", None
        )

        remove_bmp = wx.ArtProvider.GetBitmap(wx.ART_MINUS, wx.ART_TOOLBAR, t_size)
        tb_hide_browser = self.primary_toolbar.AddTool(
            80, "File Browser", remove_bmp, wx.NullBitmap, wx.ITEM_CHECK, "File Browser",
            "Long help for 'File Browser'", None
        )
        self.primary_toolbar.Bind(wx.EVT_TOOL, self.handle_tb_hide_browser, tb_hide_browser)

        self.primary_toolbar.Realize()

    def gui_build_output_toolbar(self):
        t_size = (24, 24)
        self.output_toolbar = wx.ToolBar(self, style=wx.TB_HORIZONTAL | wx.NO_BORDER | wx.TB_FLAT | wx.TB_TEXT)
        self.output_toolbar.SetToolBitmapSize(t_size)

        norm_bmp = wx.ArtProvider.GetBitmap(wx.ART_NORMAL_FILE, wx.ART_TOOLBAR, t_size)

        self.output_toolbar.AddTool(
            10, "Table.html", norm_bmp, wx.NullBitmap, wx.ITEM_NORMAL, "Help", "Long help for 'Help'", None
        )
        self.output_toolbar.AddTool(
            10, "Meters.csv", norm_bmp, wx.NullBitmap, wx.ITEM_NORMAL, "Help", "Long help for 'Help'", None
        )
        self.output_toolbar.AddTool(
            10, ".csv", norm_bmp, wx.NullBitmap, wx.ITEM_NORMAL, "Help", "Long help for 'Help'", None
        )
        self.output_toolbar.AddTool(
            10, ".err", norm_bmp, wx.NullBitmap, wx.ITEM_NORMAL, "Help", "Long help for 'Help'", None
        )
        self.output_toolbar.AddTool(
            10, ".rdd", norm_bmp, wx.NullBitmap, wx.ITEM_NORMAL, "Help", "Long help for 'Help'", None
        )
        self.output_toolbar.AddTool(
            10, ".eio", norm_bmp, wx.NullBitmap, wx.ITEM_NORMAL, "Help", "Long help for 'Help'", None
        )
        self.output_toolbar.AddSeparator()
        self.output_toolbar.AddTool(
            10, ".dxf", norm_bmp, wx.NullBitmap, wx.ITEM_NORMAL, "Help", "Long help for 'Help'", None
        )
        self.output_toolbar.AddTool(
            10, ".mtd", norm_bmp, wx.NullBitmap, wx.ITEM_NORMAL, "Help", "Long help for 'Help'", None
        )
        self.output_toolbar.AddTool(
            10, ".bnd", norm_bmp, wx.NullBitmap, wx.ITEM_NORMAL, "Help", "Long help for 'Help'", None
        )
        self.output_toolbar.AddTool(
            10, ".eso", norm_bmp, wx.NullBitmap, wx.ITEM_NORMAL, "Help", "Long help for 'Help'", None
        )
        self.output_toolbar.AddTool(
            10, ".mtr", norm_bmp, wx.NullBitmap, wx.ITEM_NORMAL, "Help", "Long help for 'Help'", None
        )
        self.output_toolbar.AddTool(
            10, ".shd", norm_bmp, wx.NullBitmap, wx.ITEM_NORMAL, "Help", "Long help for 'Help'", None
        )
        self.output_toolbar.Realize()

    def gui_build_menu_bar(self):

        self.menu_bar = wx.MenuBar()

        file_menu = wx.Menu()
        self.menu_file_run = file_menu.Append(10, "Run File", "Run currently selected file for selected workflow")
        self.Bind(wx.EVT_MENU, self.handle_menu_file_run, self.menu_file_run)
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
        recent_folder_menu = folder_menu.Append(31, "Recent", "Recent folders where a workflow was run.")
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
        self.menu_bar.Enable(31, False)
        self.menu_bar.Enable(36, False)

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
        self.menu_bar.Enable(42, False)
        self.menu_bar.Enable(47, False)

        output_menu = wx.Menu()

        out_table_menu = wx.Menu()
        out_table_menu.Append(501, "Table.csv")
        out_table_menu.Append(502, "Table.tab")
        out_table_menu.Append(503, "Table.txt")
        out_table_menu.Append(504, "Table.html")
        out_table_menu.Append(505, "Table.xml")
        output_menu.Append(599, "Table", out_table_menu)

        out_variable_menu = wx.Menu()
        out_variable_menu.Append(506, ".csv")
        out_variable_menu.Append(507, ".tab")
        out_variable_menu.Append(508, ".txt")
        output_menu.Append(598, "Variables", out_variable_menu)

        out_meter_menu = wx.Menu()
        out_meter_menu.Append(509, "Meter.csv")
        out_meter_menu.Append(510, "Meter.tab")
        out_meter_menu.Append(511, "Meter.txt")
        output_menu.Append(597, "Meter", out_meter_menu)

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
        output_menu.Append(596, "Sizing", out_sizing_menu)

        out_delight_menu = wx.Menu()
        out_delight_menu.Append(527, "DElight.in")
        out_delight_menu.Append(528, "DElight.out")
        out_delight_menu.Append(529, "DElight.eldmp")
        out_delight_menu.Append(530, "DElight.dfdmp")
        output_menu.Append(595, "DElight", out_delight_menu)

        out_map_menu = wx.Menu()
        out_map_menu.Append(531, "Map.csv")
        out_map_menu.Append(532, "Map.tab")
        out_map_menu.Append(533, "Map.txt")
        output_menu.Append(594, "Map", out_map_menu)

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
        output_menu.Append(593, "bsmt", out_bsmt_menu)

        out_slab_menu = wx.Menu()
        out_slab_menu.Append(556, ".slab")
        out_slab_menu.Append(557, "_slab.out")
        out_slab_menu.Append(558, "_slab.ger")
        output_menu.Append(592, "slab", out_slab_menu)

        self.menu_bar.Append(output_menu, "&Output")

        options_menu = wx.Menu()
        option_version_menu = wx.Menu()
        option_version_menu.Append(711, "EnergyPlus 8.6.0")
        option_version_menu.Append(712, "EnergyPlus 8.7.0")
        option_version_menu.Append(713, "EnergyPlus 8.8.0")
        option_version_menu.Append(714, "EnergyPlus 8.9.0")
        options_menu.Append(71, "Version", option_version_menu)
        options_menu.AppendSeparator()
        menu_option_workflow_directories = options_menu.Append(72, "Workflow Directories...")
        self.Bind(wx.EVT_MENU, self.handle_menu_option_workflow_directories, menu_option_workflow_directories)
        menu_workflow_order = options_menu.Append(73, "Workflow Order...")
        self.Bind(wx.EVT_MENU, self.handle_menu_workflow_order, menu_workflow_order)
        options_menu.AppendSeparator()

        option_favorite_menu = wx.Menu()
        option_favorite_menu.Append(741, "4")
        option_favorite_menu.Append(742, "8")
        option_favorite_menu.Append(743, "12")
        option_favorite_menu.Append(744, "Clear")
        options_menu.Append(74, "Favorites", option_favorite_menu)

        option_recent_menu = wx.Menu()
        option_recent_menu.Append(741, "4")
        option_recent_menu.Append(742, "8")
        option_recent_menu.Append(743, "12")
        option_recent_menu.Append(744, "Clear")
        options_menu.Append(74, "Recent", option_recent_menu)

        options_menu.Append(75, "Remote...")
        menu_viewers = options_menu.Append(77, "Viewers...")
        self.Bind(wx.EVT_MENU, self.handle_menu_viewers, menu_viewers)
        options_menu.AppendSeparator()
        self.menu_output_toolbar = options_menu.Append(761, "<workspacename> Output Toolbar...")
        self.Bind(wx.EVT_MENU, self.handle_menu_output_toolbar, self.menu_output_toolbar)
        self.menu_columns = options_menu.Append(762, "<workspacename> Columns...")
        self.Bind(wx.EVT_MENU, self.handle_menu_columns, self.menu_columns)
        self.menu_command_line = options_menu.Append(763, "<workspacename> Command Line...")
        self.Bind(wx.EVT_MENU, self.handle_menu_command_line, self.menu_command_line)
        self.menu_bar.Append(options_menu, "&Settings")

        help_menu = wx.Menu()
        help_menu.Append(61, "EnergyPlus Getting Started")
        help_menu.Append(62, "EnergyPlus Input Output Reference")
        help_menu.Append(63, "EnergyPlus Output Details and Examples")
        help_menu.Append(64, "EnergyPlus Engineering Reference")
        help_menu.Append(65, "EnergyPlus Auxiliary Programs")
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

    def gui_build_status_bar(self):
        self.status_bar = self.CreateStatusBar(1)
        # self.status_bar.SetStatusText('Status bar - reports on simulations in progress')

    def handle_list_ctrl_selection(self, event):
        self.current_file_name = event.Item.Text

    def handle_menu_file_run(self, event):
        self.run_workflow()

    def handle_tb_run(self, event):
        self.run_workflow()

    def handle_workflow_done(self, event):
        status_message = 'Invalid workflow response'
        try:
            successful = event.data.success
            if successful:
                status_message = 'Successfully completed a workflow: ' + event.data.message
            else:
                status_message = 'Workflow failed: ' + event.data.message
        except Exception as e:
            status_message = 'Workflow response was invalid'
        self.status_bar.SetStatusText(status_message)
        self.workflow_worker = None
        self.primary_toolbar.EnableTool(self.Identifiers.ToolBarRunButtonID, True)

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
        # self.status_bar.SetStatusText("Dir-SelectionChanged")
        self.directory_name = self.directory_tree_control.GetPath()
        try:
            self.status_bar.SetStatusText(self.directory_name)
            self.update_file_lists()
        except:  # status_bar and things may not exist during initialization, just ignore
            pass
        event.Skip()

    def handle_choice_selection_change(self, event):
        self.current_workflow = self.workflow_instances[event.Selection]
        self.update_control_list_columns()
        self.update_file_lists()
        self.update_workflow_dependent_menu_items()
        self.status_bar.SetStatusText('Choice selection changed to ' + event.String)

    def handle_tb_weather(self, event):
        self.status_bar.SetStatusText('Clicked Weather toolbar item')

    def handle_tb_hide_browser(self, event):
        # the following remove the top pane of the right hand splitter
        if self.split_top_bottom.IsSplit():
            self.split_top_bottom.Unsplit(toRemove=self.right_bottom_pane)
        else:
            self.split_top_bottom.SplitHorizontally(self.right_top_pane, self.right_bottom_pane)

    def handle_menu_option_workflow_directories(self, event):
        workflow_dir_dialog = workflow_directories_dialog.WorkflowDirectoriesDialog(None, title='Workflow Directories')
        return_value = workflow_dir_dialog.ShowModal()
        print(return_value)
        # May need to refresh the main UI if something changed in the settings
        workflow_dir_dialog.Destroy()

    def handle_menu_workflow_order(self, event):

        items = [
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

        order = [0, 1, 2, 3, 4, 5, 6, 7, 8]

        dlg = wx.RearrangeDialog(None,
                                 "Arrange the workflows in the order to appear in the toolbar",
                                 "Workflow Order",
                                 order, items)

        if dlg.ShowModal() == wx.ID_OK:
            order = dlg.GetOrder()
            # for n in order:
            #     if n >= 0:
            #         wx.LogMessage("Your most preferred item is \"%s\"" % n)
            #         break

    def handle_menu_command_line(self, event):
        cmdline_dialog = command_line_dialog.CommandLineDialog(None)
        return_value = cmdline_dialog.ShowModal()
        print(return_value)
        # May need to refresh the main UI if something changed in the settings
        cmdline_dialog.Destroy()

    def handle_menu_output_toolbar(self, event):
        items = [
            "Table.htm.",
            "Meters.csv",
            ".csv",
            ".err",
            ".rdd",
            ".eio",
            ".dxf",
            ".mtd",
            ".bnd",
            ".eso",
            ".mtr"
        ]

        order = [0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10]

        dlg = wx.RearrangeDialog(None,
                                 "Arrange the buttons on the output toolbar",
                                 "<workspacename> Output Toolbar",
                                 order, items)

        if dlg.ShowModal() == wx.ID_OK:
            order = dlg.GetOrder()

    def handle_menu_columns(self, event):
        items = [
            "Status",
            "File Name",
            "Weather File",
            "Size",
            "Errors",
            "EUI",
            "Floor Area",
        ]

        order = [0, 1, 2, 3, 4, 5, 6]

        dlg = wx.RearrangeDialog(None,
                                 "Arrange the columns for the main grid",
                                 "<workspacename> Columns",
                                 order, items)

        if dlg.ShowModal() == wx.ID_OK:
            order = dlg.GetOrder()

    def handle_menu_viewers(self, event):
        file_viewer_dialog = viewer_dialog.ViewerDialog(None)
        return_value = file_viewer_dialog.ShowModal()
        print(return_value)
        # May need to refresh the main UI if something changed in the settings
        file_viewer_dialog.Destroy()
