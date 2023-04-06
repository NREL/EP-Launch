from datetime import datetime
from fnmatch import fnmatch

from json import dumps
from mimetypes import guess_type
from pathlib import Path
from platform import system
from queue import Queue

from subprocess import Popen
from tkinter import Tk, PhotoImage, StringVar, Menu, DISABLED, OptionMenu, Frame, Label, Button, NSEW, \
    SUNKEN, S, LEFT, BOTH, messagebox, END, BooleanVar, ACTIVE, LabelFrame, RIGHT, EW, PanedWindow, NS, filedialog
from tkinter.ttk import Combobox
from typing import Dict, List, Optional, Tuple
from uuid import uuid4
from webbrowser import open as open_web
from plan_tools.runtime import fixup_taskbar_icon_on_windows

from eplaunch import VERSION, DOCS_URL, NAME
from eplaunch.interface.dialog_generic import TkGenericDialog
from eplaunch.utilities.exceptions import EPLaunchFileException
from eplaunch.interface.config import ConfigManager
from eplaunch.interface.widget_dir_list import DirListScrollableFrame
from eplaunch.interface.widget_file_list import FileListScrollableFrame
from eplaunch.interface.dialog_external_viewers import TkViewerDialog
from eplaunch.interface.dialog_weather import TkWeatherDialog
from eplaunch.interface.dialog_workflow_dirs import TkWorkflowsDialog
from eplaunch.interface.dialog_output import TkOutputDialog
from eplaunch.workflows.workflow_thread import WorkflowThread
from eplaunch.utilities.cache import CacheFile
from eplaunch.workflows.base import EPLaunchWorkflowResponse1
from eplaunch.workflows.manager import WorkflowManager
from eplaunch.workflows.workflow import Workflow


class EPLaunchWindow(Tk):

    # region Construction and GUI building functions

    def __init__(self):
        super().__init__(className=NAME)
        # set the form title and icon, basic stuff
        self.title("EnergyPlus Launch")
        if system() == 'Darwin':
            self.icon_path = Path(__file__).resolve().parent.parent / 'icons' / 'icon.icns'
            if self.icon_path.exists():
                self.iconbitmap(str(self.icon_path))
            else:
                print(f"Could not set icon for Mac, expecting to find it at {self.icon_path}")
        elif system() == 'Windows':
            self.icon_path = Path(__file__).resolve().parent.parent / 'icons' / 'icon.png'
            img = PhotoImage(file=str(self.icon_path))
            if self.icon_path.exists():
                self.iconphoto(False, img)
            else:
                print(f"Could not set icon for Windows, expecting to find it at {self.icon_path}")
        else:  # Linux
            self.icon_path = Path(__file__).resolve().parent.parent / 'icons' / 'icon.png'
            img = PhotoImage(file=str(self.icon_path))
            if self.icon_path.exists():
                self.iconphoto(False, img)
            else:
                print(f"Could not set icon for Windows, expecting to find it at {self.icon_path}")
        fixup_taskbar_icon_on_windows(NAME)
        self.pad = {'padx': 3, 'pady': 3}
        self.dd_only_string = '<No_Weather_File>'  # Can we change to just using blank?  It's fine for now.
        self.generic_dialogs = TkGenericDialog(self.pad)

        # initialize variables which will track output dialogs
        self.dialog_counter: int = 0
        self.output_dialogs: Dict[str, TkOutputDialog] = {}

        # create a config manager and load up the saved, or default, configuration
        self.conf = ConfigManager()
        self.conf.load()

        # initialize some dir/file selection variables
        self.previous_selected_directory: Optional[Path] = None
        self.current_cache: Optional[CacheFile] = None

        # create a workflow manager, it will initialize (EnergyPlus) workflows in predetermined locations
        self.workflow_manager = WorkflowManager()
        # but now, if the saved configuration exists, use that as the list of directories to use moving forward
        if self.conf.workflow_directories:
            self.workflow_manager.workflow_directories = self.conf.workflow_directories
        # now that we have a list of workflows, instantiate any/all of them
        self.workflow_manager.instantiate_all_workflows()
        if len(self.workflow_manager.warnings) > 0:
            self.generic_dialogs.display(
                self, 'Workflow Processing Errors', '\n'.join(self.workflow_manager.warnings)
            )

        # set up the GUI update queue
        self._gui_queue = Queue()
        self._check_queue()

        # set up some tk tracking variables and then build the GUI itself
        self._define_tk_variables()
        self._build_gui()

        # start filling in the UI with contents, optionally from the previous config
        self.available_workflows: List[Workflow] = []  # stores workflows under the current context
        self._init = True
        self._repopulate_workflow_context_menu()
        self._repopulate_workflow_instance_menu()
        self._repopulate_recent_weather_list()
        self._rebuild_recent_folder_menu()
        self._rebuild_favorite_folder_menu()
        self._rebuild_group_menu()
        self._init = False

        # finally set the initial directory and update the file listing
        self.dir_tree.dir_list.refresh_listing(self.conf.directory)
        self._update_file_list()

        # set the minimum size and redraw the app
        self.minsize(1050, 400)
        self.update()

        # one time update of the status bar
        self._update_status_bar("Program Initialized")

        # potentially show a welcome screen if we are on a new version
        self._open_welcome()

        # bind key presses for the app
        self.bind('<Key>', self._handle_keyboard_press)

    def _define_tk_variables(self):
        self._tk_var_workflow_context = StringVar(value='<context>')
        self._tk_var_workflow_instance = StringVar(value='<instance>')
        self._tk_var_output_suffix = StringVar(value='<output')
        self._tk_var_status_dir = StringVar(value="Selected dir")
        self._tk_var_status_workflow = StringVar(value="Selected workflow")
        self._tk_var_status_message = StringVar(value="Status Message")
        self._tk_var_weather_recent = StringVar(value="<recent>")

    def _build_gui(self):
        self._build_top_menu()

        top_action_bar = Frame(self)
        self._build_top_icon_bar(top_action_bar)
        top_action_bar.grid(row=0, column=0, sticky=NSEW)

        listing_frame = Frame(self)
        self._build_listings(listing_frame)
        listing_frame.grid(row=1, column=0, sticky=NSEW)

        status_frame = Frame(self)
        self._build_status_bar(status_frame)
        status_frame.grid(row=2, column=0, sticky=NSEW)

        self.grid_rowconfigure(1, weight=1)
        self.grid_columnconfigure(0, weight=1)

        height = max(self.conf.height, 500)
        width = max(self.conf.width, 1000)
        x = max(self.conf.x, 128)
        y = max(self.conf.y, 128)
        self.wm_geometry(f"{width}x{height}+{x}+{y}")

    def _build_top_menu(self):
        menubar = Menu(self)

        menu_file = Menu(menubar, tearoff=False)
        menu_file.add_command(label="Run Current Workflow on Selection", command=self._run_workflow)
        menu_file.add_command(label="Quit", command=self.window_close)
        menubar.add_cascade(label="File", menu=menu_file)

        menu_nav = Menu(menubar, tearoff=False)
        self.menu_nav_recent = Menu(menu_nav, tearoff=False)
        menu_nav.add_cascade(label="Recent", menu=self.menu_nav_recent)
        menu_nav.add_command(label="Navigate to previous folder", command=self._navigate_to_previous_folder)
        menu_nav.add_separator()
        self.menu_nav_favorites = Menu(menu_nav, tearoff=False)
        menu_nav.add_cascade(label="Favorites", menu=self.menu_nav_favorites)
        menu_nav.add_command(label="Add Current Folder to Favorites", command=self.add_folder_to_favorites)
        menu_nav.add_command(label="Remove Current Folder from Favorites", command=self.remove_folder_from_favorites)
        menu_nav.add_separator()
        self.menu_nav_group = Menu(menu_nav, tearoff=False)
        menu_nav.add_cascade(label="Current Group", menu=self.menu_nav_group)
        menu_nav.add_command(label="Clear Current Group", command=self._clear_group)
        menu_nav.add_command(label="Load new Group file...", command=self._load_new_group_file)
        menu_nav.add_command(label="Save Current Group to file...", command=self._save_group_file)
        menu_nav.add_command(
            label="Add current folder to current group", command=self._add_current_dir_to_group
        )
        menu_nav.add_command(
            label="Add current file selection to current group", command=self._add_current_files_to_group
        )
        menu_nav.add_command(
            label="Remove current folder from current group", command=self._remove_current_dir_from_group
        )
        menu_nav.add_command(
            label="Remove current file selection from current group", command=self._remove_current_files_from_group
        )
        menu_nav.add_command(
            label="Cycle through current group entries", command=self._cycle_through_group
        )
        menubar.add_cascade(label="Navigation", menu=menu_nav)

        menu_settings = Menu(menubar, tearoff=False)
        menu_settings.add_command(label="Workflow Directories", command=self._open_workflow_dir_dialog)
        self._tk_var_keep_dialogs_open = BooleanVar(value=True)
        menu_settings.add_checkbutton(
            label="Keep Output Dialog Open", onvalue=True, offvalue=False, variable=self._tk_var_keep_dialogs_open
        )

        def _update_keep_dialog_open(*_):
            """Called whenever the checkbox is checked, updates configuration value"""
            self.conf.keep_dialog_open = self._tk_var_keep_dialogs_open.get()

        self._tk_var_keep_dialogs_open.trace('w', _update_keep_dialog_open)
        menu_settings.add_command(label="Viewers...", command=self._open_viewers_dialog)
        menubar.add_cascade(label="Settings", menu=menu_settings)

        menu_help = Menu(menubar, tearoff=False)
        menu_help.add_command(label="EP-Launch Documentation", command=self._open_documentation)
        menu_help.add_command(label="About...", command=self._open_about)
        menubar.add_cascade(label="Help", menu=menu_help)

        self.config(menu=menubar)

    # noinspection SqlNoDataSourceInspection
    def _build_top_icon_bar(self, container: Frame):
        lf = LabelFrame(container, text="Workflow Operations")
        Label(lf, text="Context:", justify=RIGHT).grid(row=0, column=0, **self.pad)
        self.option_workflow_context = OptionMenu(lf, self._tk_var_workflow_context, '<context>')
        self.option_workflow_context.grid(row=0, column=1, sticky=EW, **self.pad)
        Label(lf, text="Workflow: ", justify=RIGHT).grid(row=1, column=0, **self.pad)
        self.option_workflow_instance = OptionMenu(lf, self._tk_var_workflow_instance, '<instance>')
        self.option_workflow_instance.grid(row=1, column=1, sticky=EW, **self.pad)
        Button(
            lf, text=u"\U000025B6 Run Workflow on Current File(s)", command=self._run_workflow
        ).grid(row=2, column=0, columnspan=2, sticky=EW, **self.pad)
        lf.grid(row=0, column=0, **self.pad)

        lf = LabelFrame(container, text="Weather")
        Label(lf, text="Set Weather from Recent or from File").grid(row=0, column=0, columnspan=3, **self.pad)
        Label(lf, text="Recent: ", justify=RIGHT).grid(row=1, column=0, **self.pad)
        self.option_weather_recent = Combobox(lf, textvariable=self._tk_var_weather_recent)
        self.option_weather_recent.grid(row=1, column=1, **self.pad)
        self.option_weather_recent['state'] = 'readonly'
        self.button_weather_set = Button(lf, text=u"\U00002713 Set", command=self._set_weather_from_recent)
        self.button_weather_set.grid(row=1, column=2, **self.pad)
        self.button_weather_select = Button(
            lf, text=u"\U0001f325 Select Weather From Disk...", command=self._open_weather_dialog
        )
        self.button_weather_select.grid(row=2, column=0, columnspan=3, sticky=EW, **self.pad)
        lf.grid(row=0, column=1, sticky=NS, **self.pad)

        lf = LabelFrame(container, text="File/Folder Actions")
        Label(lf, text="Open Output: ", justify=RIGHT).grid(row=0, column=0, **self.pad)
        self.option_workflow_outputs = Combobox(lf, textvariable=self._tk_var_output_suffix)
        self.option_workflow_outputs.grid(row=0, column=1, **self.pad)
        self.option_workflow_outputs['state'] = 'readonly'
        self.button_open_output_file = Button(lf, text=u"\U0001f325 Open", command=self._open_output_file)
        self.button_open_output_file.grid(row=0, column=2, **self.pad)
        self.button_open_in_text = Button(
            lf, text=u"\U0001F5B9 Open Selected File in Text Editor", command=self._open_text_editor, state=DISABLED
        )
        self.button_open_in_text.grid(row=1, column=0, columnspan=3, sticky=EW, **self.pad)
        Button(
            lf, text=u"\U0001F5C0 Open Dir in File Browser", command=self._open_file_browser
        ).grid(row=2, column=0, columnspan=3, sticky=EW, **self.pad)
        lf.grid(row=0, column=2, **self.pad)

    def _build_listings(self, container: Frame):
        pw = PanedWindow(container)  # default horizontal
        self.dir_tree = DirListScrollableFrame(pw, on_select=self._new_dir_selected, on_root_changed=self._new_root_dir)
        pw.add(self.dir_tree)
        self.file_list = FileListScrollableFrame(container, on_selection_changed=self._callback_file_selection_changed)
        pw.add(self.file_list)
        pw.pack(fill=BOTH, expand=True, **self.pad)

    def _build_status_bar(self, container: Frame):
        Label(container, relief=SUNKEN, anchor=S, textvariable=self._tk_var_status_dir).pack(
            side=LEFT, fill=BOTH, expand=True
        )
        Label(container, relief=SUNKEN, anchor=S, textvariable=self._tk_var_status_workflow).pack(
            side=LEFT, fill=BOTH, expand=True
        )
        Label(container, relief=SUNKEN, anchor=S, textvariable=self._tk_var_status_message).pack(
            side=LEFT, fill=BOTH, expand=True
        )

    def _check_queue(self):
        """Checks the GUI queue for actions and sets a timer to check again each time"""
        while True:
            # noinspection PyBroadException
            try:
                task = self._gui_queue.get(block=False)
                self.after_idle(task)
            except Exception:
                break
        self.after(100, self._check_queue)

    # endregion

    # region main window run/close/update functions

    def run(self):
        """Main entry point to register a close handler and execute the app main loop"""
        self.protocol('WM_DELETE_WINDOW', self.window_close)
        self.mainloop()

    def window_close(self, *_):
        # block for running threads
        if len(self.workflow_manager.threads) > 0:
            msg = 'Program closing, but there are threads running; would you like to kill the threads and close?'
            if messagebox.askyesno(msg):
                for thread_id in self.workflow_manager.threads:
                    try:
                        self.workflow_manager.threads[thread_id].abort()
                        self.output_dialogs[thread_id].close()
                    except Exception as e:
                        print("Tried to abort thread, but something went awry: " + str(e))
            else:
                return  # will leave the window open
        # close completed windows
        keys = list(self.output_dialogs.keys())
        for dialog_id in keys:
            self.output_dialogs[dialog_id].close()
        # save the configuration and close
        self.conf.x = self.winfo_x()
        self.conf.y = self.winfo_y()
        self.conf.width = self.winfo_width()
        self.conf.height = self.winfo_height()
        self.conf.save()
        self.destroy()

    def _update_status_bar(self, message: str) -> None:
        """Updates all the status bar entries for current status and status by setting tk variables"""
        if self.conf.directory:
            self._tk_var_status_dir.set(str(self.conf.directory))
        else:
            self._tk_var_status_dir.set('<No Directory>')
        if self.workflow_manager.current_workflow:
            self._tk_var_status_workflow.set(self.workflow_manager.current_workflow.description)
        else:
            self._tk_var_status_workflow.set('<No Workflow>')
        self._tk_var_status_message.set(message)

    def _handle_keyboard_press(self, event) -> None:
        # Update docs/navigation.rst whenever this set of keybindings changes
        # relevant_modifiers
        # mod_shift = 0x1
        mod_control = 0x4
        # mod_alt = 0x20000
        if event.keysym == 'F5':
            self._update_file_list()
        elif event.keysym == 'w' and mod_control & event.state:
            self._open_weather_dialog()
        elif event.keysym == 'r' and mod_control & event.state:
            self._run_workflow()
        elif event.keysym == 'm' and mod_control & event.state:
            self._cycle_through_group()
        elif event.keysym == 'z' and mod_control & event.state:
            self._navigate_to_previous_folder()

    # endregion

    # region group operations

    def _clear_group(self):
        self.conf.group_locations.clear()
        self._rebuild_group_menu()

    def _load_new_group_file(self):
        group_file_path = filedialog.askopenfilename(
            title="Load a new EPLaunch Group File",
            initialdir=self.conf.directory,
            filetypes=(("EP-Launch Group Files", "*.epg"),)
        )
        if not group_file_path:
            return
        group_file_path_object = Path(group_file_path)
        entries = group_file_path_object.read_text().splitlines()
        self.conf.group_locations = []
        for e in sorted(entries):
            if e:
                self.conf.group_locations.append(Path(e))
        self._rebuild_group_menu()

    def _save_group_file(self):
        group_file_path = filedialog.asksaveasfilename(
            title="Save EPLaunch Group File",
            initialdir=self.conf.directory,
            filetypes=(("EP-Launch Group Files", "*.epg"),)
        )
        if not group_file_path:
            return
        group_file_path_object = Path(group_file_path)
        try:
            group_file_path_object.write_text('\n'.join([str(p) for p in self.conf.group_locations]))
        except Exception as e:  # could be permission or just about anything
            messagebox.showerror("Error", f"Could not save group file, error message:\n{str(e)}")
            return

    def _add_current_dir_to_group(self):
        if self.conf.directory in self.conf.group_locations:
            messagebox.showwarning("Warning", "This folder already exists in this group, skipping")
            return
        self.conf.group_locations.append(self.conf.directory)
        self._rebuild_group_menu()

    def _add_current_files_to_group(self):
        if len(self.conf.file_selection) == 0:
            messagebox.showwarning("Warning", "No files selected, so none added to current group")
            return
        issue_warning = False
        for f in self.conf.file_selection:
            potential_path = self.conf.directory / f
            if potential_path in self.conf.group_locations:
                issue_warning = True
            else:
                self.conf.group_locations.append(potential_path)
        if issue_warning:
            messagebox.showwarning("Warning", "At least one file path was already in the group and skipped")
        self._rebuild_group_menu()

    def _remove_current_dir_from_group(self):
        if self.conf.directory not in self.conf.group_locations:
            messagebox.showwarning("Warning", "This folder isn't in the current group, not doing anything")
            return
        self.conf.group_locations.remove(self.conf.directory)
        self._rebuild_group_menu()

    def _remove_current_files_from_group(self):
        issue_warning = False
        for f in self.conf.file_selection:
            potential_path = self.conf.directory / f
            if potential_path in self.conf.group_locations:
                self.conf.group_locations.remove(potential_path)
            else:
                issue_warning = True
        if issue_warning:
            messagebox.showwarning("Warning", "At least one file path was not in the current group and was skipped")
        self._rebuild_group_menu()

    def _cycle_through_group(self):
        if len(self.conf.group_locations) == 0:
            messagebox.showwarning("Invalid Group Cycle", "Could not cycle through empty group list")
            return
        self._handle_group_selection(self.group_cycle_next_index)
        self.group_cycle_next_index += 1
        if self.group_cycle_next_index + 1 > len(self.conf.group_locations):
            self.group_cycle_next_index = 0

    def _rebuild_group_menu(self):
        self.group_cycle_next_index = 0
        self.menu_nav_group.delete(0, END)
        for index, entry in enumerate(self.conf.group_locations):
            self.menu_nav_group.add_command(
                label=str(entry), command=lambda i=index: self._handle_group_selection(i)
            )

    def _handle_group_selection(self, index: int):
        entry = self.conf.group_locations[index]
        if not entry.exists():
            messagebox.showerror("Error", f"Could not navigate to group entry, it doesn't exist: {entry}")
            return
        self.conf.directory = entry if entry.is_dir() else entry.parent
        self.dir_tree.dir_list.refresh_listing(self.conf.directory)
        self._update_file_list()
        if entry.is_file():
            self.file_list.tree.try_to_reselect([entry.name])

    # endregion

    # region handling file/folder navigation

    def _repopulate_control_list_columns(self):
        """Rebuilds the file list columns based on the current workflow status and column headers"""
        # add stale if the current workflow supports output suffixes
        column_list = []
        if len(self.workflow_manager.current_workflow.output_suffixes) > 0:
            column_list.append('Stale')
        # if the current workflow is set (should always be) extend the array dynamically
        if self.workflow_manager.current_workflow:
            if self.workflow_manager.current_workflow.uses_weather:
                column_list.append("Weather")
            column_list.extend(self.workflow_manager.current_workflow.columns)
        # ask the file listing widget to update columns
        self.file_list.tree.set_new_columns(column_list)

    def add_folder_to_favorites(self):
        if self.conf.directory in self.conf.folders_favorite:
            messagebox.showwarning("Favorite Selection", "Folder already exists in favorites, skipping")
            return
        self.conf.folders_favorite.append(self.conf.directory)
        self._rebuild_favorite_folder_menu()

    def remove_folder_from_favorites(self):
        if self.conf.directory not in self.conf.folders_favorite:
            messagebox.showwarning("Favorite Selection", "Folder is not in favorites, skipping")
            return
        self.conf.folders_favorite.remove(self.conf.directory)
        self._rebuild_favorite_folder_menu()

    def _rebuild_favorite_folder_menu(self):
        self.menu_nav_favorites.delete(0, END)
        for index, folder in enumerate(self.conf.folders_favorite):
            self.menu_nav_favorites.add_command(
                label=str(folder), command=lambda i=index: self._handle_favorite_folder_selection(i)
            )

    def _handle_favorite_folder_selection(self, folder_index: int):
        self.conf.directory = self.conf.folders_favorite[folder_index]
        self.dir_tree.dir_list.refresh_listing(self.conf.directory)
        self._update_file_list()

    def _rebuild_recent_folder_menu(self):
        self.menu_nav_recent.delete(0, END)
        for index, folder in enumerate(self.conf.folders_recent):
            self.menu_nav_recent.add_command(
                label=str(folder), command=lambda i=index: self._handle_recent_folder_selection(i)
            )

    def _navigate_to_previous_folder(self):
        if len(self.conf.folders_recent) > 1:
            self._handle_recent_folder_selection(1)

    def _handle_recent_folder_selection(self, folder_index: int):
        self.conf.directory = self.conf.folders_recent[folder_index]
        self.dir_tree.dir_list.refresh_listing(self.conf.directory)
        self._update_file_list()

    def _get_files_in_current_directory(self, workflow_file_patterns: List[str]) -> List[Tuple[str, str, str, str]]:
        """
        Returns a list of file information for each file in the currently selected directory
        :param workflow_file_patterns: List of file patterns that this workflow supports, for filtering
        :return: A list of tuples which each contain (file name, file type, file size, modified time) for each file
        """
        file_list = []
        # loop over all non-hidden files to retrieve data for each
        for iter_path in self.conf.directory.glob('*'):
            if iter_path.is_file() and not iter_path.name.startswith('.'):
                base_name = iter_path.name
                # check to see if this file type matches any of the workflow patterns
                for file_type in workflow_file_patterns:
                    if fnmatch(base_name, file_type):
                        break  # breaks out of for loop, allowing processing to continue 3 lines down
                else:  # if we never broke, we will hit this else block
                    continue  # in which case, we want to skip this file, so continue the outer for loop
                file_size = iter_path.stat().st_size
                file_modified_time = iter_path.lstat().st_mtime
                modified_time_string = str(datetime.fromtimestamp(file_modified_time).replace(microsecond=0))
                file_size_string = '{0:12,.0f} KB'.format(file_size / 1024)  # size
                guessed_type = guess_type(base_name)[0]
                file_type_string = "(unknown)" if guessed_type is None else guessed_type
                file_list.append((base_name, file_type_string, file_size_string, modified_time_string))
        # sort the list and return it
        file_list.sort(key=lambda x: x[0])
        return file_list

    def _new_dir_selected(self, _: bool, selected_path: Path):
        self.previous_selected_directory = self.conf.directory
        self.conf.directory = selected_path
        if len(self.conf.folders_recent) > 0 and self.conf.folders_recent[0] != selected_path:
            self.conf.folders_recent.appendleft(selected_path)
        self._rebuild_recent_folder_menu()
        self.current_cache = CacheFile(self.conf.directory)
        try:
            self._update_status_bar(f"Selected directory: {self.conf.directory}")
            self._update_file_list()
        except Exception as e:  # noqa -- status_bar and things may not exist during initialization, just ignore
            print(str(e))  # log it to the console for fun

    def _new_root_dir(self, new_root_path: Path):
        self._new_dir_selected(True, new_root_path)

    def _update_file_list(self):
        """Update the file listing widget by querying the directory and cache contents, try to reselect current files"""
        # If selected directory hasn't been set up yet then just carry on, this is only happening during app init
        if self._init or not self.conf.directory:
            return

        # If we aren't in a directory, just warn and abort, should not really be possible to get him after init
        if not self.conf.directory.exists() or not self.conf.directory.is_dir():
            self._update_status_bar(f"Bad directory selection: {self.conf.directory}")
            return

        # If we are staying in the same directory, try to select the files that were previously selected
        if self.previous_selected_directory == self.conf.directory:
            previous_selected_files = self.conf.file_selection
        else:
            previous_selected_files = []

        # there should be a cache file there, so get the cached data for the current workflow if it exists
        files_in_current_workflow = {}
        workflow_file_patterns = []
        workflow_columns = []
        if self.workflow_manager.current_workflow:
            files_in_current_workflow = self.current_cache.get_files_for_workflow(
                self.workflow_manager.current_workflow.name
            )
            workflow_file_patterns = self.workflow_manager.current_workflow.file_types
            workflow_columns = self.workflow_manager.current_workflow.columns

        # then get the entire list of files in the current directory to build up the listview items
        # if they happen to match the filename in the workflow cache, then add that info to the row structure
        control_list_rows = []
        files_in_dir = self._get_files_in_current_directory(workflow_file_patterns)
        for file_structure in files_in_dir:
            # always add the columns to the raw list for all files
            file_name = file_structure[0]
            # listview row always includes the filename itself, so start the array with that
            row = [file_name]
            # if it in the cache then the listview row can include additional data
            if file_name in files_in_current_workflow:
                # potentially add a stale column token
                response = self._is_file_stale(file_name)
                if response is None:  # doesn't support stale, so ignore
                    pass
                elif response:  # does support stale and it's true
                    row.append('*')
                else:  # does support stale and it's not
                    row.append('')
                cached_file_info = files_in_current_workflow[file_name]
                if self.workflow_manager.current_workflow.uses_weather:
                    if CacheFile.ParametersKey in cached_file_info:
                        if CacheFile.WeatherFileKey in cached_file_info[CacheFile.ParametersKey]:
                            full_weather_path = cached_file_info[CacheFile.ParametersKey][CacheFile.WeatherFileKey]
                            weather_path_object = Path(full_weather_path)
                            row.append(weather_path_object.name)
                        else:
                            row.append('<no_weather_files>')
                    else:
                        row.append('<no_weather_file>')
                if CacheFile.ResultsKey in cached_file_info:
                    for column in workflow_columns:
                        if column in cached_file_info[CacheFile.ResultsKey]:
                            row.append(cached_file_info[CacheFile.ResultsKey][column])

            # always add the row to the main list
            control_list_rows.append(row)

        # clear all items from the listview and then add them back in
        self.file_list.tree.set_files(control_list_rows)
        if previous_selected_files:
            self.file_list.tree.try_to_reselect(previous_selected_files)

    def _is_file_stale(self, input_file_name: str) -> Optional[bool]:
        """
        Returns a tri-state value trying to characterize whether the current file is "stale."
        It tries to determine this based on the output suffixes of the current workflow.
        If the current workflow does not include any output suffixes, "stale" cannot be determined.
        If '.err' is in the output suffixes, this is the only suffix checked.

        :returns: None if stale cannot be determined, True if it is stale, and False if not.
        """
        if len(self.workflow_manager.current_workflow.output_suffixes) == 0:
            return None  # can't support stale without output suffixes
        full_file_path = self.conf.directory / input_file_name
        if full_file_path.exists():
            input_file_date = full_file_path.lstat().st_mtime
            suffixes = self.workflow_manager.current_workflow.output_suffixes
            if '.err' in suffixes:  # for energyplus workflows just use the err file
                suffixes = ['.err']
            file_name_no_ext = full_file_path.with_suffix('').name
            for suffix in suffixes:
                tentative_output_file_path = self.conf.directory / (file_name_no_ext + suffix)
                if tentative_output_file_path.exists():
                    output_file_date = tentative_output_file_path.lstat().st_mtime
                    if output_file_date < input_file_date:
                        return True
        return False

    def _callback_file_selection_changed(self, selected_file_names: List[str]) -> None:
        """This gets called back by the file listing widget when a selection changes"""
        self.conf.file_selection = selected_file_names
        status = ACTIVE if len(self.conf.file_selection) > 0 else DISABLED
        self.button_open_in_text['state'] = status

    # endregion

    # region weather operations

    def set_weather_widget_state(self, weather_enabled) -> None:
        self.option_weather_recent.configure(state=weather_enabled)
        self.button_weather_select.configure(state=weather_enabled)
        self.button_weather_set.configure(state=weather_enabled)

    def _repopulate_recent_weather_list(self, try_to_select: Optional[Path] = None):
        recent_weather = self.conf.weathers_recent
        combobox_weather_enabled = 'readonly' if len(recent_weather) > 0 else 'disabled'
        button_weather_enabled = ACTIVE if len(recent_weather) > 0 else DISABLED
        self.option_weather_recent.configure(state=combobox_weather_enabled)
        self.button_weather_set.configure(state=button_weather_enabled)

        if button_weather_enabled == ACTIVE:
            if try_to_select:
                desired_weather_path = str(try_to_select)
            else:
                desired_weather_path = str(self.conf.weathers_recent[self.option_weather_recent.current()])
            self.option_weather_recent['values'] = [x.name for x in recent_weather]
            self.option_weather_recent.current(0)
            for i, r in enumerate(recent_weather):
                if str(r) == desired_weather_path:
                    self.option_weather_recent.current(i)
                    break
        else:
            self.option_weather_recent['values'] = []

    def _set_weather_from_recent(self) -> None:
        current_index = self.option_weather_recent.current()
        selected_recent_weather_string = str(self.conf.weathers_recent[current_index])
        for selected_file_name in self.conf.file_selection:
            self.current_cache.add_config(
                self.workflow_manager.current_workflow.name,
                selected_file_name,
                {'weather': selected_recent_weather_string}
            )
        self._update_file_list()

    def _open_weather_dialog(self) -> None:
        dialog_weather = TkWeatherDialog(
            self, list(self.conf.weathers_recent), self.conf.weathers_favorite
        )
        self.wait_window(dialog_weather)
        if dialog_weather.exit_code == TkWeatherDialog.CLOSE_SIGNAL_CANCEL:
            return
        if not dialog_weather.selected_weather_file:
            weather_file_to_use = self.dd_only_string
        else:
            weather_file_to_use = dialog_weather.selected_weather_file
            if weather_file_to_use not in self.conf.weathers_recent:
                self.conf.weathers_recent.appendleft(weather_file_to_use)
                self._repopulate_recent_weather_list(weather_file_to_use)
        for selected_file_name in self.conf.file_selection:
            self.current_cache.add_config(
                self.workflow_manager.current_workflow.name,
                selected_file_name,
                {'weather': str(weather_file_to_use)}
            )
        self._update_file_list()

    # endregion

    # region workflow running, tracking, callbacks and handlers

    def _repopulate_workflow_context_menu(self):
        """Clears and repopulates the workflow context menu; tries to reselect the last context saved in config"""
        # save the currently selected workflow context for later
        desired_selected_workflow_context = self.conf.cur_workflow_context
        # get all known contexts from the workflow manager
        all_available_contexts = sorted(list(self.workflow_manager.workflow_contexts))
        # clear the context menu entirely
        self.option_workflow_context['menu'].delete(0, END)
        # add in all the contexts, registering a lambda that will set the tk var and request a workflow list update
        for opt in all_available_contexts:
            self.option_workflow_context['menu'].add_command(
                label=opt, command=lambda c=opt: self._handler_workflow_context_option_changed(c)
            )
        # call the handler method with either the saved context name, or the top one in the list
        if desired_selected_workflow_context in all_available_contexts:
            self._handler_workflow_context_option_changed(desired_selected_workflow_context)
        else:
            self._handler_workflow_context_option_changed(all_available_contexts[0])

    def _handler_workflow_context_option_changed(self, new_value: str):
        """This is called when the workflow context option menu changes value"""
        # set the tk var and the config var to the new value
        self._tk_var_workflow_context.set(new_value)
        self.conf.cur_workflow_context = self._tk_var_workflow_context.get()
        # then refresh the workflow list with the new context
        self._repopulate_workflow_instance_menu()

    def _repopulate_workflow_instance_menu(self):
        """Clears and repopulates the workflow instance menu; tries to reselect the last instance saved in config"""
        # save the currently selected workflow instance for later
        desired_selected_workflow_name = self.conf.cur_workflow_name
        # get all known workflows for the current context
        self.available_workflows = self.workflow_manager.workflow_instances(self.conf.cur_workflow_context)
        # clear the option menu entirely
        self.option_workflow_instance['menu'].delete(0, END)
        # add in all the instances, registering a lambda that will set the tk var and refresh the file list as needed
        just_names = []
        for w in self.available_workflows:
            workflow_name = w.name
            just_names.append(workflow_name)
            self.option_workflow_instance['menu'].add_command(
                label=workflow_name,
                command=lambda n=workflow_name: self._handler_workflow_instance_option_changed(n)
            )
        # call the handler method with either the saved instance name, or the top one in the list
        if desired_selected_workflow_name in just_names:
            self._handler_workflow_instance_option_changed(desired_selected_workflow_name)
        else:
            self._handler_workflow_instance_option_changed(just_names[0])

    def _handler_workflow_instance_option_changed(self, new_value: str):
        """This is called when the workflow instance option menu changes value"""
        # store the new instance name in the tk var and in the config
        self._tk_var_workflow_instance.set(new_value)
        self.conf.cur_workflow_name = new_value
        # find the new workflow in the list of currently available workflows
        new_workflow = None
        for w in self.available_workflows:
            if w.name == self._tk_var_workflow_instance.get():
                new_workflow = w
                break
        if new_workflow is None:
            messagebox.showerror("There was an unexpected error updating the workflow list, suggest restarting app.")
        # assign the current workflow instance in the workflow manager
        self.workflow_manager.current_workflow = new_workflow
        # update the weather buttons accordingly depending on if the workflow uses weather inputs
        self.set_weather_widget_state(ACTIVE if new_workflow.uses_weather else DISABLED)
        # clear the output menu entirely, and set status conditionally
        self._repopulate_output_suffix_options()
        # now that the workflow has been set, repopulate the file list columns and the file list itself
        self._repopulate_control_list_columns()
        self._update_file_list()

    def _repopulate_output_suffix_options(self):
        suffixes = sorted(self.workflow_manager.current_workflow.output_suffixes)
        combobox_output_enabled = 'readonly' if len(suffixes) > 0 else 'disabled'
        output_enabled = ACTIVE if len(suffixes) > 0 else DISABLED
        self.option_workflow_outputs.configure(state=combobox_output_enabled)
        self.button_open_output_file.configure(state=output_enabled)

        # rebuild the option menu if applicable
        current_selection = self._tk_var_output_suffix.get()
        if output_enabled == ACTIVE:
            self.option_workflow_outputs['values'] = suffixes
            if current_selection not in suffixes:
                self._tk_var_output_suffix.set(suffixes[0])
        else:
            self.option_workflow_outputs['values'] = []
            self._tk_var_output_suffix.set('')
        self.option_workflow_outputs.selection_clear()

    def _open_workflow_dir_dialog(self):
        if len(self.workflow_manager.threads) > 0:
            messagebox.showerror("Workflow Selection Error", 'Cannot change workflows while threads are running')
            return  # will leave the window open
        # refresh the list of workflows auto-found on the machine
        self.workflow_manager.auto_find_workflow_directories()
        # pass the newly found folders in, as well as the current active list of workflow directories
        auto_find_workflows = self.workflow_manager.auto_found_workflow_dirs
        current_workflows = self.workflow_manager.workflow_directories
        wf_dialog = TkWorkflowsDialog(self, list(current_workflows), list(auto_find_workflows))
        self.wait_window(wf_dialog)
        if wf_dialog.exit_code == TkWorkflowsDialog.CLOSE_SIGNAL_CANCEL:
            return
        self.workflow_manager.workflow_directories = wf_dialog.list_of_directories
        self.workflow_manager.instantiate_all_workflows()
        if len(self.workflow_manager.warnings) > 0:
            self.generic_dialogs.display(
                self, 'Workflow Processing Errors', '\n'.join(self.workflow_manager.warnings)
            )
        self.conf.workflow_directories = self.workflow_manager.workflow_directories
        self._repopulate_workflow_context_menu()
        self._repopulate_workflow_instance_menu()

    def _run_workflow(self) -> None:
        if self.conf.directory and self.conf.file_selection and self.workflow_manager.current_workflow:
            pass
        else:
            messagebox.showerror(
                title='Selection Error', message='ERROR: Make sure you select a workflow, directory and a file'
            )
            return

        files_in_current_workflow = self.current_cache.get_files_for_workflow(
            self.workflow_manager.current_workflow.name
        )
        weather_file_to_use: Optional[str] = None
        if self.workflow_manager.current_workflow.uses_weather:
            for selected_file_name in self.conf.file_selection:
                if selected_file_name in files_in_current_workflow:
                    cached_file_info = files_in_current_workflow[selected_file_name]
                    if CacheFile.ParametersKey in cached_file_info:
                        if CacheFile.WeatherFileKey in cached_file_info[CacheFile.ParametersKey]:
                            weather_file_to_use = cached_file_info[CacheFile.ParametersKey][CacheFile.WeatherFileKey]
            if not weather_file_to_use:
                recent_files = list(self.conf.weathers_recent)
                favorite_files = self.conf.weathers_favorite
                w = TkWeatherDialog(self, recent_files, favorite_files)
                self.wait_window(w)
                if w.exit_code == TkWeatherDialog.CLOSE_SIGNAL_CANCEL:
                    return  # might need to do some other clean up
                else:  # a valid response was encountered
                    if not w.selected_weather_file:
                        weather_file_to_use = self.dd_only_string
                    else:
                        weather_file_to_use = str(w.selected_weather_file)
                        if w.selected_weather_file not in self.conf.weathers_recent:
                            self.conf.weathers_recent.appendleft(w.selected_weather_file)
            for selected_file_name in self.conf.file_selection:
                self.current_cache.add_config(
                    self.workflow_manager.current_workflow.name,
                    selected_file_name,
                    {'weather': weather_file_to_use}
                )
            self._update_file_list()

        sel_dir = self.conf.directory
        cur_wf = self.workflow_manager.current_workflow.name
        for selected_file_name in self.conf.file_selection:
            for thread_id, t in self.workflow_manager.threads.items():
                if t.file_name == selected_file_name and t.run_directory == sel_dir and \
                        t.workflow_instance.name() == cur_wf:
                    # self.show_error_message('ERROR: This workflow/dir/file combination is already running')
                    return
            new_uuid = str(uuid4())
            self._update_status_bar('Starting workflow')
            new_instance = self.workflow_manager.current_workflow.workflow_class()
            new_instance.register_standard_output_callback(
                new_uuid,
                self._callback_workflow_stdout
            )
            this_weather = ''
            if weather_file_to_use != self.dd_only_string:
                this_weather = weather_file_to_use
            self.workflow_manager.threads[new_uuid] = WorkflowThread(
                new_uuid, new_instance, self.conf.directory, selected_file_name,
                {
                    'weather': this_weather,
                    'workflow location': self.workflow_manager.current_workflow.workflow_directory
                },
                self._callback_workflow_done
            )
            self.output_dialogs[new_uuid] = self._create_output_dialog(new_uuid)
            self.output_dialogs[new_uuid].add_output("*** STARTING WORKFLOW ***")

        self._update_status_bar("Currently %s processes running" % len(self.workflow_manager.threads))

    def _create_output_dialog(self, workflow_id: str) -> TkOutputDialog:
        """Generates an output dialog with the specified ID, updating dialog counter and setting dialog position"""
        max_dialog_vertical_increments = 5.0
        self.dialog_counter += 1
        if self.dialog_counter == max_dialog_vertical_increments:
            self.dialog_counter = 1

        this_workflow = self.workflow_manager.threads[workflow_id]

        x_right_edge = self.winfo_x() + self.winfo_width()
        y_top = self.winfo_y()
        vertical_increment = int(self.winfo_height() / max_dialog_vertical_increments / 2.0)
        this_x = x_right_edge + 5
        this_y = y_top + vertical_increment * (self.dialog_counter - 1)
        thread_data = self.workflow_manager.threads[workflow_id]
        config_string = dumps(
            {
                'workflow_name:': thread_data.workflow_instance.name(),
                'workflow_dir': str(thread_data.workflow_directory),
                'file_name:': thread_data.file_name,
                'run_directory:': str(thread_data.run_directory),
            },
            indent=2
        )
        return TkOutputDialog(
            self,
            workflow_id,
            this_workflow.workflow_instance.name(),
            config_string,
            this_x,
            this_y
        )

    def _callback_workflow_done(self, workflow_response: EPLaunchWorkflowResponse1) -> None:
        self._gui_queue.put(lambda: self._handler_workflow_done(workflow_response))

    def _handler_workflow_done(self, workflow_response: EPLaunchWorkflowResponse1) -> None:
        try:
            if workflow_response.success:
                status_message = 'Successfully completed a workflow: ' + workflow_response.message
                try:
                    data_from_workflow = workflow_response.column_data
                    workflow_working_directory = self.workflow_manager.threads[workflow_response.id].run_directory
                    workflow_directory_cache = CacheFile(workflow_working_directory)
                    workflow_directory_cache.add_result(
                        self.workflow_manager.threads[workflow_response.id].workflow_instance.name(),
                        self.workflow_manager.threads[workflow_response.id].file_name,
                        data_from_workflow
                    )
                    if self.conf.directory == workflow_working_directory:
                        # only update file lists if we are still in that directory
                        self._update_file_list()
                except EPLaunchFileException:
                    pass
                if not self.conf.keep_dialog_open:
                    self.output_dialogs[workflow_response.id].close()
            else:
                status_message = 'Workflow failed: ' + workflow_response.message
                self.output_dialogs[workflow_response.id].add_output('Workflow FAILED: ' + workflow_response.message)
                self.output_dialogs[workflow_response.id].add_output("*** WORKFLOW FINISHED ***")
        except Exception as e:  # noqa -- there is *no* telling what all exceptions could occur inside a workflow
            print(e)
            status_message = 'Workflow response was invalid'
        self._update_status_bar(status_message)
        try:
            del self.workflow_manager.threads[workflow_response.id]
        except Exception as e:
            print(e)
        self._update_status_bar("Currently %s processes running" % len(self.workflow_manager.threads))

    def _callback_workflow_stdout(self, workflow_id: str, message: str) -> None:
        self._gui_queue.put(lambda: self._handler_workflow_stdout(workflow_id, message))

    def _handler_workflow_stdout(self, workflow_id: str, message: str) -> None:
        if workflow_id in self.output_dialogs:
            if self.output_dialogs[workflow_id].winfo_exists():
                self.output_dialogs[workflow_id].add_output(message)

    # endregion

    # region misc dialog and external tool launchers

    def _open_viewers_dialog(self) -> None:
        if self.workflow_manager.current_workflow:
            output_suffixes = self.workflow_manager.current_workflow.output_suffixes
        else:
            output_suffixes = []
        viewer_dialog = TkViewerDialog(self, output_suffixes, self.conf.viewer_overrides)
        self.wait_window(viewer_dialog)
        if viewer_dialog.exit_code == TkViewerDialog.CLOSE_SIGNAL_CANCEL:
            return
        self.conf.viewer_overrides = {
            **viewer_dialog.extension_to_viewer, **self.conf.viewer_overrides
        }

    def _open_welcome(self):
        if self.conf.welcome_shown and VERSION == self.conf.latest_welcome_shown:
            return
        message = """
EP-Launch has been around for many years as a part of the EnergyPlus distribution.
Starting with the 3.0 release, it has changed drastically, completely redesigned and rewritten.
For full documentation or a quick start guide, click the "Open Docs" button below.
This dialog will only be shown once, but documentation is available in the Help menu."""
        self.generic_dialogs.display(
            self, 'Welcome to EP-Launch ' + VERSION, message, 'Open Documentation', self._open_documentation
        )
        self.conf.welcome_shown = True
        self.conf.latest_welcome_shown = VERSION

    def _open_about(self) -> None:
        text = """
EP-Launch

EP-Launch is a graphical workflow manager for EnergyPlus.
Originally written in VB6 and released with essentially every version of EnergyPlus,
it is now a cross platform Python tool.
Users are encouraged to leverage EP-Launch and write their own workflow scripts
to enable new capabilities.

Version %s
Copyright (c) 2023, Alliance for Sustainable Energy, LLC  and GARD Analytics, Inc

Redistribution and use in source and binary forms, with or without
modification, are permitted provided that the following conditions are met:

* Redistributions of source code must retain the above copyright notice, this
 list of conditions and the following disclaimer.

* Redistributions in binary form must reproduce the above copyright notice,
this list of conditions and the following disclaimer in the documentation
and/or other materials provided with the distribution.

* The name of the copyright holder(s), any contributors, the United States
Government, the United States Department of Energy, or any of their employees
may not be used to endorse or promote products derived from this software
without specific prior written permission from the respective party.

THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDER(S) AND ANY CONTRIBUTORS
"AS IS" AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO,
THE IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR
PURPOSE ARE DISCLAIMED. IN NO EVENT SHALL THE COPYRIGHT HOLDER(S), ANY ,
CONTRIBUTORS THE UNITED STATES GOVERNMENT, OR THE UNITED STATES DEPARTMENT
OF ENERGY, NOR ANY OF THEIR EMPLOYEES, BE LIABLE FOR ANY DIRECT, INDIRECT,
INCIDENTAL, SPECIAL, EXEMPLARY, OR CONSEQUENTIAL DAMAGES (INCLUDING, BUT
NOT LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR SERVICES; LOSS OF USE,
DATA, OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER CAUSED AND ON ANY THEORY
OF LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY, OR TORT (INCLUDING
NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE OF THIS SOFTWARE,
EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.
        """ % VERSION
        self.generic_dialogs.display(self, "About EP-Launch", text)

    def _open_output_file(self):
        if len(self.conf.file_selection) > 2:
            message = """More than 2 files were selected when choosing to open workflow outputs.
This could generate many output windows and is usually not intentional.  Select up to 2 input files."""
            messagebox.showerror("File Selection Issue", message)
            return
        for f in self.conf.file_selection:
            original_path = self.conf.directory / f
            new_path_str = str(original_path.with_suffix('')) + self._tk_var_output_suffix.get()
            new_path = Path(new_path_str)
            if not new_path.exists():
                message = """At least some of the output files were not found.
Make sure that the workflow has run on the selected input file(s), and that the runs
actually generated the requested outputs.  Any found output files are being opened now."""
                messagebox.showwarning("Missing Output Files", message)
            if self._tk_var_output_suffix.get() in self.conf.viewer_overrides:
                if self.conf.viewer_overrides[self._tk_var_output_suffix.get()] is not None:
                    # then the viewer override was found, and not None, so use it
                    Popen([str(self.conf.viewer_overrides[self._tk_var_output_suffix.get()]), new_path_str])
                    return
            # if we make it this far, we didn't open it with a custom viewer, try to use the default
            self._open_file_or_dir_with_default(new_path)

    @staticmethod
    def _open_file_or_dir_with_default(full_path_obj: Path) -> None:
        full_path = str(full_path_obj)
        if system() == 'Windows':
            from os import startfile
            startfile(full_path)
        elif system() == 'Linux':
            Popen(['xdg-open', full_path])
        else:  # assuming Mac
            Popen(['open', full_path])

    def _open_text_editor(self) -> None:
        for file_name in self.conf.file_selection:
            full_path_str = self.conf.directory / file_name
            if 'txt' in self.conf.viewer_overrides:
                text_editor_binary = str(self.conf.viewer_overrides['txt'])
                Popen([text_editor_binary, full_path_str])
            else:
                self._open_file_or_dir_with_default(full_path_str)

    def _open_file_browser(self) -> None:
        self._open_file_or_dir_with_default(self.conf.directory)

    @staticmethod
    def _open_documentation() -> None:
        open_web(DOCS_URL)

    # endregion


if __name__ == "__main__":
    window = EPLaunchWindow()
    window.run()
