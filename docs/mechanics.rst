Application Mechanics
=====================

This document is heavily geared toward developers interested in understanding or modifying the EP-Launch code itself.
This document explains several parts of the operation and mechanics of the main EP-Launch app frame.

Frame Ownership and Management
------------------------------

The app is generally launched using the ``energyplus_launch/runner.py`` script.  The script only does two core operations:

- Instantiation of the application, an instance of the ``EPLaunchApplication`` class
- Execution of the main program loop, using the ``MainLoop`` function

The entire life cycle of the program is contained within this call to the main program loop.
This includes all user-triggered events, and the code that handles it, except for one known item.
Whenever a workflow is executed, a new background process, possibly with additional children processes, is spawned.
If the main interface is killed, some of these processes may remain as orphaned processes.
The main application tries to avoid allowing this to occur by blocking closing events when threads are running.
However, it is possible to kill the main interface while child processes are running.

Application Class
-----------------

The application is built around the ``wx.App`` base class, deriving it, and calling it ``EpLaunchApplication``.
During instantiation, the derived class overrides the base class constructor only to initialize a member variable.
During the OnInit call, the derived class follows these steps:

- Instantiation of the frame class, an instance of the ``EpLaunchFrame`` class
- Setting this as the top-level window for this application
- Showing the frame instance

Frame Class
-----------

The frame class is where nearly all the program logic lives.
Because of the nature of the workflows and caching, it is easy to get confused about events, threads, and handlers.
This section of the documentation will attempt to break this into smaller, easier to understand, pieces.

Construction
************

Construction of the frame class is comprised of the following process:

- Creating a configuration class instance
- Set up instances of support classes
- Initializing many member variables to avoid warnings
- Initial workflow setup:

  - Retrieve any saved configuration around the workflow directories
  - Set ``list_of_versions`` member variable by calling the ``get_energyplus_versions`` method on the workflow support class
  - Update the workflow array member variable by calling the ``update_workflow_array`` method on the frame

- Perform the GUI build, including the main frame elements, menu bar, toolbars, and status bar
- Initialize the raw file list column names and the running number of processes member variables
- Get the potentially previously saved working directory and attempt to browse to it in the tree view
- Check to see if a specific version of E+ is selected and store that if so
- Update the workflow list by filtering to a possible E+ version
- Check to see if the user's last workflow was saved in the config, and store that if so
- Update the workflow combobox with the list of workflows
- Create and subscribe to a cross-thread workflow complete event using the ``pubsub`` structure
- There are then a few processes called during construction that are also called frequently throughout operation:

  - Update control file columns, as they are different based on the selected workflow
  - Update file lists, as they are different for each folder explored
  - Update workflow dependent menu items, as some items need to be reset based on the selected workflow

Details on the GUI Build Process
********************************

Building out the GUI begins with a call to ``gui_build_menu_bar`` which is responsible for building out the main menu for the app.
The content there is primarily static, but there are a few dynamic pieces:

- The Workflows top-level menu contains a list of menu items each corresponding to an imported workflow.
  These menu items are associated with a zero-based ID that mimics the index in the workflow combobox.
- Weather files, recent folders, favorite folders are all examples of menus that are dynamically updated
- The Workflow Directories menu item allows a user to specify additional folders for finding workflows

Once complete, the menubar is set as the frame's primary menu bar using the ``SetMenuBar`` function.
Once the menu bar is built out, the main pieces of the interface are built.
The directory tree, control file list, and raw file list are all built out and added to sizers.
The main vertical sizer is then created to hold the primary toolbar, the output toolbar, and the main element sizer.

The primary toolbar has the added complexity of managing the workflow combobox (on some platforms).
On Mac machines, the ``workflow_choice`` is constructed, but never assigned to a parent or added to a toolbar.
The Mac has known issues with comboboxes on toolbars that are not the _primary_ toolbar for the frame.
On other platforms, the ``workflow_choice`` is constructed and assigned to the primary toolbar

The output toolbar is a simple list of icons that is generated dynamically for each workflow selection.
A status bar is then created on the frame at the bottom.
To wrap up the GUI build, the frame is resized, attempting to match the state of the frame at last closing.




