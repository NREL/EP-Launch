Workflows
=========

Starting with EP-Launch 3.0, the code has been 100% rewritten from VB6 to Python, with an eye toward creating a cross-platform tool that can be developed, built, and packaged easily by many developers.
Also at the heart of this new version of EP-Launch is something called "Workflows."

Quickstart Using EnergyPlus Workflows
-------------------------------------

Although EP-Launch is packaged up with some built-in workflows, the power of EP-Launch is exercised through using workflows with external tools.
As EP-Launch has historically been geared toward supporting EnergyPlus, this is the natural first starting point.
Starting with version 9.0, in September 2018, EnergyPlus will be packaged with workflows for exercising its own utilities.
As of this writing, the EnergyPlus packages will come with workflows for running:

- EnergyPlus itself (along with pre- and post-processors), in both SI and IP unit conventions
- The CalcSoilSurfTemp ground temperature calculator
- The CoeffConv conversion utility
- The CoeffCheck unit utility
- The AppendixG post processor

Each platform has a "standard" EnergyPlus installation folder:

- ``C:\EnergyPlus-VX-Y-Z`` on Windows
- ``/Applications/EnergyPlus-X-Y-Z`` on Mac
- ``/usr/local/bin/EnergyPlus-X-Y-Z`` on Linux

If EnergyPlus is installed in a standard location, the EP-Launch tool will be able to find the workflows for that installation.
If EnergyPlus is installed in a different location, you can still point EP-Launch to that directory using the Settings->WorkflowDirectories dialog.
In the same manner, if workflows are created in a totally unrelated directory, use that same dialog to point EP-Launch to those workflows.

Once workflows have been processed by EP-Launch, they are available in the menu bar in the workflows menu item.
On Windows and Linux they are also available in the combobox in the toolbar.
On Mac, there is a known issue with this dropdown, so it isn't available there.
Once EP-Launch is ready with workflows, simply select a workflow from the list.
The available files in the control file list will filter down to the file extension defined by the workflow.
If the workflow is applicable to ``*.txt`` files, then only text files in the currently selected file will be shown.
As a quick start, browse to the EnergyPlus install folder, into the weather directory.
Then select the ``CalcSoilSurfTemp`` workflow from the dropdown or menu bar.
Select a weather file in the file listing, and click Run in the toolbar or menu bar.
The program should start and run instantly, and the column data in the file listing will be updated with output parameters.

Definition
----------

Now we'll dig into the details of the workflow.  A workflow can be defined as:

- a Python class,
- that inherits from an EP-Launch Workflow base class, and
- properly overrides all abstract methods on the base class.

Example
-------

Let's jump right in with an example of a workflow.
To begin, we must know enough about the base class to know what methods we need to override.
For base class ``BaseEPLaunchWorkflow1``, the methods that must be overridden are:

- ``name()``  (returns a string)
- ``description()``  (returns a string)
- ``get_file_types()``  (returns a list of file extensions)
- ``get_output_suffixes()``  (returns a list of output file suffixes)
- ``main()``  (main operation, returns an instance of an ``EPLaunchWorkflowResponse1``

Another function of interest that can be overridden is the ``get_interface_columns()``, which is used to pass data back to the GUI.

Now that we know what methods need to be written, let's just write out a workflow.
For this example, a workflow named "dummy" will be written that operates on ".txt" files, and returns data in the "foo" column.
Here's the entire code for the workflow, followed by commentary::

    from eplaunch.workflows.base import BaseEPLaunchWorkflow1, EPLaunchWorkflowResponse1
    class SiteLocationWorkflow(BaseEPLaunchWorkflow1):
        def name(self):
            return 'foo'
        def description(self):
            return 'Foo workflow'
        def get_file_types(self):
            return ['*.txt']
        def get_output_suffixes(self):
            return []
        def get_interface_columns(self):
            return ['foo']
        def main(self, run_directory, file_name, args):
            return EPLaunchWorkflowResponse1(success=True, message='Hello', column_data={'foo': 'bar'})

We'll run through this code line by line:

1. We first import the required base classes so we can inherit the base workflow, and return an instance of the expected return type.
2. We create a Python class that inherits from the base class.
3. We override the ``name`` function,
4. and return a suitable name for our workflow.
5. We override the ``description`` function,
6. and return a suitable description for our workflow.
7. We override the ``get_file_types`` function,
8. and return a list of file extensions; for this workflow, it's just one: ``.txt``
9. We override the ``get_output_suffixes`` function,
10. and return an empty array, since no output files will be associated with this workflow
11. We override the ``get_interface_columns`` function,
12. and return an array of column names; for this workflow, it's just one: ``foo``
13. We override the ``main`` function,
14. and return a trivial ``EPLaunchWorkflowResponse1`` instance, with a hello response message, and column data containing one key (foo) and the value (bar)

Actual Workflow Operation
-------------------------

When a workflow run is started, the following process is put into motion:

- Verify that this workflow is not already being run (uniqueness is calculated through workflow name, run directory, and run file)
- Generate a new unique identifier for this particular workflow run
- Create a new instance of the workflow
- Store the unique id, and an instantiated callback function with the workflow base class, so that the workflow can easily call back to the GUI
- Create a new workflow thread instance with all the data required to setup the workflow run (constructor will also run the workflow)
- Create and show a dialog with parameters and output from the workflow run
- Update the GUI to reflect a workflow is running

When a workflow calls back with progress updates, the update comes with the unique identifier created for that run.
The update triggers the workflow output dialog to update the textbox to include the updated information.

When a workflow is completed, the following series of events occur:

- The workflow status flag is checked, and if it was NOT successful, the output dialog is left with additional info and held open for the user to inspect
- If the workflow was successful, additional information is mined from the run, including the run directory and file name
- Mined information is used to determine if the current file list should be refreshed to reflect updated outputs from the workflow run
- The workflow output dialog is closed, the status bar is updated, and the workflow thread is deleted
