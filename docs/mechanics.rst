Application Mechanics
=====================

This document is heavily geared toward developers interested in understanding or modifying the EP-Launch code itself.
This document explains several parts of the operation and mechanics of the main EP-Launch app frame.

Frame Ownership and Management
------------------------------

The app is generally launched using the ``eplaunch/runner.py`` script.  The script only does two core operations:

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
- Create and subscribe to a cross-thread workflow complete event using the ``pubsub`` structure
- There are then a few processes called during construction that are also called frequently throughout operation:

  - Update control file columns, as they are different based on the selected workflow
  - Update file lists, as they are different for each folder explored
  - Update workflow dependent menu items, as some items need to be reset based on the selected workflow


