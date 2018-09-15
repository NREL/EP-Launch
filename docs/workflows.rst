Workflows
=========

Starting with EP-Launch 3.0, the code has been 100% rewritten from VB6 to Python, with an eye toward creating a cross-platform tool that can be developed, built, and packaged easily by many developers.
Also at the heart of this new version of EP-Launch is something called "Workflows."

Definition
----------

A workflow can be defined as:

- a Python class,
- that inherits from an EP-Launch Workflow base class, and
- properly overrides all abstract methods on the base class.

Some additional interesting features:

- A workflow has a context function that allows the EPLaunch interface to do grouping of related workflows.

  - If multiple workflow files are packaged up with one tool, like they are with EnergyPlus, all those workflows should have the same context.
  - If the workflow is tied to a specific version of a piece of software, and you might have more than one version on your computer, the context should have the version number in it.

Example
-------

Let's move now to an example of a workflow.
To begin, we must know enough about the base class to know what methods we need to override.
For base class ``BaseEPLaunchWorkflow1``, the methods that must be overridden are:

- ``name()``  (returns a string)
- ``context()``  (returns a string)
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
        def context(self):
            return 'my_workflow_collection'
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
5. We override the ``context`` function,
6. and return a suitable context for this workflow.
7. We override the ``description`` function,
8. and return a suitable description for our workflow.
9. We override the ``get_file_types`` function,
10. and return a list of file extensions; for this workflow, it's just one: ``.txt``
11. We override the ``get_output_suffixes`` function,
12. and return an empty array, since no output files will be associated with this workflow
13. We override the ``get_interface_columns`` function,
14. and return an array of column names; for this workflow, it's just one: ``foo``
15. We override the ``main`` function,
16. and return a trivial ``EPLaunchWorkflowResponse1`` instance, with a hello response message, and column data containing one key (foo) and the value (bar)

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

Workflow Testing
----------------

A standalone tool has been developed to allow users to test their workflows.
This tool is available as a plain Python script in the repository, and a packaged executable for Linux.
Windows and Mac executables will come soon.

The script accepts one command line argument, the path to the workflow to test.
Consider the workflow that was created for the example above.
If we run that through the test script, this is the output::

    ./EpLaunchWorkflowTester /tmp/example_workflow.py
       OK: File path exists at: /tmp/example_workflow.py
       OK: File ends with .py
       OK: Python import process completed successfully!
     INFO: Encountered class: "BaseEPLaunchWorkflow1", testing now...
     INFO: Inheritance does not check out, will continue with other classes in this file
     INFO: Encountered class: "EPLaunchWorkflowResponse1", testing now...
     INFO: Inheritance does not check out, will continue with other classes in this file
     INFO: Encountered class: "SiteLocationWorkflow", testing now...
       OK: Basic inheritance checks out OK for class: SiteLocationWorkflow
       OK: Instantiation of derived class works
       OK: Overridden name() function execution works
       OK: Overridden get_file_types() function execution works
       OK: Overridden get_output_suffixes() function execution works
       OK: Overridden get_interface_columns() function execution works
       OK: Overridden context() function execution works
       OK: Found 1 successful workflow imports

This output was generated using the packaged tool.

If running from the Python script, you would need to execute using Python, and ensure that the PYTHONPATH includes the folder where EPLaunch can be accessed.
The command line, if run from the root of the repository would bee::

    PYTHONPATH="." python3 eplaunch/workflows/workflow_tester.py /tmp/example_workflow.py

The tester checks some basic file details, then loops over all classes encountered in the file and validates them.
Note that classes found in the module include classes that are imported, so even though we only defined one workflow class, it checks four.
The final note summarizes the results of the test.
The process return code also captures the success/failure:

- 0: success
- 1: failure due to bad workflow file
- 2: failure for some other reason

Checking these error codes can allow groups of workflow files to be tested in an automated fashion.
