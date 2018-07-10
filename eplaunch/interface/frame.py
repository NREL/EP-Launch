import datetime
import fnmatch
import json
import os
from gettext import gettext as _

import wx

from eplaunch.interface.filenamemenus.base import FileNameMenus
from eplaunch.interface import command_line_dialog
from eplaunch.interface import viewer_dialog
from eplaunch.interface import workflow_directories_dialog
from eplaunch.interface.externalprograms import EPLaunchExternalPrograms
from eplaunch.interface.workflow_processing import event_result, WorkflowThread
from eplaunch.utilities.cache import CacheFile
from eplaunch.utilities.exceptions import EPLaunchDevException, EPLaunchFileException
from eplaunch.utilities.filenamemanipulation import FileNameManipulation
from eplaunch.utilities.version import Version
from eplaunch.workflows import manager as workflow_manager
from eplaunch.utilities.locateworkflows import LocateWorkflows


# wx callbacks need an event argument even though we usually don't use it, so the next line disables that check
# noinspection PyUnusedLocal
class EpLaunchFrame(wx.Frame):
    WeatherFileKey = 'weather'

    class Identifiers:
        ToolBarRunButtonID = 20

    def __init__(self, *args, **kwargs):

        kwargs["style"] = wx.DEFAULT_FRAME_STYLE

        wx.Frame.__init__(self, *args, **kwargs)

        # Set the title!
        self.SetTitle(_("EP-Launch 3"))
        # set the window exit
        self.Bind(wx.EVT_CLOSE, self.handle_exit_box)

        # Get saved settings
        self.config = wx.Config("EP-Launch3")

        # initialize these here (and early) in the constructor to hush up the compiler messages
        self.primary_toolbar = None
        self.f = None
        self.output_toolbar = None
        self.tb_run = None
        self.menu_file_run = None
        self.menu_bar = None
        self.current_workflow = None
        self.workflow_instances = None
        self.workflow_choice = None
        self.workflow_directories = None
        self.directory_name = None
        self.current_file_name = None
        self.menu_output_toolbar = None
        self.menu_command_line = None
        self.status_bar = None
        self.raw_file_list = None
        self.control_file_list = None
        self.current_cache = None
        self.current_weather_file = None
        self.output_toolbar_icon_size = None
        self.directory_tree_control = None
        self.file_lists_splitter = None
        self.control_file_list_panel = None
        self.raw_file_list_panel = None
        self.folder_menu = None
        self.folder_recent = None
        self.folder_favorites = None
        self.weather_menu = None
        self.weather_recent = None
        self.weather_favorites = None
        self.output_menu = None
        self.extra_output_menu = None
        self.tb_idf_editor_id = None
        self.output_menu_item = None
        self.extra_output_menu_item = None
        self.current_selected_version = None

        # this is currently just a single background thread, eventually we'll need to keep a list of them
        self.workflow_worker = None

        # get the saved workflow directories
        self.retrieve_workflow_directories_config()

        # find workflow directories
        self.locate_workflows = LocateWorkflows()
        self.list_of_directories = self.locate_workflows.find()
        self.list_of_versions = self.locate_workflows.get_energyplus_versions()

        # build out the whole GUI and do other one-time inits here
        self.gui_build()
        self.reset_raw_list_columns()

        # this sets up an event handler for workflow completion events
        event_result(self, self.handle_workflow_done)

        # these are things that need to be done frequently
        self.update_control_list_columns()
        self.update_file_lists()
        self.update_workflow_dependent_menu_items()

        # get the saved active directory
        self.retrieve_current_directory_config()

        # create external program runner
        self.external_runner = EPLaunchExternalPrograms()
        # create file name manipulation object
        self.file_name_manipulator = FileNameManipulation()

    def close_frame(self):
        """May do additional things during close, including saving the current window state/settings"""
        self.save_config()
        self.Close()

    def handle_exit_box(self, event):
        self.save_config()
        self.Destroy()

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
        self.menu_command_line.SetText("%s Command Line..." % current_workflow_name)
        self.update_output_menu()
        self.update_output_toolbar()

    def update_output_menu(self):
        # remove all the old menu items first
        old_menu_items = self.output_menu.GetMenuItems()
        for old_menu_item in old_menu_items:
            old_id = old_menu_item.GetId()
            self.output_menu.Delete(old_id)
        # all all the new menu items
        output_suffixes = self.current_workflow.get_output_suffixes()
        output_suffixes.sort()
        number_of_items_in_main = 30
        if len(output_suffixes) < number_of_items_in_main:
            for count, suffix in enumerate(output_suffixes):
                self.output_menu_item = self.output_menu.Append(500 + count, suffix)
                self.Bind(wx.EVT_MENU, self.handle_output_menu_item, self.output_menu_item)
        else:
            main_suffixes = output_suffixes[:number_of_items_in_main]
            extra_suffixes = output_suffixes[number_of_items_in_main:]
            for count, suffix in enumerate(main_suffixes):
                self.output_menu_item = self.output_menu.Append(500 + count, suffix)
                self.Bind(wx.EVT_MENU, self.handle_output_menu_item, self.output_menu_item)
            self.extra_output_menu = wx.Menu()
            for count, suffix in enumerate(extra_suffixes):
                self.extra_output_menu_item = self.extra_output_menu.Append(550 + count, suffix)
                self.Bind(wx.EVT_MENU, self.handle_extra_output_menu_item, self.extra_output_menu_item)
            self.output_menu.Append(549, "Extra", self.extra_output_menu)

    def update_output_toolbar(self):
        # remove all the old menu items first
        self.output_toolbar.ClearTools()
        # add tools based on the workflow
        norm_bmp = wx.ArtProvider.GetBitmap(wx.ART_NORMAL_FILE, wx.ART_TOOLBAR, self.output_toolbar_icon_size)
        # disable_bmp = wx.ArtProvider.GetBitmap(wx.ART_MISSING_IMAGE, wx.ART_TOOLBAR, self.output_toolbar_icon_size)
        tb_output_suffixes = []
        output_suffixes = self.current_workflow.get_output_suffixes()
        if self.current_workflow.output_toolbar_order is None:
            tb_output_suffixes = output_suffixes[:15]
        else:
            for item in self.current_workflow.output_toolbar_order:
                if item >= 0:
                    tb_output_suffixes.append(output_suffixes[item])

        for count, tb_output_suffix in enumerate(tb_output_suffixes):
            out_tb_button = self.output_toolbar.AddTool(
                10 + count, tb_output_suffix, norm_bmp, wx.NullBitmap, wx.ITEM_NORMAL, tb_output_suffix,
                "Long help for " + tb_output_suffix,
                None
            )
            self.output_toolbar.Bind(wx.EVT_TOOL, self.handle_out_tb_button, out_tb_button)
            if count % 3 == 2:
                self.output_toolbar.AddSeparator()
        self.output_toolbar.Realize()

    def handle_out_tb_button(self, event):
        full_path_name = os.path.join(self.directory_name, self.current_file_name)
        tb_button = self.output_toolbar.FindById(event.GetId())
        output_file_name = self.file_name_manipulator.replace_extension_with_suffix(full_path_name, tb_button.Label)
        self.external_runner.run_program_by_extension(output_file_name)

    def update_control_list_columns(self):
        self.control_file_list.DeleteAllColumns()
        self.control_file_list.AppendColumn(_("File Name"), format=wx.LIST_FORMAT_LEFT, width=-1)
        self.control_file_list.AppendColumn(_("Weather File"), format=wx.LIST_FORMAT_LEFT, width=-1)
        current_workflow_columns = self.current_workflow.get_interface_columns()
        for current_column in current_workflow_columns:
            self.control_file_list.AppendColumn(_(current_column), format=wx.LIST_FORMAT_LEFT, width=-1)

    def reset_raw_list_columns(self):
        self.raw_file_list.AppendColumn(_("File Name"), format=wx.LIST_FORMAT_LEFT, width=-1)
        self.raw_file_list.AppendColumn(_("Date Modified"), format=wx.LIST_FORMAT_LEFT, width=-1)
        # self.raw_file_list.AppendColumn(_("Type"), format=wx.LIST_FORMAT_LEFT, width=-1)
        self.raw_file_list.AppendColumn(_("Size"), format=wx.LIST_FORMAT_RIGHT, width=-1)

    def get_files_in_directory(self):
        debug = False
        if debug:
            file_list = [
                {"name": "5Zone.idf", "size": 128, "modified": "1/2/3"},
                {"name": "6Zone.idf", "size": 256, "modified": "1/2/3"},
                {"name": "7Zone.idf", "size": 389, "modified": "1/2/3"},
                {"name": "8Zone.idf", "size": 495, "modified": "1/2/3"},
                {"name": "9Zone.what", "size": 529, "modified": "1/2/3"},
                {"name": "admin.html", "size": 639, "modified": "1/2/3"}
            ]
        else:
            if self.directory_name:
                file_list = []
                files = os.listdir(self.directory_name)
                for this_file in files:
                    if this_file.startswith('.'):
                        continue
                    file_path = os.path.join(self.directory_name, this_file)
                    if os.path.isdir(file_path):
                        continue
                    file_modified_time = os.path.getmtime(file_path)
                    modified_time_string = datetime.datetime.fromtimestamp(file_modified_time).replace(microsecond=0)
                    file_size_string = '{0:12,.0f} KB'.format(os.path.getsize(file_path) / 1024)  # size
                    file_list.append({"name": this_file, "size": file_size_string, "modified": modified_time_string})
            else:
                file_list = []
        file_list.sort(key=lambda x: x['name'])
        return file_list

    def update_file_lists(self):

        # if we don't have a directory name, it's probably during init, just ignore
        if not self.directory_name:
            return

        # get the local cache file path for this folder
        cache_file_path = os.path.join(self.directory_name, CacheFile.FileName)

        # if there is a cache file there, read the cached file data for the current workflow
        files_in_workflow = {}
        if os.path.exists(cache_file_path):
            file_blob = open(cache_file_path, 'r').read()
            content = json.loads(file_blob)
            workflows = content[CacheFile.RootKey]
            current_workflow_name = self.current_workflow.name()
            if current_workflow_name in workflows:
                files_in_workflow = workflows[current_workflow_name][CacheFile.FilesKey]

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
            file_modified = file_struct['modified']
            raw_list_rows.append([file_name, file_modified, file_size])
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
                if CacheFile.ParametersKey in cached_file_info:
                    if self.WeatherFileKey in cached_file_info[CacheFile.ParametersKey]:
                        full_weather_path = cached_file_info[CacheFile.ParametersKey][self.WeatherFileKey]
                        row.append(os.path.basename(full_weather_path))
                    else:
                        row.append('<no_weather_files>')
                else:
                    row.append('<no_weather_file>')
                for column in self.current_workflow.get_interface_columns():
                    if column in cached_file_info[CacheFile.ResultsKey]:
                        row.append(cached_file_info[CacheFile.ResultsKey][column])
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
                self.status_bar.SetLabel('Starting workflow', i=0)
                self.workflow_worker = WorkflowThread(
                    self, self.current_workflow, self.directory_name, self.current_file_name,
                    {'weather': self.current_weather_file}
                )
                self.tb_run.Enable(False)
                self.primary_toolbar.Realize()
                # self.menu_file_run.Enable(False)
            else:
                self.status_bar.SetLabel('A workflow is already running, concurrence will come soon...', i=0)
        else:
            self.status_bar.SetLabel(
                'Error: Make sure you select a directory and a file', i=0
            )

    def gui_build(self):

        self.gui_build_menu_bar()

        # build the left/right main splitter
        main_left_right_splitter = wx.SplitterWindow(self, wx.ID_ANY)

        # build tree view and add it to the left pane
        directory_tree_panel = wx.Panel(main_left_right_splitter, wx.ID_ANY)
        self.directory_tree_control = wx.GenericDirCtrl(directory_tree_panel, -1, size=(600, 525),
                                                        style=wx.DIRCTRL_DIR_ONLY)
        tree = self.directory_tree_control.GetTreeCtrl()
        self.Bind(wx.EVT_TREE_ITEM_RIGHT_CLICK, self.handle_dir_right_click, tree)
        self.Bind(wx.EVT_TREE_SEL_CHANGED, self.handle_dir_selection_changed, tree)
        self.directory_tree_control.SelectPath("/tmp/test")
        directory_tree_sizer = wx.BoxSizer(wx.VERTICAL)
        directory_tree_sizer.Add(self.directory_tree_control, 1, wx.EXPAND, 0)
        directory_tree_panel.SetSizer(directory_tree_sizer)

        # build list views and add to the right pane
        file_lists_panel = wx.Panel(main_left_right_splitter, wx.ID_ANY)
        self.file_lists_splitter = wx.SplitterWindow(file_lists_panel, wx.ID_ANY)

        # build control list view (top right)
        self.control_file_list_panel = wx.Panel(self.file_lists_splitter, wx.ID_ANY)
        self.control_file_list = wx.ListCtrl(self.control_file_list_panel, wx.ID_ANY,
                                             style=wx.LC_HRULES | wx.LC_REPORT | wx.LC_VRULES)
        self.Bind(wx.EVT_LIST_ITEM_SELECTED, self.handle_list_ctrl_selection, self.control_file_list)
        control_file_list_sizer = wx.BoxSizer(wx.VERTICAL)
        control_file_list_sizer.Add(self.control_file_list, 1, wx.EXPAND, 0)
        self.control_file_list_panel.SetSizer(control_file_list_sizer)

        # build raw list view (bottom right)
        self.raw_file_list_panel = wx.Panel(self.file_lists_splitter, wx.ID_ANY)
        self.raw_file_list = wx.ListCtrl(self.raw_file_list_panel, wx.ID_ANY,
                                         style=wx.LC_HRULES | wx.LC_REPORT | wx.LC_VRULES)
        raw_file_list_sizer = wx.BoxSizer(wx.VERTICAL)
        raw_file_list_sizer.Add(self.raw_file_list, 1, wx.EXPAND, 0)
        self.raw_file_list_panel.SetSizer(raw_file_list_sizer)

        # not sure why but it works better if you make the split and unsplit it right away
        self.file_lists_splitter.SetMinimumPaneSize(20)
        self.file_lists_splitter.SplitHorizontally(self.control_file_list_panel, self.raw_file_list_panel)
        self.file_lists_splitter.Unsplit(toRemove=self.raw_file_list_panel)

        sizer_right = wx.BoxSizer(wx.HORIZONTAL)
        sizer_right.Add(self.file_lists_splitter, 1, wx.EXPAND, 0)

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

        # get the window size and position
        previous_height = self.config.ReadInt("/ActiveWindow/height")
        previous_width = self.config.ReadInt("/ActiveWindow/width")
        previous_x = self.config.ReadInt("/ActiveWindow/x")
        previous_y = self.config.ReadInt("/ActiveWindow/y")
        self.SetSize(previous_x, previous_y, previous_width, previous_height)

        # call this to finalize
        self.Layout()

    def gui_build_primary_toolbar(self):

        self.primary_toolbar = wx.ToolBar(self, style=wx.TB_HORIZONTAL | wx.NO_BORDER | wx.TB_FLAT | wx.TB_TEXT)

        t_size = (24, 24)
        self.primary_toolbar.SetToolBitmapSize(t_size)

        self.workflow_instances, workflow_choice_strings = self.update_workflow_list()
        self.workflow_choice = wx.Choice(self.primary_toolbar, choices=workflow_choice_strings)

        # So, on my Mac, the workflow_choice went invisible when I left the AddControl call in there
        # There was space where it obviously went, but it was invisible
        # This needs to be remedied, big time, but until then, on this branch I am:
        #  - removing the call to AddControl, thus the dropdown will show up, but not be aligned properly, then
        #  -  making it really wide so that I can easily click it on the right half of the toolbar
        self.workflow_choice.Size = (700, -1)
        # self.primary_toolbar.AddControl(self.workflow_choice)

        self.primary_toolbar.Bind(wx.EVT_CHOICE, self.handle_choice_selection_change, self.workflow_choice)

        if not self.workflow_instances:
            self.current_workflow = None
        else:
            previous_workflow = self.config.Read('/ActiveWindow/SelectedWorkflow')
            if previous_workflow:
                found = False
                for index, workflow_choice_string in enumerate(workflow_choice_strings):
                    if previous_workflow in workflow_choice_string:
                        self.current_workflow = self.workflow_instances[index]
                        self.workflow_choice.SetSelection(index)
                        found = True
                        break
                if not found:
                    self.current_workflow = self.workflow_instances[0]
                    self.workflow_choice.SetSelection(0)
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
        self.tb_idf_editor_id = 40
        tb_idf_editor = self.primary_toolbar.AddTool(
            self.tb_idf_editor_id, "IDF Editor", exe_bmp, wx.NullBitmap, wx.ITEM_NORMAL, "IDF Editor",
            "Long help for 'IDF Editor'", None
        )
        self.primary_toolbar.Bind(wx.EVT_TOOL, self.handle_tb_idf_editor, tb_idf_editor)

        tb_text_editor = self.primary_toolbar.AddTool(
            50, "Text Editor", exe_bmp, wx.NullBitmap, wx.ITEM_NORMAL, "Text Editor", "Long help for 'Text Editor'",
            None
        )
        self.primary_toolbar.Bind(wx.EVT_TOOL, self.handle_tb_text_editor, tb_text_editor)

        self.primary_toolbar.AddSeparator()

        folder_bmp = wx.ArtProvider.GetBitmap(wx.ART_FOLDER, wx.ART_TOOLBAR, t_size)
        self.primary_toolbar.AddTool(
            80, "Explorer", folder_bmp, wx.NullBitmap, wx.ITEM_NORMAL, "Explorer", "Long help for 'Explorer'", None
        )

        up_bmp = wx.ArtProvider.GetBitmap(wx.ART_GO_UP, wx.ART_TOOLBAR, t_size)
        tb_update_file_version = self.primary_toolbar.AddTool(
            90, "Update", up_bmp, wx.NullBitmap, wx.ITEM_NORMAL, "Update", "Long help for 'Update'", None
        )
        self.primary_toolbar.Bind(wx.EVT_TOOL, self.handle_tb_update_file_version, tb_update_file_version)

        remove_bmp = wx.ArtProvider.GetBitmap(wx.ART_MINUS, wx.ART_TOOLBAR, t_size)
        tb_hide_all_files_pane = self.primary_toolbar.AddTool(
            100, "All Files", remove_bmp, wx.NullBitmap, wx.ITEM_CHECK, "All Files",
            "Long help for 'Show All Files Pane'", None
        )
        self.primary_toolbar.Bind(wx.EVT_TOOL, self.handle_tb_hide_all_files_pane, tb_hide_all_files_pane)

        self.primary_toolbar.Realize()

    def gui_build_output_toolbar(self):
        # initializes the toolbar the
        self.output_toolbar_icon_size = (16, 15)
        self.output_toolbar = wx.ToolBar(self, style=wx.TB_HORIZONTAL | wx.NO_BORDER | wx.TB_FLAT | wx.TB_TEXT)
        self.output_toolbar.SetToolBitmapSize(self.output_toolbar_icon_size)
        wx.ArtProvider.GetBitmap(wx.ART_NORMAL_FILE, wx.ART_TOOLBAR, self.output_toolbar_icon_size)
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

        self.folder_menu = wx.Menu()
        self.folder_menu.Append(301, "Recent", "Recent folders where a workflow as run.")
        self.folder_menu.Append(302, kind=wx.ITEM_SEPARATOR)
        self.folder_menu.Append(303, kind=wx.ITEM_SEPARATOR)
        self.folder_recent = FileNameMenus(self.folder_menu, 302, 303, self.config, "/FolderMenu/Recent")
        self.folder_recent.retrieve_config()
        for menu_item in self.folder_recent.menu_items_for_files:
            self.Bind(wx.EVT_MENU, self.handle_folder_recent_menu_selection, menu_item)

        self.folder_menu.Append(304, "Favorites")
        self.folder_menu.Append(305, kind=wx.ITEM_SEPARATOR)
        self.folder_menu.Append(306, kind=wx.ITEM_SEPARATOR)
        self.folder_favorites = FileNameMenus(self.folder_menu, 305, 306, self.config, "/FolderMenu/Favorite")
        self.folder_favorites.retrieve_config()
        for menu_item in self.folder_favorites.menu_items_for_files:
            self.Bind(wx.EVT_MENU, self.handle_folder_favorites_menu_selection, menu_item)

        add_current_folder_to_favorites = self.folder_menu.Append(307, "Add Current Folder to Favorites")
        self.Bind(wx.EVT_MENU, self.handle_add_current_folder_to_favorites_menu_selection,
                  add_current_folder_to_favorites)
        remove_current_folder_from_favorites = self.folder_menu.Append(308, "Remove Current Folder from Favorites")
        self.Bind(wx.EVT_MENU, self.handle_remove_current_folder_from_favorites_menu_selection,
                  remove_current_folder_from_favorites)
        self.menu_bar.Append(self.folder_menu, "F&older")
        # disable the menu items that are just information
        self.menu_bar.Enable(301, False)
        self.menu_bar.Enable(304, False)

        self.weather_menu = wx.Menu()
        menu_weather_select = self.weather_menu.Append(401, "Select..")
        self.Bind(wx.EVT_MENU, self.handle_menu_weather_select, menu_weather_select)
        self.weather_menu.Append(402, kind=wx.ITEM_SEPARATOR)
        self.weather_menu.Append(403, "Recent")
        self.weather_menu.Append(404, kind=wx.ITEM_SEPARATOR)
        self.weather_menu.Append(405, kind=wx.ITEM_SEPARATOR)
        self.weather_recent = FileNameMenus(self.weather_menu, 404, 405, self.config, "/WeatherMenu/Recent")
        self.weather_recent.retrieve_config()
        for menu_item in self.weather_recent.menu_items_for_files:
            self.Bind(wx.EVT_MENU, self.handle_weather_recent_menu_selection, menu_item)

        self.weather_menu.Append(406, "Favorites")
        self.weather_menu.Append(407, kind=wx.ITEM_SEPARATOR)
        self.weather_menu.Append(408, kind=wx.ITEM_SEPARATOR)
        add_current_weather_to_favorites = self.weather_menu.Append(409, "Add Weather to Favorites")
        self.Bind(wx.EVT_MENU, self.handle_add_current_weather_to_favorites_menu_selection,
                  add_current_weather_to_favorites)
        remove_current_weather_from_favorites = self.weather_menu.Append(410, "Remove Weather from Favorites")
        self.Bind(wx.EVT_MENU, self.handle_remove_current_weather_from_favorites_menu_selection,
                  remove_current_weather_from_favorites)
        self.weather_favorites = FileNameMenus(self.weather_menu, 407, 408, self.config, "/WeatherMenu/Favorite")
        self.weather_favorites.retrieve_config()
        for menu_item in self.weather_favorites.menu_items_for_files:
            self.Bind(wx.EVT_MENU, self.handle_weather_favorites_menu_selection, menu_item)

        self.menu_bar.Append(self.weather_menu, "&Weather")
        # disable the menu items that are just information
        self.menu_bar.Enable(403, False)
        self.menu_bar.Enable(406, False)

        self.output_menu = wx.Menu()
        self.menu_bar.Append(self.output_menu, "&Output")

        options_menu = wx.Menu()
        self.option_version_menu = wx.Menu()
        for index, version_info in enumerate(self.list_of_versions):
            version_string = version_info['version']
            specific_version_menu = self.option_version_menu.Append(710 + index, version_string, kind=wx.ITEM_RADIO)
            self.Bind(wx.EVT_MENU, self.handle_specific_version_menu, specific_version_menu)
        options_menu.Append(71, "Version", self.option_version_menu)
        self.retrieve_selected_version_config()
        options_menu.AppendSeparator()
        menu_option_workflow_directories = options_menu.Append(72, "Workflow Directories...")
        self.Bind(wx.EVT_MENU, self.handle_menu_option_workflow_directories, menu_option_workflow_directories)
        menu_workflow_order = options_menu.Append(73, "Workflow Order...")
        self.Bind(wx.EVT_MENU, self.handle_menu_workflow_order, menu_workflow_order)
        options_menu.AppendSeparator()

        # for now do not allow changing of the number of favorites
        # option_favorite_menu = wx.Menu()
        # option_favorite_menu.Append(741, "4")
        # option_favorite_menu.Append(742, "8")
        # option_favorite_menu.Append(743, "12")
        # option_favorite_menu.Append(744, "Clear")
        # options_menu.Append(74, "Favorites", option_favorite_menu)

        # for now do not allow changing of the number of recent
        # option_recent_menu = wx.Menu()
        # option_recent_menu.Append(741, "4")
        # option_recent_menu.Append(742, "8")
        # option_recent_menu.Append(743, "12")
        # option_recent_menu.Append(744, "Clear")
        # options_menu.Append(74, "Recent", option_recent_menu)

        options_menu.Append(75, "Remote...")
        menu_viewers = options_menu.Append(77, "Viewers...")
        self.Bind(wx.EVT_MENU, self.handle_menu_viewers, menu_viewers)
        options_menu.AppendSeparator()
        self.menu_output_toolbar = options_menu.Append(761, "<workspacename> Output Toolbar...")
        self.Bind(wx.EVT_MENU, self.handle_menu_output_toolbar, self.menu_output_toolbar)
        self.menu_command_line = options_menu.Append(763, "<workspacename> Command Line...")
        self.Bind(wx.EVT_MENU, self.handle_menu_command_line, self.menu_command_line)
        self.menu_bar.Append(options_menu, "&Settings")

        self.help_menu = wx.Menu()
        self.help_menu.AppendSeparator()
        self.help_menu.Append(612, "Check for Updates..")
        self.help_menu.Append(613, "View Entire Update List on Web..")
        self.help_menu.AppendSeparator()
        self.help_menu.Append(614, "Using EP-Launch Help")
        self.help_menu.Append(615, "About EP-Launch")
        self.current_selected_version = self.get_current_selected_version()
        self.current_workflow_directory = self.locate_workflows.get_workflow_directory(self.current_selected_version)
        self.populate_help_menu()
        self.menu_bar.Append(self.help_menu, "&Help")

        self.SetMenuBar(self.menu_bar)

    def gui_build_status_bar(self):
        self.status_bar = self.CreateStatusBar(3)
        # self.status_bar.SetStatusText('Status bar - reports on simulations in progress')

    def handle_list_ctrl_selection(self, event):
        self.current_file_name = event.Item.Text
        self.update_output_file_status()
        self.enable_disable_idf_editor_button()

    def handle_menu_file_run(self, event):
        self.folder_recent.add_recent(self.directory_tree_control.GetPath())
        self.run_workflow()

    def handle_tb_run(self, event):
        self.folder_recent.add_recent(self.directory_tree_control.GetPath())
        if not self.current_weather_file:
            self.current_weather_file = ''
        self.current_cache.add_config(
            self.current_workflow.name(), self.current_file_name, {'weather': self.current_weather_file}
        )
        self.current_cache.write()
        self.run_workflow()
        self.update_output_file_status()

    def handle_workflow_done(self, event):
        status_message = 'Invalid workflow response'
        try:
            successful = event.data.success
            if successful:
                status_message = 'Successfully completed a workflow: ' + event.data.message
                try:
                    data_from_workflow = event.data.column_data
                    self.current_cache.add_result(
                        self.current_workflow.name(), self.current_file_name, data_from_workflow
                    )
                    self.current_cache.write()
                    self.update_file_lists()
                except EPLaunchFileException:
                    pass
            else:
                status_message = 'Workflow failed: ' + event.data.message
        except Exception as e:  # noqa -- there is *no* telling what all exceptions could occur inside a workflow
            print(e)
            status_message = 'Workflow response was invalid'
        self.status_bar.SetStatusText(status_message, i=0)
        self.workflow_worker = None
        self.primary_toolbar.EnableTool(self.Identifiers.ToolBarRunButtonID, True)

    def handle_menu_file_cancel_selected(self, event):
        self.status_bar.SetStatusText('Clicked File->CancelSelected', i=0)

    def handle_menu_file_cancel_all(self, event):
        self.status_bar.SetStatusText('Clicked File->CancelAll', i=0)

    def handle_menu_file_quit(self, event):
        self.close_frame()
        self.status_bar.SetStatusText('Quitting Program', i=0)

    def handle_menu_edit_undo(self, event):
        self.status_bar.SetStatusText('Clicked Edit->Undo', i=0)

    def handle_menu_edit_cut(self, event):
        self.status_bar.SetStatusText('Clicked Edit->Cut', i=0)

    def handle_menu_edit_copy(self, event):
        self.status_bar.SetStatusText('Clicked Edit->Copy', i=0)

    def handle_menu_edit_paste(self, event):
        self.status_bar.SetStatusText('Clicked Edit->Paste', i=0)

    def handle_dir_item_selected(self, event):
        self.status_bar.SetStatusText("Dir-ItemSelected", i=0)
        # event.Skip()

    def handle_dir_right_click(self, event):
        self.status_bar.SetStatusText("Dir-RightClick", i=0)
        # event.Skip()

    def handle_dir_selection_changed(self, event):
        # self.status_bar.SetStatusText("Dir-SelectionChanged")
        self.directory_name = self.directory_tree_control.GetPath()
        # manage the check marks when changing directories
        self.folder_recent.uncheck_all()
        self.folder_recent.put_checkmark_on_item(self.directory_name)
        self.folder_favorites.uncheck_all()
        self.folder_favorites.put_checkmark_on_item(self.directory_name)
        self.current_cache = CacheFile(self.directory_name)
        try:
            self.status_bar.SetStatusText(self.directory_name, i=0)
            self.update_file_lists()
        except Exception as e:  # noqa -- status_bar and things may not exist during initialization, just ignore
            print(e)
            pass
        event.Skip()

    def handle_choice_selection_change(self, event):
        self.current_workflow = self.workflow_instances[event.Selection]
        self.update_control_list_columns()
        self.update_file_lists()
        self.update_workflow_dependent_menu_items()
        self.status_bar.SetStatusText('Choice selection changed to ' + event.String, i=0)

    def handle_tb_weather(self, event):
        filename = wx.FileSelector("Select a weather file", wildcard="EnergyPlus Weather File(*.epw)|*.epw",
                                   flags=wx.FD_OPEN | wx.FD_FILE_MUST_EXIST)
        self.current_weather_file = filename
        self.weather_recent.uncheck_all()
        self.weather_recent.add_recent(filename)
        self.weather_favorites.uncheck_all()
        self.weather_favorites.put_checkmark_on_item(filename)
        self.status_bar.SetStatusText('Weather: ' + self.current_weather_file, i=1)

    def handle_tb_hide_all_files_pane(self, event):
        # the following remove the top pane of the right hand splitter
        if self.file_lists_splitter.IsSplit():
            self.file_lists_splitter.Unsplit(toRemove=self.raw_file_list_panel)
        else:
            self.file_lists_splitter.SplitHorizontally(self.control_file_list_panel, self.raw_file_list_panel)

    def handle_menu_option_workflow_directories(self, event):
        workflow_dir_dialog = workflow_directories_dialog.WorkflowDirectoriesDialog(None, title='Workflow Directories')
        workflow_dir_dialog.set_listbox(self.workflow_directories)
        return_value = workflow_dir_dialog.ShowModal()
        if return_value == wx.ID_OK:
            self.workflow_directories = workflow_dir_dialog.list_of_directories
            print(self.workflow_directories)
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

        output_suffixes = self.current_workflow.get_output_suffixes()

        if self.current_workflow.output_toolbar_order is None:
            order = []
            for count, suffix in enumerate(output_suffixes):
                if count < 15:
                    order.append(count)
                else:
                    order.append(-count)
        else:
            order = self.current_workflow.output_toolbar_order

        dlg = wx.RearrangeDialog(None,
                                 "Arrange the buttons on the output toolbar",
                                 "{} Output Toolbar".format(self.current_workflow.name()),
                                 order, output_suffixes)

        if dlg.ShowModal() == wx.ID_OK:
            order = dlg.GetOrder()
            print(order)
            self.current_workflow.output_toolbar_order = order
            self.update_output_toolbar()

    def handle_menu_viewers(self, event):
        file_viewer_dialog = viewer_dialog.ViewerDialog(None)
        return_value = file_viewer_dialog.ShowModal()
        print(return_value)
        # May need to refresh the main UI if something changed in the settings
        file_viewer_dialog.Destroy()

    def save_config(self):
        self.folder_favorites.save_config()
        self.folder_recent.save_config()
        self.weather_favorites.save_config()
        self.weather_recent.save_config()
        self.save_workflow_directories_config()
        self.save_currect_directory_config()
        self.save_selected_workflow_config()
        self.save_window_size()
        self.save_selected_version_config()

    def handle_menu_weather_select(self, event):
        filename = wx.FileSelector("Select a weather file", wildcard="EnergyPlus Weather File(*.epw)|*.epw",
                                   flags=wx.FD_OPEN | wx.FD_FILE_MUST_EXIST)
        self.current_weather_file = filename
        self.weather_recent.uncheck_all()
        self.weather_recent.add_recent(filename)
        self.weather_favorites.uncheck_all()
        self.weather_favorites.put_checkmark_on_item(filename)
        self.status_bar.SetStatusText('Weather: ' + self.current_weather_file, i=1)

    def handle_folder_recent_menu_selection(self, event):
        menu_item = self.folder_menu.FindItemById(event.GetId())
        print('from frame.py - folder recent clicked menu item:', menu_item.GetLabel(), menu_item.GetId())
        self.folder_recent.uncheck_other_items(menu_item)
        real_path = os.path.abspath(menu_item.GetLabel())
        self.directory_tree_control.SelectPath(real_path, True)
        self.directory_tree_control.ExpandPath(real_path)

    def handle_folder_favorites_menu_selection(self, event):
        menu_item = self.folder_menu.FindItemById(event.GetId())
        print('from frame.py - folder favorites clicked menu item:', menu_item.GetLabel(), menu_item.GetId())
        self.folder_favorites.uncheck_other_items(menu_item)
        real_path = os.path.abspath(menu_item.GetLabel())
        self.directory_tree_control.SelectPath(real_path, True)
        self.directory_tree_control.ExpandPath(real_path)

    def handle_add_current_folder_to_favorites_menu_selection(self, event):
        self.folder_favorites.add_favorite(self.directory_tree_control.GetPath())

    def handle_remove_current_folder_from_favorites_menu_selection(self, event):
        self.folder_favorites.remove_favorite(self.directory_tree_control.GetPath())

    def handle_weather_recent_menu_selection(self, event):
        menu_item = self.weather_menu.FindItemById(event.GetId())
        print('from frame.py - weather recent clicked menu item:', menu_item.GetLabel(), menu_item.GetId())
        self.current_weather_file = menu_item.GetLabel()
        self.weather_recent.uncheck_all()
        self.weather_recent.put_checkmark_on_item(self.current_weather_file)
        self.weather_favorites.uncheck_all()
        self.weather_favorites.put_checkmark_on_item(self.current_weather_file)
        self.status_bar.SetStatusText('Weather: ' + self.current_weather_file, i=1)

    def handle_weather_favorites_menu_selection(self, event):
        menu_item = self.weather_menu.FindItemById(event.GetId())
        print('from frame.py - weather favorites clicked menu item:', menu_item.GetLabel(), menu_item.GetId())
        self.current_weather_file = menu_item.GetLabel()
        self.weather_recent.uncheck_all()
        self.weather_recent.put_checkmark_on_item(self.current_weather_file)
        self.weather_favorites.uncheck_all()
        self.weather_favorites.put_checkmark_on_item(self.current_weather_file)
        self.status_bar.SetStatusText('Weather: ' + self.current_weather_file, i=1)

    def handle_add_current_weather_to_favorites_menu_selection(self, event):
        self.weather_favorites.add_favorite(self.current_weather_file)

    def handle_remove_current_weather_from_favorites_menu_selection(self, event):
        self.weather_favorites.remove_favorite(self.current_weather_file)

    def update_output_file_status(self):
        file_name_no_ext, extension = os.path.splitext(self.current_file_name)
        full_path_name_no_ext = os.path.join(self.directory_name, file_name_no_ext)
        self.disable_output_menu_items()
        self.enable_existing_menu_items(full_path_name_no_ext)
        self.disable_output_toolbar_buttons()
        self.enable_existing_output_toolbar_buttons(full_path_name_no_ext)

    def disable_output_menu_items(self):
        output_menu_items = self.output_menu.GetMenuItems()
        for output_menu_item in output_menu_items:
            if output_menu_item.GetLabel() != "Extra":
                output_menu_item.Enable(False)
        if self.extra_output_menu is not None:
            extra_output_menu_items = self.extra_output_menu.GetMenuItems()
            for extra_output_menu_item in extra_output_menu_items:
                extra_output_menu_item.Enable(False)

    def enable_existing_menu_items(self, path_no_ext):
        output_menu_items = self.output_menu.GetMenuItems()
        for output_menu_item in output_menu_items:
            if output_menu_item.GetLabel() != "Extra":
                if os.path.exists(path_no_ext + output_menu_item.GetLabel()):
                    output_menu_item.Enable(True)
        if self.extra_output_menu is not None:
            extra_output_menu_items = self.extra_output_menu.GetMenuItems()
            for extra_output_menu_item in extra_output_menu_items:
                if os.path.exists(path_no_ext + extra_output_menu_item.GetLabel()):
                    extra_output_menu_item.Enable(True)

    def disable_output_toolbar_buttons(self):
        number_of_tools = self.output_toolbar.GetToolsCount()
        for tool_num in range(number_of_tools):
            cur_tool = self.output_toolbar.GetToolByPos(tool_num)
            cur_id = cur_tool.GetId()
            self.output_toolbar.EnableTool(cur_id, False)
        self.output_toolbar.Realize()

    def enable_existing_output_toolbar_buttons(self, path_no_ext):
        number_of_tools = self.output_toolbar.GetToolsCount()
        for tool_num in range(number_of_tools):
            cur_tool = self.output_toolbar.GetToolByPos(tool_num)
            cur_id = cur_tool.GetId()
            if os.path.exists(path_no_ext + cur_tool.GetLabel()):
                self.output_toolbar.EnableTool(cur_id, True)
        self.output_toolbar.Realize()

    def handle_tb_update_file_version(self, event):
        full_path_name = os.path.join(self.directory_name, self.current_file_name)
        v = Version()
        is_version_found, version_string, version_number = v.check_energyplus_version(full_path_name)
        print(is_version_found, version_string, version_number)

    def handle_tb_idf_editor(self, event):
        full_path_name = os.path.join(self.directory_name, self.current_file_name)
        self.external_runner.run_idf_editor(full_path_name)

    def handle_tb_text_editor(self, event):
        full_path_name = os.path.join(self.directory_name, self.current_file_name)
        self.external_runner.run_text_editor(full_path_name)

    def enable_disable_idf_editor_button(self):
        file_name_no_ext, extension = os.path.splitext(self.current_file_name)
        self.primary_toolbar.EnableTool(self.tb_idf_editor_id, extension.upper() == ".IDF")
        self.output_toolbar.Realize()

    def save_workflow_directories_config(self):
        # in Windows using RegEdit these appear in:
        #    HKEY_CURRENT_USER\Software\EP-Launch3
        self.config.WriteInt("/WorkflowDirectories/Count", len(self.workflow_directories))
        # save menu items to configuration file
        for count, workflow_directory in enumerate(self.workflow_directories):
            self.config.Write("/WorkflowDirectories/Path-{:02d}".format(count), workflow_directory)

    def retrieve_workflow_directories_config(self):
        count_directories = self.config.ReadInt("/WorkflowDirectories/Count", 0)
        list_of_directories = []
        for count in range(0, count_directories):
            directory = self.config.Read("/WorkflowDirectories/Path-{:02d}".format(count))
            if directory:
                if os.path.exists(directory):
                    list_of_directories.append(directory)
        self.workflow_directories = list_of_directories

    def handle_output_menu_item(self, event):
        full_path_name = os.path.join(self.directory_name, self.current_file_name)
        menu_item = self.output_menu.FindItemById(event.GetId())
        output_file_name = self.file_name_manipulator.replace_extension_with_suffix(full_path_name,
                                                                                    menu_item.GetLabel())
        self.external_runner.run_program_by_extension(output_file_name)

    def handle_extra_output_menu_item(self, event):
        full_path_name = os.path.join(self.directory_name, self.current_file_name)
        menu_item = self.extra_output_menu.FindItemById(event.GetId())
        output_file_name = self.file_name_manipulator.replace_extension_with_suffix(full_path_name,
                                                                                    menu_item.GetLabel())
        self.external_runner.run_program_by_extension(output_file_name)

    def save_currect_directory_config(self):
        if self.directory_name:
            self.config.Write("/ActiveWindow/CurrentDirectory", self.directory_name)
        if self.current_file_name:
            self.config.Write("/ActiveWindow/CurrentFileName", self.current_file_name)

    def retrieve_current_directory_config(self):
        possible_directory_name = self.config.Read("/ActiveWindow/CurrentDirectory")
        if possible_directory_name:
            self.directory_name = possible_directory_name
            real_path = os.path.abspath(self.directory_name)
            self.directory_tree_control.SelectPath(real_path, True)
            self.directory_tree_control.ExpandPath(real_path)

    def save_selected_workflow_config(self):
        self.config.Write("/ActiveWindow/SelectedWorkflow", self.current_workflow.name())

    def save_window_size(self):
        current_size = self.GetSize()
        self.config.WriteInt("/ActiveWindow/height", current_size.height)
        self.config.WriteInt("/ActiveWindow/width", current_size.width)
        current_position = self.GetPosition()
        self.config.WriteInt("/ActiveWindow/x", current_position.x)
        self.config.WriteInt("/ActiveWindow/y", current_position.y)

    def handle_specific_version_menu(self, event):
        menu_item = self.option_version_menu.FindItemById(event.GetId())
        self.current_selected_version = self.get_current_selected_version()
        self.current_workflow_directory = self.locate_workflows.get_workflow_directory(self.current_selected_version)
        print('from frame.py - specific version menu item:', menu_item.GetLabel(), menu_item.GetId(), self.current_workflow_directory)
        self.populate_help_menu()

    def retrieve_selected_version_config(self):
        possible_selected_version = self.config.Read("/ActiveWindow/CurrentVersion")
        menu_list = self.option_version_menu.GetMenuItems()
        for menu_item in menu_list:
            if menu_item.GetLabel() == possible_selected_version:
                menu_item.Check(True)
                break

    def get_current_selected_version(self):
        self.current_selected_version = None
        menu_list = self.option_version_menu.GetMenuItems()
        for menu_item in menu_list:
            if menu_item.IsChecked():
                self.current_selected_version = menu_item.GetLabel()
                break
        return self.current_selected_version

    def save_selected_version_config(self):
        self.get_current_selected_version()
        if self.current_selected_version:
            self.config.Write("/ActiveWindow/CurrentVersion", self.current_selected_version)

    def populate_help_menu(self):
        self.remove_old_help_menu_items()
        energyplus_application_directory, _ = os.path.split(self.current_workflow_directory)
        energyplus_documentation_directory = os.path.join(energyplus_application_directory, 'Documentation')
        if not os.path.exists(energyplus_documentation_directory):
            return
        documentation_files = os.listdir(energyplus_documentation_directory)
        for index, doc in enumerate(documentation_files):
            specific_documentation_menu = self.help_menu.Insert(index, 620 + index, doc, helpString=os.path.join(energyplus_documentation_directory, doc))
            self.Bind(wx.EVT_MENU, self.handle_specific_documentation_menu, specific_documentation_menu)

    def remove_old_help_menu_items(self):
        menu_list = self.help_menu.GetMenuItems()
        for menu_item in menu_list:
            if not menu_item.IsSeparator():
                self.help_menu.Remove(menu_item)
            else:
                break

    def handle_specific_documentation_menu(self, event):
        menu_item = self.help_menu.FindItemById(event.GetId())
        documentation_item_full_path = menu_item.GetHelp()
        self.external_runner.run_program_by_extension(documentation_item_full_path)
